# CORRECTED STATISTICAL COMPARISON AND UNCERTAINTY AUDIT
**LEXAUDIT INDEPENDENT RESEARCH AUDIT — PHASE 4D-B**
**Auditor:** Independent Legal NLP Research Auditor & Statistical Verification Lead
**Date:** 2026-10-22

---

## 1. Executive Statistical Review

The Phase 4D-B report highlighted a headline metric of **"100.0% Recall and 100.0% Specificity"** on the held-out test partition for Candidate C3. 

This independent audit reveals that:
1. **The sample size of the held-out test partition is $N = 4$ perturbations** ($n_{\text{pos}} = 2, n_{\text{neg}} = 2$).
2. **The number of independent parent contracts in the test set is $N_{\text{parent}} = 2$** (`SYNTH_DOC_01_MSA` and `SYNTH_DOC_02_SLA`), both of which were extensively utilized in Diagnostic and Validation splits.
3. **The number of genuinely unseen parent contracts in the test set is ZERO ($N_{\text{unseen}} = 0$)**.
4. **Candidate C3's pooled recall across all 9 eligible positive benchmark cases is only 44.44% (4/9)**, with a two-sided Wilson 95% confidence interval of **$[0.1888, 0.7333]$**.
5. The paired difference between Candidate C3 and Baseline B0 on the held-out test partition ($b = 2, c = 0, N = 2$) yields an exact McNemar / binomial $p\text{-value}$ of **$p = 0.50$**, which is **statistically indistinguishable from chance**.

---

## 2. Exhaustive Confusion Matrices Recalculated from Raw Case Data

### 2.1 Held-Out Test Partition ($N = 4$ cases, 2 positive, 2 negative)
- **Baseline B0 (Frozen Channel B):**
  - $\text{TP} = 0, \text{FP} = 0, \text{FN} = 2, \text{TN} = 2$
  - $\text{Recall} = 0.0000$ (Wilson 95% CI: $[0.0000, 0.6576]$)
  - $\text{Specificity} = 1.0000$ (Wilson 95% CI: $[0.3424, 1.0000]$)
- **Candidate C3 (Topological Precedence DAG):**
  - $\text{TP} = 2, \text{FP} = 0, \text{FN} = 0, \text{TN} = 2$
  - $\text{Recall} = 1.0000$ (Wilson 95% CI: $[0.3424, 1.0000]$)
  - $\text{Specificity} = 1.0000$ (Wilson 95% CI: $[0.3424, 1.0000]$)
- **Candidate C1 (Contextual Boundary Contrast):**
  - $\text{TP} = 2, \text{FP} = 1, \text{FN} = 0, \text{TN} = 1$
  - $\text{Recall} = 1.0000$ (Wilson 95% CI: $[0.3424, 1.0000]$)
  - $\text{Specificity} = 0.5000$ (Wilson 95% CI: $[0.0945, 0.9055]$), $\text{FPR} = 50.0\%$

### 2.2 Validation Partition ($N = 3$ cases, 2 positive, 1 negative)
- **Baseline B0:** $\text{TP} = 0, \text{FP} = 0, \text{FN} = 2, \text{TN} = 1 \implies \text{Recall} = 0.0000$ ($[0.0, 0.6576]$)
- **Candidate C3:** $\text{TP} = 1, \text{FP} = 0, \text{FN} = 1, \text{TN} = 1 \implies \text{Recall} = 0.5000$ ($[0.0945, 0.9055]$)
- **Candidate C1:** $\text{TP} = 2, \text{FP} = 1, \text{FN} = 0, \text{TN} = 0 \implies \text{Recall} = 1.0000$, $\text{Specificity} = 0.0000$ ($\text{FPR} = 100.0\%$)

