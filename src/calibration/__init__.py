"""
src/calibration — Conformal uncertainty quantification and calibration package.
"""
from src.calibration.conformal import ConformalCalibrator, ConformalInterval
from src.calibration.synthetic_generator import (
    SyntheticCalibrationItem,
    SyntheticShuffleDatasetGenerator,
    assert_is_synthetic_only
)

__all__ = [
    "ConformalCalibrator",
    "ConformalInterval",
    "SyntheticCalibrationItem",
    "SyntheticShuffleDatasetGenerator",
    "assert_is_synthetic_only"
]
