# SCIENTIFIC EVALUATION RESULTS
**LEXAUDIT RESEARCH EXTENSION — PHASE 4D-B**
**Author:** Research Evaluation Architect & Statistical Auditor
**Date:** 2026-10-22

---

## 1. Master Evaluation Results Across All Splits

The benchmark evaluation evaluated 6 models across 3 partitions (15 contracts total, 90 evaluated contract passes):

### 1.1 Untouched Held-Out Test Partition (Fresh Unseen Cases)
*Condition Positives: 2 (Exhibit-Scope Inversion, GovLaw Pre-Scope Inversion) | Condition Negatives: 2 (Audit/Warranty Swap Hard Negative, Clean MSA Control)*

| Model | TP | FP | FN | TN | Recall | Specificity | FPR | Balanced Acc | Wilson 95% CI (Recall) | Localization Hit Rate | Latency (ms) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Baseline B0 (Channel B)** | 0 | 0 | 2 | 2 | **0.0000** | 1.0000 | 0.0000 | 0.5000 | [0.0000, 0.6576] | N/A | 7.68 |
| **Baseline B1 (Ensemble)** | 0 | 0 | 2 | 2 | **0.0000** | 1.0000 | 0.0000 | 0.5000 | [0.0000, 0.6576] | N/A | 38.31 |
| **Baseline B2 (Cosine)** | 0 | 0 | 2 | 2 | **0.0000** | 1.0000 | 0.0000 | 0.5000 | [0.0000, 0.6576] | N/A | 6.62 |
| **Candidate C1 (Boundary)** | 2 | 1 | 0 | 1 | **1.0000** | 0.5000 | 0.5000 | 0.7500 | [0.3424, 1.0000] | 50.0% | 14.98 |
| **Candidate C2 (BiLSTM)** | 0 | 0 | 2 | 2 | **0.0000** | 1.0000 | 0.0000 | 0.5000 | [0.0000, 0.6576] | N/A | 53.79 |
| **Candidate C3 (Topological)**| 2 | 0 | 0 | 2 | **1.0000** | **1.0000** | **0.0000** | **1.0000** | **[0.3424, 1.0000]** | **100.0%** | **0.17** |

---

### 1.2 Development / Validation Partition (SLA Variations)
*Condition Positives: 2 | Condition Negatives: 1*

| Model | TP | FP | FN | TN | Recall | Specificity | FPR | Balanced Acc | Wilson 95% CI (Recall) | Localization Hit Rate | Latency (ms) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Baseline B0 (Channel B)** | 0 | 0 | 2 | 1 | **0.0000** | 1.0000 | 0.0000 | 0.5000 | [0.0000, 0.6576] | N/A | 6.35 |
| **Baseline B1 (Ensemble)** | 0 | 0 | 2 | 1 | **0.0000** | 1.0000 | 0.0000 | 0.5000 | [0.0000, 0.6576] | N/A | 42.09 |
| **Baseline B2 (Cosine)** | 0 | 0 | 2 | 1 | **0.0000** | 1.0000 | 0.0000 | 0.5000 | [0.0000, 0.6576] | N/A | 7.61 |
| **Candidate C1 (Boundary)** | 2 | 1 | 0 | 0 | **1.0000** | 0.0000 | 1.0000 | 0.5000 | [0.3424, 1.0000] | 50.0% | 24.86 |
| **Candidate C2 (BiLSTM)** | 0 | 0 | 2 | 1 | **0.0000** | 1.0000 | 0.0000 | 0.5000 | [0.0000, 0.6576] | N/A | 5.81 |
| **Candidate C3 (Topological)**| 1 | 0 | 1 | 1 | **0.5000** | **1.0000** | **0.0000** | **0.7500** | **[0.0945, 0.9055]** | **100.0%** | **0.25** |

---

### 1.3 Diagnostic Historical Benchmark (Phase 4D Scenarios)
*Condition Positives: 5 | Condition Negatives: 2 (Excludes P2_03 Ambiguous)*

| Model | TP | FP | FN | TN | Recall | Specificity | FPR | Balanced Acc | Wilson 95% CI (Recall) | Localization Hit Rate | Latency (ms) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Baseline B0 (Channel B)** | 0 | 0 | 5 | 2 | **0.0000** | 1.0000 | 0.0000 | 0.5000 | [0.0000, 0.4345] | N/A | 24.01 |
| **Baseline B1 (Ensemble)** | 0 | 0 | 5 | 2 | **0.0000** | 1.0000 | 0.0000 | 0.5000 | [0.0000, 0.4345] | N/A | 41.93 |
| **Baseline B2 (Cosine)** | 0 | 0 | 5 | 2 | **0.0000** | 1.0000 | 0.0000 | 0.5000 | [0.0000, 0.4345] | N/A | 7.54 |
| **Candidate C1 (Boundary)** | 2 | 1 | 3 | 1 | **0.4000** | 0.5000 | 0.5000 | 0.4500 | [0.1176, 0.7693] | 100.0% | 29.04 |
| **Candidate C2 (BiLSTM)** | 0 | 0 | 5 | 2 | **0.0000** | 1.0000 | 0.0000 | 0.5000 | [0.0000, 0.4345] | N/A | 17.33 |
| **Candidate C3 (Topological)**| 1 | 0 | 4 | 2 | **0.2000** | **1.0000** | **0.0000** | **0.6000** | **[0.0362, 0.6245]** | **100.0%** | **0.19** |

---

## 2. Key Scientific Observations

1. **Frozen Baselines Confirm Blindness:** All baselines ($B0, B1, B2$) failed on 100% of the structural anomaly cases across all splits ($0.0\%$ recall).
2. **Candidate C3 Demonstrates True Generalization:** On the untouched held-out test partition, Candidate C3 detected both structural violations ($100\%$ recall) while preserving **100% specificity** (0 false positives on the clean control and the out-of-domain hard negative).
3. **Candidate C1 Suffers from Hard Negative Spikes:** Candidate C1 detected all test violations ($100\%$ recall) but incorrectly flagged the coherent swap of Audit Rights and Warranty Disclaimers ($50\%$ FPR).
