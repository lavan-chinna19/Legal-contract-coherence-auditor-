# Phase 4D Clean Negative-Control Analysis & Discrepancy Note

## 1. Clean Negative-Control Results
- Evaluated Fixtures: `SYNTH_DOC_01_MSA` (11 clauses) and `SYNTH_DOC_02_SLA` (8 clauses).
- Injected Perturbations: None (0).
- Results:
  - Baseline Anomaly Count: 0
  - Perturbed Anomaly Count: 0
  - Rule Violations: 0
  - False-Positive Findings: 0
  - False-Positive Rate: **0.0%** (0/2 on clean synthetic controls)

## 2. Historical Audit Inconsistency Reconciliation
Prior Phase 4C-A audit materials noted two differing unthresholded false-repair rates for nine clean held-out contracts:
- 33.3% (3/9) in one report.
- 55.6% (5/9) in a subsequent audit.

### Reconciliation Findings:
1. **Cause of Discrepancy**: The difference stems from the candidate eligibility filter and tie-breaking rule:
   - When candidates with non-positive objective delta ($\Delta J \le 0$) are strictly excluded from "repair recommendations", only 3 of 9 clean contracts received an unthresholded non-identity rank 1 (33.3%).
   - When equal-scoring candidates ($\Delta J = 0.0$) were broken arbitrarily by lexical slot index rather than remaining at the baseline slot, 5 of 9 clean contracts were classified as false repairs (55.6%).
2. **Phase 4D Stance**: Phase 4D evaluates *perturbation detection* rather than *clause repositioning recovery*. In Phase 4D, negative control evaluation measures whether unmodified documents generate false anomaly spikes or false rule flags. As verified empirically, the false-positive rate on clean controls is **0.0%**.
