# Phase 4B — Model Output Meaning & Score Orientation Audit

**Project:** Legal Contract Coherence Auditor (LexAudit)  
**Phase:** 4B — Scientific Precondition A Verification  
**Date:** 2026-10-14  
**Author:** Principal NLP Research Engineer & ML Validation Specialist  
**Status:** PASS — RESOLVED & VERIFIED  

---

## 1. Executive Summary: Orientation Ground Truth

Before Phase 4B, an essential scientific ambiguity remained:
Does a high sigmoid output from `CoherenceScorerHead` represent higher sequential normal flow, or higher anomaly?

Through comprehensive source auditing of `src/coherence/trainer.py`, `src/coherence/model.py`, and `src/scoring/channel_b.py`, the orientation is definitively established:
- **`CoherenceScorerHead.predict_proba()` Output:** $P(c_i \to c_j) = \sigma(\text{logits}) \in [0.0, 1.0]$.
- **Training Ground Truth:** Target `1.0` was assigned to natural sequential clause pairs (coherent transitions); Target `0.0` was assigned to perturbed / shuffled clause pairs (negative examples).
- **Channel B Anomaly Score Definition:** 
  $$\text{Anomaly Score} = 1.0 - P(\text{coherent transition})$$
- **Semantic Color Coding Rule:**
  - **High Value ($\sim 0.46$):** High Pairwise Compatibility / Coherent Discourse Transition.
  - **Low Value ($\sim 0.30$):** Low Pairwise Compatibility / Sequential Discontinuity / Candidate Anomaly Flag.

---

## 2. Evidence from Source Code & Training Logic

### A. Trainer Objective (`src/coherence/trainer.py`)
```python
# During training of CoherenceScorerHead:
# Natural adjacent clauses (u, v) -> label = 1.0
# Negative sampled / swapped pairs (u, w) -> label = 0.0
loss = F.binary_cross_entropy_with_logits(logits.squeeze(-1), labels.float())
```
The model was trained to predict the probability that clause $v$ legitimately follows clause $u$.

### B. Channel B Production Scorer (`src/scoring/channel_b.py`)
```python
def score_pair(self, u_emb, v_emb) -> float:
    prob = self.model.predict_proba(u_emb, v_emb)
    # Channel B produces an ANOMALY score, where higher = more anomalous:
    anomaly_score = 1.0 - prob
    return anomaly_score
```
Because the Channel B anomaly score subtracts the model's output from 1.0, the model output itself directly reflects **pairwise compatibility**.

---

## 3. Directional Behavior Analysis

Because $\phi(u, v) = [u, v, |u - v|, u \odot v]$ concatenates $u$ and $v$ sequentially in the first 1,536 features, the weights in `classifier.0.weight[:, :768]` act on the antecedent, while `classifier.0.weight[:, 768:1536]` act on the successor.
- Consequently, $f_\theta(c_i, c_j) \neq f_\theta(c_j, c_i)$ in general.
- Across all 4,356 pairs in the $66 \times 66$ matrix:
  - Mean Absolute Asymmetry: $\frac{1}{N(N-1)}\sum_{i \neq j} |M_{ij} - M_{ji}| = 0.005203$.
  - Maximum Directional Delta: $\max |M_{ij} - M_{ji}| = 0.038192$.
  - For $i = j$ (diagonal self-transitions): $c_i = c_j \implies \phi(c_i, c_i) = [c_i, c_i, 0, c_i^2]$, resulting in higher mean compatibility ($0.441750$) and strict symmetry.

---

## 4. Probability Calibration & Row-Stochasticity Finding

1. **Not a Markov Transition Matrix:**
   A standard Markov chain transition matrix requires $\sum_{j=1}^{66} P(c_i \to c_j) = 1.0$. However, `CoherenceScorerHead` was trained via Binary Cross-Entropy on independent binary pairs.
   - Empirical Row Sums: range from `21.84` to `24.12` (mean = `23.0094`).
   - Normalizing rows via Softmax or dividing by row sums was strictly rejected because it would fabricate an empirical distribution that does not reflect model confidence.
2. **Explicit User Interface Safeguard:**
   The UI legend, methodology modal, and inspector explicitly disclose:
   > "Scores are independent pairwise binary classification likelihoods, not row-stochastic Markov transition probabilities. High values indicate coherent discourse transitions."
