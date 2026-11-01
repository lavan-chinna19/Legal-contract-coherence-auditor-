# Phase 4D-A Verification Evidence Index

**Audit Date**: October 22, 2026  
**Auditor**: ML Research Auditor & Independent Verification Lead  
**Scope**: LexAudit Self Red-Team Robustness Laboratory (Phase 4D-A)  

This index catalogs all empirical evidence artifacts generated during the independent scientific validation and browser acceptance suite run.

---

## 1. Visual Evidence Artifacts (Browser Screenshots)

All screenshots were captured live via automated Chrome DevTools Protocol (CDP) during the 32-check acceptance run on port 9222 against Next.js (port 3000) and FastAPI backend (port 8001):

| # | Artifact Filename | Description | Resolution | Check Mapping |
| :-: | :--- | :--- | :--- | :--- |
| 1 | [01_robustness_lab_overview_1440x900.png](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/design/ui_redesign/phase_04da/evidence/01_robustness_lab_overview_1440x900.png) | Desktop Robustness Lab workspace overview showing P1–P10 catalog cards | 1440x900 | CHK-01, CHK-02 |
| 2 | [02_p1_displacement_evaluation.png](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/design/ui_redesign/phase_04da/evidence/02_p1_displacement_evaluation.png) | P1 Displacement outcome showing NOT DETECTED badge & exploratory cutoff note | 1440x900 | CHK-03, CHK-04 |
| 3 | [03_p2_swap_evaluation.png](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/design/ui_redesign/phase_04da/evidence/03_p2_swap_evaluation.png) | P2 Clause Swap outcome showing CLEAN tier and ΔSB below exploratory cutoff | 1440x900 | CHK-05, CHK-06 |
| 4 | [04_p5_broken_reference_detected.png](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/design/ui_redesign/phase_04da/evidence/04_p5_broken_reference_detected.png) | P5 Broken Cross-Reference outcome: DETECTED with VERIFIED MATCH attribution | 1440x900 | CHK-07, CHK-08, CHK-09 |
| 5 | [05_p7_date_inversion_detected.png](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/design/ui_redesign/phase_04da/evidence/05_p7_date_inversion_detected.png) | P7 Date Inversion outcome: DETECTED with 2 chronological rule flags rendered | 1440x900 | CHK-10, CHK-11 |
| 6 | [06_p3_duplicate_descriptive_panel.png](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/design/ui_redesign/phase_04da/evidence/06_p3_duplicate_descriptive_panel.png) | P3 Exact Duplication unsupported-state callout & P4 Near-Duplicate disclaimer | 1440x900 | CHK-12, CHK-13, CHK-14 |
| 7 | [07_p9_clean_negative_control.png](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/design/ui_redesign/phase_04da/evidence/07_p9_clean_negative_control.png) | P9 Clean Negative Control (zero FP, CLEAN tier) & P10 Compound Perturbation | 1440x900 | CHK-15, CHK-16, CHK-17, CHK-18 |
| 8 | [08_cross_workspace_review.png](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/design/ui_redesign/phase_04da/evidence/08_cross_workspace_review.png) | Lateral navigation across Ingest, Analytics, XAI, Transparency, and Feedback | 1440x900 | CHK-21, CHK-22, CHK-23, CHK-24, CHK-25 |
| 9 | [09_light_theme_parity.png](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/design/ui_redesign/phase_04da/evidence/09_light_theme_parity.png) | Light theme styling, typography, and contrast compliance | 1440x900 | CHK-26 |
| 10 | [10_dark_theme_restored.png](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/design/ui_redesign/phase_04da/evidence/10_dark_theme_restored.png) | Dark theme restored with deep obsidian slate palette | 1440x900 | CHK-27 |
| 11 | [11_viewport_laptop_1024x768.png](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/design/ui_redesign/phase_04da/evidence/11_viewport_laptop_1024x768.png) | Responsive 2-column layout at Laptop viewport | 1024x768 | CHK-28 |
| 12 | [12_viewport_tablet_768x1024.png](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/design/ui_redesign/phase_04da/evidence/12_viewport_tablet_768x1024.png) | Responsive stacked layout at Tablet portrait viewport | 768x1024 | CHK-29 |
| 13 | [13_viewport_mobile_390x844.png](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/design/ui_redesign/phase_04da/evidence/13_viewport_mobile_390x844.png) | Mobile viewport layout showing zero horizontal overflow | 390x844 | CHK-30 |

---

## 2. Experimental Data & Recalculation Artifacts

