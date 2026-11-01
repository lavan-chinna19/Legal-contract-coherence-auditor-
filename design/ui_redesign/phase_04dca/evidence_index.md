# Phase 4D-C-A: Authoritative Evidence Index

**Program**: LexAudit Benchmark Integrity, Scientific Evidence & Reproducibility Correction  
**Phase**: 4D-C-A  
**Auditor**: Independent ML Research Auditor, Senior Documentation Engineer  
**Date**: October 23, 2026  
**Artifact Directory**: `design/ui_redesign/phase_04dca/`  

---

## 1. Directory Manifest of Phase 4D-C-A Deliverables

All 24 authoritative deliverables have been generated in `design/ui_redesign/phase_04dca/`:

| File Name | Format | Category | Core Purpose & Scope |
| :--- | :---: | :---: | :--- |
| [`implementation_summary.md`](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/design/ui_redesign/phase_04dca/implementation_summary.md) | Markdown | Summary | Executive summary of Phase 4D-C-A audit resolutions and findings. |
| [`git_and_artifact_preservation.md`](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/design/ui_redesign/phase_04dca/git_and_artifact_preservation.md) | Markdown | Integrity | Git working tree baseline, commit HEAD, diff record, and regression count reconciliation. |
| [`checkpoint_hash_reconciliation.csv`](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/design/ui_redesign/phase_04dca/checkpoint_hash_reconciliation.csv) | CSV | Checkpoint | Cross-phase SHA-256 hash comparison across Git commits, audits, and runtime manifests. |
| [`checkpoint_integrity_investigation.md`](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/design/ui_redesign/phase_04dca/checkpoint_integrity_investigation.md) | Markdown | Checkpoint | Root-cause analysis of documentation typos vs verified physical byte identity. |
| [`benchmark_execution_timeline.csv`](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/design/ui_redesign/phase_04dca/benchmark_execution_timeline.csv) | CSV | Chronology | Microsecond-accurate UTC event timeline of benchmark generation and reporting. |
| [`preregistration_chronology_audit.md`](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/design/ui_redesign/phase_04dca/preregistration_chronology_audit.md) | Markdown | Chronology | Forensic timing analysis of protocol co-generation vs model prediction passes. |
| [`sealed_test_status_decision.md`](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/design/ui_redesign/phase_04dca/sealed_test_status_decision.md) | Markdown | Governance | Formal governance decision downgrading test set to exploratory pilot. |
| [`parent_split_count_reconciliation.csv`](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/design/ui_redesign/phase_04dca/parent_split_count_reconciliation.csv) | CSV | Dataset | Parent-by-parent split allocation and perturbation breakdown. |
| [`dataset_denominator_audit.md`](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/design/ui_redesign/phase_04dca/dataset_denominator_audit.md) | Markdown | Dataset | Mathematical proof of 18 dev + 9 val + 5 test = 32 parents and SEC manifest inventory. |
| [`sec_edgar_licensing_correction.md`](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/design/ui_redesign/phase_04dca/sec_edgar_licensing_correction.md) | Markdown | Legal Rights | Statutory correction of 17 U.S.C. §105 public domain claims on private contracts. |
| [`source_rights_status.csv`](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/design/ui_redesign/phase_04dca/source_rights_status.csv) | CSV | Legal Rights | SEC filing accession-level legal status and redistribution restrictions (50 entries). |
| [`positive_case_evidence_review.csv`](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/design/ui_redesign/phase_04dca/positive_case_evidence_review.csv) | CSV | Annotation | Exhaustive audit of all 28 positive cases, antecedent locality, and defect validity. |
| [`negative_case_evidence_review.csv`](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/design/ui_redesign/phase_04dca/negative_case_evidence_review.csv) | CSV | Annotation | Audit of 16 held-out negatives, 5 excluded cases, and dev/val samples. |
| [`ground_truth_validity_report.md`](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/design/ui_redesign/phase_04dca/ground_truth_validity_report.md) | Markdown | Annotation | Technical report on intra-clause discourse markers and positive label flaws. |
| [`corrected_metric_consistency.json`](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/design/ui_redesign/phase_04dca/corrected_metric_consistency.json) | JSON | Metrics | Machine-readable metrics for historical baseline, C2 reconciliation, and sensitivity views. |
| [`posthoc_sensitivity_analysis.md`](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/design/ui_redesign/phase_04dca/posthoc_sensitivity_analysis.md) | Markdown | Metrics | Reconciled C2 raw vs underfitting metrics and sensitivity modeling ($N=1$ and $N=0$). |
| [`claims_and_evidence_matrix.csv`](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/design/ui_redesign/phase_04dca/claims_and_evidence_matrix.csv) | CSV | Evidence | Cross-cutting matrix of 8 scientific claims, audit findings, and qualified claims. |
| [`test_results.log`](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/design/ui_redesign/phase_04dca/test_results.log) | Text Log | Testing | Captured stdout/stderr from pytest execution covering 26 test items (100% pass). |
| [`test_results.json`](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/design/ui_redesign/phase_04dca/test_results.json) | JSON | Testing | Machine-readable test execution report and reconciled regression baseline counts. |
| [`defect_register.csv`](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/design/ui_redesign/phase_04dca/defect_register.csv) | CSV | Defects | Log of 8 identified engineering, narrative, legal, and annotation defects. |
| [`execution_log.md`](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/design/ui_redesign/phase_04dca/execution_log.md) | Markdown | Execution | Chronological record of all audit investigations and technical commands run. |
| [`evidence_index.md`](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/design/ui_redesign/phase_04dca/evidence_index.md) | Markdown | Index | This navigational directory and metadata index. |
| [`handoff_phase_04dca.json`](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/design/ui_redesign/phase_04dca/handoff_phase_04dca.json) | JSON | Handoff | Machine-readable program handoff manifest and gate status. |
| [`handoff_phase_04dca_summary.md`](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/design/ui_redesign/phase_04dca/handoff_phase_04dca_summary.md) | Markdown | Handoff | Executive handoff summary and downstream research guidance. |

---

## 2. Cross-Referenced External Assets

| System Asset | Location | Integrity Status |
| :--- | :--- | :---: |
| Checkpoint: Coherence Classifier | `models/coherence_classifier.pt` | Verified SHA-256 `9c0a5a096c...` |
| Fixture: LEDGAR Centroids | `fixtures/ledgar_centroids.npz` | Verified SHA-256 `2ea33ac1cb...` |
| SEC EDGAR Manifest | `data/raw/sec_edgar/edgar_manifest.json` | 50 exhibit entries (19 accessions, 19 CIKs, 10 metadata keys) |
| Historical Benchmark Predictions | `research/independent_contract_benchmark_phase_04dc/case_level_predictions.csv` | 108 prediction rows verified |
| Audit Test Suite | `tests/test_phase_04dca_audit.py` | 16 focused audit tests passing |
| Independent Benchmark Test Suite | `tests/test_independent_benchmark.py` | 10 research unit tests passing |
