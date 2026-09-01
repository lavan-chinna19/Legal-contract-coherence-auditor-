"""
src/xai/sensitivity.py — Channel B Perturbation Sensitivity Analysis.
"""
import uuid
import datetime
from typing import List, Optional

from src.config import ClauseRecord
from src.scoring.channel_b import ChannelBScorer
from src.xai.schema import ExplanationResult, SensitivityExplanation, ClaimScope


class ChannelBSensitivityAnalyzer:
    """
    Measures the sensitivity of the Channel B (Coherence) anomaly score
    to perturbations in neighboring clauses.
    """
    def __init__(self, channel_b_scorer: ChannelBScorer):
        self.scorer = channel_b_scorer

    def explain(self, target_clause: ClauseRecord, doc_clauses: List[ClauseRecord]) -> ExplanationResult:
        """
        Computes sensitivity of the target clause's anomaly score to its immediate neighbors.
        """
        # Find index of target clause
        try:
            idx = next(i for i, c in enumerate(doc_clauses) if c.clause_id == target_clause.clause_id)
        except StopIteration:
            raise ValueError("Target clause not found in document clauses.")

        # Compute baseline scores for the entire document
        baseline_scores = self.scorer.score_document_clauses(doc_clauses)
        baseline_score, _ = baseline_scores[idx]

        neighbors = []
        if idx > 0:
            neighbors.append((idx - 1, "prev"))
        if idx < len(doc_clauses) - 1:
            neighbors.append((idx + 1, "next"))

        best_delta = 0.0
        best_explanation = None

        for n_idx, position in neighbors:
            neighbor = doc_clauses[n_idx]
            
            # Perturb the neighbor clause (mask it out)
            perturbed_doc = list(doc_clauses)
            perturbed_doc[n_idx] = ClauseRecord(
                doc_id=neighbor.doc_id,
                clause_id=neighbor.clause_id + "_masked",
                text="[MASK]",  # Perturbation: replacing context with empty string/mask
                sequence_idx=neighbor.sequence_idx,
                label=neighbor.label,
                char_start=neighbor.char_start,
                char_end=neighbor.char_end,
                source=neighbor.source
            )

            # Recompute scores
            perturbed_scores = self.scorer.score_document_clauses(perturbed_doc)
            perturbed_score, _ = perturbed_scores[idx]
            
            delta = abs(baseline_score - perturbed_score)
            
            # Record the neighbor with the highest sensitivity impact
            if best_explanation is None or delta > best_delta:
                best_delta = delta
                best_explanation = SensitivityExplanation(
                    neighbor_clause_id=neighbor.clause_id,
                    neighbor_position=position,
                    original_score=round(float(baseline_score), 4),
                    perturbed_score=round(float(perturbed_score), 4),
                    score_delta=round(float(delta), 4),
                    perturbation_method="mask_neighbor_text"
                )

        if best_explanation is None:
            # Fallback if no neighbors (single-clause document)
            best_explanation = SensitivityExplanation(
                neighbor_clause_id="NONE",
                neighbor_position="none",
                original_score=round(float(baseline_score), 4),
                perturbed_score=round(float(baseline_score), 4),
                score_delta=0.0,
                perturbation_method="none"
            )

        claim_scope = ClaimScope(
            what_this_shows="This perturbation measures how sensitive the model score is to this neighboring content under the tested intervention.",
            what_this_does_not_show="It does not establish that the neighbor is legally responsible for the anomaly or that the observed relationship is causal."
        )

        return ExplanationResult(
            explanation_id=str(uuid.uuid4()),
            doc_id=target_clause.doc_id,
            clause_id=target_clause.clause_id,
            explanation_type="SENSITIVITY",
            model_version=self.scorer.coherence_model.name,
            timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            claim_scope=claim_scope,
            sensitivity_payload=best_explanation
        )
