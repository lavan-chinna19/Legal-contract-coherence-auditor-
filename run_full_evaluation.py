"""
run_full_evaluation.py — Main Execution Script for Prompt 14 Full Benchmark & Claim-Evidence Validation.
Runs all 6 Work Packages (A-F) with real empirical runs, logs all metrics with timestamps & 95% CIs,
and writes structured fixtures to fixtures/evaluation_benchmark_results.json and fixtures/claim_evidence_matrix.json.
"""
import sys
import json
import time
from pathlib import Path

from src.evaluation.benchmarks import EvaluationRunner


def main():
    print("=" * 80)
    print("  LEGAL CONTRACT COHERENCE AUDITOR: PROMPT 14 FULL BENCHMARK SUITE")
    print("=" * 80)

    start_time = time.time()
    runner = EvaluationRunner()

    # 0. Starting State Verification
    print("\n[0/6] Starting State Verification: Single document end-to-end check...")
    from src.config import ClauseRecord
    sample_clause = [
        ClauseRecord("check_0", "check_doc", "Section 1.01. Definitions. 'Terms' defined herein.", "Definitions", 0, 0, 52, "test"),
        ClauseRecord("check_1", "check_doc", "Section 1.02. Payment. Remit under Section 1.01.", "Payment", 1, 53, 102, "test")
    ]
    check_report = runner.auditor.audit_document(sample_clause, doc_id="check_doc")
    print(f"  [PASS] Single document audited successfully: {check_report.total_clauses} clauses, {check_report.total_flags} flags.")

    # 1. Work Package A: Kendall's Tau on Shuffled LEDGAR
    print("\n[1/6] Work Package A: Computing Kendall's Tau on shuffled LEDGAR test set...")
    tau_results = runner.evaluate_kendall_tau_ledgar(n_clauses=40, n_permutations=5, seed=42)
    print(f"  Kendall's Tau: {tau_results['kendall_tau']} (p-val: {tau_results['p_value']})")
    print(f"  95% Bootstrap CI: [{tau_results['ci_95'][0]}, {tau_results['ci_95'][1]}]")
    print(f"  Statistically Significant: {tau_results['statistically_significant']}")

    # 2. Work Package B: False Positive Rate on ~50 Clean SEC EDGAR Contracts
    print("\n[2/6] Work Package B: Evaluating False Positive Rate on 50 SEC EDGAR clean contracts...")
    fpr_results = runner.evaluate_fpr_sec_edgar(max_contracts=50, clauses_per_contract=15)
    print(f"  Contracts Audited: {fpr_results['contracts_audited']} | Clauses: {fpr_results['total_clauses_audited']}")
    print(f"  FPR (High Severity): {fpr_results['fpr_high_severity']:.4f} (95% CI: {fpr_results['fpr_high_severity_ci_95']})")
    print(f"  FPR (Med + High):    {fpr_results['fpr_med_plus_high']:.4f} (95% CI: {fpr_results['fpr_med_plus_high_ci_95']})")
    print(f"  Mean Anomaly Score:  {fpr_results['mean_anomaly_score']:.4f} (95% CI: {fpr_results['mean_anomaly_score_ci_95']})")

    # 3. Work Package C: Case Studies Evaluation
    print("\n[3/6] Work Package C: Evaluating Verified Legal Dispute Case Studies...")
    case_results = runner.evaluate_case_studies()
    print(f"  Verified Cases: {case_results['verified_cases_count']} Fully Verified, {case_results['partially_verified_count']} Partially Verified.")
    for cs in case_results["case_details"]:
        print(f"  - {cs['case_name']}: {cs['verification_status']}")
        print(f"    Defect: {cs['structural_defect']} | Flags Raised: {cs.get('total_flags', 0)}")

    # 4. Work Package D: CUAD Out-of-Distribution Generalization
    print("\n[4/6] Work Package D: Evaluating CUAD Out-of-Distribution Generalization...")
    cuad_results = runner.evaluate_cuad_generalization(max_clauses=50)
    print(f"  Clauses Evaluated: {cuad_results['total_clauses_evaluated']}")
    print(f"  Mean Combined Anomaly: {cuad_results['mean_combined_anomaly']:.4f} (95% CI: {cuad_results['mean_combined_ci_95']})")
    print(f"  Mean Channel A (OOD):  {cuad_results['mean_channel_a_ood']:.4f} (95% CI: {cuad_results['mean_channel_a_ci_95']})")
    print(f"  Mean Channel B (Coh):  {cuad_results['mean_channel_b_coherence']:.4f} (95% CI: {cuad_results['mean_channel_b_ci_95']})")

    # 5. Work Package E: Baseline Comparison
    print("\n[5/6] Work Package E: Running Side-by-Side Baseline Comparison...")
    baseline_results = runner.evaluate_baselines_comparison()
    for model_name, m_metrics in baseline_results["comparison_metrics"].items():
        print(f"  [{model_name}]")
        print(f"    Accuracy: {m_metrics['accuracy']} | F1: {m_metrics['f1_score']} | Tau: {m_metrics['kendall_tau']}")

    # 6. Work Package F: Claim-Evidence Matrix Generation
    print("\n[6/6] Work Package F: Generating Claim-Evidence Matrix...")
    claim_matrix = runner.generate_claim_evidence_matrix(
        tau_res=tau_results,
        fpr_res=fpr_results,
        cuad_res=cuad_results,
        case_res=case_results,
        baseline_res=baseline_results
    )
    print(f"  Generated {len(claim_matrix)} claim-evidence rows with verified empirical backing.")

    # Persist results to fixtures
    fixtures_dir = Path("fixtures")
    fixtures_dir.mkdir(parents=True, exist_ok=True)

    benchmark_bundle = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "execution_time_seconds": round(time.time() - start_time, 2),
        "kendall_tau_ledgar": tau_results,
        "fpr_sec_edgar": fpr_results,
        "case_studies": case_results,
        "cuad_generalization": cuad_results,
        "baselines_comparison": baseline_results
    }

    with open(fixtures_dir / "evaluation_benchmark_results.json", "w", encoding="utf-8") as f:
        json.dump(benchmark_bundle, f, indent=2)

    with open(fixtures_dir / "claim_evidence_matrix.json", "w", encoding="utf-8") as f:
        json.dump(claim_matrix, f, indent=2)

    print(f"\n[DONE] Saved fixtures to {fixtures_dir / 'evaluation_benchmark_results.json'} and {fixtures_dir / 'claim_evidence_matrix.json'}")
    return benchmark_bundle, claim_matrix


if __name__ == "__main__":
    main()
