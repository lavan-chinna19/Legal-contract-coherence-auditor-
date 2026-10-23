"""
src/research/independent_benchmark/statistics.py
Statistical Uncertainty, Wilson Confidence Intervals, and Family-Grouped Bootstrap.
"""
import math
from typing import List, Tuple, Dict, Any, Optional
import numpy as np

from src.research.independent_benchmark.schema import WilsonInterval


def compute_wilson_score_interval(
    k: int,
    n: int,
    confidence_level: float = 0.95
) -> WilsonInterval:
    """
    Computes two-sided Wilson score confidence interval for a binomial proportion.
    Accurate for small sample sizes, k=0, and k=n.
    """
    if n <= 0:
        return WilsonInterval(point_estimate=0.0, lower_bound=0.0, upper_bound=0.0, confidence_level=confidence_level)

    # z for 95% is ~1.95996
    if confidence_level == 0.95:
        z = 1.959963984540054
    elif confidence_level == 0.90:
        z = 1.6448536269514722
    elif confidence_level == 0.99:
        z = 2.5758293035489004
    else:
        # Default approximation
        z = 1.95996

    p_hat = float(k) / float(n)
    z_sq = z * z
    denom = 1.0 + z_sq / float(n)
    center = (p_hat + z_sq / (2.0 * float(n))) / denom
    margin = (z / denom) * math.sqrt((p_hat * (1.0 - p_hat) / float(n)) + (z_sq / (4.0 * float(n) * float(n))))

    lower = max(0.0, center - margin)
    upper = min(1.0, center + margin)

    return WilsonInterval(
        point_estimate=round(p_hat, 4),
        lower_bound=round(lower, 4),
        upper_bound=round(upper, 4),
        confidence_level=confidence_level
    )


def compute_family_grouped_bootstrap_ci(
    family_case_diffs: Dict[str, List[float]],
    n_bootstraps: int = 1000,
    confidence_level: float = 0.95,
    random_seed: int = 42
) -> Tuple[float, float, float]:
    """
    Performs cluster bootstrap resampling at the document-family level to assess
    uncertainty in paired differences between two models.
    """
    rng = np.random.RandomState(random_seed)
    families = list(family_case_diffs.keys())
    n_families = len(families)

    if n_families <= 1:
        # Insufficient families for cluster bootstrap
        all_diffs = [d for diff_list in family_case_diffs.values() for d in diff_list]
        mean_diff = float(np.mean(all_diffs)) if all_diffs else 0.0
        return round(mean_diff, 4), round(mean_diff, 4), round(mean_diff, 4)

    boot_means = []
    for _ in range(n_bootstraps):
        sampled_fams = rng.choice(families, size=n_families, replace=True)
        sampled_diffs = []
        for fam in sampled_fams:
            sampled_diffs.extend(family_case_diffs[fam])
        if sampled_diffs:
            boot_means.append(np.mean(sampled_diffs))

    if not boot_means:
        return 0.0, 0.0, 0.0

    alpha = (1.0 - confidence_level) / 2.0
    lower = float(np.percentile(boot_means, alpha * 100))
    upper = float(np.percentile(boot_means, (1.0 - alpha) * 100))
    point = float(np.mean(boot_means))

    return round(point, 4), round(lower, 4), round(upper, 4)
