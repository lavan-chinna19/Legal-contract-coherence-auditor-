# Phase 4D-D Split Integrity and Contamination Report
## Benchmark Partitioning, Family Isolation, and Leakage Prevention

### 1. Fundamental Split Policy and Remediation of False Claims

In historical Phase 4D-C benchmarking, certain contract families were described as an "untouched sealed test set". However, the research audit in Phase 4D-C-A established that:
1. Those exact contract texts and accessions had already been inspected, segmented, and evaluated during earlier development cycles.
2. Describing them as a fresh, unexposed test set violated empirical machine learning integrity standards.

**Phase 4D-D Policy Mandate**:
- **100% Development Allocation**: All 72 cases generated in Phase 4D-D are derived from the 32 development parent contracts.
- **Explicit Labeling**: Every record in [dataset_manifest.csv](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/research/dependency_ground_truth_phase_04dd/dataset_manifest.csv) and [source_family_manifest.csv](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/research/dependency_ground_truth_phase_04dd/source_family_manifest.csv) has `split_assignment = "development"` and `split_eligibility = "DEVELOPMENT_ONLY"`.
- **Zero False Holdout Claims**: No portion of this pilot benchmark is represented as an untouched sealed test set. Any future independent test set must be sourced from newly acquired, unexposed parent contract families.

---

### 2. Source Family Distribution and Isolation

The Phase 4D-D benchmark spans **10 distinct corporate entity families** derived from SEC Central Index Keys (CIKs). Each family corresponds to a specific corporate registrant and drafting style:

| Document Family ID | SEC CIK | Registrant Name | Parent Documents | Total Cases | Positive Cases | Negative Cases | Ambiguous Cases |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `FAM_CIK_810136` | 0000810136 | Pioneer Natural Resources / Successor Entities | 4 | 16 | 6 | 7 | 3 |
| `FAM_CIK_1090872` | 0001090872 | Agilent Technologies Inc. | 3 | 16 | 6 | 7 | 3 |
| `FAM_CIK_932021` | 0000932021 | Westlake Chemical Corp. | 3 | 13 | 5 | 6 | 2 |
| `FAM_CIK_808326` | 0000808326 | Emergent BioSolutions Inc. | 2 | 9 | 4 | 4 | 1 |
| `FAM_CIK_1967306` | 0001967306 | CleanSpark Inc. Related Entities | 2 | 8 | 4 | 3 | 1 |
| `FAM_CIK_1645590` | 0001645590 | Hewlett Packard Enterprise Co. | 1 | 3 | 2 | 0 | 1 |
| `FAM_CIK_1101396` | 0001101396 | Virgin Media / NTL Inc. | 1 | 3 | 1 | 1 | 1 |
| `FAM_CIK_1397016` | 0001397016 | Bright Horizons Family Solutions | 1 | 2 | 1 | 1 | 0 |
| `FAM_CIK_1643988` | 0001643988 | Biohaven Pharmaceutical Holding | 1 | 1 | 1 | 0 | 0 |
| `FAM_CIK_1802974` | 0001802974 | Snowflake Inc. Related Entities | 1 | 1 | 0 | 1 | 0 |
| **Totals** | — | **10 Corporate Registrants** | **19 Unique Parents** | **72 Cases** | **30** | **30** | **12** |

---

### 3. Template-Level and Intra-Family Duplicate Audit

When constructing synthetic perturbations from legal agreements, template duplication presents a serious threat of artificial data inflation:
1. **Parent Document Deduplication**:
   - The 32 candidate parent agreements in `data/raw/sec_edgar/` were hashed using SHA-256.
   - Text hash comparison confirmed that all 19 utilized parent agreements possess unique cryptographic hashes, confirming zero duplicate files.
2. **Template Overlap Verification**:
   - While certain contracts within the same family share standard boilerplate clauses (e.g., standard Delaware governing law provisions), each agreement contains unique commercial terms, section numbering, and substantive covenants.
   - Positives and negatives are distributed proportionally across families, preventing any single corporate template from dominating the benchmark.
3. **Cross-Case Perturbation Independence**:
   - Each benchmark case represents an isolated perturbation applied to a fresh copy of the parent contract.
   - In no case are multiple overlapping perturbations combined in a single benchmark record.

---

### 4. Leakage and Oracle Isolation Controls

To guarantee that future detector evaluations are scientifically untainted, the following architectural controls are enforced:
- **No Oracle Labels in Detector Inputs**: Evaluated models receive only `perturbed_clause_sequence` text strings; ground-truth labels (`ground_truth_label`), case types (`case_type`), and transformation descriptions are strictly withheld.
- **Hash-Based Immutability**: Each case includes both `source_text_hash` and `perturbed_text_hash`. Any alteration to clause order or text invalidates the hash signature.
- **Split Immutability Verification**: Automated test suites ([tests/test_phase_04dd_dataset.py](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/tests/test_phase_04dd_dataset.py)) enforce that all records maintain `split_assignment == "development"`.
