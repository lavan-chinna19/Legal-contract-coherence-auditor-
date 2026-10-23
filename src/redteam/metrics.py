"""
src/redteam/metrics.py — Metric family computations and statistical evaluations for red-team benchmarks.
Computes structural sensitivity, rule detection confusion matrices, duplicate descriptive impact,
and clean-document false-positive rates with rigorous denominator discipline.
"""
from typing import List, Dict, Any, Tuple
from datetime import datetime, timezone
from src.redteam.schema import (
    PerturbationType,
    DetectionStatus,
    RedTeamCaseResult,
    RedTeamBatchReport
)


def compute_redteam_batch_report(case_results: List[RedTeamCaseResult]) -> RedTeamBatchReport:
    """
    Aggregates individual RedTeamCaseResult records into a formal RedTeamBatchReport.
    Maintains strict separation between structural sensitivity, rule metrics, and exploratory tests.
    """
    total_attempted = len(case_results)
    valid_transformations = sum(1 for c in case_results if c.oracle_result.valid_transformation)
    invalid_transformations = total_attempted - valid_transformations
    strict_eligible = sum(1 for c in case_results if c.oracle_result.eligible_for_strict_evaluation)

    # 1. Structural Scenarios (P1 Displacement, P2 Swap)
    structural_cases = [c for c in case_results if c.perturbation_type in (PerturbationType.P1_DISPLACEMENT, PerturbationType.P2_SWAP)]
    struct_eval = len(structural_cases)
    struct_detected = sum(1 for c in structural_cases if c.detection_status == DetectionStatus.DETECTED)
    struct_rate = (struct_detected / max(struct_eval, 1)) if struct_eval > 0 else 0.0
    mean_struct_b_delta = sum(c.max_affected_clause_b_delta for c in structural_cases) / max(struct_eval, 1)

    # 2. Rule Scenarios (P5 Broken Ref, P6 Missing Exhibit, P7 Date Inversion, P8 Deletion w/ surviving ref)
    rule_cases = [
        c for c in case_results
        if c.oracle_result.eligible_for_strict_evaluation and
        c.perturbation_type in (
            PerturbationType.P5_BROKEN_REFERENCE,
            PerturbationType.P6_MISSING_EXHIBIT,
            PerturbationType.P7_DATE_INVERSION,
            PerturbationType.P8_DELETION
        )
    ]
    rule_eval = len(rule_cases)
    tp = sum(1 for c in rule_cases if c.detection_status == DetectionStatus.DETECTED and c.attribution_valid)
    fn = sum(1 for c in rule_cases if c.detection_status != DetectionStatus.DETECTED)

    # Negative controls evaluate false positives and true negatives for rule and ML detectors
    clean_cases = [c for c in case_results if c.perturbation_type == PerturbationType.P9_NEGATIVE_CONTROL]
    clean_eval = len(clean_cases)
    # A clean case is a True Negative if 0 false positives produced
    tn = sum(1 for c in clean_cases if c.perturbed_rule_flag_count == 0 and c.delta_anomaly_count <= 0)
    fp = sum(1 for c in clean_cases if c.perturbed_rule_flag_count > 0 or c.delta_anomaly_count > 0)

    precision = tp / max(tp + fp, 1) if (tp + fp) > 0 else 0.0
    recall = tp / max(tp + fn, 1) if (tp + fn) > 0 else 0.0
    f1 = (2 * precision * recall) / max(precision + recall, 1e-9) if (precision + recall) > 0 else 0.0

    # 3. Duplicate Scenarios (P3 Exact Duplication)
    dup_cases = [c for c in case_results if c.perturbation_type == PerturbationType.P3_EXACT_DUPLICATION]
    dup_eval = len(dup_cases)
    mean_dup_b_delta = sum(c.max_affected_clause_b_delta for c in dup_cases) / max(dup_eval, 1)

    # 4. Deletion Scenarios (P8 Deletion)
    del_cases = [c for c in case_results if c.perturbation_type == PerturbationType.P8_DELETION]
    del_eval = len(del_cases)
    del_consequence_detected = sum(
        1 for c in del_cases
        if c.oracle_result.eligible_for_strict_evaluation and c.detection_status == DetectionStatus.DETECTED
    )
    del_consequence_eligible = sum(1 for c in del_cases if c.oracle_result.eligible_for_strict_evaluation)
    del_rate = (del_consequence_detected / max(del_consequence_eligible, 1)) if del_consequence_eligible > 0 else 0.0

    # 5. Clean Negative Controls
    clean_fp_rate = fp / max(clean_eval, 1) if clean_eval > 0 else 0.0
    clean_mean_anom = sum(c.perturbed_anomaly_count for c in clean_cases) / max(clean_eval, 1)

    # 6. Combined Scenarios (P10)
    comb_cases = [c for c in case_results if c.perturbation_type == PerturbationType.P10_COMBINED]
    comb_eval = len(comb_cases)
    comb_detected = sum(1 for c in comb_cases if c.detection_status == DetectionStatus.DETECTED)
    comb_rate = (comb_detected / max(comb_eval, 1)) if comb_eval > 0 else 0.0

    return RedTeamBatchReport(
        timestamp=datetime.now(timezone.utc).isoformat(),
        total_scenarios_attempted=total_attempted,
        valid_transformations_count=valid_transformations,
        invalid_transformations_count=invalid_transformations,
        strict_evaluation_eligible_count=strict_eligible,
        structural_scenarios_evaluated=struct_eval,
        structural_detection_rate=round(struct_rate, 4),
        mean_structural_channel_b_delta=round(mean_struct_b_delta, 4),
        rule_scenarios_evaluated=rule_eval,
        rule_true_positives=tp,
        rule_false_negatives=fn,
        rule_false_positives=fp,
        rule_true_negatives=tn,
        rule_precision=round(precision, 4),
        rule_recall=round(recall, 4),
        rule_f1=round(f1, 4),
        duplicate_scenarios_evaluated=dup_eval,
        duplicate_detector_available=False,  # Explicitly documented limitation
        mean_duplicate_channel_b_delta=round(mean_dup_b_delta, 4),
        deletion_scenarios_evaluated=del_eval,
        deletion_consequence_detection_rate=round(del_rate, 4),
        negative_controls_evaluated=clean_eval,
        clean_control_false_positive_rate=round(clean_fp_rate, 4),
        clean_control_mean_anomaly=round(clean_mean_anom, 4),
        combined_scenarios_evaluated=comb_eval,
        combined_detection_rate=round(comb_rate, 4),
        case_results=case_results
    )
