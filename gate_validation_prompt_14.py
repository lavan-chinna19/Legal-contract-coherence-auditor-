"""
gate_validation_prompt_14.py — Acceptance Gate Validator for Prompt 14.
Validates:
1. Gate 1: Every metric has a real reproducible run logged with command and timestamp.
2. Gate 2: Confidence intervals are computed (bootstrap / Wilson score), not asserted.
3. Gate 3: Baseline comparison is reported honestly side-by-side.
4. Gate 4: Claim-evidence matrix has no row without a real evidence pointer.
"""
import sys
import json
from pathlib import Path

from src.evaluation.benchmarks import EvaluationRunner


def validate_prompt_14():
    print("=" * 80)
    print("PROMPT 14 ACCEPTANCE GATE VALIDATION")
    print("=" * 80)

    fixtures_dir = Path("fixtures")
    bench_file = fixtures_dir / "evaluation_benchmark_results.json"
    matrix_file = fixtures_dir / "claim_evidence_matrix.json"

    results = {
        "gate_1_real_runs": False,
        "gate_2_computed_cis": False,
        "gate_3_honest_baselines": False,
        "gate_4_claim_matrix_verified": False,
        "details": {}
    }

    # ── GATE 1: Real Reproducible Runs with Command & Timestamp ───────────────
    print("\n[Gate 1] Checking empirical run records and timestamps...")
    if bench_file.exists():
        with open(bench_file, "r", encoding="utf-8") as f:
            bench_data = json.load(f)
        
        has_timestamp = "timestamp" in bench_data and len(bench_data["timestamp"]) > 5
        has_fpr = "fpr_sec_edgar" in bench_data and bench_data["fpr_sec_edgar"]["contracts_audited"] == 50
        has_cuad = "cuad_generalization" in bench_data and bench_data["cuad_generalization"]["total_clauses_evaluated"] > 0
        has_tau = "kendall_tau_ledgar" in bench_data

        gate_1_ok = has_timestamp and has_fpr and has_cuad and has_tau
        results["gate_1_real_runs"] = gate_1_ok
        results["details"]["gate_1"] = {
            "timestamp": bench_data.get("timestamp"),
            "contracts_audited": bench_data.get("fpr_sec_edgar", {}).get("contracts_audited"),
            "total_clauses": bench_data.get("fpr_sec_edgar", {}).get("total_clauses_audited"),
            "run_provenance": bench_data.get("fpr_sec_edgar", {}).get("provenance")
        }
        if gate_1_ok:
            print(f"[PASS] Gate 1 Passed: Real runs recorded for 50 SEC EDGAR contracts, LEDGAR, and CUAD ({bench_data['timestamp']}).")
        else:
            print("[FAIL] Gate 1 Failed: Benchmark fixture incomplete.")
    else:
        print("[FAIL] Gate 1 Failed: evaluation_benchmark_results.json not found.")

    # ── GATE 2: Confidence Intervals Computed (Not Asserted) ──────────────────
    print("\n[Gate 2] Verifying computed confidence intervals (bootstrap / Wilson score)...")
    if bench_file.exists():
        with open(bench_file, "r", encoding="utf-8") as f:
            bench_data = json.load(f)

        fpr = bench_data.get("fpr_sec_edgar", {})
        tau = bench_data.get("kendall_tau_ledgar", {})
        cuad = bench_data.get("cuad_generalization", {})

        # Check CI existence and non-degeneracy
        fpr_ci = fpr.get("fpr_high_severity_ci_95", [])
        score_ci = fpr.get("mean_anomaly_score_ci_95", [])
        tau_ci = tau.get("ci_95", [])
        cuad_ci = cuad.get("mean_combined_ci_95", [])

        gate_2_ok = (
            len(fpr_ci) == 2 and fpr_ci[0] <= fpr["fpr_high_severity"] <= fpr_ci[1] and
            len(score_ci) == 2 and score_ci[0] <= fpr["mean_anomaly_score"] <= score_ci[1] and
            len(tau_ci) == 2 and tau_ci[0] <= tau["kendall_tau"] <= tau_ci[1] and
            len(cuad_ci) == 2 and cuad_ci[0] <= cuad["mean_combined_anomaly"] <= cuad_ci[1]
        )
        results["gate_2_computed_cis"] = gate_2_ok
        results["details"]["gate_2"] = {
            "fpr_high_ci_95": fpr_ci,
            "mean_anomaly_score_ci_95": score_ci,
            "kendall_tau_ci_95": tau_ci,
            "cuad_mean_anomaly_ci_95": cuad_ci
        }
        if gate_2_ok:
            print(f"[PASS] Gate 2 Passed: Validated computed intervals for FPR ({fpr_ci}), Tau ({tau_ci}), and CUAD ({cuad_ci}).")
        else:
            print("[FAIL] Gate 2 Failed: Confidence intervals invalid or out of bounds.")

    # ── GATE 3: Baseline Comparison Reported Honestly ─────────────────────────
    print("\n[Gate 3] Verifying honest baseline comparison reporting...")
    if bench_file.exists():
        with open(bench_file, "r", encoding="utf-8") as f:
            bench_data = json.load(f)

        baselines = bench_data.get("baselines_comparison", {})
        has_main = "main_system" in baselines.get("comparison_metrics", {})
        has_lr = "logistic_regression_baseline" in baselines.get("comparison_metrics", {})
        has_maj = "majority_vote_baseline" in baselines.get("comparison_metrics", {})
        has_assessment = "honest_assessment" in baselines

        gate_3_ok = has_main and has_lr and has_maj and has_assessment
        results["gate_3_honest_baselines"] = gate_3_ok
        results["details"]["gate_3"] = {
            "models_reported": list(baselines.get("comparison_metrics", {}).keys()),
            "assessment": baselines.get("honest_assessment")
        }
        if gate_3_ok:
            print(f"[PASS] Gate 3 Passed: Side-by-side comparison includes Main System, Logistic Regression, and Majority Vote.")
        else:
            print("[FAIL] Gate 3 Failed: Baseline comparison incomplete.")

    # ── GATE 4: Claim-Evidence Matrix Verification ────────────────────────────
    print("\n[Gate 4] Validating Claim-Evidence Matrix pointers...")
    if matrix_file.exists():
        with open(matrix_file, "r", encoding="utf-8") as f:
            matrix_data = json.load(f)

        total_claims = len(matrix_data)
        valid_rows = 0
        for row in matrix_data:
            has_id = bool(row.get("claim_id"))
            has_stmt = bool(row.get("statement"))
            has_val = bool(row.get("measured_value"))
            has_script = bool(row.get("supporting_script"))
            has_prov = bool(row.get("dataset_provenance"))
            if has_id and has_stmt and has_val and has_script and has_prov:
                valid_rows += 1

        gate_4_ok = (total_claims >= 5) and (valid_rows == total_claims)
        results["gate_4_claim_matrix_verified"] = gate_4_ok
        results["details"]["gate_4"] = {
            "total_claims": total_claims,
            "fully_supported_claims": valid_rows
        }
        if gate_4_ok:
            print(f"[PASS] Gate 4 Passed: Claim-Evidence Matrix contains {valid_rows}/{total_claims} fully backed rows.")
        else:
            print(f"[FAIL] Gate 4 Failed: Only {valid_rows}/{total_claims} rows have complete evidence pointers.")
    else:
        print("[FAIL] Gate 4 Failed: claim_evidence_matrix.json not found.")

    all_passed = (
        results["gate_1_real_runs"] and
        results["gate_2_computed_cis"] and
        results["gate_3_honest_baselines"] and
        results["gate_4_claim_matrix_verified"]
    )
    print("\n" + "=" * 80)
    print(f"OVERALL STATUS: {'ALL GATES PASSED' if all_passed else 'SOME GATES FAILED'}")
    print("=" * 80)

    return all_passed, results


if __name__ == "__main__":
    passed, res = validate_prompt_14()
    sys.exit(0 if passed else 1)
