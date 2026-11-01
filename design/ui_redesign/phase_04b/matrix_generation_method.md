# Phase 4B — Track A Offline Matrix Generation Methodology

**Project:** Legal Contract Coherence Auditor (LexAudit)  
**Phase:** 4B — Learned Clause-Pair Compatibility Map  
**Date:** 2026-10-14  
**Author:** Principal NLP Research Engineer & ML Validation Specialist  
**Status:** PASS — REPRODUCIBLE & VERIFIED  

---

## 1. Generation Pipeline Overview

The learned clause-pair compatibility matrix was computed offline using a deterministic generation script:
- **Generation Script:** `scripts/generate_compatibility_matrix.py`
- **Output Artifact:** `frontend/public/research/learned_clause_pair_compatibility.json`
- **Total Dimensions:** $66 \times 66 = 4,356$ ordered clause-type pairs.
- **Runtime Environment:** CPU inference, PyTorch evaluation mode (`torch.no_grad()`, `model.eval()`).

---

## 2. Mathematical Algorithm

For each ordered pair $(i, j) \in \{0, \dots, 65\}^2$:
1. Retrieve reference centroid vectors $c_i, c_j \in \mathbb{R}^{768}$ from `fixtures/ledgar_centroids.npz`.
2. Construct the 3,072-dimensional feature vector:
   $$\phi(c_i, c_j) = [c_i, c_j, |c_i - c_j|, c_i \odot c_j] \in \mathbb{R}^{3072}$$
3. Perform forward inference through the frozen `CoherenceScorerHead`:
   $$z_1 = \text{ReLU}(W_1 \phi + b_1) \in \mathbb{R}^{256}$$
   $$z_2 = \text{ReLU}(W_2 z_1 + b_2) \in \mathbb{R}^{64}$$
   $$M_{ij} = \sigma(W_3 z_2 + b_3) \in [0.0, 1.0]$$
4. Record floating point value $M_{ij}$ into row $i$, column $j$ of the matrix.

---

## 3. Preserved Scientific Invariants

1. **Frozen Weights:** Checkpoint weights remained bitwise unaltered (SHA-256 verified).
2. **Deterministic Evaluation:** Dropout was deactivated via `model.eval()`.
3. **Centroid Ordering:** Index 0 through 65 strictly matches the original LEDGAR cluster ordering.
4. **Precision Preservation:** Raw matrix entries are stored with full IEEE 754 float precision (serialized to 6 decimal places in JSON) without quantization artifacts.
5. **No Synthetic Normalization:** Rows were not normalized to sum to 1.0; authentic sigmoid likelihoods are preserved.

---

## 4. Verification Gate

The numerical validity of the exported JSON was independently verified by `tests/test_matrix_numerical_validation.py`:
- Checked all 4,356 cells for finite values ($\text{NaN} = 0, \text{Inf} = 0$).
- Extracted 10 pseudo-randomly sampled pairs across diverse diagonal and off-diagonal positions.
- Recomputed forward inference from scratch using the raw checkpoint and compared values against the JSON artifact.
- Maximum observed delta: `0.000000` (exceeding the $< 10^{-5}$ tolerance requirement).
- Output recorded in `design/ui_redesign/phase_04b/matrix_numerical_validation.csv`.
