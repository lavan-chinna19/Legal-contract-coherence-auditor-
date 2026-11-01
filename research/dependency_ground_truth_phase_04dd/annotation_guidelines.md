# Phase 4D-D Linguistic and Legal Annotation Guidelines
## Ground-Truth Dependency Annotation for Contractual Provisions

### 1. Objective and Theoretical Framework

The primary task of LexAudit Phase 4D-D is defined as:
> **The detection of broken explicit textual or structural dependencies in contractual provisions.**

This benchmark strictly isolates objective dependency violations from stylistic, customary, or subjective drafting variations:
- **Explicit Textual Dependencies**: Anaphoric discourse markers (e.g., *"notwithstanding the foregoing"*, *"the preceding sentence"*), explicit cross-references (e.g., *"pursuant to Section 2.1 above"*, *"as set forth in Section 4.2 hereof"*), and defined term instantiations that depend on prior textual introduction.
- **Distinction from Non-Defects**:
  - *Customary Clause Order*: Placing governing law or notices before representations is a non-standard drafting style, not a broken textual dependency.
  - *Substantive Contradictions*: Conflicting business terms (e.g., 30-day payment vs. 60-day payment) are legal contradictions, not discourse dependency breaks.
  - *Commutative Covenants*: Independent commercial covenants (e.g., Notices, Severability, Governing Law) are logically commutative and can swap positions without breaking anaphoric links.

---

### 2. Label Taxonomy

Each evaluated candidate case must be classified into exactly one of the following primary statuses:

