# STATISTICAL UNCERTAINTY AND ESTIMATION PROTOCOL
**LEXAUDIT RESEARCH EXTENSION — PHASE 4D-B**
**Author:** Statistical Auditor & Principal NLP Research Scientist
**Date:** 2026-10-22

---

## 1. Mathematical Formulation of Confidence Intervals

### 1.1 Exact Two-Sided Wilson Score Interval
For an observed proportion $\hat{p} = k / n$ of successes across $n$ independent trials, the two-sided $(1 - \alpha)$ Wilson score confidence interval $[p_{\text{lower}}, p_{\text{upper}}]$ is defined as:

$$p_{\text{lower}}, p_{\text{upper}} = \frac{\hat{p} + \frac{z^2}{2n} \pm z \sqrt{\frac{\hat{p}(1-\hat{p})}{n} + \frac{z^2}{4n^2}}}{1 + \frac{z^2}{n}}$$

Where $z = \Phi^{-1}(1 - \alpha/2) \approx 1.959964$ for a 95% confidence level.

Unlike normal approximations (Wald intervals), the Wilson interval:
1. Never exceeds $[0, 1]$.
2. Avoids degenerate zero-width intervals when $k = 0$ or $k = n$.
3. Asymmetrically reflects sampling skew near parameter boundaries.

---

## 2. Exhaustive Wilson 95% Confidence Intervals Across All Models

| Model | Partition | Condition Positives ($n$) | True Positives ($k$) | Point Recall ($\hat{p}$) | Wilson 95% CI | Point Specificity | Wilson 95% CI |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Baseline B0 (Channel B)** | DIAGNOSTIC | 5 | 0 | 0.0000 | **[0.0000, 0.4345]** | 1.0000 (2/2) | [0.3424, 1.0000] |
| **Baseline B0 (Channel B)** | VALIDATION | 2 | 0 | 0.0000 | **[0.0000, 0.6576]** | 1.0000 (1/1) | [0.2065, 1.0000] |
| **Baseline B0 (Channel B)** | HELDOUT_TEST | 2 | 0 | 0.0000 | **[0.0000, 0.6576]** | 1.0000 (2/2) | [0.3424, 1.0000] |
| **Baseline B1 (Ensemble)** | DIAGNOSTIC | 5 | 0 | 0.0000 | **[0.0000, 0.4345]** | 1.0000 (2/2) | [0.3424, 1.0000] |
| **Baseline B1 (Ensemble)** | VALIDATION | 2 | 0 | 0.0000 | **[0.0000, 0.6576]** | 1.0000 (1/1) | [0.2065, 1.0000] |
| **Baseline B1 (Ensemble)** | HELDOUT_TEST | 2 | 0 | 0.0000 | **[0.0000, 0.6576]** | 1.0000 (2/2) | [0.3424, 1.0000] |
| **Candidate C1 (Boundary)** | DIAGNOSTIC | 5 | 2 | 0.4000 | **[0.1176, 0.7693]** | 0.5000 (1/2) | [0.0945, 0.9055] |
| **Candidate C1 (Boundary)** | VALIDATION | 2 | 2 | 1.0000 | **[0.3424, 1.0000]** | 0.0000 (0/1) | [0.0000, 0.7935] |
| **Candidate C1 (Boundary)** | HELDOUT_TEST | 2 | 2 | 1.0000 | **[0.3424, 1.0000]** | 0.5000 (1/2) | [0.0945, 0.9055] |
| **Candidate C2 (BiLSTM)** | DIAGNOSTIC | 5 | 0 | 0.0000 | **[0.0000, 0.4345]** | 1.0000 (2/2) | [0.3424, 1.0000] |
| **Candidate C2 (BiLSTM)** | VALIDATION | 2 | 0 | 0.0000 | **[0.0000, 0.6576]** | 1.0000 (1/1) | [0.2065, 1.0000] |
| **Candidate C2 (BiLSTM)** | HELDOUT_TEST | 2 | 0 | 0.0000 | **[0.0000, 0.6576]** | 1.0000 (2/2) | [0.3424, 1.0000] |
| **Candidate C3 (Topological)**| DIAGNOSTIC | 5 | 1 | 0.2000 | **[0.0362, 0.6245]** | 1.0000 (2/2) | [0.3424, 1.0000] |
| **Candidate C3 (Topological)**| VALIDATION | 2 | 1 | 0.5000 | **[0.0945, 0.9055]** | 1.0000 (1/1) | [0.2065, 1.0000] |
| **Candidate C3 (Topological)**| HELDOUT_TEST | 2 | 2 | 1.0000 | **[0.3424, 1.0000]** | 1.0000 (2/2) | [0.3424, 1.0000] |

---

## 3. Paired Effect Sizes and Hypothesis Testing

### 3.1 Held-Out Test Paired Comparison
On the matched held-out test partition ($n = 4$, 2 positives, 2 negatives):
- **Candidate C3 vs Frozen Baseline B0:**
  - Paired Recall Difference: $\Delta \text{Recall} = +100.0\%$ (2/2 detected vs 0/2 detected).
  - Paired Specificity Difference: $\Delta \text{Specificity} = 0.0\%$ (2/2 preserved vs 2/2 preserved).
  - McNemar's exact test contingency ($b = 2, c = 0$): $p = 0.50$ (two-tailed exact binomial under $N = 2$).
- **Candidate C1 vs Frozen Baseline B0:**
  - Paired Recall Difference: $\Delta \text{Recall} = +100.0\%$.
  - Paired Specificity Difference: $\Delta \text{Specificity} = -50.0\%$ (1 false positive on hard negative swap).

### 3.2 Methodological Integrity Statement
Because the sample size of the untouched held-out test partition is bounded ($N = 4$ contracts), the 95% Wilson interval for $2/2$ ($[0.3424, 1.0000]$) overlaps with the interval for $0/2$ ($[0.0000, 0.6576]$). 

**Scientifically Defensible Finding:**
Candidate C3 demonstrates clear empirical structural sensitivity on verified major inversions where Baseline B0 is completely blind, while maintaining zero false positives on coherent hard negatives. However, claims of asymptotic superiority ($p < 0.05$) are **not statistically justified** and are explicitly rejected pending larger-scale multi-template validation ($N \ge 30$).
