# LexAudit Phase 4C-A — Benchmark Consistency Correction & Investigation Report

## 1. Executive Summary & Root Cause Analysis

### The Discrepancy
In the initial narrative of the Phase 4C-A audit report, Section J listed the following nine individual case ranks:
$$\text{Reported text list: } [1, 3, 2, 2, 2, 1, 4, 3, 1]$$
As correctly identified during review, this list mathematically implies:
- $\text{Top-1 Recovery} = 3/9 = 33.33\%$
- $\text{Top-3 Recovery} = 8/9 = 88.89\%$ (since 8 out of 9 ranks are $\le 3$)
- $\text{MRR} = \frac{1}{9}(1 + \frac{1}{3} + \frac{1}{2} + \frac{1}{2} + \frac{1}{2} + 1 + \frac{1}{4} + \frac{1}{3} + 1) = \frac{5.4167}{9} \approx 0.6019$
- $\text{Mean Rank} = \frac{1 + 3 + 2 + 2 + 2 + 1 + 4 + 3 + 1}{9} = \frac{19}{9} \approx 2.11$

However, the report's aggregate summary claimed:
- $\text{Top-1 Recovery} = 3/9 = 33.33\%$
- $\text{Top-3 Recovery} = 7/9 = 77.78\%$
- $\text{MRR} = 0.5448$
- $\text{Mean Rank} = 3.33$

### Root Cause Determination
An exhaustive audit of the repository's authoritative experimental data was conducted across:
1. Original Phase 4C execution artifact: `design/ui_redesign/phase_04c/position_recovery_results.json`
2. Independent Phase 4C-A reproduction data: `design/ui_redesign/phase_04ca/benchmark_case_level_results.csv`
3. Benchmark evaluation script: `scripts/run_synthetic_recovery_benchmark.py`

**Finding**:
The actual per-case true-position ranks in both authoritative source files were, and remain:
$$\mathbf{Authoritative\ Ranks:\ } [8, 1, 2, 1, 9, 3, 3, 1, 2]$$

The sequence $[1, 3, 2, 2, 2, 1, 4, 3, 1]$ was an **isolated textual transcription hallucination** in the assistant's narrative markdown text of Section J. It never existed in `position_recovery_results.json` or `benchmark_case_level_results.csv`.
The reported aggregate metrics (Top-1 = 3/9, Top-3 = 7/9, MRR = 0.5448, Mean Rank = 3.33) were **100% mathematically correct derivations from the true underlying ranks $[8, 1, 2, 1, 9, 3, 3, 1, 2]$**.

---

## 2. Authoritative Case-by-Case Breakdown

The 9 held-out evaluation contracts and their exact ranks under the frozen neural scorer and baseline models are:

| Case | Document ID | Length ($N$) | Target Clause | Displaced ($d$) $\to$ True ($s$) | Scorer Rank | Scorer RR | Cosine Rank | Cosine RR | Paired Delta |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **C-01** | `0001493152_23_045259_EX-10_14` | 28 | Clause 21 | $3 \to 21$ | **8** | 0.1250 | 8 | 0.1250 | $0.0000$ |
| **C-02** | `0001558370_23_019889_EX-10_41` | 6 | Clause 1 | $5 \to 1$ | **1** | 1.0000 | 4 | 0.2500 | $+0.7500$ |
| **C-03** | `0001558370_23_019889_EX-10_42` | 9 | Clause 3 | $1 \to 3$ | **2** | 0.5000 | 2 | 0.5000 | $0.0000$ |
| **C-04** | `0001558370_23_019889_EX-10_43` | 17 | Clause 4 | $2 \to 4$ | **1** | 1.0000 | 2 | 0.5000 | $+0.5000$ |
| **C-05** | `0001558370_23_019892_EX-10_88` | 13 | Clause 2 | $11 \to 2$ | **9** | 0.1111 | 6 | 0.1667 | $-0.0556$ |
| **C-06** | `0001558370_23_020000_EX-10_26` | 15 | Clause 2 | $12 \to 2$ | **3** | 0.3333 | 4 | 0.2500 | $+0.0833$ |
| **C-07** | `0001558370_23_020000_EX-10_30` | 19 | Clause 14 | $1 \to 14$ | **3** | 0.3333 | 1 | 1.0000 | $-0.6667$ |
| **C-08** | `0001802974_23_000037_EX-10_18` | 5 | Clause 1 | $3 \to 1$ | **1** | 1.0000 | 3 | 0.3333 | $+0.6667$ |
| **C-09** | `0001802974_23_000037_EX-10_24` | 15 | Clause 4 | $6 \to 4$ | **2** | 0.5000 | 2 | 0.5000 | $0.0000$ |

---

## 3. Mathematical Recalculation & Proof

### Primary Frozen Model
1. **Top-1 Count & Rate**:
   - Ranks equal to 1: Cases C-02, C-04, C-08 $\implies \mathbf{3\text{ cases}}$.
   - $\text{Top-1} = \frac{3}{9} = \mathbf{0.3333\ (33.33\%)}$.
   - $95\%\text{ Bootstrap CI: } [0.0000, 0.6667]$.
2. **Top-3 Count & Rate**:
   - Ranks $\le 3$: Cases C-02 (1), C-03 (2), C-04 (1), C-06 (3), C-07 (3), C-08 (1), C-09 (2) $\implies \mathbf{7\text{ cases}}$.
   - Non-Top-3 cases: Case C-01 (Rank 8) and Case C-05 (Rank 9) $\implies 2\text{ cases}$.
   - $\text{Top-3} = \frac{7}{9} = \mathbf{0.7778\ (77.78\%)}$.
   - $95\%\text{ Bootstrap CI: } [0.4444, 1.0000]$.
