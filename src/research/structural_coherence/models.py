"""
src/research/structural_coherence/models.py — Candidate Models and Baselines for Structural Coherence.
Phase 4D-B Research Extension.

Implements:
- Baseline B0: Frozen Channel B (Pairwise Transition Scorer)
- Baseline B1: Production Dual-Channel Ensemble (Frozen Production Formula)
- Baseline B2: Adjacent Cosine Similarity Baseline
- Candidate C1: Contextual Boundary Contrast Detector (Feature-Based)
- Candidate C2: Global Contextual Sequence Coherence Model (Lightweight BiLSTM Head)
- Candidate C3: Structure-Aware Topological Dependency Model (Graph-Based)
"""
import time
from typing import List, Tuple, Dict, Optional, Any
import numpy as np
import torch
import torch.nn as nn

from src.config import ClauseRecord, ENSEMBLE_ALPHA
from src.embeddings.factory import get_embedder
from src.coherence.factory import get_coherence_model
from src.scoring.pipeline import DualChannelScorer
from src.research.structural_coherence.schema import (
    DocumentStructuralResult,
    ClauseStructuralScore,
    BoundaryEvidence
)
from src.research.structural_coherence.features import (
    extract_contextual_window_distances,
    extract_progression_discordance,
    extract_boundary_contrast,
    infer_clause_lifecycle_stage
)


# ==============================================================================
# BASELINES
# ==============================================================================

class BaselineB0_ChannelB:
    """Baseline B0: Original frozen Channel B pairwise coherence model."""
    name = "Baseline_B0_FrozenChannelB"
    version = "1.0.0_frozen"

    def __init__(self, threshold: float = 0.70):
        self.coherence_model = get_coherence_model()
        self.threshold = threshold

    def evaluate_document(self, clauses: List[ClauseRecord], doc_id: str = "doc") -> DocumentStructuralResult:
        t0 = time.perf_counter()
        n = len(clauses)
        if n <= 1:
            return DocumentStructuralResult(
                doc_id=doc_id, model_name=self.name, model_version=self.version,
                is_anomaly=False, max_structural_score=0.0, mean_structural_score=0.0,
                threshold_used=self.threshold, execution_time_ms=0.0
            )

        pairs = [(clauses[i], clauses[i+1]) for i in range(n - 1)]
        probs = self.coherence_model.score_pairs(pairs)
        anomalies = [1.0 - p for p in probs]

        clause_scores = []
        for i in range(n):
            if i == 0:
                s = anomalies[0]
            elif i == n - 1:
                s = anomalies[-1]
            else:
                s = max(anomalies[i-1], anomalies[i])
            clause_scores.append(ClauseStructuralScore(
                clause_id=clauses[i].clause_id, sequence_idx=i, structural_score=round(float(s), 4),
                is_anomaly=s >= self.threshold, contextual_distance=0.0, progression_discordance=0.0,
                boundary_contrast=0.0, predicted_role_stage=3
            ))

        max_score = max(c.structural_score for c in clause_scores) if clause_scores else 0.0
        mean_score = float(np.mean([c.structural_score for c in clause_scores])) if clause_scores else 0.0
        is_anom = max_score >= self.threshold
        flagged_ids = [c.clause_id for c in clause_scores if c.is_anomaly]

        dt = (time.perf_counter() - t0) * 1000
        return DocumentStructuralResult(
            doc_id=doc_id, model_name=self.name, model_version=self.version,
            is_anomaly=is_anom, max_structural_score=max_score, mean_structural_score=mean_score,
            threshold_used=self.threshold, clause_scores=clause_scores,
            predicted_anomaly_clause_ids=flagged_ids, execution_time_ms=dt
        )


