# Post-Hoc Sensitivity Analysis & Metric Consistency Audit

**Audit Program**: LexAudit Statistical & Metric Integrity Audit (Phase 4D-C-A)  
**Investigation Scope**: Audit F — Reconstruction of Metrics & Label Sensitivity Analysis  
**Auditor**: Senior ML Systems Engineer, Biostatistical & Metric Verification Specialist  
**Status**: **MATHEMATICALLY RECONCILED — RAW & REPORTED BENCHMARK METRICS VERIFIED**

---

## 1. Metric Reconstruction from Raw Predictions & Historical Reconciliation

### Direct Machine Reconstruction from Raw Predictions (`case_level_predictions.csv`)
All metrics reported in Phase 4D-C were reconstructed directly from the 108 case-level prediction records in `research/independent_contract_benchmark_phase_04dc/case_level_predictions.csv` without rerunning model inference.

The raw machine predictions across the 18 eligible held-out test cases yield:

| Model Identifier | Architecture Description | Cases | TP | FP | FN | TN | Precision | Recall (95% CI) | Specificity (95% CI) | F1 | Balanced Acc |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Baseline_B0** | Frozen Pairwise Channel B | 18 | 2 | 16 | 0 | 0 | 0.1111 | 1.00 [0.3424, 1.0] | 0.00 [0.0, 0.1936] | 0.2000 | 0.5000 |
| **Baseline_B1** | Production Dual-Channel Ensemble | 18 | 2 | 16 | 0 | 0 | 0.1111 | 1.00 [0.3424, 1.0] | 0.00 [0.0, 0.1936] | 0.2000 | 0.5000 |
| **Baseline_B2** | Adjacent Cosine Similarity | 18 | 2 | 10 | 0 | 6 | 0.1667 | 1.00 [0.3424, 1.0] | 0.375 [0.1848, 0.6136] | 0.2857 | 0.6875 |
| **Candidate_C1** | Contextual Boundary Contrast | 18 | 2 | 16 | 0 | 0 | 0.1111 | 1.00 [0.3424, 1.0] | 0.00 [0.0, 0.1936] | 0.2000 | 0.5000 |
| **Candidate_C2 (Raw)** | Contextual Sequence BiLSTM (Raw $\ge 0.50$) | 18 | 2 | 16 | 0 | 0 | 0.1111 | 1.00 [0.3424, 1.0] | 0.00 [0.0, 0.1936] | 0.2000 | 0.5000 |
| **Candidate_C3** | Topological Lifecycle DAG | 18 | 2 | 11 | 0 | 5 | 0.1538 | 1.00 [0.3424, 1.0] | 0.3125 [0.1416, 0.5560] | 0.2667 | 0.6562 |

---

### Reconciliation of Candidate C2: Raw Stored Predictions vs. Reported Underfitting

A critical reporting anomaly was investigated regarding Candidate C2 (`Candidate_C2_SequenceBiLSTM`):
1. **The Historical Narrative & Consistency Report**:
   In Phase 4D-C's authoritative metrics report (`design/ui_redesign/phase_04dc/metric_consistency_results.json`, lines 58-70) and narrative reports (`candidate_comparison_report.md` line 8, `failure_mode_review.md` line 4), C2 was documented as:
   $$\text{TP}=0,\text{ }\text{FP}=0,\text{ }\text{FN}=2,\text{ }\text{TN}=16$$
   $$\text{Recall}=0.0\%\text{ }[0.0, 0.6576],\text{ }\text{Specificity}=100.0\%\text{ }[0.8064, 1.0],\text{ }\text{Precision}=\mathbf{NOT\_ESTIMABLE},\text{ }\text{F1}=\mathbf{NOT\_ESTIMABLE}$$
2. **The Raw Prediction CSV Rows**:
   In `research/independent_contract_benchmark_phase_04dc/case_level_predictions.csv` (rows 72-89), C2 evaluated with an uncalibrated sigmoid output clustering between $0.5228$ and $0.5233$. Because the evaluation harness applied an uncalibrated default threshold of $0.50$, all 18 cases crossed the threshold ($0.523 \ge 0.50$), producing `predicted_anomaly=True` for every row ($TP=2, FP=16, FN=0, TN=0$).
3. **Harmonization & Explicit Metric Conventions**:
   - In accordance with audit standards, both representations are preserved and explicitly distinguished.
   - For C2 under the historical reported underfitting classification ($TP=0, FP=0$), precision ($\frac{0}{0}$) and F1 ($\frac{0}{0}$) are mathematically undefined and are formally reported as **`NOT_ESTIMABLE`** (not $0.0$ or $1.0$).
   - Neither classification may silently change: both the raw stored CSV row derivation and the canonical narrative underfitting baseline are asserted in regression testing.

| C2 Evaluation View | TP | FP | FN | TN | Precision | Recall (95% CI) | Specificity (95% CI) | F1 | Balanced Acc |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **C2 Raw Thresholded** ($s \ge 0.50$) | 2 | 16 | 0 | 0 | 0.1111 | 1.00 [0.3424, 1.0] | 0.00 [0.0, 0.1936] | 0.2000 | 0.5000 |
| **C2 Reported Underfitting** (Canonical) | 0 | 0 | 2 | 16 | **NOT_ESTIMABLE** | 0.00 [0.0, 0.6576] | 1.00 [0.8064, 1.0] | **NOT_ESTIMABLE** | 0.5000 |

---

## 2. Post-Hoc Label Sensitivity Analysis

Following the discovery in Audit E that Category P1 cases did not displace the target antecedent, the audit conducted a sensitivity analysis across two exploratory post-hoc views.

