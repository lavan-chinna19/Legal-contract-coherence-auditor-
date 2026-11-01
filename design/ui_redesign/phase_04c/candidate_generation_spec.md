# LexAudit Phase 4C — Candidate Generation Specification

## 1. Algorithmic Overview
Given a contract document $D = [c_0, c_1, \dots, c_{N-1}]$ represented by authoritative clause IDs and their associated text and embeddings, the candidate generator systematically produces all $N$ distinct valid insertion positions for a selected target clause $c_k$.

## 2. Formal Specification

### 2.1 Inputs
- `doc_id` (str): Authoritative document identifier.
- `clause_id` (str): Stable backend clause identifier to be evaluated for repositioning.
- `clauses` (list[Clause]): Ordered list of clause objects in their original document order.
- `embeddings` (torch.Tensor or ndarray): Pre-computed embeddings of shape $(N, 768)$.

### 2.2 Preconditions & Validation
1. Verify $N \ge 2$. If $N=1$, repositioning is undefined; return `ABSTAIN_DOCUMENT_TOO_SHORT`.
2. Locate index $k$ such that $\text{clauses}[k].\text{clause\_id} == \text{clause\_id}$. If not found, raise `404` / `SELECTED_CLAUSE_NOT_FOUND`.
3. Verify $N \le 100$ (bounded candidate limit to protect server resources). If $N > 100$, raise `400` / `DOCUMENT_TOO_LARGE`.

### 2.3 Insertion Slot Enumeration
Let the remaining sequence without $c_k$ be:
$$D' = D \setminus \{c_k\} = [c'_0, c'_1, \dots, c'_{N-2}]$$
There are exactly $N$ possible insertion positions $p \in \{0, 1, \dots, N-1\}$:
$$D^{(p)} = [c'_0, \dots, c'_{p-1}, c_k, c'_p, \dots, c'_{N-2}]$$

Notice:
- For $p = k$: $D^{(k)}$ is identical to the original sequence $D$. This is explicitly retained as the reference baseline candidate (`is_original = True`).
- For $p \ne k$: $D^{(p)}$ is a novel candidate ordering.

### 2.4 Relative Placement Labeling
To provide clear, unambiguous context to the legal reviewer, each candidate slot is assigned descriptive relative placement metadata:

| Insertion Index $p$ | Preceding Clause | Following Clause | Generated Label |
| :--- | :--- | :--- | :--- |
| $p = 0$ | `None` | $c'_0$ | `"Document start (before §1: [Title])"` |
| $0 < p < N-1$ | $c'_{p-1}$ | $c'_p$ | `"Between §{p}: [Title] and §{p+1}: [Title]"` |
| $p = N-1$ | $c'_{N-2}$ | `None` | `"Document end (after §{N-1}: [Title])"` |

### 2.5 Invariant Preservation
- **Identity Stability**: Every clause maintains its immutable `clause_id`. No IDs are generated or renumbered.
- **Order of Non-Selected Clauses**: The relative order among all clauses in $D'$ is strictly preserved:
  $$\forall i < j, \quad \text{idx}(c'_i) < \text{idx}(c'_j) \text{ in } D^{(p)}$$
- **Zero Mutation**: $D$ is never mutated. All operations are strictly read-only in memory.

---

## 3. Boundary & Edge Case Handling Matrix

| Scenario | Behavior | Validation Test |
| :--- | :--- | :--- |
| **$N = 1$ clause** | Return HTTP 400 or abstention: document contains no alternative positions. | `test_repositioning.py::test_single_clause_document` |
| **$N = 2$ clauses** | Returns exactly 2 candidates ($p=0, p=1$). One original, one swapped. | `test_repositioning.py::test_two_clause_document` |
| **Identical clause texts** | Correctly resolved via unique UUID `clause_id`. Permutations are tracked by ID, not string comparison. | `test_repositioning.py::test_identical_clause_bodies` |
| **Moving from $k=0$ to $p=N-1$** | Validated: initial outgoing edge removed; end incoming edge added. | `test_repositioning.py::test_first_to_last_move` |
| **Moving from $k=N-1$ to $p=0$** | Validated: end incoming edge removed; start outgoing edge added. | `test_repositioning.py::test_last_to_first_move` |
| **Adjacent move ($p = k \pm 1$)** | Handled correctly without creating duplicate or self-edges. | `test_repositioning.py::test_adjacent_move` |

---

## 4. Structural Movement Constraints Disclaimer
In real-world commercial contracts, certain structural constraints exist (e.g., preamble must remain first; definitions must precede operative terms; signature blocks and exhibits must remain at the end).

Because automated NLP cannot fully verify legal enforceability across heterogeneous contract formats, LexAudit explicitly qualifies all candidate generation with:
> **"Structural movement constraints could not be fully verified. This model-suggested position is an experimental coherence score comparison and requires human legal review."**
Unconstrained search is performed across all $N$ positions, allowing the human attorney to assess both structural and narrative implications.
