# Phase 4B — Conformal Coverage Target Verification

**Project:** Legal Contract Coherence Auditor (LexAudit)  
**Phase:** 4B — Scientific Precondition C Verification  
**Date:** 2026-10-14  
**Author:** Senior ML Validation Specialist & Principal NLP Research Engineer  
**Status:** VERIFIED & DOCUMENTED  

---

## 1. Code Ground Truth: Configured Target Coverage

Historical notes across the repository referenced both 90% and 95% nominal coverage targets. An audit of `src/calibration/conformal.py` and `tests/test_conformal.py` was conducted to establish the definitive ground truth:

```python
# src/calibration/conformal.py (Line 38)
class ConformalCalibrator:
    def __init__(self, target_coverage: float = 0.90):
        self.target_coverage = target_coverage
        self.significance_level = 1.0 - target_coverage  # alpha = 0.10
        ...
```

- **Nominal Configured Coverage:** **90.0%** ($\alpha = 0.10$).
- **Calibration Engine:** Inductive Conformal Prediction (ICP) implemented via `crepes` / inductive residual quantile calculation.
- **Reference Calibration Dataset:** Clean held-out SEC EDGAR filing clauses (unperturbed, standard sequence ordering).

---

## 2. Reconciling the 90% vs 95% Historical Documentation

- **Source of the 95% Figure:** Prompt 14 empirical evaluation reported Kendall's Tau and clean SEC false positive rates with 95% bootstrap confidence intervals (e.g., `Kendall's Tau 95% CI: [-0.125, +0.073]`).
- **Source of the 90% Figure:** The production prediction intervals output on each clause score in `UnifiedAuditReportModel` represent the $90\%$ conformal prediction interval $[y_{\min}, y_{\max}]$ computed by `ConformalCalibrator`.
- **UI Clarification:** Both numbers are legitimate within their respective statistical contexts, but must not be conflated:
  - **Statistical Bootstrap CIs:** 95% confidence intervals used in Transparency & Benchmarks (`Clean SEC FPR (High) 1.18% [0.57%, 2.41%]`).
  - **Clause-Level Prediction Intervals:** 90% nominal conformal coverage ($\alpha = 0.10$) used in per-clause anomaly score uncertainty bounds.
