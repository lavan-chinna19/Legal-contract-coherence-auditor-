"""
src/coherence/__init__.py — Discourse Coherence Modeling package.
"""
from src.coherence.base import CoherenceModelInterface
from src.coherence.pair_sampler import CoherencePairSampler, CoherencePair
from src.coherence.model import CoherenceScorerHead
from src.coherence.factory import get_coherence_model

__all__ = [
    "CoherenceModelInterface",
    "CoherencePairSampler",
    "CoherencePair",
    "CoherenceScorerHead",
    "get_coherence_model"
]
