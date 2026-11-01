# BASELINE VS. CANDIDATE COMPARISON REPORT
**LEXAUDIT RESEARCH EXTENSION — PHASE 4D-B**
**Author:** Statistical Auditor & ML Systems Engineer
**Date:** 2026-10-22

---

## 1. Direct Paired Comparison on Matched Held-Out Test Data

To avoid dataset shift artifacts, all models were evaluated on the exact same held-out test contracts:

| Performance Metric | Frozen Baseline B0 (Channel B) | Production Ensemble B1 | Candidate C1 (Boundary) | Candidate C3 (Topological DAG) | Paired Gain (C3 vs B0) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Held-Out Structural Recall** | **0.00%** (0/2) | **0.00%** (0/2) | **100.00%** (2/2) | **100.00%** (2/2) | **+100.00%** |
| **Held-Out Specificity** | **100.00%** (2/2) | **100.00%** (2/2) | **50.00%** (1/2) | **100.00%** (2/2) | **0.00%** |
| **False-Positive Rate (FPR)** | **0.00%** | **0.00%** | **50.00%** | **0.00%** | **0.00%** |
| **Balanced Accuracy** | **50.00%** | **50.00%** | **75.00%** | **100.00%** | **+50.00%** |
| **Evidence Localization Hit Rate**| **0.00%** | **0.00%** | **50.00%** | **100.00%** | **+100.00%** |
| **Mean CPU Latency** | **7.68 ms** | **38.31 ms** | **14.98 ms** | **0.17 ms** | **-7.51 ms (45x faster)** |
| **Peak Memory Footprint** | **~42 MB** | **~58 MB** | **~38 MB** | **< 2 MB** | **-40 MB** |

---

## 2. Qualitative and Architectural Differences

### 2.1 The Baseline B0 Failure Mode
Baseline B0 treats clause pairs as independent classification items without global document context. Its fine-tuned MLP head maps almost all valid legal text into a compressed logit interval $[-0.799, -0.668]$, producing probabilities in $[0.31, 0.34]$. Displacing a clause by 9 slots only changes the score by $+0.015$, leaving it far below the $0.70$ anomaly threshold.

### 2.2 The Candidate C3 Advantage
Candidate C3 recognizes that legal contracts are ordered hierarchies where specific clause categories (preambles, scopes, considerations, boilerplate, exhibits) have rigorous precedence constraints. By verifying directed edges along this lifecycle graph:
1. It immediately flags when Exhibit A precedes Scope of Services (score $1.0$).
2. It flags when Governing Law precedes Scope (score $1.0$).
3. It completely ignores when two commutative operational covenants (Audit Rights and Warranty Disclaimers) are reordered, preserving 100% specificity.
