# LexAudit Phase 4C — Synthetic Displacement Protocol & Dataset Provenance

## 1. Dataset Provenance and Train/Test Split Separation

To ensure scientific validity and eliminate data contamination, the evaluation dataset was audited against the frozen model training pipeline (`src/coherence/train_coherence_model.py`).

### 1.1 Ingestion Audit
- **Source Corpus**: SEC EDGAR Material Contracts (Exhibit 10 filings, public commercial agreements).
- **Total Contracts in Corpus**: 50 contracts (`contract_000.txt` through `contract_049.txt`).
- **Training Split**: In `train_coherence_model.py`, ingestion stops as soon as total ingested clauses reaches $\ge 300$:
  - Contracts `contract_000.txt` through `contract_011.txt` (12 contracts, 310 clauses total) formed the training set.
- **Strictly Held-Out Test Split**:
  - Contracts `contract_012.txt` through `contract_049.txt` (38 contracts, 892 clauses total) were **never ingested, trained on, calibrated with, or seen by the model**.
- **Split Manifests**:
  - `benchmark_dataset_manifest.csv`: Full file inventory, clause counts, and character lengths.
  - `benchmark_split_manifest.csv`: Explicit partition into `TRAIN` (12 contracts) vs `HELD_OUT_TEST` (38 contracts).

---

## 2. Synthetic Displacement Perturbation Protocol

### 2.1 Contract Eligibility Criteria
1. Must belong to the `HELD_OUT_TEST` partition.
2. Must contain at least $N \ge 4$ segmented clauses to permit non-trivial displacement.
3. Clause boundaries must be verifiable and non-empty.

### 2.2 Perturbation Algorithm
For each eligible test contract $D = [c_0, c_1, \dots, c_{N-1}]$:
1. **Target Selection**: Select an interior clause $c_k$ with index $1 \le k \le N-2$.
2. **Displacement Injection**: Move $c_k$ to a displaced index $p_{\text{pert}} \ne k$ such that $|p_{\text{pert}} - k| \ge 2$ (or boundary if $|p_{\text{pert}} - k| \ge 1$ for short documents).
3. **Synthetic Ground Truth**: The true original insertion index $k$ in the unperturbed document is recorded as the recovery target $y^* = k$.
4. **Permutation Space**: The model must search across all $N$ candidate positions in the perturbed document without any knowledge of $y^*$.
5. **Candidate Evaluation**: Evaluate objective $J(D^{(p)})$ for all $p \in \{0, \dots, N-1\}$.
6. **Ranking**: Rank candidate positions in descending order of $\Delta J(p)$ (ascending order of $J(D^{(p)})$).
7. **Rank Extraction**: Let $r_i \in \{1, \dots, N\}$ be the 1-based rank of the true original position $y^*$.

### 2.3 Baseline Comparisons
Three baselines are evaluated on identical perturbations:
1. **Random Insertion Baseline**: Picks a slot uniformly at random from $\{0, \dots, N-1\}$. Expected Top-1 $= \frac{1}{N}$; Expected MRR $= \frac{1}{N} \sum_{r=1}^N \frac{1}{r}$.
2. **Current-Position (No-Op) Baseline**: Maintains the displaced position.
3. **Cosine Similarity Heuristic**: Places $c_k$ adjacent to the clause having the highest cosine embedding similarity.

---

## 3. Negative Control Protocol
To test whether the system exhibits an anti-social bias toward always recommending movement even when a document is in pristine legal drafting order:
1. **Input**: Unperturbed original documents from the held-out test set.
2. **Target Clause**: Any selected clause $c_k$ in its original natural position.
3. **Expected Behavior**: The system should identify that the current position $p=k$ is optimal or that any alternate position yields $\Delta J \le \tau_{\text{abstain}}$.
4. **Abstention Verification**: Verify that the system abstains from recommending a move (`recommends_move = False`, `abstention_reason = "NO_IMPROVEMENT"`).
