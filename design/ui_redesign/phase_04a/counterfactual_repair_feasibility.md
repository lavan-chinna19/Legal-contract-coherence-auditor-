# LexAudit Phase 4A — Counterfactual Clause Repair Feasibility Audit & Research Blueprint

## 1. Feasibility Verdict & Architectural Foundation
- **Feasibility Verdict**: **HIGHLY FEASIBLE** ($O(N)$ local complexity with 100% frozen embedding reuse).
- **Phase Restriction**: Research blueprint only. **No counterfactual repair engine is implemented during Phase 4A.**
- **Human Review Principle**: Suggested relocations must be presented as non-binding diagnostic hypotheses. The human legal reviewer retains sole decision-making authority over contract restructuring.

---

## 2. Invariance Properties of the Dual-Channel Scorer

### 2.1 Channel A Position-Invariance Proof
Channel A calculates the semantic distance between a clause's Legal-BERT embedding $u_i \in \mathbb{R}^{768}$ and the nearest LEDGAR topic centroid $c^* \in \mathbb{R}^{768}$:
$$S_A(c_i) = \min_{k} \left( 1.0 - \frac{u_i \cdot c_k}{\|u_i\|_2 \|c_k\|_2} \right)$$
Because $u_i$ is generated solely from the token text of $c_i$, **Channel A is strictly invariant to clause permutation**:
$$\forall \pi \in \mathcal{S}_N, \quad S_A(c_{\pi(i)}) = S_A(c_i)$$
Relocating a clause anywhere in the document leaves its Channel A score and OOD status completely unchanged.

### 2.2 Channel B Local Locality Proof
Channel B evaluates consecutive transitions $P(c_t \to c_{t+1})$. When clause $c_k$ is relocated from source position $s$ to destination position $d$:
1. **At Source Position $s$**:
   The old incoming and outgoing transitions $(c_{s-1} \to c_k)$ and $(c_k \to c_{s+1})$ are removed, and a new direct bridge transition is formed:
   $$T_{bridge} = P(c_{s-1} \to c_{s+1})$$
2. **At Destination Position $d$**:
   The old direct transition $(c_{d-1} \to c_d)$ is split into two new transitions:
   $$T_{in} = P(c_{d-1} \to c_k), \quad T_{out} = P(c_k \to c_d)$$
3. **All Other $N - 4$ Transitions**:
   Remain 100% unchanged!
4. **Computational Consequence**:
   Evaluating candidate position $d$ requires only **three forward passes** of `CoherenceScorerHead` ($O(1)$ work) without re-embedding text or re-scoring unaffected document segments.

---

## 3. Algorithmic Design for Future Implementation

### 3.1 Candidate Generation & Objective
For a flagged anomaly clause $c_k$:
1. Generate candidate insertion slots $j \in \{0, 1, \dots, N-1\} \setminus \{s\}$.
2. Evaluate document transition loss delta:
   $$\Delta \mathcal{L}(j) = \left[ (1 - T_{bridge}) + (1 - T_{in}) + (1 - T_{out}) \right] - \left[ (1 - P(c_{s-1} \to c_k)) + (1 - P(c_k \to c_{s+1})) + (1 - P(c_{j-1} \to c_j)) \right]$$
3. Rank destination slots $j$ in descending order of improvement $-\Delta \mathcal{L}(j)$.

### 3.2 Legal Cross-Reference Exclusion Constraints
A proposed relocation slot $j$ must be strictly disqualified (masked out) if:
- **Dependency Inversion**: Moving $c_k$ places a definition after its first statutory invocation.
- **Reference Disruption**: Moving $c_k$ breaks an established sequential citation pattern (e.g. placing Section 5 between Section 2.1 and Section 2.2).
- **Recitals Boundary Violation**: Moving substantive covenants into the preamble recitals (before operative words of agreement).

### 3.3 Abstention Criteria
The counterfactual engine must explicitly **abstain** from recommending a relocation when:
1. Max score improvement $\Delta S_B < \epsilon_{min}$ ($\epsilon_{min} = 0.15$).
2. Channel A is the sole driver of the anomaly ($S_A \ge 0.60$ while $S_B \le 0.30$), indicating that the clause is an out-of-distribution subject matter rather than an out-of-order section.
3. Multiple destinations produce tie improvements within numerical noise tolerance ($\pm 0.01$).

---

## 4. Evaluation Protocol on Held-Out Benchmarks
To validate counterfactual repair before production release:
1. **Synthetic Perturbation Dataset**:
   Take 100 clean, canonical contracts from CUAD and LEDGAR. Randomly displace one clause by $k$ positions ($k \in [2, 10]$).
2. **Metrics**:
   - **Top-1 Recovery Rate**: Fraction of cases where the true original position is ranked #1.
   - **Top-3 Recovery Rate**: Fraction of cases where original position is within top 3 candidates.
   - **Mean Reciprocal Rank (MRR)**: $\frac{1}{M} \sum_{m=1}^M \frac{1}{\text{rank}_m}$.
   - **False Repair Rate**: Frequency of recommending relocation for clean, unperturbed contracts.
3. **Runtime Target**: $< 200\text{ms}$ total repair evaluation per flagged clause.
