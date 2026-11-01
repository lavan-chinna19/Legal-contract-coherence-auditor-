# LexAudit Research — Synthetic Displacement Protocol & Data Provenance
<!-- Reference copy for research archive -->

## 1. Dataset Provenance
- 50 SEC EDGAR commercial contracts (`data/contracts/contract_000.txt` to `contract_049.txt`).
- Train Split: `contract_000.txt` to `contract_011.txt` (12 documents, 310 clauses).
- Held-out Test Split: `contract_012.txt` to `contract_049.txt` (38 documents, 892 clauses). Contamination: 0.0%.

## 2. Evaluation Protocol
- Seed: 42 (deterministic).
- Target selection: Interior clause $c_k$ with non-zero semantic content.
- Perturbation: Relocate $c_k$ to $p_{\text{pert}} \ne k$.
- Ground Truth: True slot $k$.
- Candidate generation: Evaluate all $N$ insertion positions.
- Ranking: Sorted by primary objective $J(D^{(p)})$.
- Metrics: Top-1, Top-3, Mean Reciprocal Rank (MRR), Mean Objective Improvement, Negative Control Abstention.
