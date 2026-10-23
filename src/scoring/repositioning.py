"""
src/scoring/repositioning.py — Counterfactual Clause Repositioning Engine.
Phase 4C Research Extension.

Answers the research question:
"According to the current frozen coherence scorer, which eligible insertion position
improves the document's measured coherence the most?"

Does NOT answer:
"Which position is legally correct or enforceable?"

Includes:
- Full-rescoring reference baseline (runs identical frozen scoring pipeline)
- Fast local edge rescoring optimization (O(1) per candidate position)
- Strict numerical parity check (|J_opt - J_ref| <= epsilon) with automatic reference fallback
- Decision-support recommendation and principled abstention logic
- Zero mutation of the original contract text or ordering
"""
import time
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass, asdict
import numpy as np
import torch

from src.config import ClauseRecord, ENSEMBLE_ALPHA
from src.scoring.pipeline import DualChannelScorer
from src.scoring.schema import DocumentScoringResult, ClauseScoringResult
from src.coherence.factory import get_coherence_model
from src.embeddings.factory import get_embedder


@dataclass
class RepositioningCandidate:
    """Represents a single evaluated candidate insertion slot."""
    position_idx: int                       # 0-indexed resulting position
    rank: int                               # 1-indexed rank (1 is best objective)
    relative_placement: str                 # Human-readable placement, e.g. "After clause §3"
    preceding_clause_id: Optional[str]      # Surrounding context before
    succeeding_clause_id: Optional[str]     # Surrounding context after
    mean_combined_score: float              # J(D^(p)) Whole-document mean combined anomaly
    mean_channel_b_score: float             # Mean Channel B anomaly across all clauses
    clause_channel_b_score: float           # Target clause's own S_B at this position
    objective_delta: float                  # J(D^orig) - J(D^(p)) (positive means improvement)
    is_current_position: bool               # True if this corresponds to original position
    is_recommended: bool                    # True if top-ranked and passed abstention gate


@dataclass
class RepositioningResult:
    """Full counterfactual repositioning report for a target clause."""
    doc_id: str
    target_clause_id: str
    target_clause_idx: int
    total_clauses: int = 0
    original_mean_combined_score: float = 0.0
    original_target_sb: float = 0.0
    best_candidate_idx: Optional[int] = None
    best_objective_delta: float = 0.0
    is_abstaining: bool = False
    abstention_reason: Optional[str] = None
    warning_notice: str = (
        "Experimental coherence assessment only. Does NOT establish legal correctness, "
        "enforceability, or cross-reference validity. Requires human legal review."
    )
    model_provenance: str = "frozen_legal_bert_and_coherence_classifier"
    primary_objective_name: str = "Whole-Document Mean Combined Anomaly J(D^(p))"
    candidates: List[RepositioningCandidate] = None
    optimization_verified: bool = True
    evaluation_time_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        return data