3. **Mean Reciprocal Rank (MRR)**:
   - Sum of Reciprocal Ranks:
     $$\sum_{i=1}^9 \frac{1}{\text{rank}_i} = \frac{1}{8} + 1 + \frac{1}{2} + 1 + \frac{1}{9} + \frac{1}{3} + \frac{1}{3} + 1 + \frac{1}{2} = 4.902778$$
   - $\text{MRR} = \frac{4.902778}{9} = \mathbf{0.544753... \approx 0.5448}$.
   - $95\%\text{ Bootstrap CI: } [0.3287, 0.7731]$.
4. **Mean Rank**:
   - $\text{Mean Rank} = \frac{8 + 1 + 2 + 1 + 9 + 3 + 3 + 1 + 2}{9} = \frac{30}{9} = \mathbf{3.3333... \approx 3.33}$.
5. **Median Rank**:
   - Sorted ranks: $[1, 1, 1, 2, \mathbf{2}, 3, 3, 8, 9] \implies \mathbf{2.0}$.

### Paired Baseline Comparisons

| Metric | Primary Frozen Scorer | Cosine Heuristic | Random Insertion | Identity (No Movement) |
| :--- | :---: | :---: | :---: | :---: |
| **Top-1** | **33.33% (3/9)** | 11.11% (1/9) | 9.28% | 0.00% |
| **Top-3** | **77.78% (7/9)** | 55.56% (5/9) | 27.84% | 0.00% |
| **MRR** | **0.5448** | 0.4028 | 0.2662 | 0.0000* |
| **Mean Rank** | **3.33** | 3.56 | 6.42 | N/A |
| **Median Rank** | **2.0** | 3.0 | 5.0 | N/A |
| **Paired RR Delta vs Cosine** | — | $+0.1420$ | $+0.2785$ | N/A |
| **Paired 95% Bootstrap CI** | — | $[-0.1328, +0.4105]$ | $[+0.0528, +0.5143]$ | N/A |

*Scientific Note on Uncertainty*:  
The neural scorer outperforms the Cosine Heuristic by $+35.3\%$ in MRR ($+0.1420$). However, because the paired 95% bootstrap confidence interval crosses zero ($[-0.1328, +0.4105]$), the superiority is **directionally positive but not statistically proven at $p < 0.05$** due to the $N=9$ sample size constraint.

---

## 4. Tie Handling, Abstention & Exclusion Review

1. **Candidate Tie Handling**:
   - In `CounterfactualRepositioningEngine`, sorting is performed by `(mean_combined_score, clause_channel_b_score)`.
   - In all 9 displacement trials, the true position slot had distinct scores from adjacent positions; no tie-breaking ambiguity affected the rank of the true slot.
2. **Multi-Candidate Tie Abstention**:
   - In negative controls (unperturbed original contracts), Case 1 (`..._14`) encountered tied candidates within $1\text{e-}4$. The engine correctly abstained under `MULTI_CANDIDATE_OBJECTIVE_TIE`.
3. **Excluded Positions**:
   - In the benchmark protocol, candidate positions include all valid insertion slots $p \in \{0, \dots, N-1\}$. None were excluded.

---

## 5. Architectural Clarification: `min_delta_threshold = 0`

### Research Exploratory vs. Server Operational Policy
The request schema allows `min_delta_threshold: float = Field(0.005, ge=0.0, le=1.0)`.
A question was raised: *Does `min_delta_threshold = 0` intentionally support exploratory behavior, or can it bypass server-enforced recommendation safety?*

1. **Exploratory Behavior**:
   - Setting `min_delta_threshold = 0.0` is an intentional **research/exploratory mode** supported exclusively on the experimental route (`POST /v1/experimental/reposition`).
   - It allows research scientists and auditors to observe raw candidate rankings and unthresholded score deltas without filtering.
2. **Safety Risk if Used in Production**:
   - When $\delta = 0.0$, any alternative candidate with $\Delta J > 0.0$ triggers `is_recommended = True`.
   - In unperturbed negative controls, 5 of 9 clean contracts exhibited marginal alternative deltas ($\Delta J \in [0.0002, 0.0013]$) due to slight embedding variances.
   - At $\delta = 0.0$, these 5 clean contracts would be falsely flagged for repositioning (a **55.6% false repair rate**).
3. **Server-Enforced Operational Policy Decoupling**:
   - A client-supplied threshold **must not** control operational contract mutation.
   - For any future production recommendation workflow, the server must decouple:
     - **Diagnostic Exposure**: Expose raw deltas and client-requested exploratory thresholds.
     - **Server Operational Policy**: Server must enforce a hard minimum policy floor (e.g., $\delta_{\text{min}} \ge 0.0025$) for official recommendations.

---

## 6. Automated Consistency Regression Test

To prevent future regression or narrative divergence between case-level results and aggregate reports, an automated pytest suite was added:
`tests/test_benchmark_consistency.py`

This suite performs 4 automated assertions:
1. `test_case_level_data_integrity`: Verifies `benchmark_case_level_results.csv` matches authoritative ranks $[8, 1, 2, 1, 9, 3, 3, 1, 2]$ exactly.
2. `test_aggregate_metrics_mathematical_derivation`: Directly recomputes Top-1, Top-3, MRR, Mean Rank, and Median Rank from the CSV and asserts exact equivalence with `benchmark_metric_recalculation.json`.
3. `test_paired_baseline_consistency`: Asserts paired diffs vs Cosine Heuristic equal $+0.1420$ and confirms bootstrap CI crosses zero.
4. `test_negative_control_abstention_consistency`: Confirms all 9 negative controls abstain under the default 0.005 threshold.

Execution Result: **4 passed in 3.52s**.
