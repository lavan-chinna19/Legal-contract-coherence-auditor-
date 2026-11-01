# Phase 4D-C-A: Execution Log & Audit Trajectory

**Program**: LexAudit Benchmark Integrity, Scientific Evidence & Reproducibility Correction  
**Phase**: 4D-C-A  
**Auditor**: Independent ML Research Auditor, Senior Python Testing Engineer  
**Execution Date**: October 23, 2026  
**Execution Environment**: Windows 11 Enterprise, Python 3.11.9, pytest-9.1.1, PyTorch 2.13.0+cpu  

---

## 1. Sequential Audit Trajectory

### Step 1: Git Working Tree Baseline Inspection & Preservation
- Inspected active repository working tree: Git HEAD at `23dbcf536f2fb3dce1611e2d2ae71e9ca8c86f55` (`main`).
- Verified uncommitted working changes in `README.md`, `fixtures/load_test_results.json`, `frontend/`, `src/api/`, `tests/test_api_integration.py`.
- Formally recorded working tree baseline in `design/ui_redesign/phase_04dca/git_and_artifact_preservation.md`.
- Enforced strict non-destructive constraints: zero `git add`, zero `git commit`, zero `git checkout`, zero `git clean`.

### Step 2: Checkpoint Hash Reconciliation (Audit A)
- Calculated physical SHA-256 digests of active files on disk:
  - `models/coherence_classifier.pt`: `9c0a5a096cdf03a63615134500a64f4bc559314be64366812d6a6f1762d4017f` (3,218,819 bytes)
  - `fixtures/ledgar_centroids.npz`: `2ea33ac1cb8430e720be85cd501f11539c143901b2173b63b942b34b9d31ce07` (203,763 bytes)
- Traced Git commit history:
  - `git show 490a429:models/coherence_classifier.pt` SHA-256 = `9c0a5a09...` (Identical)
  - `git show b0ee639:fixtures/ledgar_centroids.npz` SHA-256 = `2ea33ac1...` (Identical)
- Traced historical phase documentation:
  - `phase_04b/checkpoint_compatibility_audit.md` verified `9c0a5a09...` and `2ea33ac1...`.
  - `phase_04db/source_and_feasibility_audit.md` verified `9c0a5a09...`.
  - `phase_04dc_backup_snapshot` verified `9c0a5a09...` and `2ea33ac1...`.
- Identified that `7e3bc48b...` and `f748282b...` in Phase 4D-B preservation markdown were typographical copy-paste errors.
- Exported `checkpoint_hash_reconciliation.csv` and authored `checkpoint_integrity_investigation.md`.

### Step 3: Held-Out Test Chronology Forensic Reconstruction (Audit B)
- Inspected file timestamps (`CTime` and `MTime`) across `src/research/independent_benchmark/` and `research/.../`.
- Discovered that `reporting.py` runs `BenchmarkDatasetBuilder`, `BenchmarkEvaluator`, and JSON manifest exports in a single script.
- Verified that `protocol_hash_manifest.json` and `preregistered_evaluation_protocol.md` were created at 18:58:16 UTC, after `case_level_predictions.csv` was written at 18:58:14 UTC.
- Verified that model thresholds were frozen at default constants without post-test tuning.
- Formally issued `EXECUTION_REPEATED_WITH_FROZEN_CONFIGURATION` and authored `preregistration_chronology_audit.md` and `sealed_test_status_decision.md`.

### Step 4: Parent-Contract Denominator Reconciliation (Audit C)
- Extracted and audited all 32 parent contract records from `parent_contract_manifest.csv` and 15 family records from `source_family_split_manifest.csv`.
- Discovered narrative typo in Phase 4D-C summary report (which stated 19 dev + 7 val + 5 test = 31).
- Mathematically verified the true authoritative counts: **18 Development (9 families) + 9 Validation (3 families) + 5 Sealed Test (3 families) = 32 Parents across 15 Families**.
- Validated that all 5 split invariants passed with zero leakage.
- Exported `parent_split_count_reconciliation.csv` and authored `dataset_denominator_audit.md`.

