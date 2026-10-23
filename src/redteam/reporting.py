"""
src/redteam/reporting.py — Generates the 21 research artifacts in research/redteam_robustness/
by executing the canonical benchmark suite on the frozen LexAudit pipeline.
"""
import os
import csv
import json
import time
from typing import List, Dict, Any
from pathlib import Path

from src.config import ClauseRecord
from src.redteam.schema import (
    PerturbationType,
    PerturbationDifficulty,
    DetectionStatus,
    RedTeamCaseResult,
    RedTeamBatchReport
)
from src.redteam.fixtures import SYNTHETIC_FIXTURE_REGISTRY
from src.redteam.scenarios import get_canonical_benchmark_scenarios
from src.redteam.runner import RedTeamExperimentRunner
from src.redteam.metrics import compute_redteam_batch_report


def run_full_benchmark_and_generate_artifacts(output_dir: str = "research/redteam_robustness") -> RedTeamBatchReport:
    """
    Executes all 20 canonical scenarios and persists the complete 21-artifact research package.
    """
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    runner = RedTeamExperimentRunner()
    scenarios = get_canonical_benchmark_scenarios()
    case_results: List[RedTeamCaseResult] = []

    print(f"Executing {len(scenarios)} canonical red-team benchmark scenarios...")
    for sc in scenarios:
        doc_fn = SYNTHETIC_FIXTURE_REGISTRY.get(sc.source_doc_id)
        if not doc_fn:
            raise ValueError(f"Unknown fixture doc_id: {sc.source_doc_id}")
        clauses = doc_fn()
        case_res = runner.run_scenario(sc, clauses)
        case_results.append(case_res)
        print(f"  [{case_res.scenario_id}] {case_res.detection_status.value} (time: {case_res.execution_time_ms}ms)")

    batch_report = compute_redteam_batch_report(case_results)

    # 1. experiment_manifest.json
    manifest = {
        "benchmark_title": "LexAudit Phase 4D Self Red-Team Robustness Benchmark",
        "timestamp": batch_report.timestamp,
        "frozen_pipeline_version": "LexAudit 4C-A Frozen Baseline",
        "total_scenarios": batch_report.total_scenarios_attempted,
        "valid_transformations": batch_report.valid_transformations_count,
        "strict_eligible_scenarios": batch_report.strict_evaluation_eligible_count,
        "metric_summaries": {
            "structural_detection_rate": batch_report.structural_detection_rate,
            "mean_structural_channel_b_delta": batch_report.mean_structural_channel_b_delta,
            "rule_precision": batch_report.rule_precision,
            "rule_recall": batch_report.rule_recall,
            "rule_f1": batch_report.rule_f1,
            "duplicate_detector_available": False,
            "mean_duplicate_channel_b_delta": batch_report.mean_duplicate_channel_b_delta,
            "deletion_consequence_detection_rate": batch_report.deletion_consequence_detection_rate,
            "clean_control_false_positive_rate": batch_report.clean_control_false_positive_rate,
            "clean_control_mean_anomaly": batch_report.clean_control_mean_anomaly,
            "combined_detection_rate": batch_report.combined_detection_rate
        }
    }
    with open(out_path / "experiment_manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    # 2. perturbation_taxonomy.md
    with open(out_path / "perturbation_taxonomy.md", "w", encoding="utf-8") as f:
        f.write("""# Perturbation Scenario Taxonomy

| Category | Identifier | Target Detector | Ground Truth Condition | Evaluability Mode |
|---|---|---|---|---|
| P1 | Clause Displacement | Channel B (Discourse Transition) | SYNTHETIC_DISPLACEMENT | Strict ML Sensitivity |
| P2 | Clause Swapping | Channel B (Discourse Transition) | CLAUSE_SWAP | Strict ML Sensitivity |
| P3 | Exact Clause Duplication | Channel B / None | EXACT_DUPLICATION | Descriptive Only (`DEDICATED_DUPLICATE_DETECTOR_UNAVAILABLE`) |
| P4 | Near-Duplicate Clause | Channel A / B | NEAR_DUPLICATION | Exploratory Evaluation |
| P5 | Broken Internal Cross-Reference | CrossReferenceChecker | DANGLING_INTERNAL_REFERENCE | Strict Rule Verification |
| P6 | Missing Exhibit Reference | CrossReferenceChecker | DANGLING_EXHIBIT_REFERENCE | Strict Rule Verification |
| P7 | Date Chronology Inversion | DateLogicChecker | CHRONOLOGICAL_INVERSION | Strict Rule Verification |
| P8 | Clause Deletion | CrossReferenceChecker / None | CLAUSE_DELETION | Strict only if surviving dependency exists; else Descriptive |
| P9 | Clean Negative Control | Full Unified Pipeline | CLEAN_NEGATIVE_CONTROL | Strict False-Positive Evaluation |
| P10 | Combined Perturbations | Multi-Detector Ensemble | COMBINED_MULTI_PERTURBATION | Strict Compound Evaluation |
""")

    # 3. oracle_specification.md
    with open(out_path / "oracle_specification.md", "w", encoding="utf-8") as f:
        f.write("""# Independent Ground-Truth Oracle Specification

The Oracle (`src/redteam/oracle.py`) operates as a completely independent verification layer.
It strictly prohibits calling the evaluated models or rule checkers:
1. **Displacement / Swap**: Validated via clause sequence permutations, relative index invariant checking, and sequence length checks.
2. **Duplication**: Validated via pairwise text equivalence and unique inserted clause ID validation.
3. **Internal References**: Validated by compiling a regex-based independent section inventory and checking that the target section number is not declared as a heading.
4. **Exhibit References**: Validated by verifying absence of exhibit definitions matching the injected citation.
5. **Date Inversions**: Validated using pure standard library `datetime.strptime` comparisons between extracted date strings, bypassing `DateLogicChecker` and `dateparser`.
6. **Deletion Consequences**: Validated by scanning surviving clauses for citations pointing to the deleted section number.
7. **Negative Controls**: Validated by SHA-256 bitwise checksum equivalence.
""")

    # 4. scenario_catalog.csv
    with open(out_path / "scenario_catalog.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["scenario_id", "perturbation_type", "difficulty", "source_doc_id", "title", "expected_detector", "target_clause_ids", "limitations"])
        for sc in scenarios:
            writer.writerow([sc.scenario_id, sc.perturbation_type.value, sc.difficulty.value, sc.source_doc_id, sc.title, sc.expected_detector, "|".join(sc.target_clause_ids), sc.limitations])

    # 5. dataset_provenance.csv
    with open(out_path / "dataset_provenance.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["doc_id", "contract_type", "clause_count", "license", "confidentiality_tier", "purpose", "split"])
        writer.writerow(["SYNTH_DOC_01_MSA", "Master Services Agreement", 10, "CC0-1.0 Public Synthetic", "PUBLIC_NONCONFIDENTIAL", "Red-Team Robustness Benchmark", "synthetic_test"])
        writer.writerow(["SYNTH_DOC_02_SLA", "Software License Agreement", 8, "CC0-1.0 Public Synthetic", "PUBLIC_NONCONFIDENTIAL", "Red-Team Robustness Benchmark", "synthetic_test"])

    # 6. evaluation_split_manifest.csv
    with open(out_path / "evaluation_split_manifest.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["split_name", "document_count", "scenario_count", "leakage_risk_mitigation"])
        writer.writerow(["synthetic_test", 2, 20, "Held-out non-training synthetic fixtures; pure copy-on-write transient evaluation"])

    # 7. original_perturbed_checksums.csv
    with open(out_path / "original_perturbed_checksums.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["scenario_id", "perturbation_type", "original_checksum", "perturbed_checksum", "checksums_differentiated"])
        for c in case_results:
            diff = (c.original_checksum != c.perturbed_checksum)
            writer.writerow([c.scenario_id, c.perturbation_type.value, c.original_checksum, c.perturbed_checksum, diff])

    # 8. experiment_case_results.csv
    with open(out_path / "experiment_case_results.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "scenario_id", "perturbation_type", "difficulty", "detection_status", "attribution_valid",
            "delta_mean_combined", "delta_anomaly_count", "new_rule_flags_count",
            "mean_channel_a_delta", "mean_channel_b_delta", "max_affected_clause_b_delta",
            "failure_category", "execution_time_ms"
        ])
        for c in case_results:
            writer.writerow([
                c.scenario_id, c.perturbation_type.value, c.difficulty.value, c.detection_status.value, c.attribution_valid,
                c.delta_mean_combined, c.delta_anomaly_count, len(c.new_rule_flags),
                c.mean_channel_a_delta, c.mean_channel_b_delta, c.max_affected_clause_b_delta,
                c.failure_category or "NONE", c.execution_time_ms
            ])

    # 9. transformation_validity_results.csv
    with open(out_path / "transformation_validity_results.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["scenario_id", "valid_transformation", "oracle_condition", "ground_truth_supported", "eligible_for_strict_eval", "conditions_checked"])
        for c in case_results:
            o = c.oracle_result
            writer.writerow([c.scenario_id, o.valid_transformation, o.oracle_condition, o.ground_truth_supported, o.eligible_for_strict_evaluation, len(o.conditions)])

    # 10. structural_detection_results.csv
    with open(out_path / "structural_detection_results.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["scenario_id", "perturbation_type", "difficulty", "detection_status", "max_affected_b_delta", "delta_anomaly_count", "delta_combined"])
        for c in case_results:
            if c.perturbation_type in (PerturbationType.P1_DISPLACEMENT, PerturbationType.P2_SWAP):
                writer.writerow([c.scenario_id, c.perturbation_type.value, c.difficulty.value, c.detection_status.value, c.max_affected_clause_b_delta, c.delta_anomaly_count, c.delta_mean_combined])

    # 11. reference_detection_results.csv
    with open(out_path / "reference_detection_results.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["scenario_id", "perturbation_type", "detection_status", "attribution_valid", "new_rule_flags_count", "flag_types"])
        for c in case_results:
            if c.perturbation_type in (PerturbationType.P5_BROKEN_REFERENCE, PerturbationType.P6_MISSING_EXHIBIT):
                ftypes = "|".join([f.get("flag_type", "") for f in c.new_rule_flags])
                writer.writerow([c.scenario_id, c.perturbation_type.value, c.detection_status.value, c.attribution_valid, len(c.new_rule_flags), ftypes])

    # 12. date_detection_results.csv
    with open(out_path / "date_detection_results.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["scenario_id", "perturbation_type", "detection_status", "attribution_valid", "new_rule_flags_count", "flag_types"])
        for c in case_results:
            if c.perturbation_type == PerturbationType.P7_DATE_INVERSION:
                ftypes = "|".join([f.get("flag_type", "") for f in c.new_rule_flags])
                writer.writerow([c.scenario_id, c.perturbation_type.value, c.detection_status.value, c.attribution_valid, len(c.new_rule_flags), ftypes])

    # 13. duplicate_response_results.csv
    with open(out_path / "duplicate_response_results.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["scenario_id", "detection_status", "dedicated_detector_status", "mean_b_delta", "delta_combined", "descriptive_observation"])
        for c in case_results:
            if c.perturbation_type == PerturbationType.P3_EXACT_DUPLICATION:
                writer.writerow([
                    c.scenario_id, c.detection_status.value, "UNAVAILABLE", c.mean_channel_b_delta, c.delta_mean_combined,
                    "Channel B registers transition shifts, but no dedicated duplicate detection rule exists."
                ])

    # 14. deletion_consequence_results.csv
    with open(out_path / "deletion_consequence_results.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["scenario_id", "eligible_for_strict_eval", "detection_status", "new_rule_flags_count", "evaluation_mode"])
        for c in case_results:
            if c.perturbation_type == PerturbationType.P8_DELETION:
                mode = "STRICT_CONSEQUENCE" if c.oracle_result.eligible_for_strict_evaluation else "DESCRIPTIVE_ONLY"
                writer.writerow([c.scenario_id, c.oracle_result.eligible_for_strict_evaluation, c.detection_status.value, len(c.new_rule_flags), mode])

    # 15. negative_control_results.csv
    with open(out_path / "negative_control_results.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["scenario_id", "baseline_anomalies", "perturbed_anomalies", "delta_anomalies", "rule_violations", "false_positive_status"])
        for c in case_results:
            if c.perturbation_type == PerturbationType.P9_NEGATIVE_CONTROL:
                fp_status = "CLEAN_ZERO_FALSE_POSITIVES" if (c.delta_anomaly_count <= 0 and c.perturbed_rule_flag_count == 0) else "FALSE_POSITIVES_DETECTED"
                writer.writerow([c.scenario_id, c.original_anomaly_count, c.perturbed_anomaly_count, c.delta_anomaly_count, c.perturbed_rule_flag_count, fp_status])

    # 16. channel_ablation_results.csv
    with open(out_path / "channel_ablation_results.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["scenario_id", "perturbation_type", "channel_a_delta", "channel_b_delta", "dual_channel_combined_delta", "rule_checker_flags", "integrated_flags"])
        for c in case_results:
            ab = c.ablations
            writer.writerow([c.scenario_id, c.perturbation_type.value, ab.channel_a_only_anomaly_delta, ab.channel_b_only_anomaly_delta, ab.dual_channel_combined_delta, ab.rule_checker_flags_count, ab.integrated_pipeline_flags_count])

    # 17. threshold_sensitivity_results.csv
    with open(out_path / "threshold_sensitivity_results.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["threshold_b", "structural_detected_count", "structural_detection_rate", "notes"])
        struct_cases = [c for c in case_results if c.perturbation_type in (PerturbationType.P1_DISPLACEMENT, PerturbationType.P2_SWAP)]
        for th in [0.02, 0.04, 0.06, 0.08, 0.10, 0.12, 0.15]:
            det = sum(1 for c in struct_cases if c.max_affected_clause_b_delta >= th or c.delta_anomaly_count > 0)
            rate = det / max(len(struct_cases), 1)
            writer.writerow([th, det, round(rate, 4), f"Sensitivity evaluated across {len(struct_cases)} structural scenarios"])

    # 18. latency_results.csv
    with open(out_path / "latency_results.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["scenario_id", "execution_time_ms", "throughput_scenarios_per_sec"])
        for c in case_results:
            t = max(c.execution_time_ms, 0.1)
            writer.writerow([c.scenario_id, t, round(1000.0 / t, 2)])

    # 19. failure_analysis.csv
    with open(out_path / "failure_analysis.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["scenario_id", "perturbation_type", "detection_status", "failure_category", "failure_explanation", "candidate_remediation"])
        for c in case_results:
            if c.detection_status in (DetectionStatus.NOT_DETECTED, DetectionStatus.NOT_APPLICABLE):
                remediation = "None required (exploratory / unsupported)" if c.detection_status == DetectionStatus.NOT_APPLICABLE else "Tune boundary sensitivity or extend regex grammar"
                writer.writerow([c.scenario_id, c.perturbation_type.value, c.detection_status.value, c.failure_category or "NONE", c.failure_explanation or "None", remediation])

    # 20. metric_definitions.md
    with open(out_path / "metric_definitions.md", "w", encoding="utf-8") as f:
        f.write("""# LexAudit Phase 4D Metric Definitions

### 1. Structural Sensitivity (P1, P2)
- **Mean Channel B Delta**: Average increase in Channel B transition score across affected boundary slots.
- **Affected Boundary Detection Rate**: Proportion of structural moves causing Channel B transition increase $\ge 0.08$ or newly flagged anomalies.

### 2. Rule Precision, Recall, and F1 (P5, P6, P7, P8)
- **True Positive (TP)**: Injected rule violation detected and attributed to the affected clause/scope.
- **False Negative (FN)**: Injected rule violation eligible for strict evaluation that went undetected.
- **False Positive (FP)**: Spurious rule violation detected on clean negative controls.
- **True Negative (TN)**: Clean negative control producing zero false violations.
- **Precision**: $\\frac{TP}{TP + FP}$
- **Recall**: $\\frac{TP}{TP + FN}$
- **F1 Score**: $\\frac{2 \\times P \\times R}{P + R}$

### 3. Duplicate Sensitivity (P3)
- Evaluated descriptively via Channel B shift. Reported as `DEDICATED_DUPLICATE_DETECTOR_UNAVAILABLE`.

### 4. Clean Negative Control FPR (P9)
- Proportion of unperturbed clean contracts that trigger false positive repair recommendations or rule violations.
""")

    # 21. reproduction_instructions.md
    with open(out_path / "reproduction_instructions.md", "w", encoding="utf-8") as f:
        f.write("""# Phase 4D Benchmark Reproduction Instructions

To reproduce all 20 canonical scenario evaluations and regenerate the 21 research artifacts:

```bash
python -c "from src.redteam.reporting import run_full_benchmark_and_generate_artifacts; run_full_benchmark_and_generate_artifacts()"
```

To run the unit test suite:
```bash
pytest tests/test_redteam_transformations.py tests/test_redteam_oracle.py tests/test_redteam_runner.py -v
```
""")

    print(f"Successfully generated all 21 research artifacts in '{output_dir}'.")
    return batch_report


if __name__ == "__main__":
    run_full_benchmark_and_generate_artifacts()
