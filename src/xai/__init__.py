"""
src/xai/__init__.py — Explainability / XAI Layer for Legal Contract Coherence Auditor.
"""

from .schema import (
    ClaimScope,
    IntegratedGradientsExplanation,
    SensitivityExplanation,
    NearestNeighborEvidence,
    ExplanationResult
)
from .ig import IntegratedGradientsExplainer
from .sensitivity import ChannelBSensitivityAnalyzer
from .nearest_neighbor import NearestNeighborRetriever

__all__ = [
    "ClaimScope",
    "IntegratedGradientsExplanation",
    "SensitivityExplanation",
    "NearestNeighborEvidence",
    "ExplanationResult",
    "IntegratedGradientsExplainer",
    "ChannelBSensitivityAnalyzer",
    "NearestNeighborRetriever"
]
