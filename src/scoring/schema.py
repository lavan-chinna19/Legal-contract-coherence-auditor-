"""
src/scoring/schema.py — Canonical ScoringResult schema shared across all downstream phases
(Tier 1 heuristic screening, Tier 2 deep verification, XAI attribution, Reviewer UI).
"""
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any


@dataclass
class ChannelAEvidence:
    """
    Diagnostic evidence for Channel A: Semantic Out-of-Distribution (OOD) distance.
    """
    nearest_centroid_label: str
    centroid_distance: float
    is_ood: bool
    top_k_distances: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ChannelBEvidence:
    """
    Diagnostic evidence for Channel B: Discourse / Coherence Transition anomaly.
    """
    incoming_prob: Optional[float] = None
    outgoing_prob: Optional[float] = None
    incoming_anomaly: Optional[float] = None
    outgoing_anomaly: Optional[float] = None
    prev_clause_id: Optional[str] = None
    next_clause_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ClauseScoringResult:
    """
    Per-clause anomaly assessment combining Channel A and Channel B with full attribution.
    """
    clause_id: str
    doc_id: str
    sequence_idx: int
    text_preview: str  # Truncated preview (never long plaintext; Contract §4)
    channel_a_score: float  # [0.0, 1.0] Semantic OOD Anomaly
    channel_b_score: float  # [0.0, 1.0] Transition Coherence Anomaly
    combined_score: float   # [0.0, 1.0] Ensemble Anomaly Score
    channel_a_evidence: ChannelAEvidence
    channel_b_evidence: ChannelBEvidence
    is_anomaly: bool
    severity: str           # "HIGH" | "MEDIUM" | "LOW" | "CLEAN"
    source_label: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        return d


@dataclass
class DocumentScoringResult:
    """
    Document-level audit output containing all clause scores and aggregate summary.
    """
    doc_id: str
    total_clauses: int
    anomaly_count: int
    high_severity_count: int
    medium_severity_count: int
    mean_combined_score: float
    max_combined_score: float
    clauses: List[ClauseScoringResult]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "doc_id": self.doc_id,
            "total_clauses": self.total_clauses,
            "anomaly_count": self.anomaly_count,
            "high_severity_count": self.high_severity_count,
            "medium_severity_count": self.medium_severity_count,
            "mean_combined_score": self.mean_combined_score,
            "max_combined_score": self.max_combined_score,
            "clauses": [c.to_dict() for c in self.clauses],
            "metadata": self.metadata
        }