class BaselineB1_ProductionEnsemble:
    """Baseline B1: Original production dual-channel scoring pipeline (Channel A + B)."""
    name = "Baseline_B1_ProductionDualChannel"
    version = "1.0.0_production"

    def __init__(self, threshold: float = 0.50):
        self.scorer = DualChannelScorer()
        self.threshold = threshold

    def evaluate_document(self, clauses: List[ClauseRecord], doc_id: str = "doc") -> DocumentStructuralResult:
        t0 = time.perf_counter()
        doc_res = self.scorer.score_document(clauses, doc_id=doc_id)

        clause_scores = []
        for c in doc_res.clauses:
            clause_scores.append(ClauseStructuralScore(
                clause_id=c.clause_id, sequence_idx=c.sequence_idx, structural_score=round(c.combined_score, 4),
                is_anomaly=c.is_anomaly, contextual_distance=round(c.channel_a_score, 4),
                progression_discordance=0.0, boundary_contrast=round(c.channel_b_score, 4),
                predicted_role_stage=3
            ))

        dt = (time.perf_counter() - t0) * 1000
        is_anom = doc_res.anomaly_count > 0 or any(c.is_anomaly for c in clause_scores)
        flagged_ids = [c.clause_id for c in clause_scores if c.is_anomaly]

        return DocumentStructuralResult(
            doc_id=doc_id, model_name=self.name, model_version=self.version,
            is_anomaly=is_anom, max_structural_score=max((c.structural_score for c in clause_scores), default=0.0),
            mean_structural_score=doc_res.mean_combined_score, threshold_used=self.threshold,
            clause_scores=clause_scores, predicted_anomaly_clause_ids=flagged_ids, execution_time_ms=dt
        )


class BaselineB2_CosineDistance:
    """Baseline B2: Simple adjacent-pair cosine distance over Legal-BERT embeddings."""
    name = "Baseline_B2_AdjacentCosine"
    version = "1.0.0"

    def __init__(self, threshold: float = 0.25):
        self.embedder = get_embedder("frozen")
        self.threshold = threshold

    def evaluate_document(self, clauses: List[ClauseRecord], doc_id: str = "doc") -> DocumentStructuralResult:
        t0 = time.perf_counter()
        n = len(clauses)
        if n <= 1:
            return DocumentStructuralResult(
                doc_id=doc_id, model_name=self.name, model_version=self.version,
                is_anomaly=False, max_structural_score=0.0, mean_structural_score=0.0,
                threshold_used=self.threshold, execution_time_ms=0.0
            )

        _, embs = self.embedder.embed_clauses(clauses)
        norms = np.linalg.norm(embs, axis=1, keepdims=True) + 1e-9
        embs_norm = embs / norms

        dists = []
        for i in range(n - 1):
            d = 1.0 - float(np.dot(embs_norm[i], embs_norm[i+1]))
            dists.append(max(0.0, d))

        clause_scores = []
        for i in range(n):
            if i == 0:
                s = dists[0]
            elif i == n - 1:
                s = dists[-1]
            else:
                s = max(dists[i-1], dists[i])
            clause_scores.append(ClauseStructuralScore(
                clause_id=clauses[i].clause_id, sequence_idx=i, structural_score=round(s, 4),
                is_anomaly=s >= self.threshold, contextual_distance=s, progression_discordance=0.0,
                boundary_contrast=0.0, predicted_role_stage=3
            ))

        dt = (time.perf_counter() - t0) * 1000
        max_score = max((c.structural_score for c in clause_scores), default=0.0)
        is_anom = max_score >= self.threshold
        return DocumentStructuralResult(
            doc_id=doc_id, model_name=self.name, model_version=self.version,
            is_anomaly=is_anom, max_structural_score=max_score, mean_structural_score=float(np.mean(dists)),
            threshold_used=self.threshold, clause_scores=clause_scores,
            predicted_anomaly_clause_ids=[c.clause_id for c in clause_scores if c.is_anomaly], execution_time_ms=dt
        )


# ==============================================================================
# CANDIDATE C1: CONTEXTUAL BOUNDARY CONTRAST DETECTOR
# ==============================================================================

