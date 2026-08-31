"""
src/calibration/conformal.py — Distribution-free Conformal Calibration for Anomaly Scores.
Uses conformal prediction (via crepes / split conformal quantile calibration)
fit strictly on synthetic shuffle-test data.
"""
from dataclasses import dataclass, asdict
from typing import List, Dict, Tuple, Optional, Union, Any
import json
import numpy as np
from pathlib import Path

try:
    from crepes import ConformalRegressor
    CREPES_AVAILABLE = True
except ImportError:
    CREPES_AVAILABLE = False


@dataclass
class ConformalInterval:
    """
    Calibrated prediction interval container.
    """
    lower: float
    upper: float
    confidence_level: float
    point_prediction: float
    calibration_source: str = "synthetic_shuffle_only"

    def to_tuple(self) -> Tuple[float, float]:
        return (self.lower, self.upper)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ConformalCalibrator:
    """
    Conformal Calibration Engine for Ensembled Anomaly Scores.
    Guarantees distribution-free coverage on the synthetic shuffle calibration distribution.
    
    Calibration Source Constraint:
    Permanently hardcoded and asserted as 'synthetic_shuffle_only' (Acceptance Gate 1 & 3).
    """

    CALIBRATION_SOURCE_TAG = "synthetic_shuffle_only"

    def __init__(
        self,
        target_coverage: float = 0.90,
        use_crepes: bool = True
    ):
        if not (0.0 < target_coverage < 1.0):
            raise ValueError(f"target_coverage must be in (0, 1), got {target_coverage}")
        self.target_coverage = float(target_coverage)
        self.alpha = 1.0 - self.target_coverage
        self.use_crepes = use_crepes and CREPES_AVAILABLE
        self.calibration_source = self.CALIBRATION_SOURCE_TAG
        
        self.is_fitted = False
        self.n_calibration_samples = 0
        self.calibration_residuals: Optional[np.ndarray] = None
        self.conformal_quantile: float = 0.0
        self._crepes_model: Optional[Any] = None

    def fit(
        self,
        y_true: Union[List[float], np.ndarray],
        y_pred: Union[List[float], np.ndarray],
        calibration_source: str = "synthetic_shuffle_only"
    ) -> "ConformalCalibrator":
        """
        Fits conformal calibration on synthetic shuffle residuals.
        
        Args:
            y_true: Synthetic ground-truth anomaly scores (0.0 for clean, 1.0 for shuffled).
            y_pred: Model predicted anomaly scores [0.0, 1.0].
            calibration_source: Must strictly be 'synthetic_shuffle_only'.
        """
        if calibration_source != self.CALIBRATION_SOURCE_TAG:
            raise ValueError(
                f"Acceptance Gate Violation: calibration_source must be '{self.CALIBRATION_SOURCE_TAG}', "
                f"got '{calibration_source}'"
            )

        y_t = np.asarray(y_true, dtype=np.float64)
        y_p = np.asarray(y_pred, dtype=np.float64)

        if len(y_t) != len(y_p):
            raise ValueError(f"Length mismatch: len(y_true)={len(y_t)} vs len(y_pred)={len(y_p)}")
        if len(y_t) == 0:
            raise ValueError("Cannot fit calibrator on empty dataset.")

        residuals = np.abs(y_t - y_p)
        self.calibration_residuals = residuals
        self.n_calibration_samples = len(residuals)

        # Standard finite-sample conformal quantile:
        # q = (1 - alpha) * (1 + 1/n) quantile
        n = len(residuals)
        q_level = min(1.0, np.ceil((n + 1) * (1.0 - self.alpha)) / n)
        self.conformal_quantile = float(np.quantile(residuals, q_level, method="higher" if hasattr(np, "quantile") else "linear"))

        # Fit crepes ConformalRegressor if available
        if self.use_crepes:
            self._crepes_model = ConformalRegressor()
            # crepes expects signed or absolute residuals
            self._crepes_model.fit(residuals)

        self.is_fitted = True
        return self

    def predict_interval(
        self,
        y_pred: Union[float, List[float], np.ndarray],
        confidence_level: Optional[float] = None
    ) -> Union[Tuple[float, float], List[Tuple[float, float]]]:
        """
        Computes distribution-free calibrated confidence intervals for predicted scores.
        Output intervals are clipped to [0.0, 1.0].
        """
        if not self.is_fitted:
            raise RuntimeError("ConformalCalibrator must be fitted before calling predict_interval.")

        target_conf = float(confidence_level if confidence_level is not None else self.target_coverage)
        if not (0.0 < target_conf < 1.0):
            raise ValueError(f"confidence_level must be in (0, 1), got {target_conf}")

        is_scalar = isinstance(y_pred, (float, int, np.floating))
        y_arr = np.atleast_1d(np.asarray(y_pred, dtype=np.float64))

        if self.use_crepes and self._crepes_model is not None:
            # crepes predict_int produces intervals array [[low, high], ...]
            raw_intervals = self._crepes_model.predict_int(y_arr, confidence=target_conf)
            lowers = np.clip(raw_intervals[:, 0], 0.0, 1.0)
            uppers = np.clip(raw_intervals[:, 1], 0.0, 1.0)
        else:
            # Exact finite-sample quantile calculation
            alpha = 1.0 - target_conf
            n = self.n_calibration_samples
            q_level = min(1.0, np.ceil((n + 1) * (1.0 - alpha)) / n)
            q_val = float(np.quantile(self.calibration_residuals, q_level))
            lowers = np.clip(y_arr - q_val, 0.0, 1.0)
            uppers = np.clip(y_arr + q_val, 0.0, 1.0)

        intervals = [(round(float(l), 4), round(float(u), 4)) for l, u in zip(lowers, uppers)]
        if is_scalar:
            return intervals[0]
        return intervals

    def evaluate_coverage(
        self,
        y_true: Union[List[float], np.ndarray],
        y_pred: Union[List[float], np.ndarray],
        confidence_level: Optional[float] = None
    ) -> Dict[str, float]:
        """
        Computes empirical coverage on a held-out evaluation dataset (Acceptance Gate 2).
        
        Coverage = fraction of true targets falling within [lower, upper].
        """
        target_conf = float(confidence_level if confidence_level is not None else self.target_coverage)
        y_t = np.asarray(y_true, dtype=np.float64)
        y_p = np.asarray(y_pred, dtype=np.float64)

        intervals = self.predict_interval(y_p, confidence_level=target_conf)
        if isinstance(intervals, tuple):
            intervals = [intervals]

        covered = 0
        widths = []
        for yt, (low, high) in zip(y_t, intervals):
            # Check if true value is within calibrated interval
            if low - 1e-6 <= yt <= high + 1e-6:
                covered += 1
            widths.append(high - low)

        n = len(y_t)
        empirical_coverage = float(covered / n) if n > 0 else 0.0
        delta = empirical_coverage - target_conf

        return {
            "target_coverage": round(target_conf, 4),
            "empirical_coverage": round(empirical_coverage, 4),
            "coverage_delta": round(delta, 4),
            "mean_interval_width": round(float(np.mean(widths)), 4) if widths else 0.0,
            "sample_size": n,
            "calibration_source": self.calibration_source
        }

    def save_state(self, path: Union[str, Path]) -> None:
        """Saves fitted calibration state as a JSON fixture."""
        state = {
            "target_coverage": self.target_coverage,
            "alpha": self.alpha,
            "is_fitted": self.is_fitted,
            "n_calibration_samples": self.n_calibration_samples,
            "conformal_quantile": round(self.conformal_quantile, 6),
            "calibration_residuals": [round(float(r), 6) for r in self.calibration_residuals] if self.calibration_residuals is not None else [],
            "calibration_source": self.calibration_source
        }
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)

    @classmethod
    def from_state_file(cls, path: Union[str, Path]) -> "ConformalCalibrator":
        """Loads calibration state into a new ConformalCalibrator instance."""
        cal = cls()
        return cal._load_state_from_path(path)

    def load_state(self, path: Union[str, Path]) -> "ConformalCalibrator":
        """Loads calibration state from a JSON fixture into this instance."""
        return self._load_state_from_path(path)

    def _load_state_from_path(self, path: Union[str, Path]) -> "ConformalCalibrator":
        """Loads calibration state from a JSON fixture into this instance."""
        with open(path, "r", encoding="utf-8") as f:
            state = json.load(f)
        self.target_coverage = float(state["target_coverage"])
        self.alpha = 1.0 - self.target_coverage
        self.is_fitted = bool(state["is_fitted"])
        self.n_calibration_samples = int(state["n_calibration_samples"])
        self.conformal_quantile = float(state["conformal_quantile"])
        self.calibration_residuals = np.array(state["calibration_residuals"], dtype=np.float64)
        self.calibration_source = state.get("calibration_source", self.CALIBRATION_SOURCE_TAG)
        if self.use_crepes and len(self.calibration_residuals) > 0:
            self._crepes_model = ConformalRegressor()
            self._crepes_model.fit(self.calibration_residuals)
        return self
