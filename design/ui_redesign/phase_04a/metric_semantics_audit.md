# LexAudit Phase 4A — Scientific Metric Semantics Audit & Mathematical Validation

## 1. Metric Definition & Semantic Truth Table

| Metric | Source Formulation | Mathematical Domain | Denominator / Reference | Semantic Meaning | Common Misinterpretations (Prohibited in UI) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Anomaly Rate** | $\frac{\text{ml\_anomaly\_count}}{\text{total\_clauses}}$ | $[0.0\%, 100.0\%]$ | Total parsed clauses in document $N$ | Fraction of clauses exceeding calibrated anomaly threshold $\tau$. | **NOT** "Legal error rate" or "Contract risk probability". |
| **Document Mean Combined Score** | $\frac{1}{N} \sum_{i=1}^N S_i$ | $[0.000, 1.000]$ | $N$ clauses | Average combined anomaly across all clauses. Equal weights $w_A=0.5, w_B=0.5$. | **NOT** a clause-level threshold or overall contract safety score. |
| **Centroid Distance ($d$)** | $1.0 - \frac{u \cdot c_k}{\|u\|_2 \|c_k\|_2}$ | $[0.000, 2.000]$ | Unit sphere in $\mathbb{R}^{768}$ | Cosine distance from Legal-BERT clause embedding to nearest LEDGAR cluster centroid. | **NOT** a probability, confidence percentage, or quality score. |
| **Discourse Transition Probability ($P$)** | $\sigma(\text{MLP}([u, v, |u-v|, u \cdot v]))$ | $[0.000, 1.000]$ | Binary coherence classifier | Probability that clause $v$ legitimately follows clause $u$ under trained model. | **NOT** a probability of grammatical or legal correctness. |
| **Transition Anomaly ($S_B$)** | $1.0 - P(\text{transition})$ | $[0.000, 1.000]$ | Complement of $P$ | Degree of sequential disruption between adjacent clauses. | **NOT** a missing clause detector. |
| **Conformal Prediction Interval** | $[\hat{S} - \hat{q}, \hat{S} + \hat{q}] \cap [0, 1]$ | $[0.000, 1.000]$ | Split-conformal calibration residuals | Interval guaranteeing $1 - \alpha = 90\%$ marginal coverage over synthetic permutations. | **NOT** a guarantee of human lawyer agreement or legal certainty. |

---

## 2. Cross-Channel Scale & Metric Incompatibility Proof
Channel A and Channel B must never be plotted on a shared vertical axis or combined without calibrated normalization weights:
1. **Physical Scale**:
   - Channel A centroid distance is a unbounded geometrical cosine distance in $[0, 2]$.
   - Channel B is a sigmoidal output in $[0, 1]$.
2. **Distributional Shape**:
   - In LEDGAR baseline contracts, in-distribution centroid distances cluster around $0.20 - 0.45$. A distance of $0.50$ is already an extreme outlier.
   - For Channel B, normal sequential transitions frequently exhibit probabilities $P \ge 0.70$ ($S_B \le 0.30$), while transitions across disparate sections drop to $P \le 0.10$ ($S_B \ge 0.90$).
3. **UI Enforcement**:
   `ChannelEvidenceComparison.tsx` provides independent, clearly labeled diagnostic panels with explicit metric family and unit annotations.

---

## 3. Severity Distribution Sum Consistency
- **Validation Law**: For any document with $N$ clauses:
  $$\text{Total Clauses} = \text{Count}(\text{HIGH}) + \text{Count}(\text{MEDIUM}) + \text{Count}(\text{LOW}) + \text{Count}(\text{CLEAN})$$
- In the backend report, `high_severity_count` and `medium_severity_count` are populated directly from threshold comparisons ($S_i \ge 0.65$ and $0.40 \le S_i < 0.65$).
- In `SeverityDistribution.tsx`, `cleanCount` is evaluated as $\max(0, N - (\text{high} + \text{med} + \text{low}))$, ensuring 100.0% conservation of total clause counts across both the segmented bar and the accessible summary table.

---

## 4. Separation of Rule Violations vs. ML Anomalies
- Deterministic rule checks (in `src/rules/`) evaluate static heuristics:
  - Dangling cross-references (e.g. references to Section 14 when only 8 sections exist)
  - Broken exhibit references
  - Inverted chronological dates (effective date after termination date)
- ML scoring evaluates statistical Legal-BERT representation shifts.
- **Rule violations are separate and distinct from `ml_anomaly_count`**.
- Both are reported independently in `AnalyticsSummary` and `RuleFindingsSummary`.

---

## 5. Numerical Formatting and Missing Value Safeguards
- All floating-point numbers are rounded **strictly at the visual presentation layer** (`toFixed(3)` or `toFixed(4)`).
- Internal state retains full double-precision numbers.
- Missing or null scores are handled explicitly (e.g., boundary clauses where $P_{in}$ is undefined display `"First Clause (Bound)"` rather than converting `null` to `0.000`).
