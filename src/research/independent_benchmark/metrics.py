"""
src/research/independent_benchmark/metrics.py
Metric Computation and Evaluation Bundles for Structural Coherence Detection.
"""
from typing import List, Dict, Any, Tuple
from collections import defaultdict
import numpy as np

from src.research.independent_benchmark.schema import (
    EvaluationPrediction,
    MetricBundle,
    WilsonInterval
)
from src.research.independent_benchmark.statistics import compute_wilson_score_interval


def calculate_detection_metrics(
    predictions: List[EvaluationPrediction],
    confidence_level: float = 0.95
) -> MetricBundle:
    """
    Computes exact confusion matrix and evaluation metrics for a set of predictions.
    Separates family-level metrics and computes two-sided Wilson confidence intervals.
    """
    total = len(predictions)
    tp = sum(1 for p in predictions if p.is_ground_truth_anomaly and p.predicted_anomaly)
    fp = sum(1 for p in predictions if not p.is_ground_truth_anomaly and p.predicted_anomaly)
    fn = sum(1 for p in predictions if p.is_ground_truth_anomaly and not p.predicted_anomaly)
    tn = sum(1 for p in predictions if not p.is_ground_truth_anomaly and not p.predicted_anomaly)

    prec = float(tp) / float(tp + fp) if (tp + fp) > 0 else 0.0
    rec = float(tp) / float(tp + fn) if (tp + fn) > 0 else 0.0
    spec = float(tn) / float(tn + fp) if (tn + fp) > 0 else 0.0
    fpr = float(fp) / float(fp + tn) if (fp + tn) > 0 else 0.0
    f1 = (2.0 * prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0
    bal_acc = (rec + spec) / 2.0

    # Wilson intervals
    rec_ci = compute_wilson_score_interval(tp, tp + fn, confidence_level=confidence_level)
    prec_ci = compute_wilson_score_interval(tp, tp + fp, confidence_level=confidence_level)
    spec_ci = compute_wilson_score_interval(tn, tn + fp, confidence_level=confidence_level)

    # Family-level breakdown
    fam_preds = defaultdict(list)
    for p in predictions:
        fam_preds[p.document_family_id].append(p)

    family_results = {}
    for fam_id, preds in fam_preds.items():
        f_tp = sum(1 for p in preds if p.is_ground_truth_anomaly and p.predicted_anomaly)
        f_fp = sum(1 for p in preds if not p.is_ground_truth_anomaly and p.predicted_anomaly)
        f_fn = sum(1 for p in preds if p.is_ground_truth_anomaly and not p.predicted_anomaly)
        f_tn = sum(1 for p in preds if not p.is_ground_truth_anomaly and not p.predicted_anomaly)
        f_rec = float(f_tp) / float(f_tp + f_fn) if (f_tp + f_fn) > 0 else 0.0
        f_spec = float(f_tn) / float(f_tn + f_fp) if (f_tn + f_fp) > 0 else 0.0
        family_results[fam_id] = {
            "total": len(preds),
            "tp": f_tp,
            "fp": f_fp,
            "fn": f_fn,
            "tn": f_tn,
            "recall": round(f_rec, 4),
            "specificity": round(f_spec, 4)
        }

    return MetricBundle(
        total_cases=total,
        tp=tp,
        fp=fp,
        fn=fn,
        tn=tn,
        precision=round(prec, 4),
        recall=round(rec, 4),
        specificity=round(spec, 4),
        f1=round(f1, 4),
        false_positive_rate=round(fpr, 4),
        balanced_accuracy=round(bal_acc, 4),
        recall_ci=rec_ci,
        precision_ci=prec_ci,
        specificity_ci=spec_ci,
        family_count=len(fam_preds),
        family_level_results=family_results
    )
