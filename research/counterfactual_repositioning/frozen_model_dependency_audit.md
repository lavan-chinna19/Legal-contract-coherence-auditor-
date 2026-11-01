# LexAudit Research — Frozen Model Dependency Audit
<!-- Reference copy for research archive -->

## 1. Scope
Formal dependency audit of the frozen neural coherence model and scoring pipeline for counterfactual clause repositioning.

## 2. Model & Pipeline Specifications
- **Embedding Pipeline**: `nlpaueb/legal-bert-base-uncased`, mean pooling over non-pad subwords, unit L2 normalization $\in \mathbb{R}^{768}$.
- **Channel A**: Cosine distance to 110 LEDGAR topic centroids. Position invariant: $\forall \pi \in S_N, \sum_i S_A(c_{\pi(i)}) = \sum_i S_A(c_i)$.
- **Channel B**: Multi-layer perceptron on pairwise features $[u, v, |u-v|, u \odot v] \in \mathbb{R}^{3072}$.
  - Architecture: Linear(3072, 256) -> GELU -> Linear(256, 64) -> GELU -> Linear(64, 1) -> Sigmoid.
  - Anomaly: $A(u, v) = 1.0 - \sigma(\text{logit})$.
- **Boundary Conditions**:
  - $S_B(c_0) = A(c_0, c_1)$
  - $S_B(c_{N-1}) = A(c_{N-2}, c_{N-1})$
  - $S_B(c_i) = \frac{1}{2}[A(c_{i-1}, c_i) + A(c_i, c_{i+1})]$ for $0 < i < N-1$.
- **Combined Aggregation**:
  $$\text{Combined}(c_i) = 0.5 \cdot S_A(c_i) + 0.5 \cdot S_B(c_i)$$
  $$J(D) = \frac{1}{N} \sum_{i=0}^{N-1} \text{Combined}(c_i)$$
- **Parity Implication**: Optimization must track boundary clause weights (1.5x) versus internal clause weights (1.0x) to maintain exact floating-point equivalence with production pipelines.
