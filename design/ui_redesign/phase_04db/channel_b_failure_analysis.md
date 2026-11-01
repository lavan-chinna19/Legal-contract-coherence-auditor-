# Channel B Coherence Head Failure Analysis & Mathematical Diagnosis

**Audit Program**: LexAudit Research Extension — Phase 4D-B  
**Document ID**: `PHASE_04DB_CH_B_FAILURE_ANALYSIS`  
**Date**: October 22, 2026  
**Auditor**: Principal Legal NLP Research Scientist & Machine Learning Architect  
**Scope**: In-Depth Technical Breakdown of Channel B Structural Blindness  

---

## 1. Architectural Architecture & Design Specification

Channel B is implemented via `FineTunedCoherenceModel` (`src/coherence/fine_tuned.py`) wrapping `CoherenceScorerHead` (`src/coherence/model.py`):

1. **Backbone**: Frozen `nlpaueb/legal-bert-base-uncased` (768-dimensional sentence embeddings pooled from token hidden states).
2. **Pair Feature Representation**: For adjacent clauses $(u, v) \in \mathbb{R}^{768} \times \mathbb{R}^{768}$, features are constructed as:
   $$x_{(u, v)} = [u \,\|\, v \,\|\, |u - v| \,\|\, u \odot v] \in \mathbb{R}^{3072}$$
3. **Classification MLP**:
   - `Linear(3072, 256)` $\to$ `LayerNorm(256)` $\to$ `ReLU()` $\to$ `Dropout(0.2)`
   - `Linear(256, 64)` $\to$ `ReLU()` $\to$ `Dropout(0.1)`
   - `Linear(64, 1)` $\to$ `Sigmoid()` $\to P(c_i \to c_{i+1}) \in [0.0, 1.0]$
4. **Anomaly Inversion**: $A(c_i \to c_{i+1}) = 1.0 - P(c_i \to c_{i+1})$.
5. **Clause-Level Aggregation**:
   $$S_B(c_i) = \begin{cases} 
   A(c_0 \to c_1) & i = 0 \\
   \max(A(c_{i-1} \to c_i), A(c_i \to c_{i+1})) & 0 < i < n - 1 \\
   A(c_{n-2} \to c_{n-1}) & i = n - 1 
   \end{cases}$$

---

## 2. Training Lineage & Historical Optimization Limits

Authoritative training metadata preserved in `fixtures/coherence_training_curves.json` reveals the root limitations of the frozen model:

- **Dataset Size**: Trained on only **894 total pairs** (716 train pairs, 178 validation pairs).
- **Training Epochs**: 12 epochs with Adam optimizer ($lr = 0.001$, batch size 32).
- **Severe Class Imbalance**: In epochs 1–4, validation accuracy remained locked at $0.6854$ while precision and recall were $0.0000$, indicating that approximately $68.5\%$ of the validation pairs were negative instances.
- **Peak Validation Performance**: Best validation ROC-AUC was **$0.6345$** (Epoch 6) and best F1 was **$0.4967$** (Epoch 8).
- **Generalization Gap**: Training loss dropped from $0.6441 \to 0.3957$, while validation loss degraded from $0.6190 \to 0.7201$, demonstrating clear parameter overfitting on the tiny 716-pair training set.

---

## 3. The Four Mathematical Failure Mechanisms

### Failure Mechanism 1: Logit Compression & Probability Saturation
On standard commercial contract fixtures, the raw logits $z = W_3 h_2 + b_3$ produced by the MLP head cluster tightly in the negative region:
$$z \in [-0.799, -0.668]$$
Applying the sigmoid activation yields:
$$P(c_i \to c_{i+1}) = \sigma(z) \in [0.3102, 0.3389]$$
This results in an anomaly score band of:
$$A(c_i \to c_{i+1}) = 1 - P \in [0.6611, 0.6898]$$
**Total dynamic range across all 60 evaluated transitions is only $0.0287$**. The model cannot express high certainty of coherence ($P > 0.60$) or severe structural incoherence ($P < 0.15$).

### Failure Mechanism 2: Pairwise Proxy Objective vs Document Discourse
The model was trained strictly on isolated binary pairs $(c_i, c_{i+1})$. 
- It has **zero awareness of global document position** (whether a clause appears at 5% or 95% of the text).
- It has **zero awareness of surrounding contextual flow** beyond the immediate neighbor.
- When Section 2 (Scope) is moved to Slot 10 (after Section 10 / before Exhibit A), the newly created pair `(Section 10, Section 2)` has semantic similarity and legal topicality comparable to any other inter-clause pair in a business agreement. The pairwise MLP simply evaluates generic legal semantic compatibility, not whether Scope belongs before Payment.

### Failure Mechanism 3: Production Threshold Disconnect
The production decision engine (`SeverityRanker`) enforces:
- `MED_THRESHOLD = 0.50` (on composite score $S$)
- `MED_SINGLE_THRESHOLD = 0.70` (on single-channel $S_B$)
Because Channel B maxes out at $0.6898$ on synthetic contracts, **it is mathematically impossible for Channel B alone to trigger an anomaly detection** ($0.6898 < 0.7000$).
And because Channel A produces $S_A = 0.0000$ for in-distribution clauses, the composite score:
$$S = 0.5 \cdot 0.0000 + 0.5 \cdot 0.6898 = 0.3449$$
which is strictly below the `LOW_THRESHOLD` of $0.3500$, categorizing 100% of clauses into the `CLEAN` tier.

### Failure Mechanism 4: Negligible Delta Under Extreme Displacement
Across the canonical structural benchmark:
- `SCEN_P1_01_DISP_DISTANT` (Scope moved 9 slots to the end): Max $\Delta S_B = -0.0096$ (transition actually appeared slightly *more* compatible).
- `SCEN_P1_02_DISP_MODERATE` (Term moved 3 slots earlier): Max $\Delta S_B = -0.0037$.
- `SCEN_P1_03_DISP_SUBTLE` (IP moved 1 slot): Max $\Delta S_B = +0.0085$.
- `SCEN_P2_01_SWAP_ADJACENT` (Preamble $\leftrightarrow$ Scope): Max $\Delta S_B = +0.0152$ (largest observed shift).
- `SCEN_P2_02_SWAP_DISTANT` (Payment $\leftrightarrow$ Gov Law): Max $\Delta S_B = +0.0100$.
- `SCEN_P2_03_SWAP_SUBTLE` (Conf $\leftrightarrow$ Indemn): Max $\Delta S_B = +0.0033$.

A maximum score shift of **$+0.0152$** is completely lost in background variance and is over $23\times$ smaller than what is required to cross the production threshold gap ($0.5000 - 0.3449 = 0.1551$).

---

## 4. Architectural Requirements for Improvement

To overcome these structural limitations, an improved method must introduce:
1. **Contextual Normalization & Contrast**: Evaluating how an edge transition compares to the contract's own baseline distribution rather than relying on an uncalibrated absolute threshold.
2. **Context Window & Document Sequence Awareness**: Modeling sequence order over a multi-clause window or directed structural graph.
3. **Clear Anomaly Separation**: Ensuring that genuine structural ordering defects produce statistically separable signals from standard canonical flow.
