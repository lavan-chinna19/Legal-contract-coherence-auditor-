"""
src/evaluation/bootstrap.py — Statistical Bootstrap and Confidence Interval Utilities.
Provides non-parametric percentile bootstrap and Wilson score intervals for empirical metrics (Contract §1).
"""
import numpy as np
from scipy import stats
from typing import Tuple, Callable, List, Optional, Union


def bootstrap_ci(
    values: Union[List[float], np.ndarray],
    stat_func: Callable[[np.ndarray], float] = np.mean,
    n_boot: int = 1000,
    ci: float = 0.95,
    seed: int = 42
) -> Tuple[float, float, float]:
    """
    Computes empirical point estimate and non-parametric bootstrap percentile confidence interval.
    
    Returns:
        (point_estimate, ci_lower, ci_upper)
    """
    arr = np.asarray(values, dtype=np.float64)
    if len(arr) == 0:
        return 0.0, 0.0, 0.0
    if len(arr) == 1:
        val = float(arr[0])
        return val, val, val

    point_estimate = float(stat_func(arr))
    rng = np.random.default_rng(seed)
    n = len(arr)
    boot_stats = np.empty(n_boot, dtype=np.float64)

    for i in range(n_boot):
        sample = rng.choice(arr, size=n, replace=True)
        boot_stats[i] = stat_func(sample)

    alpha = (1.0 - ci) / 2.0
    lower = float(np.percentile(boot_stats, 100.0 * alpha))
    upper = float(np.percentile(boot_stats, 100.0 * (1.0 - alpha)))

    return point_estimate, lower, upper


def bootstrap_kendall_tau(
    x: Union[List[float], np.ndarray],
    y: Union[List[float], np.ndarray],
    n_boot: int = 1000,
    ci: float = 0.95,
    seed: int = 42
) -> Tuple[float, float, float, float]:
    """
    Computes Kendall's Tau-b rank correlation, p-value, and 95% bootstrap confidence interval.
    
    Returns:
        (tau, p_value, ci_lower, ci_upper)
    """
    x_arr = np.asarray(x, dtype=np.float64)
    y_arr = np.asarray(y, dtype=np.float64)
    
    if len(x_arr) != len(y_arr) or len(x_arr) < 2:
        return 0.0, 1.0, 0.0, 0.0

    res = stats.kendalltau(x_arr, y_arr)
    tau = float(res.statistic) if not np.isnan(res.statistic) else 0.0
    pval = float(res.pvalue) if not np.isnan(res.pvalue) else 1.0

    rng = np.random.default_rng(seed)
    n = len(x_arr)
    boot_taus = []

    for _ in range(n_boot):
        indices = rng.choice(n, size=n, replace=True)
        # Skip resamples with zero variance
        if len(np.unique(x_arr[indices])) < 2 or len(np.unique(y_arr[indices])) < 2:
            continue
        b_res = stats.kendalltau(x_arr[indices], y_arr[indices])
        if not np.isnan(b_res.statistic):
            boot_taus.append(float(b_res.statistic))

    if not boot_taus:
        return tau, pval, tau, tau

    alpha = (1.0 - ci) / 2.0
    lower = float(np.percentile(boot_taus, 100.0 * alpha))
    upper = float(np.percentile(boot_taus, 100.0 * (1.0 - alpha)))

    return tau, pval, lower, upper


def wilson_score_interval(
    k: int,
    n: int,
    ci: float = 0.95
) -> Tuple[float, float, float]:
    """
    Computes Wilson score confidence interval for binomial proportions (e.g., False Positive Rate).
    
    Returns:
        (proportion, ci_lower, ci_upper)
    """
    if n == 0:
        return 0.0, 0.0, 0.0

    p = float(k) / float(n)
    z = float(stats.norm.ppf(1.0 - (1.0 - ci) / 2.0))
    z2 = z * z
    denom = 1.0 + z2 / n
    center = (p + z2 / (2.0 * n)) / denom
    margin = (z * np.sqrt((p * (1.0 - p) + z2 / (4.0 * n)) / n)) / denom

    lower = max(0.0, float(center - margin))
    upper = min(1.0, float(center + margin))

    return p, lower, upper
