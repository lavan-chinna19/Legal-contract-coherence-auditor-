# FALSE-NEGATIVE ANALYSIS
**LEXAUDIT RESEARCH EXTENSION — PHASE 4D-B**
**Author:** Independent Verification Lead & Legal Systems Architect
**Date:** 2026-10-22

---

## 1. Exhaustive False-Negative Register

| Case ID | Split | Model | Score | Threshold | Margin | Root Cause Category | Diagnostic Finding |
| :--- | :--- | :--- | :---: | :---: | :---: | :--- | :--- |
| `VAL_SLA_01_DISP_TERM` | VALIDATION | Candidate C3 | 0.0000 | 0.50 | -0.5000 | Conservative DAG Coverage | Term clause (Stage 2) moved into slot 1 between License Grant (Stage 1) and Users (Stage 3). Does not violate Boilerplate $\to$ Scope edge. |
| `DIAG_P1_02_DISP_TERM` | DIAGNOSTIC | Candidate C3 | 0.0000 | 0.50 | -0.5000 | Conservative DAG Coverage | Term displaced to slot 2 is an operational dislocation that does not violate boilerplate-precedence edges. |
| `DIAG_P1_03_DISP_IP` | DIAGNOSTIC | Candidate C3 | 0.0000 | 0.50 | -0.5000 | Subtle Intra-Tier Shift | Subtle displacement of IP by one slot remains within Stage 3 operational tier; below DAG resolution. |
| `DIAG_P2_01_SWAP_PREAMBLE` | DIAGNOSTIC | Candidate C3 | 0.0000 | 0.50 | -0.5000 | Subtle Preamble/Scope Swap | Preamble (Stage 0) and Scope (Stage 1) swapped. Neither is Stage $\ge 5$, so no boilerplate edge triggered. |
| `DIAG_P2_02_SWAP_PAYMENT_GOVLAW`| DIAGNOSTIC | Candidate C3 | 0.0000 | 0.50 | -0.5000 | Mid-Document GovLaw Swap | Governing Law swapped with Payment (Stage 2). C3 currently checks Scope (Stage 1) and Preamble (Stage 0). |
| All 9 Positive Cases | ALL | Baseline B0 | $\le 0.689$ | 0.70 | -0.011 | Logit Saturation | Channel B MLP logits compressed in narrow interval; scores never cross 0.70. |
| All 9 Positive Cases | ALL | Candidate C2 | $\le 0.188$ | 0.50 | -0.312 | Neural Underfitting | BiLSTM trained on tiny synthetic split failed to learn displacement representations. |

---

## 2. In-Depth Root-Cause Analysis for Candidate C3

Candidate C3 is intentionally conservative:
To prevent false alarms on valid contracts, Candidate C3 strictly checks for **definitive legal discourse regressions**:
1. Boilerplate or Exhibit (Stage 5/6) appearing before Preamble or Scope (Stage 0/1).
2. Remedial boilerplate (Stage 4) appearing before Preamble (Stage 0).

When a displacement occurs purely **within the operational body** (e.g., swapping Payment [Stage 2] with IP [Stage 3], or moving Term [Stage 2] between Scope and Payment), Candidate C3 does not assert a violation because commercial contracts frequently place payment or term sections in varying positions without losing legal validity.

---

## 3. Engineering Remediation
To expand Candidate C3 coverage while preserving zero false positives:
1. Define typed operational sub-edges (e.g. Scope $\prec$ Payment/Invoices).
2. Couple Candidate C3 topological precedence checks with explicit cross-reference validation (e.g., detecting when Clause 4 references "Section 2" which appears later in the document).
