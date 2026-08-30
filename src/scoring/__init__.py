"""
src/scoring/__init__.py — Dual-Channel Contract Anomaly Scoring Package.
"""
from src.scoring.schema import (
    ChannelAEvidence,
    ChannelBEvidence,
    ClauseScoringResult,
    DocumentScoringResult
)
from src.scoring.channel_a import ChannelAScorer
from src.scoring.channel_b import ChannelBScorer
from src.scoring.pipeline import DualChannelScorer
from src.scoring.diagnostics import format_diagnostics_report

__all__ = [
    "ChannelAEvidence",
    "ChannelBEvidence",
    "ClauseScoringResult",
    "DocumentScoringResult",
    "ChannelAScorer",
    "ChannelBScorer",
    "DualChannelScorer",
    "format_diagnostics_report"
]