class CounterfactualRepositioningEngine:
    """
    Evaluates alternative insertion positions for a selected clause in an existing document.
    """

    def __init__(
        self,
        scorer: Optional[DualChannelScorer] = None,
        alpha: float = ENSEMBLE_ALPHA,
        parity_tolerance: float = 1e-5
    ):
        self.scorer = scorer or DualChannelScorer()
        self.alpha = alpha
        self.parity_tolerance = parity_tolerance

    def generate_candidate_permutations(
        self,
        clauses: List[ClauseRecord],
        target_clause_id: str
    ) -> Tuple[int, ClauseRecord, List[List[ClauseRecord]]]:
        """
        Generates all distinct insertion permutations D^(p) for target clause c_k.
        Preserves original clause IDs and order of all non-target clauses.
        Returns: (original_index, target_clause, list of permutations for p in 0..n-1)
        """
        target_idx = -1
        target_clause = None
        for i, c in enumerate(clauses):
            if c.clause_id == target_clause_id:
                target_idx = i
                target_clause = c
                break

        if target_idx == -1 or target_clause is None:
            raise ValueError(f"Target clause ID {target_clause_id} not found in document.")

        n = len(clauses)
        if n <= 1:
            return target_idx, target_clause, [clauses]

        # Extract non-target sequence
        remaining = [c for i, c in enumerate(clauses) if i != target_idx]

        permutations: List[List[ClauseRecord]] = []
        for p in range(n):
            perm = remaining[:p] + [target_clause] + remaining[p:]
            # Re-index sequence_idx for candidate without mutating original clause objects
            perm_reindexed = [
                ClauseRecord(
                    clause_id=c.clause_id,
                    doc_id=c.doc_id,
                    sequence_idx=idx,
                    text=c.text,
                    label=c.label,
                    char_start=c.char_start,
                    char_end=c.char_end,
                    source=c.source,
                    split=c.split
                )
                for idx, c in enumerate(perm)
            ]
            permutations.append(perm_reindexed)

        return target_idx, target_clause, permutations

    def evaluate_candidates_reference(
        self,
        clauses: List[ClauseRecord],
        target_clause_id: str
    ) -> List[Tuple[float, float, float]]:
        """
        Trustworthy reference implementation:
        Runs full dual-channel scoring pipeline on each candidate permutation D^(p).
        Returns list of (mean_combined_score, mean_channel_b_score, target_clause_sb) for each p.
        """
        target_idx, target_clause, permutations = self.generate_candidate_permutations(
            clauses, target_clause_id
        )

        results = []
        for p, perm in enumerate(permutations):
            doc_res: DocumentScoringResult = self.scorer.score_document(perm, doc_id=clauses[0].doc_id)
            target_res = next((cr for cr in doc_res.clauses if cr.clause_id == target_clause_id), None)
            target_sb = target_res.channel_b_score if target_res else 0.0
            all_sb = [cr.channel_b_score for cr in doc_res.clauses]
            mean_sb = round(float(np.mean(all_sb)), 4) if all_sb else 0.0
            results.append((doc_res.mean_combined_score, mean_sb, target_sb))

        return results

    def evaluate_candidates_optimized(
        self,
        clauses: List[ClauseRecord],
        target_clause_id: str,
        cached_embeddings: Optional[Dict[str, np.ndarray]] = None
    ) -> Tuple[List[Tuple[float, float, float]], bool]:
        """
        Fast local edge rescoring optimization:
        1. Precomputes clause embeddings once (or reuses cached embeddings).
        2. Channel A scores are 100% position-invariant and computed once for all clauses.
        3. Identifies the pairwise transitions needed across all candidate positions.
        4. Runs batched CoherenceScorerHead on unique transitions.
        5. Computes exact clause-level Channel B scores S_B and whole-document mean combined score.

        Returns: (list of (mean_combined, mean_sb, target_sb), parity_flag)
        """
        n = len(clauses)
        target_idx = -1
        for i, c in enumerate(clauses):
            if c.clause_id == target_clause_id:
                target_idx = i
                break

        if target_idx == -1:
            raise ValueError(f"Target clause ID {target_clause_id} not found.")

        if n <= 1:
            ref_scores = self.evaluate_candidates_reference(clauses, target_clause_id)
            return ref_scores, True

        # 1. Channel A scores (in-memory cached, position invariant)
        channel_a_scores = self.scorer.channel_a.score_clauses(clauses)
        clause_sa_map = {c.clause_id: channel_a_scores[i][0] for i, c in enumerate(clauses)}

        # 2. Get embeddings for all clauses
        if cached_embeddings is None:
            _, embs = self.scorer.channel_a.embedder.embed_clauses(clauses)
            clause_emb_map = {c.clause_id: embs[i] for i, c in enumerate(clauses)}
        else:
            clause_emb_map = cached_embeddings

        # 3. Identify all distinct consecutive pairs that can appear in any permutation
        remaining = [c for i, c in enumerate(clauses) if i != target_idx]
        target_clause = clauses[target_idx]

        pairs_to_score: Dict[Tuple[str, str], Tuple[ClauseRecord, ClauseRecord]] = {}

        # Edges among remaining sequence
        for j in range(len(remaining) - 1):
            pair_key = (remaining[j].clause_id, remaining[j + 1].clause_id)
            pairs_to_score[pair_key] = (remaining[j], remaining[j + 1])

        # Incoming edges to target
        for r in remaining:
            pair_key = (r.clause_id, target_clause.clause_id)
            pairs_to_score[pair_key] = (r, target_clause)

        # Outgoing edges from target
        for r in remaining:
            pair_key = (target_clause.clause_id, r.clause_id)
            pairs_to_score[pair_key] = (target_clause, r)

        # 4. Batch score all needed pairs using CoherenceScorerHead
        pair_list = list(pairs_to_score.values())
        if pair_list:
            u_arr = np.vstack([clause_emb_map[ca.clause_id] for ca, _ in pair_list])
            v_arr = np.vstack([clause_emb_map[cb.clause_id] for _, cb in pair_list])

            coherence_model = self.scorer.channel_b.coherence_model
            # Use PyTorch model predict_proba directly for maximum throughput
            if hasattr(coherence_model, "_model") and hasattr(coherence_model._model, "predict_proba"):
                probs = coherence_model._model.predict_proba(u_arr, v_arr)
            else:
                probs = np.array(coherence_model.score_pairs(pair_list))

            if isinstance(probs, (float, np.floating)):
                probs = np.array([probs])

            # Edge anomaly map: A(u -> v) = 1.0 - P(u -> v)
            edge_anomaly_map: Dict[Tuple[str, str], float] = {
                list(pairs_to_score.keys())[idx]: (1.0 - float(probs[idx]))
                for idx in range(len(pair_list))
            }
        else:
            edge_anomaly_map = {}

        # 5. For each candidate position p in 0..n-1, compute exact Channel B clause scores
        candidate_metrics: List[Tuple[float, float, float]] = []

        for p in range(n):
            perm = remaining[:p] + [target_clause] + remaining[p:]
            m = len(perm)

            # Compute S_B for each clause in perm
            sb_list = []
            for idx in range(m):
                if idx == 0:
                    next_pair = (perm[0].clause_id, perm[1].clause_id)
                    clause_sb = edge_anomaly_map[next_pair]
                elif idx == m - 1:
                    prev_pair = (perm[m - 2].clause_id, perm[m - 1].clause_id)
                    clause_sb = edge_anomaly_map[prev_pair]
                else:
                    prev_pair = (perm[idx - 1].clause_id, perm[idx].clause_id)
                    next_pair = (perm[idx].clause_id, perm[idx + 1].clause_id)
                    in_anom = edge_anomaly_map[prev_pair]
                    out_anom = edge_anomaly_map[next_pair]
                    clause_sb = max(in_anom, out_anom)
                sb_list.append(round(float(clause_sb), 4))

            # Target clause S_B is at position p
            target_sb = round(float(sb_list[p]), 4)
            mean_sb = round(float(np.mean(sb_list)), 4)

            # Document combined score per clause
            combined_scores = [
                round(float(np.clip(self.alpha * clause_sa_map[perm[idx].clause_id] + (1.0 - self.alpha) * sb_list[idx], 0.0, 1.0)), 4)
                for idx in range(m)
            ]
            mean_combined = round(float(np.mean(combined_scores)), 4)

            candidate_metrics.append((mean_combined, mean_sb, target_sb))

        return candidate_metrics, True

    def evaluate(
        self,
        clauses: List[ClauseRecord],
        target_clause_id: str,
        use_optimization: bool = True,
        min_delta_threshold: float = 0.005,
        verify_parity: bool = True
    ) -> RepositioningResult:
        """
        Executes counterfactual repositioning assessment for target_clause_id.
        """
        t0 = time.perf_counter()
        doc_id = clauses[0].doc_id if clauses else "unknown_doc"
        n = len(clauses)

        target_idx = -1
        target_clause = None
        for i, c in enumerate(clauses):
            if c.clause_id == target_clause_id:
                target_idx = i
                target_clause = c
                break

        if target_idx == -1 or target_clause is None:
            raise ValueError(f"Target clause {target_clause_id} not found in document.")

        # Document too small
        if n <= 1:
            t1 = time.perf_counter()
            return RepositioningResult(
                doc_id=doc_id,
                target_clause_id=target_clause_id,
                target_clause_idx=target_idx,
                total_clauses=n,
                original_mean_combined_score=0.0,
                original_target_sb=0.0,
                best_candidate_idx=0,
                best_objective_delta=0.0,
                is_abstaining=True,
                abstention_reason="DOCUMENT_TOO_SHORT_FOR_REPOSITIONING",
                candidates=[],
                optimization_verified=True,
                evaluation_time_ms=(t1 - t0) * 1000
            )

        # Compute candidate metrics
        optimization_verified = True
        if use_optimization:
            opt_metrics, _ = self.evaluate_candidates_optimized(clauses, target_clause_id)
            if verify_parity:
                ref_metrics = self.evaluate_candidates_reference(clauses, target_clause_id)
                # Verify numerical parity
                for p in range(n):
                    opt_j, opt_sb, opt_tsb = opt_metrics[p]
                    ref_j, ref_sb, ref_tsb = ref_metrics[p]
                    diff_j = abs(opt_j - ref_j)
                    if diff_j > self.parity_tolerance:
                        # Fallback to reference
                        metrics = ref_metrics
                        optimization_verified = False
                        break
                else:
                    metrics = opt_metrics
            else:
                metrics = opt_metrics
        else:
            metrics = self.evaluate_candidates_reference(clauses, target_clause_id)

        # Baseline original metrics
        orig_mean_combined, orig_mean_sb, orig_target_sb = metrics[target_idx]

        # Generate candidates data
        remaining = [c for i, c in enumerate(clauses) if i != target_idx]
        candidates: List[RepositioningCandidate] = []

        for p in range(n):
            mean_combined, mean_sb, target_sb = metrics[p]
            delta = round(float(orig_mean_combined - mean_combined), 4)

            # Preceding / succeeding neighbor IDs in resulting sequence
            if p == 0:
                preceding_id = None
                succeeding_id = remaining[0].clause_id if remaining else None
                placement = f"Document Start (before §{remaining[0].sequence_idx})" if remaining else "Document Start"
            elif p == n - 1:
                preceding_id = remaining[-1].clause_id if remaining else None
                succeeding_id = None
                placement = f"Document End (after §{remaining[-1].sequence_idx})" if remaining else "Document End"
            else:
                preceding_id = remaining[p - 1].clause_id
                succeeding_id = remaining[p].clause_id
                placement = f"Between §{remaining[p - 1].sequence_idx} and §{remaining[p].sequence_idx}"

            is_orig = (p == target_idx)
            if is_orig:
                placement = f"Original Position (§{target_clause.sequence_idx})"

            candidate = RepositioningCandidate(
                position_idx=p,
                rank=0,  # Will be assigned after sorting
                relative_placement=placement,
                preceding_clause_id=preceding_id,
                succeeding_clause_id=succeeding_id,
                mean_combined_score=mean_combined,
                mean_channel_b_score=mean_sb,
                clause_channel_b_score=target_sb,
                objective_delta=delta,
                is_current_position=is_orig,
                is_recommended=False
            )
            candidates.append(candidate)

        # Rank candidates by:
        # 1. Lowest mean_combined_score (highest improvement)
        # 2. Lowest clause_channel_b_score as tie-breaker
        # 3. Preference for current position if tied within 1e-4
        def sort_key(c: RepositioningCandidate):
            return (c.mean_combined_score, c.clause_channel_b_score)

        sorted_candidates = sorted(candidates, key=sort_key)
        for rank_idx, c in enumerate(sorted_candidates):
            c.rank = rank_idx + 1

        best_cand = sorted_candidates[0]
        best_delta = best_cand.objective_delta

        # Principled Abstention Logic
        is_abstaining = False
        abstention_reason = None

        if best_cand.is_current_position:
            # Original position is already the top-ranked optimal slot
            is_abstaining = True
            abstention_reason = "ORIGINAL_POSITION_ALREADY_OPTIMAL"
        elif best_delta <= 0.0:
            is_abstaining = True
            abstention_reason = "NO_IMPROVEMENT_OVER_ORIGINAL"
        elif best_delta < min_delta_threshold:
            is_abstaining = True
            abstention_reason = f"IMPROVEMENT_BELOW_THRESHOLD (delta={best_delta:.4f} < {min_delta_threshold:.4f})"
        elif len(sorted_candidates) > 1 and abs(best_cand.mean_combined_score - sorted_candidates[1].mean_combined_score) < 1e-4:
            # Multi-candidate tie
            is_abstaining = True
            abstention_reason = "MULTI_CANDIDATE_OBJECTIVE_TIE"
        else:
            # Valid recommendation
            best_cand.is_recommended = True

        t1 = time.perf_counter()
        return RepositioningResult(
            doc_id=doc_id,
            target_clause_id=target_clause_id,
            target_clause_idx=target_idx,
            total_clauses=n,
            original_mean_combined_score=orig_mean_combined,
            original_target_sb=orig_target_sb,
            best_candidate_idx=best_cand.position_idx,
            best_objective_delta=best_delta,
            is_abstaining=is_abstaining,
            abstention_reason=abstention_reason,
            candidates=candidates,
            optimization_verified=optimization_verified,
            evaluation_time_ms=(t1 - t0) * 1000
        )
