"""
src/api/dependencies.py — Dependency injection for FastAPI backend.
Lazily loads and caches ML models so they don't block API startup.
"""
from functools import lru_cache
from pathlib import Path
from fastapi import Depends

from src.segmentation.factory import get_segmenter
from src.scoring.pipeline import DualChannelScorer
from src.calibration.conformal import ConformalCalibrator
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
    return get_dual_channel_scorer()