class CandidateC1_ContextualBoundaryDetector:
    """
    Candidate C1: Contextual Boundary Contrast & Lifecycle Discordance Detector.

    Synthesizes:
    1. Local Boundary Contrast: Anomaly deviation from document baseline.
    2. Contextual Window Incoherence: Distance to rolling surrounding neighborhood.
    3. Lifecycle Progression Discordance: Detection of backward structural regressions.

    Fully deterministic, highly interpretable, zero-parameter inference, CPU-efficient (< 5 ms).
    """
    name = "Candidate_C1_ContextualBoundary"
    version = "1.1.0_contextual"

    def __init__(
        self,
        threshold: float = 0.42,
        w_ctx: float = 0.35,
        w_contrast: float = 0.25,
        w_discordance: float = 0.40,
        window_size: int = 2
    ):
        self.threshold = threshold
        self.w_ctx = w_ctx
        self.w_contrast = w_contrast
        self.w_discordance = w_discordance
        self.window_size = window_size
        self.embedder = get_embedder("frozen")
        self.coherence_model = get_coherence_model()

    def evaluate_document(self, clauses: List[ClauseRecord], doc_id: str = "doc") -> DocumentStructuralResult:
        t0 = time.perf_counter()
        n = len(clauses)
        if n <= 1:
            return DocumentStructuralResult(
                doc_id=doc_id, model_name=self.name, model_version=self.version,
                is_anomaly=False, max_structural_score=0.0, mean_structural_score=0.0,
                threshold_used=self.threshold, execution_time_ms=0.0
            )

        # 1. Embeddings & Contextual Window Distances
        _, embs = self.embedder.embed_clauses(clauses)
        ctx_distances = extract_contextual_window_distances(embs, window_size=self.window_size)

        # 2. Lifecycle Progression Discordance
        discordance = extract_progression_discordance(clauses)

        # 3. Transition Boundaries & Relative Contrast
        pairs = [(clauses[i], clauses[i+1]) for i in range(n - 1)]
        coherence_probs = self.coherence_model.score_pairs(pairs)
        contrasts, z_scores = extract_boundary_contrast(coherence_probs)

        # Build boundary evidence
        boundary_evidences = []
        for i in range(n - 1):
            p = coherence_probs[i]
            anom = 1.0 - p
            boundary_evidences.append(BoundaryEvidence(
                transition_idx=i, from_clause_id=clauses[i].clause_id, to_clause_id=clauses[i+1].clause_id,
                raw_transition_prob=round(p, 4), raw_anomaly_score=round(anom, 4),
                local_contrast=round(float(contrasts[i]), 4), z_score=round(float(z_scores[i]), 4),
                is_discontinuous=z_scores[i] >= 1.5
            ))

        # Assign per-clause contrast (max of incoming/outgoing contrast)
        clause_contrasts = np.zeros(n, dtype=np.float32)
        for i in range(n):
            if i == 0:
                clause_contrasts[i] = max(0.0, float(contrasts[0]))
            elif i == n - 1:
                clause_contrasts[i] = max(0.0, float(contrasts[-1]))
            else:
                clause_contrasts[i] = max(0.0, float(max(contrasts[i-1], contrasts[i])))

        # Normalize contrasts (scaled by factor to map small 0.01-0.03 delta to [0, 1])
        scaled_contrasts = np.clip(clause_contrasts / 0.03, 0.0, 1.0)

        # 4. Composite Structural Anomaly Score per Clause
        clause_scores = []
        for i in range(n):
            s_ctx = ctx_distances[i]
            s_disc = discordance[i]
            s_cont = scaled_contrasts[i]
            stage = infer_clause_lifecycle_stage(clauses[i])

            # Composite weighted score in [0.0, 1.0]
            score = (self.w_ctx * s_ctx) + (self.w_contrast * s_cont) + (self.w_discordance * s_disc)
            score = float(np.clip(score, 0.0, 1.0))
            is_anom = score >= self.threshold

            clause_scores.append(ClauseStructuralScore(
                clause_id=clauses[i].clause_id, sequence_idx=i, structural_score=round(score, 4),
                is_anomaly=is_anom, contextual_distance=round(float(s_ctx), 4),
                progression_discordance=round(float(s_disc), 4), boundary_contrast=round(float(s_cont), 4),
                predicted_role_stage=stage
            ))

        max_score = max((c.structural_score for c in clause_scores), default=0.0)
        mean_score = float(np.mean([c.structural_score for c in clause_scores])) if clause_scores else 0.0
        doc_is_anom = max_score >= self.threshold
        flagged_ids = [c.clause_id for c in clause_scores if c.is_anomaly]

        dt = (time.perf_counter() - t0) * 1000
        return DocumentStructuralResult(
            doc_id=doc_id, model_name=self.name, model_version=self.version,
            is_anomaly=doc_is_anom, max_structural_score=round(max_score, 4),
            mean_structural_score=round(mean_score, 4), threshold_used=self.threshold,
            clause_scores=clause_scores, boundary_evidences=boundary_evidences,
            predicted_anomaly_clause_ids=flagged_ids, execution_time_ms=dt
        )


