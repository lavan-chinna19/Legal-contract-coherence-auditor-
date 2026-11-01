# FROZEN BASELINE REPRODUCTION REPORT
**LEXAUDIT RESEARCH EXTENSION — PHASE 4D-B**
**Author:** Principal ML Systems Engineer & Statistical Auditor
**Date:** 2026-10-22

---

## 1. Frozen Baseline Architectures Under Evaluation

### Baseline B0: Frozen Channel B (Pairwise Neural MLP)
- **Architecture:** PyTorch MLP (`Sequential(Linear(768, 128), ReLU(), Dropout(0.2), Linear(128, 1))`).
- **Input:** Concatenated 384-d frozen SentenceTransformer (`all-MiniLM-L6-v2`) embeddings of adjacent clause pairs $(c_i, c_{i+1})$.
- **Training Lineage:** Trained on 894 LEDGAR clause pairs with Adam optimizer ($lr = 10^{-3}$, weight decay $10^{-4}$).
- **Anomaly Criterion:** Anomaly flag is asserted if $\max(1 - P_{\text{compat}}) \ge 0.70$.

### Baseline B1: Production Dual-Channel Ensemble
- **Architecture:** Weighted linear combination $S = 0.5 \cdot S_A + 0.5 \cdot S_B$.
  - $S_A$: Min cosine distance to LEDGAR centroids, clipped to $[0.20, 0.80]$ and normalized to $[0.0, 1.0]$.
  - $S_B$: $1 - P_{\text{compat}}$ from Channel B.
- **Production Anomaly Predicate:**
  $$\text{is\_anomaly} = (S \ge 0.50) \lor (\max(S_A, S_B) \ge 0.70)$$

### Baseline B2: Adjacent Cosine Distance
- **Architecture:** Unparameterized baseline measuring $1 - \cos(e_i, e_{i+1})$ between adjacent clause embeddings.
- **Threshold:** Empirical cutoff of $0.25$.

---

## 2. Baseline Reproduction Results

All baselines were evaluated on the exact same 15 contracts across Diagnostic, Validation, and Held-Out Test partitions:

| Baseline | Split | Condition Positives | True Positives | Point Recall | Wilson 95% CI | Specificity | Mean Latency (ms) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **B0 (Channel B)** | DIAGNOSTIC | 5 | 0 | **0.0000** | [0.0000, 0.4345] | 1.0000 | 24.01 |
| **B0 (Channel B)** | VALIDATION | 2 | 0 | **0.0000** | [0.0000, 0.6576] | 1.0000 | 6.35 |
| **B0 (Channel B)** | HELDOUT_TEST | 2 | 0 | **0.0000** | [0.0000, 0.6576] | 1.0000 | 7.68 |
| **B1 (Ensemble)** | DIAGNOSTIC | 5 | 0 | **0.0000** | [0.0000, 0.4345] | 1.0000 | 41.93 |
| **B1 (Ensemble)** | VALIDATION | 2 | 0 | **0.0000** | [0.0000, 0.6576] | 1.0000 | 42.09 |
| **B1 (Ensemble)** | HELDOUT_TEST | 2 | 0 | **0.0000** | [0.0000, 0.6576] | 1.0000 | 38.31 |
| **B2 (Cosine)** | DIAGNOSTIC | 5 | 0 | **0.0000** | [0.0000, 0.4345] | 1.0000 | 7.54 |
| **B2 (Cosine)** | VALIDATION | 2 | 0 | **0.0000** | [0.0000, 0.6576] | 1.0000 | 7.61 |
| **B2 (Cosine)** | HELDOUT_TEST | 2 | 0 | **0.0000** | [0.0000, 0.6576] | 1.0000 | 6.62 |

---

## 3. Scientific Verification of Historical Phase 4D-A Findings

1. **Reconstructed Exact Recall:** Baselines $B0, B1, B2$ produce exactly **$0/5$ (0.0%)** recall on the diagnostic benchmark and **$0/2$ (0.0%)** on held-out test violations.
2. **Reconstructed Wilson Intervals:** The two-sided Wilson 95% confidence interval for $0/5$ is verified at $[0.0000, 0.4345]$ and for $0/2$ at $[0.0000, 0.6576]$.
3. **Confirmed Logit Saturation:** Across all 15 evaluated contracts (114 clause pairs), Channel B probabilities remained strictly within $[0.3102, 0.3389]$, yielding anomaly scores between $0.6611$ and $0.6898$. Because no score reached the production override threshold of $0.70$, and Channel A distances were clipped to $0.0000$, composite scores never exceeded $0.3449$ (well below the $0.50$ production anomaly threshold).
4. **Reproducibility Certificate:** The frozen baseline behavior reported in Phase 4D-A is completely verified and 100% reproducible.
