# ABLATION STUDY
**LEXAUDIT RESEARCH EXTENSION — PHASE 4D-B**
**Author:** Senior Machine Learning Engineer & Research Evaluation Specialist
**Date:** 2026-10-22

---

## 1. Experimental Ablations

To isolate the individual contribution of each structural feature, component ablations were conducted across the held-out test partition:

| Ablation ID | Model Variant | Active Components | Held-Out Recall | Held-Out Spec | Held-Out FPR | Latency (ms) | Component Significance Finding |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **ABL_00** | Frozen Channel B | Pairwise MLP Alone | 0.00 (0/2) | 1.00 (2/2) | 0.00 | 7.68 | Baseline pairwise model is completely insensitive to document structure. |
| **ABL_01** | Frozen Channel A | Centroid Distance Alone | 0.00 (0/2) | 1.00 (2/2) | 0.00 | 15.20 | Channel A is invariant to clause permutations ($\Delta S_A = 0.000000$). |
| **ABL_02** | Production Ensemble| 0.5 Channel A + 0.5 Channel B | 0.00 (0/2) | 1.00 (2/2) | 0.00 | 38.31 | Zero production anomaly detections across all structural cases. |
| **ABL_03** | Full Candidate C1 | Contextual Window (0.35) + Boundary Contrast (0.25) + Progression Discordance (0.40) | 1.00 (2/2) | 0.50 (1/2) | 0.50 | 14.98 | Full multi-factor detector; achieves 100% recall but suffers 50% FPR on hard negatives. |
| **ABL_04** | C1 w/o Discordance | Contextual Window (0.50) + Boundary Contrast (0.50) | 0.50 (1/2) | 0.50 (1/2) | 0.50 | 14.50 | Without lifecycle discordance, subtle structural inversions are missed (recall drops by 50%). |
| **ABL_05** | C1 w/o Contrast | Contextual Window (0.40) + Progression Discordance (0.60) | 1.00 (2/2) | 1.00 (2/2) | 0.00 | 10.20 | Removing local boundary contrast eliminates false positives on coherent hard negative swaps. |
| **ABL_06** | C1 w/o Context | Boundary Contrast (0.40) + Progression Discordance (0.60) | 1.00 (2/2) | 0.50 (1/2) | 0.50 | 8.40 | Contextual rolling window provides minor smoothing but does not independently drive classification. |
| **ABL_07** | Candidate C2 | Sequence BiLSTM on Frozen Embeddings | 0.00 (0/2) | 1.00 (2/2) | 0.00 | 53.79 | Learned sequence head underfits without massive pretraining; produces scores < 0.19. |
| **ABL_08** | Candidate C3 | Directed Acyclic Graph Precedence Checker | 1.00 (2/2) | 1.00 (2/2) | 0.00 | 0.17 | Explicit lifecycle precedence rules achieve perfect precision, recall, and sub-millisecond execution. |

---

## 2. Key Ablation Insights

1. **Local Boundary Contrast is the Primary Driver of False Positives:**
   Ablation `ABL_05` reveals that removing the local boundary contrast component from Candidate C1 eliminates its false positives on hard negatives ($100\%$ specificity). Boundary contrast spikes whenever two unfamiliar clauses are juxtaposed, confusing novelty with incoherence.
2. **Lifecycle Precedence is the Primary Driver of Structural Sensitivity:**
   Across both C1 (`ABL_03` vs `ABL_04`) and C3 (`ABL_08`), lifecycle progression and precedence constraints provide the decisive signal for identifying contract-ordering defects.
