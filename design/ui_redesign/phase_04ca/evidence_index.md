# LexAudit Phase 4C-A — Evidence Index

This index inventories all empirical data artifacts, benchmarks, security test reports, and browser screenshots generated during Phase 4C-A.

---

## 1. Browser Acceptance Screenshots
Stored in `design/ui_redesign/phase_04ca/evidence/`:

| File Name | Description | Verified Viewport / State | Size |
| :--- | :--- | :---: | :---: |
| `01_contract_review_initial.png` | Contract ingestion and automated baseline analysis | 1440x900 (Desktop) | 138 KB |
| `02_repositioning_workspace_light.png` | Counterfactual repair modal in Light Theme | 1440x900 (Desktop) | 150 KB |
| `03_candidate_slot_selected.png` | Interactive candidate slot selection & context preview | 1440x900 (Desktop) | 150 KB |
| `04_repositioning_workspace_dark.png` | Counterfactual repair workspace in Dark Theme | 1440x900 (Desktop) | 151 KB |
| `05_xai_clause_sync.png` | Cross-workspace navigation preserving active clause in XAI | 1440x900 (Desktop) | 120 KB |
| `06_feedback_clause_sync.png` | Cross-workspace navigation preserving active clause in Feedback | 1440x900 (Desktop) | 87 KB |
| `07_responsive_1024x768.png` | Tablet viewport verification (zero horizontal overflow) | 1024x768 (Tablet) | 96 KB |
| `08_responsive_390x844_mobile.png` | Mobile viewport verification (clean vertical stacking) | 390x844 (Mobile) | 34 KB |

---

## 2. Research & Evaluation Deliverables
Stored in `design/ui_redesign/phase_04ca/`:

| File Name | Category | Primary Focus |
| :--- | :--- | :--- |
| `implementation_summary.md` | Executive Report | Comprehensive summary of Phase 4C-A findings |
| `git_baseline_and_preservation.md` | Audit Record | Git SHA baseline, uncommitted inventory, backup verification |
| `claim_reproduction_matrix.csv` | Research Verification | 8 claims compared against reproductions |
| `experimental_opt_in_audit.md` | API Security | Audit of `experimental` flag enforcement and HTTP statuses |
| `api_security_test_matrix.csv` | API Security | 18 automated security test cases |
| `resource_abuse_review.md` | Systems Engineering | Memory, CPU, and bounded-load assessment |
| `threshold_selection_provenance.md` | Scientific Validation | Provenance of 0.005 heuristic threshold |
| `threshold_sensitivity_results.csv` | Sensitivity Study | Sweep over $\delta \in [0.001..0.02]$ |
| `reference_vs_optimized_parity.csv` | Numerical Verification | 18 deterministic edge cases + scale parity |
| `randomized_parity_test_summary.json` | Numerical Verification | Bitwise parity verification ($Max \|dJ\| = 0.0$) |
| `dataset_lineage_audit.md` | Provenance Audit | Audit of 12 training vs 38 candidate contracts |
| `training_test_overlap_matrix.csv` | Contamination Audit | Pairwise n-gram overlap between train and test |
| `near_duplicate_risk_review.md` | Contamination Audit | Boilerplate overlap risk assessment |
| `benchmark_case_level_results.csv` | Benchmark Integrity | Individual rankings across cases C-01 to C-09 |
| `benchmark_metric_recalculation.json` | Statistical Rigor | Recalculated Top-1, Top-3, MRR with bootstrap CIs |
| `baseline_comparability_review.md` | Baseline Evaluation | Evaluation of Cosine, Random, and Identity baselines |
| `negative_control_decomposition.csv` | Safety Decomposition | Breakdown of 9 unperturbed negative controls |
| `runtime_reproduction.csv` | Systems Profiling | Speedup measurements across $N \in [3..20]$ |
| `ui_truthfulness_validation.md` | QA Audit | UI truthfulness, stale state, and zero-mutation |
| `benchmark_consistency_correction.md` | Benchmark Rigor | Discrepancy investigation, rank derivation proof & threshold analysis |
| `frontend_test_results.json` | Frontend QA | Static analysis, TypeScript, alignment, build |
| `backend_regression_results.json` | Backend QA | 141 passed, 2 skipped pytest regression results |
| `browser_acceptance_report.md` | E2E QA | 15/15 browser acceptance assertion report |
| `privacy_security_validation.md` | Security Review | Tenant isolation, encryption, and client privacy |
| `defect_register.csv` | Quality Management | Register of DEF-4CA-01 through DEF-4CA-06 |
| `execution_log.md` | Audit Trail | Step-by-step chronological execution record |
| `handoff_phase_04ca.json` | Handoff Manifest | Machine-readable handoff summary |
| `handoff_phase_04ca_summary.md` | Executive Summary | Human-readable signoff and Phase 4D readiness |
