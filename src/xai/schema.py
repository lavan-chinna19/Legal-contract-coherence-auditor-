"""
src/xai/schema.py — Unified Explanation Schemas for Prompt 12 XAI Layer.
"""
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional
import datetime

@dataclass
class ClaimScope:
    """
    Explicitly bounds the claims of the explanation.
    """
    what_this_shows: str
    what_this_does_not_show: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class IntegratedGradientsExplanation:
    """
    Token-level attribution for Channel A OOD Anomaly.
    """
    tokens: List[str]
    attributions: List[float]
    target_score: float
    baseline_score: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class SensitivityExplanation:
    """
    Neighbor perturbation sensitivity for Channel B Coherence Anomaly.
    """
    neighbor_clause_id: str
    neighbor_position: str  # "prev" or "next"
    original_score: float
    perturbed_score: float
    score_delta: float
    perturbation_method: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class NearestNeighborEvidence:
    """
    Nearest-neighbor retrieval evidence.
    """
    neighbor_clause_id: str
    source_document: str
    similarity: float
    label: Optional[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class ExplanationResult:
    """
    Unified container for dashboard compatibility holding all generated explanations for a clause.
    """
    explanation_id: str
    doc_id: str
    clause_id: str
    explanation_type: str  # e.g., "INTEGRATED_GRADIENTS", "SENSITIVITY", "NEAREST_NEIGHBOR"
    model_version: str
    timestamp: str
    claim_scope: ClaimScope
    
    # Payload can hold one of the explanation types
    ig_payload: Optional[IntegratedGradientsExplanation] = None
    sensitivity_payload: Optional[SensitivityExplanation] = None
    nn_payload: Optional[List[NearestNeighborEvidence]] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        # Drop None payloads for clean schema
        return {k: v for k, v in d.items() if v is not None}
