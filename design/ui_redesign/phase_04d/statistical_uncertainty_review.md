# Phase 4D Statistical Uncertainty Review

## 1. Accounting and Denominators
- **Canonical Scenarios Evaluated**: 20
- **Total Valid Transformations**: 20/20 (100.0%)
- **Strictly Evaluated Positive Conditions**: 11
- **Negative Control Evaluations**: 2
- **Descriptive / Unsupported Scenarios**: 7 (P3 duplicates: 2, P4 near-duplicates: 1, P8 arbitrary deletion: 1, P10 compound: 2, P8 consequence: 1)
- **Positive Condition Detections**: 5 / 11 (45.45% composite)
  - Deterministic Rules (P5, P6, P7): 5 / 5 (100.0%, 95% Wilson CI: [56.6%, 100.0%])
  - Neural Structural (P1, P2): 0 / 6 (0.0%, 95% Wilson CI: [0.0%, 39.0%])
- **Clean Negative Control False-Positive Rate**: 0 / 2 (0.0%, 95% Wilson CI: [0.0%, 65.8%])

## 2. Uncertainty & Small-Sample Caveats
Given the focused synthetic fixture size ($N = 20$ canonical cases derived from 2 synthetic contracts), statistical uncertainty intervals are intentionally wide. We refrain from claiming broad cross-corpus superiority and explicitly classify all empirical findings as `PRELIMINARY_SYNTHETIC_EVALUATION`.
