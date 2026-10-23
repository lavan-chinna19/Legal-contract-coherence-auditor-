"""
src/research/structural_coherence/schema.py — Data Contracts for Structural Coherence Research.
Phase 4D-B Research Extension.
"""
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import List, Dict, Tuple, Optional, Any


class StructuralAnomalyLabel(str, Enum):
    """Authoritative Ground Truth Taxonomy for Contract Ordering."""
    VALID_ORDER = "VALID_ORDER"
    VERIFIED_STRUCTURAL_DEPENDENCY_VIOLATION = "VERIFIED_STRUCTURAL_DEPENDENCY_VIOLATION"
    PREREQUISITE_ORDERING_INVERSION = "PREREQUISITE_ORDERING_INVERSION"
    INDEPENDENT_REORDERING = "INDEPENDENT_REORDERING"
    AMBIGUOUS_ORDER = "AMBIGUOUS_ORDER"
    SYNTHETIC_DISPLACEMENT_ONLY = "SYNTHETIC_DISPLACEMENT_ONLY"
    UNSUPPORTED_ORACLE = "UNSUPPORTED_ORACLE"
    INVALID_TRANSFORMATION = "INVALID_TRANSFORMATION"


@dataclass
class BoundaryEvidence:
    """Diagnostic evidence for an adjacent transition boundary (c_i -> c_{i+1})."""
    transition_idx: int
    from_clause_id: str
    to_clause_id: str
    raw_transition_prob: float
    raw_anomaly_score: float
    local_contrast: float
    z_score: float
    is_discontinuous: bool

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ClauseStructuralScore:
    """Per-clause structural anomaly score and localization evidence."""
    clause_id: str
    sequence_idx: int
    structural_score: float
    is_anomaly: bool
    contextual_distance: float
    progression_discordance: float
    boundary_contrast: float
    predicted_role_stage: int

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class DocumentStructuralResult:
    """Complete document-level structural evaluation result from a candidate detector."""
    doc_id: str
    model_name: str
    model_version: str
    is_anomaly: bool
    max_structural_score: float
    mean_structural_score: float
    threshold_used: float
    clause_scores: List[ClauseStructuralScore] = field(default_factory=list)
    boundary_evidences: List[BoundaryEvidence] = field(default_factory=list)
    predicted_anomaly_clause_ids: List[str] = field(default_factory=list)
    execution_time_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "doc_id": self.doc_id,
            "model_name": self.model_name,
            "model_version": self.model_version,
            "is_anomaly": self.is_anomaly,
            "max_structural_score": round(self.max_structural_score, 4),
            "mean_structural_score": round(self.mean_structural_score, 4),
            "threshold_used": self.threshold_used,
            "clause_scores": [c.to_dict() for c in self.clause_scores],
            "boundary_evidences": [b.to_dict() for b in self.boundary_evidences],
            "predicted_anomaly_clause_ids": self.predicted_anomaly_clause_ids,
            "execution_time_ms": round(self.execution_time_ms, 2)
        }


@dataclass
class EvaluationMetrics:
    """Standardized evaluation metric bundle with statistical uncertainty."""
    model_name: str
    split_name: str
    condition_positives: int
    condition_negatives: int
    tp: int
    fp: int
    fn: int
    tn: int
    recall: float
    precision: Optional[float]
    f1: Optional[float]
    specificity: float
    fpr: float
    balanced_accuracy: float
    pr_auc: Optional[float]
    roc_auc: Optional[float]
    wilson_95_ci_recall: Tuple[float, float]
    localization_hit_rate: Optional[float] = None
    mean_latency_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
