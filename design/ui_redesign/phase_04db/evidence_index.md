# EVIDENCE INDEX
**LEXAUDIT RESEARCH EXTENSION — PHASE 4D-B**
**Repository State:** `23dbcf536f2fb3dce1611e2d2ae71e9ca8c86f55`

---

## 1. Research Artifacts Index (`research/structural_coherence_phase_04db/`)

| Artifact Name | Format | Description |
| :--- | :---: | :--- |
| `research_questions.md` | Markdown | Formally defines RQ1 through RQ5. |
| `preregistered_experimental_protocol.md` | Markdown | Pre-registered task definitions, metrics, and threshold policies. |
| `ground_truth_taxonomy.md` | Markdown | Disjoint label families and independent oracle specifications. |
| `dataset_provenance.csv` | CSV | Source lineage, licenses, and structural ground-truth flags. |
| `label_validity_audit.csv` | CSV | Oracle audit establishing eligibility for each benchmark case. |
| `dataset_split_manifest.csv` | CSV | Strict partition assignments across Diagnostic, Validation, and Test. |
| `leakage_audit.md` | Markdown | Verification of zero cross-split or oracle leakage. |
| `baseline_results.csv` | CSV | Reconstructed performance metrics for Baselines B0, B1, and B2. |
| `candidate_selection_matrix.csv` | CSV | Quantitative comparison matrix across all candidate models. |
| `model_config.json` | JSON | Architecture parameters, dimensions, and threshold values. |
| `training_manifest.json` | JSON | Candidate C2 BiLSTM CPU training metadata and hardware profile. |
| `training_history.csv` | CSV | Epoch-by-epoch loss history for Candidate C2. |
| `validation_results.csv` | CSV | Development and validation split metrics. |
| `heldout_test_results.csv` | CSV | Primary scientific evaluation results on untouched held-out test data. |
| `case_level_predictions.csv` | CSV | Exhaustive 90-row case-level prediction database. |
| `confusion_matrices.csv` | CSV | Strict TP, FP, FN, TN counts for every model and partition. |
| `ranking_results.csv` | CSV | Task 2 (Clause Recovery) vs Task 1 (Structural Detection) separation. |
| `ablation_results.csv` | CSV | Feature component ablation results isolating contrast and discordance. |
| `calibration_results.csv` | CSV | Confidence score bands and abstention policies. |
| `robustness_results.csv` | CSV | Evaluation under cross-template transfer and hard negatives. |
| `latency_results.csv` | CSV | CPU inference latency, p95 latency, and memory profiling. |
| `failure_analysis.csv` | CSV | Root-cause diagnoses for all false positives and false negatives. |
| `statistical_uncertainty.md` | Markdown | Two-sided Wilson 95% intervals and paired effect sizes. |
| `reproduction_instructions.md` | Markdown | Step-by-step CLI reproduction instructions. |

---

## 2. Design and Handoff Artifacts Index (`design/ui_redesign/phase_04db/`)

| Artifact Name | Description |
| :--- | :--- |
| `source_and_feasibility_audit.md` | Hardware and source code audit. |
| `channel_a_zero_score_investigation.md` | Deep investigation of Channel A centroid clipping behavior. |
| `channel_b_failure_analysis.md` | Deep investigation of Channel B logit saturation. |
| `git_baseline_and_preservation.md` | Git baseline and immutable snapshot record. |
| `problem_and_ground_truth_specification.md` | Disambiguation of Tasks 1-5 and independent oracle definition. |
| `dataset_validity_and_leakage_report.md` | Lineage audit of LEDGAR, CUAD, and synthetic fixtures. |
| `baseline_reproduction.md` | Verification of frozen baseline zero-detection findings. |
| `candidate_architecture_review.md` | Architectural review of Candidates C1, C2, and C3. |
| `candidate_selection_rationale.md` | Quantitative justification for Candidate C3 selection. |
| `training_or_nontraining_decision.md` | Decision memo on non-training approach and C2 negative result. |
| `model_implementation_details.md` | Technical implementation specifications for experimental package. |
| `experiment_protocol.md` | Pre-registered experiment protocol adherence audit. |
| `evaluation_results.md` | Comprehensive evaluation results across all partitions. |
| `baseline_vs_candidate_comparison.md` | Paired baseline vs candidate comparison on held-out test data. |
| `ablation_study.md` | Component ablation study. |
| `robustness_and_hard_negative_review.md` | Hard-negative evaluation under commutative covenant reordering. |
| `false_positive_analysis.md` | In-depth false-positive root-cause analysis. |
| `false_negative_analysis.md` | In-depth false-negative root-cause analysis. |
| `statistical_significance_review.md` | Statistical uncertainty review and sample size bounds. |
| `resource_and_latency_review.md` | Computational resource and CPU latency profiling. |
| `privacy_and_security_review.md` | Data privacy, authentication, and security audit. |
| `backend_regression_results.json` | 183 passed, 2 skipped, 0 failed pytest verification. |
| `metric_consistency_results.json` | Mathematical consistency audit. |
| `defect_register.csv` | Discovered defect register and remediation roadmap. |
| `execution_log.md` | Step-by-step chronological build log. |
| `implementation_summary.md` | Executive engineering summary. |
| `handoff_phase_04db.json` | Machine-readable handoff bundle. |
| `handoff_phase_04db_summary.md` | Executive handoff summary. |
