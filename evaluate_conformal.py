"""
evaluate_conformal.py — Evaluates Conformal Calibration on Synthetic Shuffle Data (Prompt 9).

Work Package C & Acceptance Gate 2:
- Fits ConformalCalibrator strictly on synthetic shuffle calibration set.
- Evaluates empirical coverage on held-out synthetic shuffle test set.
- Stores real computed metrics and calibration state to fixtures/ directory.
- Displays target coverage, empirical coverage, and delta with full provenance.
"""
import os
import sys
import json
import time
from pathlib import Path
from typing import List, Tuple
import numpy as np

from src.config import EDGAR_RAW_DIR, ClauseRecord
from src.segmentation.factory import get_segmenter
from src.calibration.synthetic_generator import (
    SyntheticShuffleDatasetGenerator,
    assert_is_synthetic_only
)
from src.calibration.conformal import ConformalCalibrator
from src.scoring.channel_b import ChannelBScorer


def run_conformal_evaluation():
    print("=" * 80, flush=True)
    print("  PROMPT 9: CONFORMAL CALIBRATION EVALUATION (DISTRIBUTION-FREE UQ)", flush=True)
    print("=" * 80, flush=True)
    print("Constraint: Calibration and validation sets are strictly synthetic-shuffle only.", flush=True)

    # 1. Discover raw EDGAR documents for base clause pools
    segmenter = get_segmenter("v1")
    txt_files = sorted(list(EDGAR_RAW_DIR.glob("*.txt")))
    if len(txt_files) < 2:
        print("FAIL: Insufficient EDGAR source files found.", flush=True)
        sys.exit(1)

    print(f"\n[1/5] Loading and segmenting base documents...", flush=True)
    source_docs: List[Tuple[str, List[ClauseRecord]]] = []
    for f in txt_files[:4]:
        text = open(f, encoding="utf-8").read()
        clauses = segmenter.segment(text, doc_id=f.stem)[:12]
        if len(clauses) >= 4:
            source_docs.append((f.stem, clauses))
            print(f"  - Loaded {f.name}: {len(clauses)} clauses", flush=True)

    # 2. Generate Synthetic-Only Calibration and Held-Out Splits
    print("\n[2/5] Generating synthetic shuffle-test datasets (Acceptance Gate 1)...", flush=True)
    generator = SyntheticShuffleDatasetGenerator(seed=123)
    cal_items, test_items = generator.generate_calibration_and_test_splits(
        source_documents=source_docs,
        cal_fraction=0.6,
        items_per_doc=4
    )

    # Validate Gate 1 assertions
    assert_is_synthetic_only(cal_items)
    assert_is_synthetic_only(test_items)
    print(f"  - Generated {len(cal_items)} calibration synthetic sequences.", flush=True)
    print(f"  - Generated {len(test_items)} held-out test synthetic sequences.", flush=True)
    print("  [PASS] Acceptance Gate 1: Provably synthetic-only calibration provenance confirmed.", flush=True)

    # 3. Compute Anomaly Scores using Fine-Tuned Channel B Coherence Model
    print("\n[3/5] Scoring synthetic clauses with Fine-Tuned Channel B Model...", flush=True)
    channel_b = ChannelBScorer()

    def extract_scores(items):
        y_true = []
        y_pred = []
        for it in items:
            ft_results = channel_b.score_document_clauses(it.clauses)
            for idx, (score, _) in enumerate(ft_results):
                y_true.append(it.ground_truth_anomaly[idx])
                y_pred.append(score)
        return np.array(y_true, dtype=np.float64), np.array(y_pred, dtype=np.float64)

    t0 = time.time()
    y_true_cal, y_pred_cal = extract_scores(cal_items)
    y_true_test, y_pred_test = extract_scores(test_items)
    elapsed = time.time() - t0
    print(f"  - Scored {len(y_true_cal)} calibration clauses & {len(y_true_test)} test clauses in {elapsed:.2f}s.", flush=True)

    # 4. Fit Conformal Calibrator (crepes / exact split quantile)
    print("\n[4/5] Fitting ConformalCalibrator at 90% Target Coverage...", flush=True)
    target_coverage = 0.90
    calibrator = ConformalCalibrator(target_coverage=target_coverage, use_crepes=True)
    calibrator.fit(y_true_cal, y_pred_cal, calibration_source="synthetic_shuffle_only")

    # 5. Evaluate Empirical Coverage on Held-Out Test Set
    print("\n[5/5] Evaluating empirical coverage on held-out test split (Acceptance Gate 2)...", flush=True)
    coverage_metrics = calibrator.evaluate_coverage(
        y_true=y_true_test,
        y_pred=y_pred_test,
        confidence_level=target_coverage
    )

    # Save state and metrics fixtures
    fixtures_dir = Path("fixtures")
    fixtures_dir.mkdir(parents=True, exist_ok=True)
    state_fixture_path = fixtures_dir / "conformal_calibration_fixture.json"
    metrics_fixture_path = fixtures_dir / "conformal_metrics.json"

    calibrator.save_state(state_fixture_path)

    metrics_payload = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "target_coverage": coverage_metrics["target_coverage"],
        "empirical_coverage": coverage_metrics["empirical_coverage"],
        "coverage_delta": coverage_metrics["coverage_delta"],
        "mean_interval_width": coverage_metrics["mean_interval_width"],
        "calibration_sample_size": len(y_true_cal),
        "test_sample_size": len(y_true_test),
        "calibration_source": "synthetic_shuffle_only",
        "conformal_quantile": round(calibrator.conformal_quantile, 4),
        "provenance": "evaluate_conformal.py execution over held-out synthetic EDGAR shuffle test set"
    }

    with open(metrics_fixture_path, "w", encoding="utf-8") as f:
        json.dump(metrics_payload, f, indent=2)

    print("\n" + "=" * 80, flush=True)
    print("                    EMPIRICAL CONFORMAL CALIBRATION RESULTS", flush=True)
    print("=" * 80, flush=True)
    print(f"{'Metric':<30} {'Value':<15} {'Notes':<35}", flush=True)
    print("-" * 80, flush=True)
    print(f"{'Target Coverage Level':<30} {coverage_metrics['target_coverage']*100:.1f}% {'Documented confidence target':<35}")
    print(f"{'Empirical Test Coverage':<30} {coverage_metrics['empirical_coverage']*100:.1f}% {'Measured on held-out synthetic set':<35}")
    print(f"{'Coverage Delta (Emp - Tgt)':<30} {coverage_metrics['coverage_delta']*100:+.2f}% {'Distribution-free finite error':<35}")
    print(f"{'Mean Interval Width':<30} {coverage_metrics['mean_interval_width']:.4f} {'Sharpness / interval compactness':<35}")
    print(f"{'Conformal Nonconformity Q':<30} {calibrator.conformal_quantile:.4f} {'Quantile bound added to residuals':<35}")
    print(f"{'Calibration Set Size (clauses)':<30} {len(y_true_cal)} {'Provably synthetic-only':<35}")
    print(f"{'Held-Out Test Size (clauses)':<30} {len(y_true_test)} {'Provably synthetic-only':<35}")
    print(f"{'Calibration Source':<30} {calibrator.calibration_source} {'Visible limitation tag':<35}")
    print("-" * 80, flush=True)
    print(f"Saved Calibration State: {state_fixture_path}", flush=True)
    print(f"Saved Metrics Fixture:   {metrics_fixture_path}", flush=True)
    print("=" * 80, flush=True)


if __name__ == "__main__":
    run_conformal_evaluation()
