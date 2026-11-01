# Statistical Uncertainty and Small-Sample Discipline Review

**Document ID**: `PHASE_04DA_STATISTICAL_REVIEW`  
**Auditor**: Statistical Evaluation Researcher & Senior ML Auditor  
**Scope**: Uncertainty Intervals, Wilson Score Bounds, Sample-Size Limitations, and Generalizability  

---

## 1. Executive Summary

In scientific evaluation, point estimates without confidence intervals create a false sense of certainty. When evaluating small synthetic benchmark catalogs ($n \in [2, 6]$), standard asymptotic normal approximations ($\hat{p} \pm 1.96 \sqrt{\frac{p(1-p)}{n}}$) fail completely.

This review calculates **exact 95% Wilson score confidence intervals** for all observed detection rates and documents the severe statistical constraints of small benchmark fixtures.

---

## 2. Wilson Score Confidence Interval Calculations

For small sample sizes with observed proportions at boundary extremes ($\hat{p} = 0.0$ or $\hat{p} = 1.0$), the Wilson score interval provides robust coverage without overflowing the $[0, 1]$ interval:
$$w = \frac{\hat{p} + \frac{z^2}{2n} \pm z \sqrt{\frac{\hat{p}(1-\hat{p})}{n} + \frac{z^2}{4n^2}}}{1 + \frac{z^2}{n}}$$
where $z = 1.96$ for a 95% confidence level.

| Task Metric | Observed Successes ($k$) | Denominator ($n$) | Point Estimate ($\hat{p}$) | Exact 95% Wilson Score Interval | Scientific Interpretation |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Reference Rule Recall** | 3 | 3 | **100.0%** | **$[43.85\%, 100.00\%]$** | High uncertainty. A sample of 3 successes is consistent with true recall as low as 43.9%. |
| **Date Rule Recall** | 2 | 2 | **100.0%** | **$[34.24\%, 100.00\%]$** | Severe uncertainty. Sample of 2 cannot establish true production reliability. |
| **Combined Rule Recall** | 5 | 5 | **100.0%** | **$[56.55\%, 100.00\%]$** | Even with 5/5 successes, true population recall could be as low as 56.6%. |
| **Rule Specificity (FP Rate)** | 2 (clean) | 2 | **100.0%** | **$[34.24\%, 100.00\%]$** | Zero false positives on 2 synthetic documents does NOT prove 0% FPR in production. |
| **Structural Anomaly Recall (Prod)** | 0 | 5 (strictly eligible) | **0.0%** | **$[0.00\%, 43.45\%]$** | True structural anomaly recall is bounded above at 43.5%. |
| **Structural Anomaly Recall (Broad)** | 0 | 6 (all struct) | **0.0%** | **$[0.00\%, 39.03\%]$** | True sensitivity is bounded above at 39.0%. |

---

## 3. Critical Scientific Takeaways

### A. Point Estimates Cannot Be Extrapolated to Commercial Contracts
- Reporting "100.0% accuracy" for rule checkers is mathematically true on the tested 5 synthetic fixtures, but statistically represents a wide credible interval ($[56.6\%, 100.0\%]$).
- Commercial contracts contain complex cross-referencing grammars, multi-section enumerations, parentheticals, and ambiguous date definitions not represented in these minimal synthetic documents.

### B. The Danger of Over-Interpreting Small Negative Controls
- Phase 4D reported 100% specificity based on 2 negative controls (`SYNTH_DOC_01_MSA` and `SYNTH_DOC_02_SLA`).
- Two clean documents provide minimal statistical power ($N=2$). They prove that the evaluation runner does not introduce spurious noise into clean synthetic inputs, but they provide zero statistical evidence regarding the false positive rate on diverse, real-world SEC EDGAR or CUAD filings.

### C. Formal Inestimability of Population Metrics
- **Population Precision, Recall, and F1 are formally NOT estimable from this benchmark alone.**
- The benchmark was designed as a **diagnostic probe laboratory** (to verify whether specific mechanisms trigger), NOT as an unbiased epidemiological test of contract review performance.
- Any marketing or product claim asserting "LexAudit detects 100% of contract errors" based on Phase 4D data is statistically deceptive and scientifically indefensible.

---

## 4. Auditor Guidelines for Future Benchmarking

1. Always report integer ratios ($k/n$) alongside percentages.
2. Accompany every percentage with its 95% Wilson score interval.
3. Distinguish diagnostic probe evaluations on synthetic fixtures from representative validation on held-out commercial corpuses.
