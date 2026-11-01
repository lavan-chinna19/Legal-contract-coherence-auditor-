# Phase 4D Subsystem and Channel Ablation Analysis

## 1. Channel Invariance and Responsiveness
A key architectural finding of Phase 4D is the operational divergence between Channel A and Channel B:

1. **Channel A (OOD Semantic Centroid Distance)**:
   - Evaluates bag-of-clauses embeddings against pre-trained LEDGAR cluster centroids.
   - **Permutation Invariance**: Across all displacement (P1) and swapping (P2) scenarios, $\Delta S_A = 0.0000$.
   - **Implication**: Channel A cannot detect clause displacements or structural disorganizations, as it is oblivious to sequence order.

2. **Channel B (Adjacent Discourse Pair Scorer)**:
   - Evaluates adjacent transition probability $P(c_{i+1} \mid c_i)$.
   - **Boundary Responsiveness**: Reacts directly to the disruption of predecessor and successor transitions. For P2 adjacent swap, maximum transition shift $\Delta S_B = +0.0152$.
   - **Implication**: Channel B is the sole neural component capable of sensing displacement and swapping disturbances.

3. **Deterministic Rule Checkers (CrossReferenceChecker & DateLogicChecker)**:
   - Exhibit binary step-function sensitivity: 0 on compliant structures, 1+ on invalid targets.
   - Immune to embedding noise and semantic variance.

## 2. Integrated Pipeline Synergy
The dual-channel ensemble plus rule pipeline provides complementary defense: deterministic rules catch hard logical inversions and broken references with 100% precision, while Channel B captures soft narrative discourse friction.