- [browser_acceptance_32_check_matrix.csv](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/design/ui_redesign/phase_04da/browser_acceptance_32_check_matrix.csv): Full 32-check execution matrix with statuses and observed results.
- [browser_acceptance_report.md](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/design/ui_redesign/phase_04da/browser_acceptance_report.md): Detailed narrative browser acceptance report (32/32 PASS, 100.0%).
- [structural_case_level_results.csv](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/design/ui_redesign/phase_04da/structural_case_level_results.csv): 66 clause-level rows across all 6 structural cases (P1: 3, P2: 3) tracking $S_A, S_B, S, \Delta S_B, \Delta S$.
- [structural_detection_recalculation.json](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/design/ui_redesign/phase_04da/structural_detection_recalculation.json): Machine-readable verification data for all structural test cases.
- [channel_b_boundary_analysis.csv](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/design/ui_redesign/phase_04da/channel_b_boundary_analysis.csv): 60 clause-transition edges analyzing transition probability shifts.
- [absolute_vs_delta_score_comparison.csv](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/design/ui_redesign/phase_04da/absolute_vs_delta_score_comparison.csv): Comparison of absolute anomaly detection vs exploratory score shifts.
- [negative_control_reanalysis.csv](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/design/ui_redesign/phase_04da/negative_control_reanalysis.csv): Differential verification of clean negative controls ($\Delta = 0.000000$).
- [defect_register.csv](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/design/ui_redesign/phase_04da/defect_register.csv): Structured defect catalog covering DEF-01 through DEF-06.

---

## 3. Decoupled Confusion Matrices

- [reference_detection_confusion_matrix.csv](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/design/ui_redesign/phase_04da/reference_detection_confusion_matrix.csv): Broken Reference Detection (TP=3, FP=0, FN=0, TN=2, Precision=1.0, Recall=1.0).
- [date_detection_confusion_matrix.csv](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/design/ui_redesign/phase_04da/date_detection_confusion_matrix.csv): Date Inversion Detection (TP=2, FP=0, FN=0, TN=2, Precision=1.0, Recall=1.0).
- [structural_detection_confusion_matrix.csv](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/design/ui_redesign/phase_04da/structural_detection_confusion_matrix.csv): Structural Detection under strict and broad definitions (TP=0, FN=5/6, TN=2, FP=0, Recall=0.0).

---

## 4. Test Suite Execution Logs & Regression Summaries

- [backend_pytest_raw.log](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/design/ui_redesign/phase_04da/backend_pytest_raw.log): Complete raw terminal stdout/stderr of full pytest suite (170 passed, 2 skipped, 0 failed).
- [backend_regression_results.json](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/design/ui_redesign/phase_04da/backend_regression_results.json): Structured test counts, duration, and remediation records.
- [backend_test_evidence_audit.md](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/design/ui_redesign/phase_04da/backend_test_evidence_audit.md): Complete backend audit report explaining test failure, root cause, and remediation diff.
- [frontend_test_results.json](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/design/ui_redesign/phase_04da/frontend_test_results.json): Frontend verification results (`tsc`, `eslint`, `test:alignment`, Next.js `build`).
- [frontend_truthfulness_review.md](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/design/ui_redesign/phase_04da/frontend_truthfulness_review.md): Audit of UI truthfulness, disclaimers, and metric reporting.
- [metrics_consistency_tests.json](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/design/ui_redesign/phase_04da/metrics_consistency_tests.json): 8/8 automated mathematical consistency checks passed.

---

## 5. Architectural & Scientific Audit Reports

- [structural_threshold_semantics_audit.md](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/design/ui_redesign/phase_04da/structural_threshold_semantics_audit.md): Definitive source audit of threshold `0.08` (verdict: `PHASE_4D_CRITERION_INCORRECT`).
- [production_detection_predicate.md](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/design/ui_redesign/phase_04da/production_detection_predicate.md): Reconstruction of `SeverityRanker.assess_clause()` production predicate.
- [scorer_formula_verification.md](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/design/ui_redesign/phase_04da/scorer_formula_verification.md): Exact verification of scoring formulas and channel weights.
- [channel_a_invariance_verification.md](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/design/ui_redesign/phase_04da/channel_a_invariance_verification.md): Mathematical proof and empirical verification of Channel A permutation invariance.
- [structural_failure_root_cause_review.md](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/design/ui_redesign/phase_04da/structural_failure_root_cause_review.md): Classification of structural non-detection root causes.
- [scenario_eligibility_and_denominators.md](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/design/ui_redesign/phase_04da/scenario_eligibility_and_denominators.md): Dynamic denominator justification.
- [statistical_uncertainty_review.md](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/design/ui_redesign/phase_04da/statistical_uncertainty_review.md): Wilson score 95% confidence intervals across all metrics.
- [rule_detection_reproduction.md](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/design/ui_redesign/phase_04da/rule_detection_reproduction.md): Reproduction of rule engine detection behavior.
- [security_privacy_preservation.md](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/design/ui_redesign/phase_04da/security_privacy_preservation.md): Confidentiality, Fernet encryption, and privacy guarantee audit.
- [git_baseline_and_preservation.md](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/design/ui_redesign/phase_04da/git_baseline_and_preservation.md): Git baseline verification and external snapshot record.
