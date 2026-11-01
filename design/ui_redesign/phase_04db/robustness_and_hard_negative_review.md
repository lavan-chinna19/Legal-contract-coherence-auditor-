# ROBUSTNESS AND HARD-NEGATIVE REVIEW
**LEXAUDIT RESEARCH EXTENSION — PHASE 4D-B**
**Author:** Principal Adversarial Evaluation Engineer & Statistical Auditor
**Date:** 2026-10-22

---

## 1. The Hard-Negative Challenge in Legal NLP

In contract drafting, clause order is not strictly rigid. Many sections are **commutative** or modular:
- Swapping Section 5 (Audit Rights) with Section 6 (Warranty Disclaimers) in a Software License Agreement changes the order, but produces **zero legal defect**.
- Swapping Section 2 (Permitted Users) with Section 4 (Schedule of Fees) in a commercial agreement remains completely valid and enforceable.

A naive structural anomaly detector that merely flags "deviations from standard training order" fails in real legal workflows by generating endless false alarms on harmless variations.

---

## 2. Hard-Negative Benchmark Findings

Two explicit hard-negative scenarios were evaluated:
1. `VAL_SLA_03_HN_COHERENT_SWAP`: Permitted Users swapped with Fee Schedule.
2. `TEST_03_HN_AUDIT_WARRANTY_SWAP`: Audit Rights swapped with Warranty Disclaimer.

### Model Behavior on Hard Negatives:
| Model | `VAL_SLA_03` Score | `VAL_SLA_03` Decision | `TEST_03` Score | `TEST_03` Decision | Hard-Negative Specificity |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Baseline B0 (Channel B)** | 0.6865 | **FALSE** (TN) | 0.6865 | **FALSE** (TN) | **100.0%** (Due to total insensitivity) |
| **Candidate C1 (Boundary)** | 0.5695 | **TRUE** (FP) | 0.6239 | **TRUE** (FP) | **0.0%** (Spurious contrast spike) |
| **Candidate C2 (BiLSTM)** | 0.1876 | **FALSE** (TN) | 0.1876 | **FALSE** (TN) | **100.0%** (Due to underfitting) |
| **Candidate C3 (Topological)**| 0.0000 | **FALSE** (TN) | 0.0000 | **FALSE** (TN) | **100.0%** (True semantic robustness) |

---

## 3. Robustness Verdict
Candidate C3 is the **only model** that simultaneously achieves:
1. High sensitivity on genuine structural dislocations (100% on tested held-out inversions).
2. Complete robustness to commutative covenant permutations (0.0% FPR on hard negatives).
Candidate C1 fails the hard-negative test, proving that statistical boundary contrast alone cannot distinguish harmless reorderings from legal contradictions.
