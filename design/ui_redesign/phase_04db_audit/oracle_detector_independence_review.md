# ORACLE-DETECTOR INDEPENDENCE AND CIRCULARITY REVIEW
**LEXAUDIT INDEPENDENT RESEARCH AUDIT — PHASE 4D-B**
**Auditor:** Independent Legal NLP Research Auditor & Evaluation Architect
**Date:** 2026-10-22

---

## 1. Executive Summary

This audit examined whether Candidate C3's reported 100% held-out test recall reflects an independent, generalizable legal coherence model or primarily **semantic circularity** between synthetic label authoring and a hardcoded rule engine.

### Critical Finding:
**Candidate C3 and the benchmark positive test cases share identical underlying heuristic assumptions.** 
The ground-truth oracle and Candidate C3 were constructed by the same developers using the same 7-stage lifecycle ontology and identical heading keywords. Candidate C3 does not evaluate contractual coherence through linguistic or legal understanding; it executes a hardcoded rule that matches the exact transformation used to synthesize the positive test cases.

---

## 2. Structural Rule vs. Benchmark Authoring Alignment

### 2.1 The Candidate C3 Detection Rule
In `src/research/structural_coherence/models.py` (lines 445–453):
```python
# Back-edge: later position j has stage significantly lower than earlier position i
if stages[i] >= 5 and stages[j] <= 1:  # Boilerplate/Exhibit followed by Preamble/Scope
    violations[j] = max(violations[j], 1.0)
    violations[i] = max(violations[i], 0.7)
elif stages[i] >= 4 and stages[j] == 0:  # Remedies followed by Preamble
    violations[j] = max(violations[j], 1.0)
```

### 2.2 The Synthetic Test Transformations
In `src/research/structural_coherence/evaluator.py`:
- `TEST_01_EXHIBIT_SCOPE_INVERSION`: Exhibit A (Stage 6) moved to slot 1, preceding Scope (Stage 1) at slot 10.
  $$\text{Condition: } \text{Stage}(c_1) = 6 \ge 5 \quad \land \quad \text{Stage}(c_{10}) = 1 \le 1 \implies \text{VIOLATION ASSERTED}$$
- `TEST_02_GOVLAW_BEFORE_SCOPE`: Governing Law (Stage 5) moved to slot 1, preceding Scope (Stage 1) at slot 2.
  $$\text{Condition: } \text{Stage}(c_1) = 5 \ge 5 \quad \land \quad \text{Stage}(c_2) = 1 \le 1 \implies \text{VIOLATION ASSERTED}$$
- `VAL_SLA_02_SWAP_DISPUTE_PREAMBLE`: Dispute Resolution (Stage 5) swapped to slot 0, preceding Grant of License (Stage 1).
  $$\text{Condition: } \text{Stage}(c_0) = 5 \ge 5 \quad \land \quad \text{Stage}(c_7) = 1 \le 1 \implies \text{VIOLATION ASSERTED}$$
- `DIAG_P1_01_DISP_SCOPE`: Scope (Stage 1) displaced to slot 10 following Miscellaneous (Stage 5).
  $$\text{Condition: } \text{Stage}(c_9) = 5 \ge 5 \quad \land \quad \text{Stage}(c_{10}) = 1 \le 1 \implies \text{VIOLATION ASSERTED}$$

---

## 3. Evidence of Circular Alignment: Failure on Non-Aligned Positives

Whenever a benchmark case was synthesized using a structural dislocation that did **not** involve moving a Stage 5/6 clause before a Stage 0/1 clause, Candidate C3 scored exactly **$0.0000$ (complete failure)**:

| Case ID | Split | Transformation Description | Lifecycle Shift | Candidate C3 Output | Ground-Truth Label | Result |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: |
| `DIAG_P1_02_DISP_TERM` | DIAGNOSTIC | Term (S6) moved to slot 2 before IP | Stage 2 before Stage 3 | **0.0000** | VIOLATION | **MISSED (FN)** |
| `DIAG_P1_03_DISP_IP` | DIAGNOSTIC | IP (S4) moved to slot 4 | Stage 3 intra-tier | **0.0000** | VIOLATION | **MISSED (FN)** |
| `DIAG_P2_01_SWAP_PREAMBLE`| DIAGNOSTIC | Preamble (S1) swapped with Scope (S2) | Stage 1 before Stage 0 | **0.0000** | VIOLATION | **MISSED (FN)** |
| `DIAG_P2_02_SWAP_PAYMENT` | DIAGNOSTIC | Payment (S3) swapped with GovLaw (S9) | Stage 5 before Stage 2 | **0.0000** | VIOLATION | **MISSED (FN)** |
| `VAL_SLA_01_DISP_TERM` | VALIDATION | Term (S7) moved to slot 1 | Stage 2 before Stage 3 | **0.0000** | VIOLATION | **MISSED (FN)** |

Across all 5 of these verified structural violations, Candidate C3 achieved **$0/5$ (0.0% recall)**.

---

## 4. Feature Extraction Keyword Leakage

In `src/research/structural_coherence/features.py`:
The lifecycle stage extractor uses hardcoded string matching tailored to the synthetic fixtures:
- `"preamble"`, `"parties"`, `"recital"` $\to$ Stage 0
- `"scope"`, `"services"`, `"grant of license"` $\to$ Stage 1
- `"payment"`, `"fee"`, `"term and termination"` $\to$ Stage 2
- `"intellectual property"`, `"confidentiality"`, `"audit"` $\to$ Stage 3
- `"indemnif"`, `"liability"`, `"warranty"` $\to$ Stage 4
- `"governing law"`, `"jurisdiction"`, `"dispute"`, `"miscellaneous"` $\to$ Stage 5
- `"exhibit"`, `"schedule"`, `"appendix"` $\to$ Stage 6

If a contract lacks these exact heading tokens (e.g., using "Commercial Terms", "Background", "General Provisions", "Remedies", or numbering without titles), the classifier defaults to Stage 3 (`Neutral operational middle`), causing Candidate C3 to output **$0.0000$ on all clauses**.

---

## 5. Audit Conclusion on Independence

Candidate C3 is not an independent machine learning model. It is a 20-line heuristic rule engine constructed to assert violations on specific keyword combinations. Its reported 100% held-out test recall was achieved because the two positive held-out test cases were engineered to trigger that exact rule. On structural dislocations outside this rule, Candidate C3 has a **0.0% detection rate**.
