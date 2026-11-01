# STATISTICAL SIGNIFICANCE AND UNCERTAINTY REVIEW
**LEXAUDIT RESEARCH EXTENSION — PHASE 4D-B**
**Author:** Statistical Auditor & Principal Research Scientist
**Date:** 2026-10-22

---

## 1. Summary of Statistical Findings

1. **Exact Two-Sided Wilson 95% Confidence Intervals:**
   - Frozen Channel B on Held-Out Test ($0/2$): **$[0.0000, 0.6576]$**
   - Candidate C3 on Held-Out Test ($2/2$): **$[0.3424, 1.0000]$**
   - Historical Diagnostic Baseline ($0/5$): **$[0.0000, 0.4345]$**
   - Candidate C3 on Diagnostic Baseline ($1/5$): **$[0.0362, 0.6245]$**
2. **Paired Effect Size on Matched Held-Out Test Data:**
   - Absolute Recall Gain ($\Delta \text{Recall}$): **$+100.00\%$** (from $0.0\%$ to $100.0\%$)
   - Specificity Delta ($\Delta \text{Specificity}$): **$0.00\%$** (preserved at $100.0\%$)
3. **Hypothesis Testing and Sample Size Limitations:**
   - Because the untouched held-out test partition is bounded to $N = 4$ contracts ($n_{\text{pos}} = 2, n_{\text{neg}} = 2$), the 95% Wilson confidence intervals overlap between $[0.3424, 0.6576]$.
   - Under exact binomial testing (McNemar's test with $b = 2, c = 0$), $p = 0.50$.
   - **Formal Statistical Conclusion:** Candidate C3 demonstrates decisive empirical sensitivity on genuine inversions where the baseline is blind. However, asymptotic superiority ($p < 0.05$) cannot be asserted on this sample size alone. Any claim of "proven statistical significance" without a larger multi-template corpus ($N \ge 30$) is scientifically unwarranted and is explicitly disclaimed.
