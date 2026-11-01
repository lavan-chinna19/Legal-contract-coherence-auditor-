"""
tests/test_benchmark_consistency.py — Automated Consistency Tests for Phase 4C-A Benchmark.

Ensures that:
1. Case-level data and ranks in benchmark_case_level_results.csv are authoritative and immutable.
2. Aggregate metrics (Top-1, Top-3, MRR, Mean Rank, Median Rank) mathematically agree with case-level ranks.
3. Paired baseline statistics (Cosine Heuristic, Random, Identity) match case-level differences.
4. Any regression or divergence between case-level data and reported metrics immediately triggers test failure.
"""
import csv
import json
import pytest
import numpy as np
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = REPO_ROOT / "design" / "ui_redesign" / "phase_04ca" / "benchmark_case_level_results.csv"
JSON_PATH = REPO_ROOT / "design" / "ui_redesign" / "phase_04ca" / "benchmark_metric_recalculation.json"
NEG_PATH = REPO_ROOT / "design" / "ui_redesign" / "phase_04ca" / "negative_control_decomposition.csv"

# Authoritative ground truth ranks for the 9 held-out contracts
AUTHORITATIVE_SCORER_RANKS = [8, 1, 2, 1, 9, 3, 3, 1, 2]
AUTHORITATIVE_COSINE_RANKS = [8, 4, 2, 2, 6, 4, 1, 3, 2]


def test_case_level_data_integrity():
    """Verify that case-level results file exists and contains exactly 9 valid cases with authoritative ranks."""
    assert CSV_PATH.exists(), f"Benchmark case-level results CSV missing: {CSV_PATH}"
    
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        
    assert len(rows) == 9, f"Expected 9 benchmark contracts, found {len(rows)}"
    
    scorer_ranks = [int(r["truth_slot_rank"]) for r in rows]
    cosine_ranks = [int(r["cosine_truth_rank"]) for r in rows]
    
    assert scorer_ranks == AUTHORITATIVE_SCORER_RANKS, (
        f"Scorer ranks mismatch! Found {scorer_ranks}, expected {AUTHORITATIVE_SCORER_RANKS}"
    )
    assert cosine_ranks == AUTHORITATIVE_COSINE_RANKS, (
        f"Cosine ranks mismatch! Found {cosine_ranks}, expected {AUTHORITATIVE_COSINE_RANKS}"
    )


def test_aggregate_metrics_mathematical_derivation():
    """Recompute aggregate metrics directly from case-level ranks and verify exact mathematical equality."""
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
        
    ranks = np.array([int(r["truth_slot_rank"]) for r in rows])
    rrs = np.array([float(r["scorer_rr"]) for r in rows])
    n = len(ranks)
    
    # 1. Top-1 Recovery Rate
    top1_count = int(np.sum(ranks == 1))
    assert top1_count == 3, f"Expected 3 Top-1 recoveries, got {top1_count}"
    assert np.isclose(top1_count / n, 3 / 9, atol=1e-4)
    
    # 2. Top-3 Recovery Rate
    top3_count = int(np.sum(ranks <= 3))
    assert top3_count == 7, f"Expected 7 Top-3 recoveries, got {top3_count}"
    assert np.isclose(top3_count / n, 7 / 9, atol=1e-4)
    
    # 3. Mean Reciprocal Rank (MRR)
    expected_mrr = np.mean(1.0 / ranks)
    actual_mrr = np.mean(rrs)
    assert np.isclose(actual_mrr, expected_mrr, atol=1e-4)
    assert np.isclose(actual_mrr, 0.5448, atol=5e-4), f"MRR {actual_mrr:.4f} diverges from 0.5448"
    
    # 4. Mean and Median Rank
    assert np.isclose(np.mean(ranks), 30 / 9, atol=1e-2), f"Mean rank {np.mean(ranks)} != 3.33"
    assert np.median(ranks) == 2.0, f"Median rank {np.median(ranks)} != 2.0"
    
    # 5. Verify against benchmark_metric_recalculation.json
    assert JSON_PATH.exists(), f"Benchmark recalculation JSON missing: {JSON_PATH}"
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        recalc = json.load(f)
        
    metrics = recalc["recalculated_metrics"]
    assert metrics["top1_numerator"] == 3
    assert metrics["top1_denominator"] == 9
    assert np.isclose(metrics["top1_recovery_rate"], 0.3333, atol=1e-4)
    assert metrics["top3_numerator"] == 7
    assert metrics["top3_denominator"] == 9
    assert np.isclose(metrics["top3_recovery_rate"], 0.7778, atol=1e-4)
    assert np.isclose(metrics["mean_reciprocal_rank"], 0.5447, atol=5e-4)
    assert np.isclose(metrics["mean_rank"], 3.33, atol=1e-2)
    assert metrics["median_rank"] == 2.0


def test_paired_baseline_consistency():
    """Verify paired comparison against Cosine Heuristic matches case-by-case reciprocal rank deltas."""
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
        
    scorer_rrs = np.array([float(r["scorer_rr"]) for r in rows])
    cosine_rrs = np.array([float(r["cosine_rr"]) for r in rows])
    paired_deltas = np.array([float(r["paired_rr_delta_vs_cosine"]) for r in rows])
    
    # Check that each row's delta is exact
    expected_deltas = scorer_rrs - cosine_rrs
    assert np.allclose(paired_deltas, expected_deltas, atol=1e-4)
    
    # Check mean paired delta
    mean_delta = float(np.mean(paired_deltas))
    assert np.isclose(mean_delta, 0.1420, atol=1e-4)
    
    # Verify bootstrap paired CI crosses zero (confirming unproven statistical superiority)
    rng = np.random.RandomState(42)
    boot_deltas = [np.mean(paired_deltas[rng.choice(len(paired_deltas), size=len(paired_deltas), replace=True)]) for _ in range(5000)]
    ci_low = float(np.percentile(boot_deltas, 2.5))
    ci_high = float(np.percentile(boot_deltas, 97.5))
    
    assert ci_low < 0.0 < ci_high, f"Expected 95% CI to cross zero, but got [{ci_low:.4f}, {ci_high:.4f}]"


def test_negative_control_abstention_consistency():
    """Verify negative control decomposition and 100% abstention under default threshold."""
    assert NEG_PATH.exists(), f"Negative control CSV missing: {NEG_PATH}"
    with open(NEG_PATH, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
        
    assert len(rows) == 9
    abstained = [r["abstains_with_threshold_0_005"].lower() == "true" for r in rows]
    assert all(abstained), "All 9 negative controls must abstain under default 0.005 threshold"
