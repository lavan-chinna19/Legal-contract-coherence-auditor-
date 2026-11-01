# LexAudit Phase 4A — Transition Matrix Reconstruction Feasibility & Future Visualization Blueprint

## 1. Feasibility Assessment
- **Status**: Technically feasible using frozen artifacts without model retraining or external data.
- **Classification**: `MATRIX_RECONSTRUCTION_POSSIBLE_WITH_EXISTING_ARTIFACTS`
- **Phase Restriction**: Design blueprint only. **No heatmap implementation or computation is authorized during Phase 4A.**

---

## 2. Offline Deterministic Reconstruction Algorithm
The $66 \times 66$ canonical clause-type transition compatibility matrix $M$ can be computed deterministically in ~2.5 seconds using existing artifacts:

### Artifact Inputs
1. `fixtures/ledgar_centroids.npz`: Array `centroids` of shape `(66, 768)` and `labels` of length 66.
2. `models/coherence_classifier.pt`: State dict containing `CoherenceScorerHead` weights.

### Computation Protocol
```python
# Blueprint for future approved Phase 4B script (e.g. scripts/reconstruct_coherence_matrix.py)
import numpy as np
import torch
from src.coherence.model import CoherenceScorerHead

# 1. Load centroids & model
data = np.load("fixtures/ledgar_centroids.npz")
centroids = torch.tensor(data["centroids"], dtype=torch.float32)  # (66, 768)
labels = data["labels"]

model = CoherenceScorerHead(embed_dim=768)
model.load_state_dict(torch.load("models/coherence_classifier.pt", weights_only=True))
model.eval()

# 2. Form all 4,356 ordered pairs (i, j)
K = 66
u = centroids.unsqueeze(1).expand(K, K, -1).reshape(-1, 768)  # (4356, 768)
v = centroids.unsqueeze(0).expand(K, K, -1).reshape(-1, 768)  # (4356, 768)

diff = torch.abs(u - v)
prod = u * v
features = torch.cat([u, v, diff, prod], dim=-1)  # (4356, 3072)

# 3. Vectorized Forward Pass
with torch.no_grad():
    compat = model(features).squeeze(-1).reshape(K, K)  # (66, 66) in [0, 1]

# 4. Save reconstructed artifact
np.savez_compressed("fixtures/reconstructed_transition_matrix.npz", matrix=compat.numpy(), labels=labels)
```

---

## 3. Normalization & Sparsity Analysis
1. **Raw Compatibility vs. Markov Normalization**:
   - **Raw Compatibility Matrix $M_{ij} = P(C_i \to C_j) \in [0, 1]$**:
     Represents the unconditional pairwise coherence score between clause type $i$ and clause type $j$. High values indicate strong discourse affinity.
   - **Softmax Normalized Markov Matrix $\tilde{M}_{ij} = \frac{\exp(M_{ij} / \tau)}{\sum_k \exp(M_{ik} / \tau)}$**:
     Converts scores into row-stochastic transition probabilities ($\sum_j \tilde{M}_{ij} = 1$). Useful for Markov chain simulations but alters absolute compatibility baselines.
2. **Sparsity & Clustering**:
   - Because 66 categories create $4,356$ cells, a full $66 \times 66$ heatmap is visually dense.
   - For Phase 4B UX, recommendation is a **Top-K Subgraph or Clustered Heatmap** grouping the 66 labels into 7 functional legal clusters:
     - Recitals & Preamble
     - Operational & Commercial Covenants
     - Financial Terms & Payment
     - Warranties & Indemnification
     - Termination & Remedies
     - Dispute Resolution & Governing Law
     - Boilerplate & Miscellaneous

---

## 4. Future UI Component Blueprint (Phase 4B Candidate)
- **Component**: `CoherenceTransitionHeatmap.tsx`
- **Location**: `frontend/src/components/analytics/`
- **Display Modes**:
  1. *Global Cluster Affinity*: $7 \times 7$ high-level category flow map.
  2. *Contextual Transition Strip*: Displays top-5 most compatible and top-5 anomalous successor clause types for the currently selected clause's nearest centroid.
- **Accurate Labeling**: Labeled as *"Learned Clause-Type Transition Affinity Matrix"* with explicit disclaimer: *"Computed offline by evaluating the frozen coherence classifier head across LEDGAR centroid vectors. Not an empirical document frequency count."*
