# LexAudit Phase 4A — Learned Normal-Flow Model Architecture Audit

## 1. Executive Summary & Required Classification Decision

### Mandatory Architecture Decision
**DECISION**: `MATRIX_RECONSTRUCTION_POSSIBLE_WITH_EXISTING_ARTIFACTS`

### Decision Rationale
1. **No Explicit Discrete Matrix in Checkpoint**: Inspection of `models/coherence_classifier.pt` confirms that the checkpoint contains only the weights of a continuous multi-layer perceptron (`CoherenceScorerHead`):
   - `classifier.0.weight`: `torch.Size([256, 3072])`, `bias`: `torch.Size([256])`
   - `classifier.4.weight`: `torch.Size([64, 256])`, `bias`: `torch.Size([64])`
   - `classifier.7.weight`: `torch.Size([1, 64])`, `bias`: `torch.Size([1])`
   An explicit discrete Markov transition matrix $T \in \mathbb{R}^{K \times K}$ is **not stored directly** in the checkpoint or repository.
2. **Reconstruction Feasibility Without Retraining**: However, `fixtures/ledgar_centroids.npz` provides 66 canonical clause-type centroid vectors $C_k \in \mathbb{R}^{768}$. By computing pairwise representations $[C_i, C_j, |C_i - C_j|, C_i \cdot C_j] \in \mathbb{R}^{3072}$ for all $66 \times 66 = 4,356$ pairs and executing a single vectorized forward pass through the frozen `CoherenceScorerHead`, a deterministic, learned clause-type transition matrix can be fully reconstructed offline without any model retraining or access to private training data.
3. **Scientific Integrity**: Because the current production backend scores continuous sentence embeddings rather than lookup indices, claiming that the runtime engine operates via a discrete transition matrix is mathematically incorrect.

---

## 2. Channel B Mathematical Formulation & Pipeline Inspection

### 2.1 Feature Representation
As implemented in [src/coherence/model.py](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/src/coherence/model.py):
Given clause $u \in \mathbb{R}^{768}$ and successor clause $v \in \mathbb{R}^{768}$ extracted via frozen Legal-BERT:
$$\phi(u, v) = [u, \; v, \; |u - v|, \; u \odot v] \in \mathbb{R}^{3072}$$

### 2.2 Neural Architecture (`CoherenceScorerHead`)
```
Input: phi(u, v) in R^3072
  │
  ▼
Linear(3072 -> 256) + ReLU + Dropout(0.2)
  │
  ▼
Linear(256 -> 64) + ReLU + Dropout(0.1)
  │
  ▼
Linear(64 -> 1)
  │
  ▼
Sigmoid -> P(u -> v) in [0.0, 1.0]
```

### 2.3 Scoring Mechanism
As implemented in [src/scoring/channel_b.py](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/src/scoring/channel_b.py):
1. **Consecutive Transition Probabilities**:
   For document clause sequence $(c_0, c_1, \dots, c_{N-1})$:
   $$P_{trans}(i) = P(c_i \to c_{i+1}), \quad \text{for } i \in [0, N-2]$$
2. **Discontinuity Anomaly**:
   $$A_{trans}(i) = 1.0 - P_{trans}(i) \in [0.0, 1.0]$$
3. **Clause-Level Synthesis**:
   For interior clause $c_i$ ($0 < i < N-1$):
   - $\text{Incoming Anomaly } A_{in} = 1.0 - P(c_{i-1} \to c_i)$
   - $\text{Outgoing Anomaly } A_{out} = 1.0 - P(c_i \to c_{i+1})$
   - Combined Channel B Score:
     $$S_B(i) = \max(A_{in}, A_{out}) \quad \text{or} \quad \frac{A_{in} + A_{out}}{2}$$
4. **Boundary Clauses**:
   - Initial clause $c_0$: Has no predecessor. $A_{in} = 0.0$, $S_B(0) = A_{out}$.
   - Terminal clause $c_{N-1}$: Has no successor. $A_{out} = 0.0$, $S_B(N-1) = A_{in}$.

---

## 3. Training Corpus & Vocabulary Provenance
- **Reference Corpus**: LEDGAR dataset (SEC contract filings).
- **Clause Vocabulary**: 66 canonical legal clause categories (e.g., `Term`, `Termination`, `Confidentiality`, `Governing Law`, `Severability`, `Indemnification`, `Assignment`, `Notices`, `Representations and Warranties`).
- **Centroids Artifact**: `fixtures/ledgar_centroids.npz` (contains 66 vectors of shape `(768,)` corresponding to mean Legal-BERT embeddings for each cluster).
- **Pair Sampler**: Implemented in `src/coherence/pair_sampler.py`. Generates positive pairs $(c_t, c_{t+1})$ from continuous SEC filing sections, and negative pairs via intra-document swaps and cross-document random clause pairs.

---

## 4. Probabilistic Nature of Transition Scores
- **Binary Classification Likelihood, NOT a Markov Chain**:
  Each transition $P(u \to v)$ is estimated via logistic sigmoid $\sigma(\cdot)$ as an independent binary classification probability.
  $$\sum_{j=1}^K P(C_i \to C_j) \neq 1.0$$
  The row sums over all successor clause types do **not** equal 1.0 because the model was trained with binary cross-entropy, not softmax over a categorical transition vocabulary.
- **Scientific Implication**:
  Presenting Channel B as a Markov Transition Matrix without explicit disclosure would be technically misleading. Future visualizations must label reconstructed matrices as **Pairwise Coherence Compatibility** rather than Markov transition probabilities.
