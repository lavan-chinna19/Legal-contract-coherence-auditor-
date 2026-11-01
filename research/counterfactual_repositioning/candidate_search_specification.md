# LexAudit Research — Candidate Search Specification
<!-- Reference copy for research archive -->

## 1. Candidate Search Protocol
For a document of length $N$ and target clause $c_k$:
- Removal: $D' = D \setminus \{c_k\}$ (length $N-1$).
- Insertion: $\forall p \in \{0, \dots, N-1\}$, $D^{(p)} = \text{Insert}(D', c_k, p)$.
- Stable Identifiers: All permutations operate strictly on immutable clause IDs.
- Permutations evaluated: Exactly $N$ candidates, including baseline $p=k$.
- Bounds: Enforced limit $N \le 100$.

## 2. Structural Feasibility Distinction
In the synthetic displacement recovery benchmark, candidate search is unconstrained across all $N$ positions to provide an unbiased test of the coherence head's ability to identify the true original slot without heuristic filtering.
