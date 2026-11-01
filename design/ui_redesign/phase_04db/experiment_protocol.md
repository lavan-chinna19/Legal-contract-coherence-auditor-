# EXPERIMENT PROTOCOL AND PRE-REGISTRATION RECORD
**LEXAUDIT RESEARCH EXTENSION — PHASE 4D-B**
**Author:** Principal Legal NLP Research Scientist & Statistical Auditor
**Date:** 2026-10-22

---

## 1. Pre-Registered Experimental Protocol Summary

Prior to running evaluation on the held-out test partition, the following experimental protocol was formally registered in `research/structural_coherence_phase_04db/preregistered_experimental_protocol.md`:

- **Primary Target Task:** Task 1 — Structural Anomaly Detection.
- **Unit of Analysis:** Contract sequence level, with secondary clause-level localization.
- **Primary Metric:** Structural Recall @ $\text{FPR} \le 5\%$ on the held-out test partition.
- **Secondary Metrics:** Specificity, Balanced Accuracy, Precision, F1, Exact Two-Sided Wilson 95% Confidence Intervals, Localization Hit Rate, Mean Inference Latency.
- **Decision Threshold Selection Policy:** Thresholds selected exclusively using the Development/Validation split:
  - Baseline B0: Fixed production override threshold ($0.70$).
  - Baseline B1: Fixed production ensemble threshold ($0.50$).
  - Baseline B2: Fixed adjacent cosine threshold ($0.25$).
  - Candidate C1: Calibrated on validation partition to $0.42$.
  - Candidate C2: Calibrated on validation partition to $0.50$.
  - Candidate C3: Pre-registered threshold of $0.50$.
- **Eligibility Exclusions:** Cases labeled `AMBIGUOUS_ORDER` (such as $P2\_03$) are recorded in case-level outputs but excluded from the strict condition-positive denominator.
- **Model Promotion Criterion:** A candidate must achieve higher recall than Baseline B0 on the untouched held-out test set while preserving $\text{FPR} \le 5\%$ and operating within CPU laptop resource bounds (< 50 ms latency, < 100 MB RAM).

---

## 2. Protocol Adherence Audit

1. **Untouched Test Partition:** The 4 held-out test cases were evaluated exactly once after threshold calibration was frozen.
2. **No Post-Hoc Tuning:** Thresholds were not adjusted after observing held-out test results.
3. **No Metric Redefinition:** All formulas and metrics follow standard mathematical definitions.
4. **Transparent Negative Results:** All failures of Candidate C1 (hard negative false positives) and Candidate C2 (underfitting) are fully reported.
