# LexAudit Research — Scoring Objective Definition & Theoretical Rationale
<!-- Reference copy for research archive -->

## 1. Selected Primary Objective: Whole-Document Mean Combined Anomaly
$$J(D^{(p)}) = \frac{1}{N} \sum_{i=0}^{N-1} \left[ 0.5 \cdot S_A(c_i^{(p)}) + 0.5 \cdot S_B(c_i^{(p)}) \right]$$

## 2. Improvement Metric
$$\Delta J(p) = J(D^{\text{orig}}) - J(D^{(p)})$$
Positive $\Delta J$ indicates an overall reduction in document-level anomaly.

## 3. Rationale for Pre-Registering this Objective
- Directly matches production `/v1/analyze` document-level metric.
- Incorporates boundary clause weighting ($1.5\times$ on boundary edges vs $1.0\times$ on interior edges).
- Penalizes collateral damage when an insertion destroys a strong existing transition.
- Pre-registered prior to running synthetic displacement benchmarks to avoid p-hacking or metric shopping.