| Label Status | Description | Required Evidence |
| :--- | :--- | :--- |
| `VERIFIED_POSITIVE` | An explicit forward-pointing or anaphoric dependency has been definitively inverted, causing the referencing provision to precede its antecedent or rendering directional markers contradictory. | Exact referencing span, exact antecedent span, proof of cross-clause boundary, demonstration of broken presupposition. |
| `VERIFIED_NEGATIVE` | Clause repositioning has occurred, but all internal and cross-clause textual dependencies remain intact and fully resolvable. | Demonstration of intra-clause antecedent locality, coupled block co-movement, or covenant commutativity. |
| `AMBIGUOUS` | Dependency validity is uncertain, conflicting, or subject to competing legal canons of construction (e.g., scrivener's error vs. literalism). | Specific rationale detailing conflicting interpretations; queued for human legal adjudication. |
| `INVALID_TRANSFORMATION` | The transformation introduced ungrammatical artifacts, truncated provisions, or destroyed document syntax outside the dependency relationship. | Diagnostic description of syntax or segmentation corruption. |
| `REVIEW_REQUIRED` | Algorithmic extraction or resolution confidence is intermediate; requires manual check before benchmark admission. | Resolution record highlighting low confidence score or boundary ambiguity. |
| `EXPERT_ADJUDICATION_REQUIRED` | Complex contractual covenant interaction where only admitted legal counsel can determine substantive defect status. | Detailed memorandum submitted to expert legal adjudication queue. |

---

### 3. Step-by-Step Annotation Decision Rules

```
                      [Candidate Case]
                             │
            Does the provision contain an explicit
            reference or anaphoric marker?
                             ├── No ───> [NOT_A_DEPENDENCY_CANDIDATE]
                             │
                            Yes
                             │
            Where is the antecedent located?
               ├── Inside same clause ───> If clause moves intact:
               │                           [VERIFIED_NEGATIVE]
               │                           (INTRA_CLAUSE_DISCOURSE_PRESERVATION)
               │
               └── Across clause boundaries
                             │
            What transformation occurred?
               ├── Referencing clause moved BEFORE antecedent:
               │   ├── Deterministic section link ("Section 2.1 above") ──> [VERIFIED_POSITIVE]
               │   └── Unresolved discourse marker without section ───────> [AMBIGUOUS]
               │
               ├── Both antecedent & referencing clauses moved together:
               │   └── Relative order preserved ─────────────────────────> [VERIFIED_NEGATIVE]
               │                                                           (COUPLED_BLOCK_PRESERVATION)
               │
               ├── Independent covenants swapped without cross-reference:
               │   └── Zero cross-references between provisions ──────────> [VERIFIED_NEGATIVE]
               │                                                           (COMMUTATIVE_SWAP)
               │
               └── Directional contradiction ("Section X below" moved after Section X):
                   └── Numerical reference valid, directional marker false -> [AMBIGUOUS]
```

---

### 4. Positive Case Criteria (`VERIFIED_POSITIVE`)

To qualify as a verified positive, all four of the following criteria must be affirmatively proven:
1. **Identifiable Explicit Antecedent**: The referencing clause must contain an explicit cross-reference (e.g., `Section 3.2`) or directional anaphoric marker (`as stated above`) whose target provision exists at a known clause index $A$.
2. **Cross-Clause Boundary**: The antecedent must reside in a distinct clause from the referencing clause ($A \ne R$). Intra-clause dependencies cannot be scored as clause-level violations.
3. **Inversion of Sequence**: In the original document, $A < R$. In the transformed sequence, the referencing clause is relocated such that $R_{pert} < A_{pert}$.
4. **Demonstrable Semantic/Structural Failure**: The reader or legal interpreter encounters a reference to a defined term, obligation, or condition that has not yet been introduced, or an explicit directional pointer (`above`) that points upward into non-existent prior text.

---

### 5. Hard Negative Criteria (`VERIFIED_NEGATIVE`)

Hard negatives are designed to defeat superficial models that flag any clause displacement as an error. To qualify as a hard negative, the case must satisfy one of the following archetypes:
1. **Intra-Clause Discourse Preservation (`INTRA_CLAUSE_DISCOURSE_PRESERVATION`)**:
   - The clause contains discourse phrases such as *"notwithstanding the foregoing"* or *"the preceding sentence"*.
   - Positional analysis verifies that the phrase occurs at sentence index $\ge 1$ within a multi-sentence clause.
   - The antecedent is the immediately preceding sentence within that same clause.
   - The clause is relocated, but because the entire clause moves intact, the intra-clause antecedent relationship is completely unaffected.
2. **Coupled Block Co-Movement (`COUPLED_BLOCK_PRESERVATION`)**:
   - Clause $R$ references Clause $A$.
   - Both $A$ and $R$ are moved together as a contiguous block $[A, R]$ to a new position in the agreement.
   - Because $A$ still precedes $R$, the dependency is fully preserved.
3. **Independent Covenant Commutativity (`INDEPENDENT_COVENANT_COMMUTATIVE_SWAP`)**:
   - Two standard commercial provisions (e.g., Section 11.2 Notices and Section 11.8 Governing Law) are swapped.
   - Neither provision cites or presupposes the other.
   - Under standard commercial contract drafting, these provisions are commutative.
4. **Front-Loaded Definitions or Dispute Resolution (`FRONT_LOADED_DEFINITIONS`)**:
   - Moving the Definitions Article to the opening of the agreement (Section 1) or placing Dispute Resolution upfront represents an established commercial contract structure, creating no broken references.

---

### 6. Ambiguous Case Criteria (`AMBIGUOUS`)

Cases must be labeled `AMBIGUOUS` when:
1. **Deictic Directional Contradiction**: A clause specifies *"Section 5 below"*. If relocated after Section 5, the section number remains resolvable in the contract, but the word *"below"* is false. In contract law, courts may disregard *"below"* as a harmless scrivener's error or enforce literal terms.
2. **Unresolved Cross-Clause Discourse Reference**: A clause beginning with *"Notwithstanding the foregoing"* at sentence 0 is moved to a new position. Without an explicit section number, it is uncertain whether the preceding clause in the new position provides a viable antecedent.
3. **Intervening Subsection Displacement**: A clause referencing Section 2 is moved between Subsections 2.1 and 2.2. While Section 2 precedes it, the internal subsection hierarchy of Article 2 is disturbed.

---

### 7. Reviewer Protocol and Independence

- Annotators and reviewers evaluate cases using [annotation_queue.csv](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/research/dependency_ground_truth_phase_04dd/annotation_queue.csv).
- Reviewers are provided with:
  1. `parent_document_id` and document family.
  2. Exact referencing text span and clause ID.
  3. Exact antecedent text span and clause ID.
  4. Original and perturbed clause positions.
  5. Deterministic transformation type.
- **Zero Detector Prediction Exposure**: At no point are model predictions or benchmark detector outputs displayed to the annotator. Annotator decisions are recorded in `reviewer_verdict` and `adjudication_notes`.
