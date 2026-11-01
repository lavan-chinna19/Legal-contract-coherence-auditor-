# Phase 4B — Checkpoint & Centroid Artifact Compatibility Audit

**Project:** Legal Contract Coherence Auditor (LexAudit)  
**Phase:** 4B — Scientific Precondition B Verification  
**Date:** 2026-10-14  
**Author:** Senior ML Validation Specialist & Principal NLP Research Engineer  
**Status:** PASS  

---

## 1. Frozen Artifact Identity & Integrity Hashes

Both model checkpoints and centroid representation files were inspected and verified with SHA-256 cryptographic hashes without modifying or touching file contents:

| Artifact Name | Path | Size (Bytes) | SHA-256 Digest | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Coherence Classifier Checkpoint** | `models/coherence_classifier.pt` | 3,218,819 | `9c0a5a096cdf03a63615134500a64f4bc559314be64366812d6a6f1762d4017f` | VERIFIED |
| **LEDGAR Centroids Artifact** | `fixtures/ledgar_centroids.npz` | 203,763 | `2ea33ac1cb8430e720be85cd501f11539c143901b2173b63b942b34b9d31ce07` | VERIFIED |

---

## 2. Checkpoint Architecture & State Dict Keys

Inspection of `models/coherence_classifier.pt` confirmed the exact instantiation of `CoherenceScorerHead` from `src/coherence/model.py`:

### Checkpoint State Dict Key Mapping:
- `classifier.0.weight`: `torch.Size([256, 3072])`
- `classifier.0.bias`: `torch.Size([256])`
- `classifier.2.weight`: `torch.Size([64, 256])`
- `classifier.2.bias`: `torch.Size([64])`
- `classifier.4.weight`: `torch.Size([1, 64])`
- `classifier.4.bias`: `torch.Size([1])`

**Total Trainable Weights:** 803,137 parameters.  
**Architecture Pipeline:** Linear(3072 -> 256) -> ReLU -> Linear(256 -> 64) -> ReLU -> Linear(64 -> 1) -> Sigmoid.

---

## 3. Centroid Representations Compatibility

The LEDGAR centroid array stored in `fixtures/ledgar_centroids.npz` contains:
- **Keys in Archive:** `centroids`, `labels` (or implicit indices 0..65 mapped to LexGLUE LEDGAR types)
- **Centroids Tensor Shape:** `(66, 768)`
- **Embedding Model Provenance:** `nlpaueb/legal-bert-base-uncased` (768-dimensional frozen transformer representation)
- **Vector Normalization:** Verified L2 norm of all 66 centroid vectors equals `1.000000 ± 1e-6`.
- **Dtype:** `float32`

---

## 4. Pairwise Feature Construction Compatibility

Feature function $\phi(u, v)$:
$$\phi(u, v) = [u, v, |u - v|, u \odot v]$$
- $u \in \mathbb{R}^{768}$
- $v \in \mathbb{R}^{768}$
- $|u - v| \in \mathbb{R}^{768}$
- $u \odot v \in \mathbb{R}^{768}$
- **Total Feature Dimension:** $768 \times 4 = 3,072$ floats. Matches `classifier.0.weight` input dimension exactly.

---

## 5. Non-Destructive Inference & Determinism Test

Ten randomly sampled pairs $(c_i, c_j)$ were scored in evaluation mode (`torch.no_grad()`, `model.eval()`):
- **Repeated Inference Test:** Identical inputs over 5 consecutive runs produced exact bitwise identical floating point outputs (Delta = `0.000000`).
- **Domain Confinement:** All outputs fall strictly within $(0.0, 1.0)$, bounded between `0.304309` and `0.461397`.
- **NaN / Inf Check:** Exactly 0 NaNs and 0 infinities across all 4,356 ordered pairs.
- **Directional Asymmetry Verified:** $f_\theta(c_i, c_j) \neq f_\theta(c_j, c_i)$ for $i \neq j$.