# ==============================================================================
# CANDIDATE C2: GLOBAL CONTEXTUAL SEQUENCE BI-LSTM MODEL
# ==============================================================================

class BiLSTMContextualScorer(nn.Module):
    """
    Lightweight bidirectional sequence encoder over frozen 768-dim Legal-BERT embeddings.
    Evaluates global sequence progression and outputs calibrated position anomaly logits.
    """
    def __init__(self, embedding_dim: int = 768, hidden_dim: int = 128, num_layers: int = 2, dropout: float = 0.1):
        super().__init__()
        self.embedding_dim = embedding_dim
        self.hidden_dim = hidden_dim

        # Positional encoding projection
        self.pos_proj = nn.Linear(1, 32)

        # BiLSTM over (embedding + pos_feat)
        self.lstm = nn.LSTM(
            input_size=embedding_dim + 32,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            bidirectional=True,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0.0
        )

        # Classification head predicting structural anomaly at each position
        self.head = nn.Sequential(
            nn.Linear(hidden_dim * 2, 64),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(64, 1)
        )

    def forward(self, embeddings: torch.Tensor, positions: torch.Tensor) -> torch.Tensor:
        """
        Args:
            embeddings: (batch_size, seq_len, 768)
            positions: (batch_size, seq_len, 1) normalized positions in [0, 1]
        Returns:
            logits: (batch_size, seq_len, 1)
        """
        pos_feat = self.pos_proj(positions)
        inputs = torch.cat([embeddings, pos_feat], dim=-1)
        lstm_out, _ = self.lstm(inputs)
        logits = self.head(lstm_out)
        return logits


class CandidateC2_ContextualSequenceModel:
    """
    Candidate C2: Neural Contextual Sequence Coherence Model.
    Wraps BiLSTMContextualScorer, executes on CPU, isolates weights in experimental dir.
    """
    name = "Candidate_C2_SequenceBiLSTM"
    version = "1.0.0_experimental"

    def __init__(self, checkpoint_path: Optional[str] = None, threshold: float = 0.50):
        self.threshold = threshold
        self.checkpoint_path = checkpoint_path
        self.embedder = get_embedder("frozen")
        self.model = BiLSTMContextualScorer(embedding_dim=768, hidden_dim=128, num_layers=2)
        self.device = torch.device("cpu")
        self.model.to(self.device)
        self.model.eval()

        if checkpoint_path and torch.cuda.is_available() is False:
            try:
                state_dict = torch.load(checkpoint_path, map_location=self.device, weights_only=True)
                self.model.load_state_dict(state_dict)
            except Exception as e:
                # If checkpoint missing, will be initialized for training
                pass

    def evaluate_document(self, clauses: List[ClauseRecord], doc_id: str = "doc") -> DocumentStructuralResult:
        t0 = time.perf_counter()
        n = len(clauses)
        if n <= 1:
            return DocumentStructuralResult(
                doc_id=doc_id, model_name=self.name, model_version=self.version,
                is_anomaly=False, max_structural_score=0.0, mean_structural_score=0.0,
                threshold_used=self.threshold, execution_time_ms=0.0
            )

        _, embs = self.embedder.embed_clauses(clauses)
        norm_pos = np.linspace(0.0, 1.0, n, dtype=np.float32).reshape(1, n, 1)

        embs_tensor = torch.from_numpy(embs).unsqueeze(0).float()
        pos_tensor = torch.from_numpy(norm_pos).float()

        self.model.eval()
        with torch.no_grad():
            logits = self.model(embs_tensor, pos_tensor)
            probs = torch.sigmoid(logits).squeeze(0).squeeze(-1).numpy()

        clause_scores = []
        for i in range(n):
            p = float(probs[i])
            clause_scores.append(ClauseStructuralScore(
                clause_id=clauses[i].clause_id, sequence_idx=i, structural_score=round(p, 4),
                is_anomaly=p >= self.threshold, contextual_distance=round(p, 4),
                progression_discordance=0.0, boundary_contrast=0.0, predicted_role_stage=3
            ))

        max_score = max((c.structural_score for c in clause_scores), default=0.0)
        mean_score = float(np.mean(probs))
        doc_is_anom = max_score >= self.threshold
        flagged_ids = [c.clause_id for c in clause_scores if c.is_anomaly]

        dt = (time.perf_counter() - t0) * 1000
        return DocumentStructuralResult(
            doc_id=doc_id, model_name=self.name, model_version=self.version,
            is_anomaly=doc_is_anom, max_structural_score=round(max_score, 4),
            mean_structural_score=round(mean_score, 4), threshold_used=self.threshold,
            clause_scores=clause_scores, predicted_anomaly_clause_ids=flagged_ids, execution_time_ms=dt
        )


