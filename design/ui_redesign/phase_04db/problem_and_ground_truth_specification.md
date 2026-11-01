# PROBLEM AND GROUND-TRUTH SPECIFICATION
**LEXAUDIT RESEARCH EXTENSION — PHASE 4D-B**
**Author:** Principal Legal NLP Research Scientist & Legal Systems Architect
**Date:** 2026-10-22

---

## 1. Formal Disambiguation of Related Legal NLP Tasks

In legal document analysis, structural ordering questions are frequently conflated. Phase 4D-B formally separates five distinct tasks:

### Task 1: Structural Anomaly Detection (PRIMARY TARGET)
- **Input:** A contract clause sequence $C = [c_1, c_2, \dots, c_n]$.
- **Output:** An evidence-supported finding that a particular ordering or dependency violates a pre-declared structural condition, with an anomaly flag $\hat{y} \in \{0, 1\}$ and score $S_{\text{struct}} \in [0.0, 1.0]$.
- **Operational Rule:** Must detect genuine structural defects without penalizing benign or valid alternative orderings.

### Task 2: Clause-Position Recovery (Phase 4C/4C-A Scope)
- **Input:** A clause $c_k$ known to have been displaced from a reference ordering, and candidate insertion positions $\{0, \dots, n-1\}$.
- **Output:** A ranked list of candidate insertion slots.
- **Critical Distinction:** A model may accurately recover where a clause originally came from (e.g. Top-1 33.3%, Top-3 77.8%) without proving that the current position is legally defective. Position recovery optimizes *relative candidate coherence*; it does NOT establish *anomaly detection*.

### Task 3: Local Transition Compatibility (Frozen Channel B Scope)
- **Input:** Two adjacent clauses $(c_i, c_{i+1})$.
- **Output:** A model-derived transition probability $P_{\text{compat}} \in [0, 1]$.
- **Critical Distinction:** A low adjacent compatibility score does not prove document-level defect. Contract covenants often exhibit modularity where adjacent topics differ (e.g. Audit Rights adjacent to Warranty Disclaimers) while remaining legally valid.

### Task 4: Global Discourse Coherence
- **Input:** The full document sequence $C$.
- **Output:** A document-level or clause-level measure of contextual flow and lifecycle consistency.

### Task 5: Rule-Based Dependency Violation (Phase 4D Scope)
- **Input:** Clauses containing explicit cross-references, date expressions, or defined terms.
- **Output:** Deterministic violation findings (e.g., "Section 14 references undefined Exhibit C").

---

## 2. Ground-Truth Taxonomy and Label Families

To prevent circular ground-truth and reward-hacking, labels are partitioned into strictly defined families:

| Label Family | Definition | Evaluation Eligibility | Example in Benchmark |
| :--- | :--- | :---: | :--- |
| **`VERIFIED_STRUCTURAL_DEPENDENCY_VIOLATION`** | An ordering transformation that breaks an independently verified prerequisite, lifecycle stage, or textual dependency. | **Strict Positive** | Scope placed after Exhibits; Governing Law placed between Preamble and Scope. |
| **`VALID_ORDER`** | Canonical unperturbed contract sequence. | **Strict Negative** | Clean Master Services Agreement; Clean Software License Agreement. |
| **`INDEPENDENT_REORDERING`** | Permutations of clauses whose mutual legal relationship is commutative or modular (Hard Negative). | **Strict Negative** | Audit Rights swapped with Warranty Disclaimer; Permitted Users swapped with Fee Schedule. |
| **`AMBIGUOUS_ORDER`** | Reorderings where legal coherence is subjective or context-dependent. | **Excluded from Denominator** | Confidentiality swapped with Indemnification (P2_03). |
| **`SYNTHETIC_DISPLACEMENT_ONLY`** | Arbitrary index shift without an independently verified legal dependency failure. | **Non-Eligible** | Unverified synthetic index displacement. |
| **`UNSUPPORTED_ORACLE`** | Oracle determinations relying on candidate model outputs. | **Strictly Forbidden** | Any label authored by observing Channel B or Candidate predictions. |

---

## 3. Independent Precedence Oracle Specification

The ground-truth oracle in Phase 4D-B operates completely independently of all target models:
1. **Contract Lifecycle Hierarchy:** Standard legal contracts follow a universal discourse lifecycle:
   $$\text{Preamble/Recitals (0)} \prec \text{Grant/Scope (1)} \prec \text{Consideration/Term (2)} \prec \text{Operational Covenants (3)} \prec \text{Risk/Remedies (4)} \prec \text{Boilerplate (5)} \prec \text{Exhibits/Execution (6)}$$
2. **Defect Criteria:** A sequence violates structural ground truth if and only if:
   - A subsequent lifecycle stage precedes an essential prerequisite stage (e.g. Stage 5/6 precedes Stage 0/1).
   - An explicit operational cross-reference points backward to an unestablished term (e.g. Scope defining deliverables referenced in Exhibit A).
   - A preamble or closing clause is displaced into substantive operational sections.

This ensures the ground-truth benchmark is objective, verifiable, and free of circular bias.
