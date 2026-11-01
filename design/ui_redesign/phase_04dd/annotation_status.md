# Phase 4D-D Annotation Queue Status and Verification Report
## Adjudication Infrastructure, Reviewer Protocol, and Verification Ledger

### 1. Verification Principles and Anti-Fabrication Mandate

In strict compliance with the scientific requirements of Phase 4D-D:
- **No Fabricated Human or Legal Expert Approvals**: Where human legal counsel has not yet completed line-by-line review, cases are classified explicitly as `PENDING_REVIEW` in [annotation_queue.csv](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/research/dependency_ground_truth_phase_04dd/annotation_queue.csv).
- **Distinction Between Computational Proofs and Expert Adjudication**:
  - Computational checks provide evidence of explicitly scoped textual and structural rules (e.g. sequence inversions, section heading mapping, intra-clause sentence indexing).
  - Legal significance and doctrine-dependent disputes (such as scrivener's error vs. strict textualism) are designated as requiring professional legal adjudication.

---

### 2. Annotation Queue Status Breakdown ($N = 72$)

| Benchmark Case Category | Record Count | Adjudication Status | Basis of Pre-Annotation | Next Action |
| :--- | :--- | :--- | :--- | :--- |
| **Verified Positives** | 30 cases | `COMPUTATIONALLY_PRE_ANNOTATED` | Mapped section cross-reference with sequence inversion ($A < R \to R_{pert} < A_{pert}$) | Independent legal reviewer sanity check |
| **Hard Negatives** | 30 cases | `COMPUTATIONALLY_PRE_ANNOTATED` | Proven sentence locality (sentence $\ge 1$), coupled block retention, or covenant commutativity | Independent legal reviewer sanity check |
| **Ambiguous Cases** | 12 cases | `EXPERT_ADJUDICATION_REQUIRED` | Conflicting legal construction, deictic directional contradiction, or subsection disruption | Formal adjudication by admitted legal counsel |
| **Total Queue** | **72 cases** | — | — | **Full Queue Maintained in CSV** |

---

### 3. Detailed Ambiguous Case Adjudication Register ($N = 12$)

The 12 cases requiring expert legal adjudication are categorized into four distinct contractual problem domains:

#### Category A: Deictic Directional Contradiction (4 cases)
- **Cases**: `CASE_04DD_AMBIG_064`, `065`, `066`, `067`
- **Issue**: A clause specifying *"Section X below"* is relocated after Section X.
- **Legal Conflict**:
  - *Argument for Defect*: The directional marker *"below"* is literally false and contradicts the physical layout of the contract.
  - *Argument for Non-Defect*: Under established contract interpretation doctrines (scrivener's error, intent of the parties), courts routinely uphold cross-references where the referenced section number is clear and unambiguous, ignoring erroneous directional pointers.
- **Queue State**: Awaiting counsel ruling on whether to classify as `VERIFIED_POSITIVE` or `VERIFIED_NEGATIVE`.

#### Category B: Unresolved Cross-Clause Discourse Reference (3 cases)
- **Cases**: `CASE_04DD_AMBIG_061`, `062`, `063`
- **Issue**: Cross-clause discourse marker (*"Notwithstanding the foregoing"*) at sentence 0 moved to a new contract position.
- **Legal Conflict**: Whether the new preceding provision provides an acceptable semantic antecedent or creates a substantive contradiction.

#### Category C: Intervening Subsection Displacement (3 cases)
- **Cases**: `CASE_04DD_AMBIG_068`, `069`, `070`
- **Issue**: A provision referencing Section 2 is relocated between Subsections 2.1 and 2.2.
- **Legal Conflict**: The reference to Section 2 remains formally valid, but internal article numbering and hierarchical structure are disrupted.

#### Category D: Cross-Article Relocation with Resolvable Reference (2 cases)
- **Cases**: `CASE_04DD_AMBIG_071`, `072`
- **Issue**: Operative covenants relocated to closing boilerplate while retaining numeric section cross-references.
- **Legal Conflict**: Whether moving substantive terms into miscellaneous sections alters the legal construction of the contract.

---

### 4. Reviewer Protocol and Interface Specifications

Annotators interact with the queue via [annotation_queue.csv](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/research/dependency_ground_truth_phase_04dd/annotation_queue.csv):
1. **Double-Blind Presentation**: Annotators are presented with:
   - Full clause text of original and perturbed states.
   - Exact highlighted referencing span and candidate antecedent span.
   - Proposed label (`proposed_label`) and underlying rationale (`adjudication_notes`).
2. **Zero Detector Leakage**: Model predictions and confidence scores are completely absent from the annotation interface.
3. **Adjudication Logging**: Annotators record their finding in `reviewer_verdict`, entering `VERIFIED_POSITIVE`, `VERIFIED_NEGATIVE`, or `REJECTED`, accompanied by written legal justification.