### Step 5: SEC EDGAR Copyright & Usage Rights Audit (Audit D)
- Conducted statutory review of 17 U.S.C. §105 and §101 regarding works of the U.S. Government.
- Determined that Exhibit 10 material contracts are privately authored commercial agreements; filing with the SEC does not inject private works into the public domain.
- Corrected status from `PUBLIC_DOMAIN_US_FEDERAL_FILING` to `PUBLICLY_ACCESSIBLE_RIGHTS_UNDETERMINED`.
- Mandated non-redistribution of complete contract text. Exported `source_rights_status.csv` and authored `sec_edgar_licensing_correction.md`.

### Step 6: Ground-Truth Oracle Evidence Review (Audit E)
- Inspected all 28 positive benchmark cases across development (22), validation (4), and test (2).
- Discovered that in all 28 cases, target backward discourse markers (e.g. *"Notwithstanding the foregoing definition"*) were preceded by their antecedent within the same segmented clause.
- Determined that Category P1 clause inversions did not break discourse dependencies, classifying all 14 P1 cases as `INVALID_TRANSFORMATION`.
- Discovered that the held-out test partition contained only $N=2$ positive cases, both from a single contract (`SEC_CIK932021_EX_10_26`).
- Audited all 16 held-out negative controls and 5 excluded cases; authenticated N1 controls against raw filings.
- Exported `positive_case_evidence_review.csv`, `negative_case_evidence_review.csv`, and authored `ground_truth_validity_report.md`.

### Step 7: Metric Consistency & Post-Hoc Sensitivity Analysis (Audit F)
- Reconstructed confusion matrices directly from 108 case-level predictions without rerunning models.
- Verified exact reproduction of reported historical metrics and Wilson 95% confidence intervals.
- Modeled Sensitivity View 1 (excluding invalid P1): precision drops to $\le 9.1\%$, F1 drops to $0.1111 - 0.1667$.
- Modeled Sensitivity View 2 (excluding both P1 and P2): positive cases drop to 0; Recall, Precision, and F1 become `NOT_ESTIMABLE`.
- Exported `corrected_metric_consistency.json`, `claims_and_evidence_matrix.csv`, and authored `posthoc_sensitivity_analysis.md`.

### Step 8: Targeted Final Consistency Correction (Audit G)
- Reconciled Candidate C2 metrics between raw stored thresholded rows ($TP=2, FP=16, FN=0, TN=0$) and historical reported underfitting ($TP=0, FP=0, FN=2, TN=16$).
- Applied explicit metric convention `NOT_ESTIMABLE` for undefined precision and F1 ($0/0$).
- Dissected `edgar_manifest.json` confirming 10 top-level dictionary keys (not filings) containing 50 exhibit entries across 19 unique accession numbers and 19 unique CIKs, with 50 downloaded `.txt` files and 32 eligible parent contracts.
- Reconciled backend regression baselines: Phase 4D-B was 183 passed (185 collected); Phase 4D-C full backend suite was 193 passed (195 collected) as proved in raw log `backend_test_evidence.log`.
- Expanded `tests/test_phase_04dca_audit.py` to 16 invariant and regression assertions.
- Executed full focused suite: `pytest tests/test_independent_benchmark.py tests/test_phase_04dca_audit.py -v`.
- Achieved **26 passed in 10.30s (100% pass rate)**.
- Captured execution logs in `test_results.log` and structured results in `test_results.json`.

### Step 9: Deliverable Assembly & Governance Handoff
- Assembled all 24 required deliverables in `design/ui_redesign/phase_04dca/`.
- Authored `defect_register.csv`, `evidence_index.md`, `handoff_phase_04dca.json`, and `handoff_phase_04dca_summary.md`.
- Enforced strict stop: zero changes outside audit scope, no progression to Phase 4D-D or Phase 4E.