# ==============================================================================
# CANDIDATE C3: STRUCTURE-AWARE TOPOLOGICAL DEPENDENCY MODEL
# ==============================================================================

class CandidateC3_StructureAwareDependencyModel:
    """
    Candidate C3: Typed Structural Precedence DAG Model.
    Builds a directed acyclic lifecycle graph and detects topological ordering violations.
    """
    name = "Candidate_C3_TopologicalDependency"
    version = "1.0.0_dag"

    def __init__(self, threshold: float = 0.50):
        self.threshold = threshold

    def evaluate_document(self, clauses: List[ClauseRecord], doc_id: str = "doc") -> DocumentStructuralResult:
        t0 = time.perf_counter()
        n = len(clauses)
        if n <= 1:
            return DocumentStructuralResult(
                doc_id=doc_id, model_name=self.name, model_version=self.version,
                is_anomaly=False, max_structural_score=0.0, mean_structural_score=0.0,
                threshold_used=self.threshold, execution_time_ms=0.0
            )

        stages = [infer_clause_lifecycle_stage(c) for c in clauses]

        # Directed precedence constraints:
        # Stage 0 (Preamble) must precede Stage 1-6
        # Stage 1 (Scope) must precede Stage 4-6
        # Stage 6 (Exhibits) must follow Stage 0-4
        violations = np.zeros(n, dtype=np.float32)
        for i in range(n):
            for j in range(i + 1, n):
                # Back-edge: later position j has stage significantly lower than earlier position i
                if stages[i] >= 5 and stages[j] <= 1:  # Boilerplate/Exhibit followed by Preamble/Scope
                    violations[j] = max(violations[j], 1.0)
                    violations[i] = max(violations[i], 0.7)
                elif stages[i] >= 4 and stages[j] == 0:  # Remedies followed by Preamble
                    violations[j] = max(violations[j], 1.0)

        clause_scores = []
        for i in range(n):
            v = float(violations[i])
            clause_scores.append(ClauseStructuralScore(
                clause_id=clauses[i].clause_id, sequence_idx=i, structural_score=round(v, 4),
                is_anomaly=v >= self.threshold, contextual_distance=v,
                progression_discordance=v, boundary_contrast=0.0, predicted_role_stage=stages[i]
            ))

        max_score = max((c.structural_score for c in clause_scores), default=0.0)
        mean_score = float(np.mean(violations))
        doc_is_anom = max_score >= self.threshold
        flagged_ids = [c.clause_id for c in clause_scores if c.is_anomaly]

        dt = (time.perf_counter() - t0) * 1000
        return DocumentStructuralResult(
            doc_id=doc_id, model_name=self.name, model_version=self.version,
            is_anomaly=doc_is_anom, max_structural_score=round(max_score, 4),
            mean_structural_score=round(mean_score, 4), threshold_used=self.threshold,
            clause_scores=clause_scores, predicted_anomaly_clause_ids=flagged_ids, execution_time_ms=dt
        )