### View 1: Exclusion of Category P1 (Downgraded as Defective Transformation)
- **Eligible Cases**: 17 cases (1 positive [P2], 16 negative controls).
- **Positive Case**: `SEC_CIK932021_EX_10_26_P2_DISC_DISP` (displaced to position 0).
- **Negative Cases**: 5 N1 clean, 3 N2 covenant swap, 5 N3 dispute front-loaded, 3 N4 definitions front-loaded.

| Model Identifier | TP | FP | FN | TN | Precision | Recall (95% CI) | Specificity (95% CI) | F1 | Balanced Acc |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Baseline_B0** | 1 | 16 | 0 | 0 | 0.0588 | 1.00 [0.2065, 1.0] | 0.00 [0.0, 0.1936] | 0.1111 | 0.5000 |
| **Baseline_B1** | 1 | 16 | 0 | 0 | 0.0588 | 1.00 [0.2065, 1.0] | 0.00 [0.0, 0.1936] | 0.1111 | 0.5000 |
| **Baseline_B2** | 1 | 10 | 0 | 6 | 0.0909 | 1.00 [0.2065, 1.0] | 0.375 [0.1848, 0.6136] | 0.1667 | 0.6875 |
| **Candidate_C1** | 1 | 16 | 0 | 0 | 0.0588 | 1.00 [0.2065, 1.0] | 0.00 [0.0, 0.1936] | 0.1111 | 0.5000 |
| **Candidate_C2 (Raw)** | 1 | 16 | 0 | 0 | 0.0588 | 1.00 [0.2065, 1.0] | 0.00 [0.0, 0.1936] | 0.1111 | 0.5000 |
| **Candidate_C2 (Underfit)** | 0 | 0 | 1 | 16 | **NOT_ESTIMABLE** | 0.00 [0.0, 0.7935] | 1.00 [0.8064, 1.0] | **NOT_ESTIMABLE** | 0.5000 |
| **Candidate_C3** | 1 | 11 | 0 | 5 | 0.0833 | 1.00 [0.2065, 1.0] | 0.3125 [0.1416, 0.5560] | 0.1538 | 0.6562 |

*Impact*: Precision collapses to $< 9.1\%$ across all active detecting models; F1 drops below $0.17$.

---

### View 2: Complete Exclusion of Both P1 and P2 (Zero Confirmed Positive Cases)
When both P1 and P2 are excluded due to intra-clause antecedent containment, the test partition contains **0 confirmed positive cases and 16 negative controls**.

Under this condition:
- With zero positive cases in the ground truth ($TP + FN = 0$):
  $$\text{Recall} = \frac{0}{0} \longrightarrow \mathbf{NOT\_ESTIMABLE}$$
  $$\text{Precision} = \frac{0}{0} \longrightarrow \mathbf{NOT\_ESTIMABLE}$$
  $$\text{F1} = \frac{0}{0} \longrightarrow \mathbf{NOT\_ESTIMABLE}$$
  $$\text{Balanced Accuracy} = \frac{\text{Recall} + \text{Specificity}}{2} \longrightarrow \mathbf{NOT\_ESTIMABLE}$$
- Strict positive recall must **never** be reported as $0\%$ or $100\%$; it is fundamentally **NOT_ESTIMABLE**.
- **Specificity Qualifications**:
  While specificity calculations are mathematically estimable, they must be strictly qualified because **none of the 16 negative control cases have been independently adjudicated by qualified legal counsel** (formally marked `NO_EXPERT_ADJUDICATION`):
  - $B_0, B_1, C_1, C_2\text{ (Raw)}$: $\mathbf{0.00\%}$ ($0/16$, 95% CI $[0.0, 0.1936]$) — *Qualified: Complete false-positive failure on unadjudicated negative controls.*
  - $B_2$ (Cosine): $\mathbf{37.50\%}$ ($6/16$, 95% CI $[0.1848, 0.6136]$) — *Qualified: 62.5% false-positive rate on unadjudicated negative controls.*
  - $C_2$ (Reported Underfit): $\mathbf{100.00\%}$ ($16/16$, 95% CI $[0.8064, 1.0]$) — *Qualified: Blind negative classification without sensitivity.*
  - $C_3$ (DAG): $\mathbf{31.25\%}$ ($5/16$, 95% CI $[0.1416, 0.5560]$) — *Qualified: 68.75% false-positive rate on unadjudicated negative controls.*

---

## 3. Scientific Power & Evaluation Limitations

```
+-----------------------------------------------------------------------------------------+
|                              BENCHMARK POWER AUDIT                                      |
+-----------------------------------------------------------------------------------------+
| Test Cases Evaluated: 18 eligible cases (5 parent agreements, 3 corporate families)     |
| Positive Cases Evaluated: N = 2 (derived from 1 single contract, 1 single family)       |
| Effective Positive Sample Size: N_effective = 1 contract family                         |
| Wilson 95% Confidence Interval Span for Recall: [0.3424, 1.0000] (Width: 65.8%)         |
| Wilson 95% Confidence Interval Span for Specificity (B2): [0.1848, 0.6136] (Width: 42.9%)|
| Wilson 95% Confidence Interval Span for Specificity (C3): [0.1416, 0.5560] (Width: 41.4%)|
+-----------------------------------------------------------------------------------------+
```

### Methodological Verdict:
The statistical sample size of the held-out test partition ($N=18$ cases, with only $N=2$ positive cases from a single agreement, both compromised by intra-clause antecedents) is **statistically unpowered to establish reliable model superiority**. Confidence intervals span over 65 percentage points. 

Claims that Candidate C3 has achieved statistically significant or generalizable superiority over production baselines must remain **withdrawn as statistically unpowered**.