### 2.3 Diagnostic Benchmark Partition ($N = 7$ eligible cases, 5 positive, 2 negative; excludes 1 ambiguous)
- **Baseline B0:** $\text{TP} = 0, \text{FP} = 0, \text{FN} = 5, \text{TN} = 2 \implies \text{Recall} = 0.0000$ ($[0.0000, 0.4345]$)
- **Candidate C3:** $\text{TP} = 1, \text{FP} = 0, \text{FN} = 4, \text{TN} = 2 \implies \text{Recall} = 0.2000$ ($[0.0362, 0.6245]$)
- **Candidate C1:** $\text{TP} = 2, \text{FP} = 1, \text{FN} = 3, \text{TN} = 1 \implies \text{Recall} = 0.4000$ ($[0.1176, 0.7693]$)

---

## 3. Pooled Benchmark Statistics (All 15 Evaluated Cases)

When evaluating across all 9 eligible positive cases and all 5 eligible negative cases in the entire Phase 4D-B suite:

| Model | Eligible Positives | TP | FN | Pooled Recall | Exact Wilson 95% CI | Eligible Negatives | FP | TN | Pooled Specificity | Exact Wilson 95% CI |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Baseline B0** | 9 | 0 | 9 | **0.00% (0/9)** | **[0.0000, 0.2991]** | 5 | 0 | 5 | **100.0% (5/5)** | [0.5655, 1.0000] |
| **Candidate C1** | 9 | 6 | 3 | **66.67% (6/9)**| **[0.3542, 0.8794]** | 5 | 3 | 2 | **40.0% (2/5)** | [0.1176, 0.7693] |
| **Candidate C2** | 9 | 0 | 9 | **0.00% (0/9)** | **[0.0000, 0.2991]** | 5 | 0 | 5 | **100.0% (5/5)** | [0.5655, 1.0000] |
| **Candidate C3** | 9 | 4 | 5 | **44.44% (4/9)**| **[0.1888, 0.7333]** | 5 | 0 | 5 | **100.0% (5/5)** | [0.5655, 1.0000] |

---

## 4. Hypothesis Testing and Paired Comparisons

### 4.1 Held-Out Test Set Comparison ($N = 2$ positives)
- Baseline B0 detected: $0/2$
- Candidate C3 detected: $2/2$
- Paired contingency table (discordant pairs): $b = 2$ (C3 detected, B0 missed), $c = 0$ (B0 detected, C3 missed).
- McNemar's exact test / two-tailed binomial test:
  $$P(X \ge 2 \mid N = 2, p = 0.5) = 2 \times 0.5^2 = 0.5000$$
- **Finding:** With $p = 0.50$, the held-out test improvement is **statistically non-significant**.

### 4.2 Pooled Positive Cases Comparison ($N = 9$ positives)
- Baseline B0 detected: $0/9$
- Candidate C3 detected: $4/9$
- Discordant pairs: $b = 4, c = 0$.
- Exact two-tailed binomial test:
  $$P(X \ge 4 \mid N = 4, p = 0.5) = 2 \times 0.5^4 = 0.1250$$
- **Finding:** With $p = 0.1250$, even pooled across all 9 cases, Candidate C3 **does not achieve statistical significance at the $\alpha = 0.05$ level**.

---

## 5. Statistical Audit Verdict

1. **Overlapping Intervals:** The Wilson 95% confidence interval for C3 on the held-out test set ($[0.3424, 1.0000]$) overlaps with the confidence interval for Baseline B0 ($[0.0000, 0.6576]$) by a margin of $[0.3424, 0.6576]$.
2. **Effective Document Sample Size:** The held-out test set contains only $N_{\text{parent}} = 2$ parent contract templates, with $N_{\text{unseen\_parent}} = 0$.
3. **True Capability:** Candidate C3 achieved **44.4% recall** overall, detecting only the 4 cases where a Stage 5/6 boilerplate clause preceded a Stage 0/1 clause.
4. **Scientific Conclusion:** Candidate C3 is an interesting rule-based heuristic for catching extreme boundary dislocations, but claiming general 100% recall or proven superiority over neural baselines is statistically unfounded.
