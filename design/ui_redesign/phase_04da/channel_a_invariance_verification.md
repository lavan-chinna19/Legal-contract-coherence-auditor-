# Channel A Permutation Invariance Audit

**Document ID**: `PHASE_04DA_CHANNEL_A_INVARIANCE`  
**Auditor**: ML Research Auditor & Legal NLP Scientist  
**Scope**: Source Inspection, Mathematical Invariance Hypothesis, and Empirical Verification  

---

## 1. Executive Summary

Phase 4D claimed that Channel A (Semantic Out-Of-Distribution Anomaly Scorer) is mathematically permutation invariant under clause reordering:
$$\Delta S_A = 0.0000$$

This audit independently investigated the complete Channel A codebase and confirms:
1. **The mathematical hypothesis is VERIFIED**:
   $$A(c_i \mid D) = A(c_i \mid \pi(D))$$
   where $\pi(D)$ is any permutation of document $D$ that preserves the verbatim text of each clause $c_i$.
2. **Channel A is intentionally designed for semantic novelty, not structural sequence coherence.**
   It measures whether a clause's semantic topic belongs to the expected legal contract distribution (using Legal-BERT embeddings and LEDGAR centroids). It does not model discourse flow or clause transitions.
3. **Zero sensitivity to clause permutations is an expected architectural property**, not an implementation bug or model defect.

---

## 2. Source-Level Mathematical Verification

An audit of [`src/scoring/channel_a.py`](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/src/scoring/channel_a.py) and [`src/embeddings/frozen.py`](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/src/embeddings/frozen.py) confirms the following properties:

### A. Context Independence of Clause Embeddings
- In [`src/embeddings/frozen.py::embed_clauses`](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/src/embeddings/frozen.py#L45-L75), each clause is tokenized and embedded individually:
  ```python
  inputs = self.tokenizer(
      [c.text for c in clauses],
      padding=True,
      truncation=True,
      max_length=self.max_length,
      return_tensors="pt"
  )
  ```
- **Finding**: No cross-clause attention or document-level recurrent state is used during embedding generation. Clause embedding $e_i = \text{Embed}(c_i.\text{text})$ depends strictly and exclusively on the verbatim text of clause $c_i$.

### B. Centroid Distance Invariance
- In [`src/scoring/channel_a.py::score_clauses`](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/src/scoring/channel_a.py#L112-L125):
  ```python
  norms = np.linalg.norm(clause_embs, axis=1, keepdims=True) + 1e-9
  clause_embs_norm = clause_embs / norms
  cos_sim = np.dot(clause_embs_norm, self.centroid_matrix.T)
  ```
- **Finding**: Normalization is performed along `axis=1` (per-clause vector norm). No batch-wide or document-level normalizations exist. Centroid matrix $M$ is static and frozen. Therefore, the cosine similarity between $e_i$ and each centroid $m_k$ is strictly identical regardless of $c_i$'s sequence index in the contract.

### C. Exclusion of Rule Checks
- Rule-based flags (cross-references, date logic) are computed in completely separate modules (`src/rules/`) and are never passed to or mixed into Channel A.

---

## 3. Empirical Verification Across All 6 Structural Cases

To verify that floating-point operations or aggregation orders do not introduce numerical jitter, per-clause Channel A scores were compared before and after transformation by **STABLE CLAUSE ID** across all 6 structural cases (66 clause instances in `SYNTH_DOC_01_MSA`):

| Scenario ID | Perturbation Type | Clauses Evaluated | Max Absolute Delta ($\|A^{\text{orig}} - A^{\text{pert}}\|$) | Invariance Confirmed |
| :--- | :--- | :--- | :--- | :--- |
| `SCEN_P1_01_DISP_DISTANT` | Distant Displacement (Slot 1 $\to$ Slot 10) | 11 | $0.000000$ | YES |
| `SCEN_P1_02_DISP_MODERATE` | Moderate Displacement (Slot 5 $\to$ Slot 2) | 11 | $0.000000$ | YES |
| `SCEN_P1_03_DISP_SUBTLE` | Subtle Displacement (Slot 3 $\to$ Slot 4) | 11 | $0.000000$ | YES |
| `SCEN_P2_01_SWAP_ADJACENT` | Adjacent Swap (Slot 0 $\leftrightarrow$ Slot 1) | 11 | $0.000000$ | YES |
| `SCEN_P2_02_SWAP_DISTANT` | Distant Swap (Slot 2 $\leftrightarrow$ Slot 8) | 11 | $0.000000$ | YES |
| `SCEN_P2_03_SWAP_SUBTLE` | Subtle Swap (Slot 4 $\leftrightarrow$ Slot 6) | 11 | $0.000000$ | YES |

**Maximum Delta Across All 66 Comparisons**: **$0.000000$** (exact floating-point identity).

---

## 4. Evaluation Implications for Phase 4D-A

1. **Channel A Invariance is Verified**:
   The claim made in Phase 4D that Channel A is mathematically invariant under clause permutations is fully verified.
2. **Channel A Dilution Effect**:
   Because Channel A outputs $0.0000$ for standard legal clauses, and because the combined ensemble score is $S = 0.5 A + 0.5 B$, Channel A halves the magnitude of any transition break registered by Channel B:
   $$\Delta S = 0.5 \cdot \Delta S_B$$
   This means that for Channel B to push a combined score from $0.34$ to the $0.50$ Medium severity threshold, Channel B alone would need to shift by:
   $$\Delta S_B \ge \frac{0.50 - 0.34}{0.5} = +0.3200$$
   An enormous shift that the frozen coherence classifier cannot produce given its compressed dynamic range ($\Delta S_B \le 0.0152$).
3. **Conclusion**:
   Structural detection capability must be evaluated against Channel B alone or through dedicated sequence models. Expecting Channel A to respond to clause reordering is scientifically invalid.
