# Dual-Channel Scorer Formula and Numerical Verification

**Document ID**: `PHASE_04DA_SCORER_FORMULA_VERIFICATION`  
**Auditor**: Numerical Verification Specialist & ML Systems Engineer  
**Scope**: Code Verification, Numerical Sanity Bounds, and Reference Comparisons  

---

## 1. Primary Scorer Mathematical Equations

### A. Ensemble Combination Formula
From [`src/scoring/pipeline.py`](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/src/scoring/pipeline.py#L98-L101):
```python
combined = self.alpha * score_a + (1.0 - self.alpha) * score_b
combined = round(float(np.clip(combined, 0.0, 1.0)), 4)
```

**Authoritative Equation**:
$$S_i = \text{round}\Big(\min\big(1.0, \max(0.0, \alpha \cdot A_i + (1 - \alpha) \cdot B_i)\big), 4\Big)$$

- **Weight Parameter ($\alpha$)**: Defaults to `ENSEMBLE_ALPHA = 0.50` (`src/config.py`).
- **Score Domain**: $S_i \in [0.0000, 1.0000]$.
- **Rounding Convention**: Standard 4 decimal places via Python `round(..., 4)`.

---

## 2. Channel B Transition Aggregation Formula

From [`src/scoring/channel_b.py`](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/src/scoring/channel_b.py#L48-L101):

### A. Transition Incoherence Score
For adjacent clause pair $(c_k, c_{k+1})$:
$$\alpha_k = 1.0 - P(c_k \to c_{k+1})$$
where $P(c_k \to c_{k+1}) \in [0.0, 1.0]$ is the softmax forward coherence probability emitted by the coherence classifier.

### B. Per-Clause Aggregation
$$B_i = \begin{cases}
  \alpha_0, & i = 0 \text{ (Head boundary: outgoing edge only)} \\
  \alpha_{n-2}, & i = n-1 \text{ (Tail boundary: incoming edge only)} \\
  \max(\alpha_{i-1}, \alpha_i), & 0 < i < n-1 \text{ (Interior: maximum of incoming and outgoing discontinuities)}
\end{cases}$$

### Verification of Boundary Rules:
- **Head Clause ($c_0$)**: Has no predecessor. Channel B evaluates only whether $c_0$ smoothly introduces $c_1$.
- **Tail Clause ($c_{n-1}$)**: Has no successor. Channel B evaluates only whether $c_{n-1}$ logically follows $c_{n-2}$.
- **Interior Clauses ($c_i$)**: An interior clause has two adjacency edges ($c_{i-1} \to c_i$ and $c_i \to c_{i+1}$). The `max` aggregation ensures that if a clause creates a break on *either* side, that discontinuity is attributed to $c_i$.

---

## 3. Independent Numerical Verification Matrix

Using fixed numerical fixtures, the production code functions were compared against an independent reference implementation:

| Test ID | Document Size ($n$) | Position ($i$) | Incoming Prob | Outgoing Prob | Reference $B_i$ | Code $B_i$ | Delta | Match |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `TC_B_01` | $n=1$ | 0 (Single) | 1.0000 | 1.0000 | 0.0000 | 0.0000 | 0.0000 | PASS |
| `TC_B_02` | $n=2$ | 0 (Head) | N/A | 0.4000 | 0.6000 | 0.6000 | 0.0000 | PASS |
| `TC_B_03` | $n=2$ | 1 (Tail) | 0.4000 | N/A | 0.6000 | 0.6000 | 0.0000 | PASS |
| `TC_B_04` | $n=3$ | 0 (Head) | N/A | 0.8500 | 0.1500 | 0.1500 | 0.0000 | PASS |
| `TC_B_05` | $n=3$ | 1 (Middle) | 0.8500 | 0.2000 | $\max(0.15, 0.80)=0.8000$ | 0.8000 | 0.0000 | PASS |
| `TC_B_06` | $n=3$ | 2 (Tail) | 0.2000 | N/A | 0.8000 | 0.8000 | 0.0000 | PASS |
| `TC_B_07` | $n=5$ | 2 (Middle) | 0.5000 | 0.5000 | $\max(0.50, 0.50)=0.5000$ | 0.5000 | 0.0000 | PASS |
| `TC_B_08` | $n=5$ | 2 (Middle) | 0.9000 | 0.1000 | $\max(0.10, 0.90)=0.9000$ | 0.9000 | 0.0000 | PASS |

---

## 4. Cross-Channel Agreement Matrix

Tested against [`src/scoring/severity.py::compute_cross_channel_agreement`](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/src/scoring/severity.py#L26-L51):

| $A_i$ | $B_i$ | Expected Agreement Magnitude | Expected Agreement Type | Code Output Magnitude | Code Output Type | Match |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 0.10 | 0.15 | $1.0 - \|0.10 - 0.15\| = 0.9500$ | `CONCORDANT_CLEAN` | 0.9500 | `CONCORDANT_CLEAN` | PASS |
| 0.80 | 0.85 | $1.0 - \|0.80 - 0.85\| = 0.9500$ | `CONCORDANT_ANOMALY` | 0.9500 | `CONCORDANT_ANOMALY` | PASS |
| 0.80 | 0.20 | $1.0 - \|0.80 - 0.20\| = 0.4000$ | `CHANNEL_A_DOMINANT` | 0.4000 | `CHANNEL_A_DOMINANT` | PASS |
| 0.10 | 0.90 | $1.0 - \|0.10 - 0.90\| = 0.2000$ | `CHANNEL_B_DOMINANT` | 0.2000 | `CHANNEL_B_DOMINANT` | PASS |

---

## 5. Software Defect Analysis

Is there any software bug in the scoring pipeline?
- **Finding**: **NO SOFTWARE BUG WAS FOUND.**
- The formulas in code execute identically to their mathematical specifications.
- The reason structural perturbations do not breach severity thresholds is **model insensitivity and dynamic range compression**, not an arithmetic bug in the code.
