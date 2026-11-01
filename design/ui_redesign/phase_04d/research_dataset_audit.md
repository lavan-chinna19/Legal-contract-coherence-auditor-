# Phase 4D Research Dataset Audit & Split Lineage

## 1. Provenance and Isolation
The Phase 4D benchmark uses strictly nonconfidential synthetic contract templates:
1. `SYNTH_DOC_01_MSA`: 11 sequential clauses modeled after an enterprise Master Services Agreement. Contains clean sequential numbering (Sections 1–10), explicit Exhibit A statement of work, and harmonious temporal chronology (Effective: Jan 1, 2025; Termination: Dec 31, 2025).
2. `SYNTH_DOC_02_SLA`: 8 sequential clauses modeled after a Software License Agreement. Contains standard cross-references (Sections 1–8) and annual subscription term logic.

## 2. Held-Out Data Protection & Leakage Prevention
- **Prior Held-Out Benchmark Partition**: The nine contracts from the Phase 4C-A counterfactual benchmark were **NOT** reused as fresh unseen evaluation targets to prevent data snooping and circular metric calibration.
- **Reporting Designation**: In accordance with Contract §12, because these interactive and unit test fixtures are synthetically authored, all empirical findings are explicitly designated as `PRELIMINARY_SYNTHETIC_EVALUATION`. No false claims of universal out-of-distribution generalization are made.
- **Zero Confidentiality Exposure**: Zero client contracts, proprietary NDAs, or confidential SEC filings are stored in public fixtures or research manifests.
