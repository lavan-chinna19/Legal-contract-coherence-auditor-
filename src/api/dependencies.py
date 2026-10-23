"""
src/api/dependencies.py — Dependency injection for FastAPI backend.
Lazily loads and caches ML models so they don't block API startup.
"""
from functools import lru_cache
from pathlib import Path
from fastapi import Depends, HTTPException

from src.segmentation.factory import get_segmenter
from src.scoring.pipeline import DualChannelScorer
from src.calibration.conformal import ConformalCalibrator
from src.rules.unified_pipeline import UnifiedAuditor
from src.config import REPO_ROOT

# Temporary storage for uploaded documents
UPLOAD_DIR = REPO_ROOT / "data" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@lru_cache(maxsize=1)
def get_ml_segmenter():
    """Lazily load the Tier 1 segmenter."""
    return get_segmenter("v1")


@lru_cache(maxsize=1)
def get_dual_channel_scorer():
    """Lazily load the DualChannelScorer pipeline with calibrator if available."""
    calibrator = None
    state_path = REPO_ROOT / "fixtures" / "conformal_calibration_fixture.json"
    if state_path.exists():
        try:
            calibrator = ConformalCalibrator.from_state_file(state_path)
        except Exception:
            pass
            
    return DualChannelScorer(calibrator=calibrator)


def get_segmenter_dep():
    """FastAPI dependency for segmenter."""
    return get_ml_segmenter()


def get_scorer_dep():
    """FastAPI dependency for scoring pipeline."""
    try:
        scorer = get_dual_channel_scorer()
        if scorer.channel_a.centroid_matrix is None:
            raise RuntimeError("Centroids missing")
        return scorer
    except Exception:
        raise HTTPException(503, "Analysis model unavailable. Verify local checkpoints and dependencies.")

@lru_cache(maxsize=1)
def get_unified_auditor():
    """Lazily load the UnifiedAuditor with all rule checkers."""
    scorer = get_dual_channel_scorer()
    return UnifiedAuditor(scorer=scorer)

def get_auditor_dep():
    """FastAPI dependency for UnifiedAuditor."""
    try:
        auditor = get_unified_auditor()
        if auditor.scorer.channel_a.centroid_matrix is None:
            raise RuntimeError("Centroids missing")
        return auditor
    except Exception:
        raise HTTPException(503, "Analysis model unavailable. Verify local checkpoints and installed dependencies.")
