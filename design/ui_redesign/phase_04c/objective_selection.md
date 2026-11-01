# LexAudit Phase 4C — Scoring Objective Selection & Theoretical Rationale

## 1. Candidate Objectives Evaluated

In selecting the objective function $J(D^{(p)})$ to rank candidate insertion positions $p \in \{0, \dots, N-1\}$ for a displaced clause $c_k$, four candidate mathematical formulations were evaluated prior to running benchmark tests:

### Candidate 1: Whole-Document Mean Combined Anomaly (Selected Primary Objective)
$$J_{\text{comb}}(D^{(p)}) = \frac{1}{N} \sum_{i=0}^{N-1} \left[ \alpha S_A(c_i^{(p)}) + (1-\alpha) S_B(c_i^{(p)}) \right] \quad (\alpha = 0.5)$$
- **Scale**: $[0.0, 1.0]$ where lower represents more coherent text (less anomalous).
- **Improvement Metric**:
  $$\Delta J = J_{\text{comb}}(D^{\text{orig}}) - J_{\text{comb}}(D^{(p)})$$
  where $\Delta J > 0$ indicates a measurable reduction in document anomaly (coherence improvement).

### Candidate 2: Whole-Document Mean Channel B Anomaly
$$J_B(D^{(p)}) = \frac{1}{N} \sum_{i=0}^{N-1} S_B(c_i^{(p)})$$
- **Scale**: $[0.0, 1.0]$.
- **Relationship to $J_{\text{comb}}$**: Because $\sum_i S_A(c_i^{(p)}) = \sum_i S_A(c_i^{\text{orig}})$ is invariant under permutation, ranking by $J_B$ yields identical ordering to $J_{\text{comb}}$, but numerical differences are scaled by a factor of $\frac{1}{1-\alpha} = 2.0$.

### Candidate 3: Sum of Affected Pairwise Edge Anomalies
$$J_{\text{edges}}(D^{(p)}) = \sum_{e \in E_{\text{affected}}^{(p)}} A(e)$$
- **Definition**: Sum of anomalies on the newly created adjacent edges (e.g., $(c_{p-1}, c_k)$ and $(c_k, c_{p+1})$).
- **Scale**: Unbounded / variable depending on insertion position (2 edges for interior moves, 1 edge for document start/end).

### Candidate 4: Isolated Moved Clause Anomaly
$$J_{\text{clause}}(D^{(p)}) = S_B(c_k \text{ at position } p)$$
- **Scale**: $[0.0, 1.0]$.
- **Definition**: Measuring only how well the moved clause fits into its new neighborhood.

---

## 2. Comparative Evaluation and Vulnerability to Gaming

| Criterion | Candidate 1: Mean Combined (Selected) | Candidate 2: Mean Channel B | Candidate 3: Edge Sum | Candidate 4: Moved Clause Only |
| :--- | :--- | :--- | :--- | :--- |
| **Production Consistency** | **Exact match** to `/v1/analyze` document score | Diverges by omitting Channel A scale | Omits boundary weighting | Ignores document-wide impact |
| **Scale Alignment** | Seamlessly aligns with production thresholds (`[0, 1]`) | Requires $2\times$ mental rescaling | Scale varies with $N$ and position | Local metric only |
| **Gaming Vulnerability** | **Immune**: Penalizes collateral damage to neighbors | Immune to collateral gaming | Biased toward boundary slots (fewer edges) | **Highly vulnerable**: Can destroy bridge edge |
| **Boundary Fairness** | Mathematically weighted by actual clause impact | Mathematically weighted | Unfairly favors boundaries | Ignores severed neighbor edge |
| **Decision Support Value** | **Highest**: Answers "Does this make the document better?" | High | Moderate | Misleading to legal reviewers |

### Why Candidate 4 (Moved Clause Only) Was Rejected
If a clause $c_k$ is moved between two clauses $c_{p-1}$ and $c_p$ that originally possessed a strong, critical legal connection ($A(c_{p-1}, c_p) = 0.05$), inserting $c_k$ might give $c_k$ a moderately acceptable score ($A(c_{p-1}, c_k) = 0.30, A(c_k, c_p) = 0.35$), giving $S_B(c_k) \approx 0.325$. If its original position had $S_B(c_k) = 0.40$, Candidate 4 would declare this a "repair," completely ignoring that it severed a near-perfect transition of $0.05$ and introduced two worse transitions. Candidate 4 creates severe "collateral damage."

### Why Candidate 3 (Sum of Affected Edges) Was Rejected
Candidate 3 does not account for the fact that boundary clauses in LexAudit receive $1.0\times$ weight from their single edge, whereas interior clauses receive $0.5\times$ weight from each of their two edges. Evaluating edge sums directly creates an artificial bias toward placing clauses at the document boundary (where only 1 edge is formed).

---

## 3. Authoritative Specification of Primary Objective

### Mathematical Formulation
$$J(D^{(p)}) = \frac{1}{N} \sum_{i=0}^{N-1} \left[ 0.5 \cdot S_A(c_i^{(p)}) + 0.5 \cdot S_B(c_i^{(p)}) \right]$$

### Improvement Formulation
$$\Delta J(p) = J(D^{\text{orig}}) - J(D^{(p)})$$
- If $\Delta J(p) > 0$: The document's mean anomaly is reduced by moving $c_k$ to position $p$.
- If $\Delta J(p) \le 0$: The candidate position degrades or matches document coherence.

### Ranking Protocol
Candidates are ranked in descending order of $\Delta J(p)$ (or equivalently, ascending order of $J(D^{(p)})$). The unchanged position $p_{\text{orig}}$ is always evaluated as the reference baseline ($\Delta J(p_{\text{orig}}) = 0.0$).

### Secondary (Exploratory) Objectives Recorded
1. **Delta Channel B ($ \Delta J_B $)**: $2 \cdot \Delta J$ (unweighted by Channel A).
2. **Local Transition Anomaly ($A_{\text{local}}$)**: The raw pairwise anomaly for $(c_{p-1}, c_k)$ and $(c_k, c_{p+1})$.
These exploratory metrics are returned in the response for explainability but **never** override the primary ranking.
