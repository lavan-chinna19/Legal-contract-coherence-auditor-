# Phase 4D-D-A Task Boundary and Research Scope Specification
## Rigorous Separation of Contract Discourse Dependencies, Reference Integrity, Content Consistency, and Editorial Style

### 1. The Core Scientific Fallacy

In Phase 4D-D, an evaluation benchmark was constructed where 30 cases were labeled as `VERIFIED_POSITIVE` solely because a clause referencing a numbered section (e.g., *"pursuant to Section 4"*) was moved before Section 4.

**The Fallacy**: In contract law and document grammar, a numbered cross-reference such as *"Section 4"* or *"Section 1.10 of this Agreement"* is **non-directional**. Whether Section 4 appears on page 2 or page 20, as long as Section 4 exists within the four corners of the agreement, the reference resolves without ambiguity. Physical order inversion alone is **neither** proof of a broken reference **nor** anaphoric presupposition failure.

To prevent evaluation conflation, Phase 4D-D-A establishes strict, non-overlapping task boundaries across four distinct NLP problem domains.

---

### 2. The Four Distinct Research Targets

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                             CONTRACT AUDIT TAXONOMY                              │
├─────────────────────────┬─────────────────────────┬──────────────────────────────┤
│ Task Scope              │ Defining Invariant      │ Typical Defect Mechanism     │
├─────────────────────────┼─────────────────────────┼──────────────────────────────┤
│ Task A: Order-Sensitive │ Position-dependent      │ • "Section X above" inverted │
│ Discourse Dependency    │ deictic or anaphoric    │ • Boundary discourse marker  │
│                         │ expressions             │   bound to wrong antecedent  │
├─────────────────────────┼─────────────────────────┼──────────────────────────────┤
│ Task B: Reference       │ Unique resolvability of │ • Section target deleted     │
│ Integrity               │ identifiers regardless  │ • Section target misnumbered │
│                         │ of document position    │ • Duplicate section headings │
├─────────────────────────┼─────────────────────────┼──────────────────────────────┤
│ Task C: Content         │ Semantic compatibility  │ • Contradictory deadlines    │
│ Consistency             │ of substantive legal    │ • Conflicting payment terms  │
│                         │ obligations             │ • Mutually exclusive duties  │
├─────────────────────────┼─────────────────────────┼──────────────────────────────┤
│ Task D: Editorial       │ Customary arrangement   │ • Governing law placed first │
│ Organization            │ and structural hierarchy│ • Definitions before parties │
│                         │ of provisions           │ • Boilerplate covenant order │
└─────────────────────────┴─────────────────────────┴──────────────────────────────┘
```

---

### 3. Detailed Task Definitions

#### Task A: Order-Sensitive Discourse Dependency
- **Definition**: The detection of broken dependencies in expressions whose meaning, validity, or referent is strictly determined by physical document sequence.
- **Linguistic Markers**:
  - *Deictic directional pointers*: *"Section 2.1 above"*, *"Section 8 below"*, *"as stated above"*.
  - *Immediate-predecessor anaphora*: *"Notwithstanding the foregoing"*, *"the preceding sentence"*, *"in the immediately preceding section"*.
  - *Sequential process dependencies*: Provisions that condition action on steps introduced earlier without a self-contained section number.
- **Defect Criterion**: The clause is displaced such that:
  1. The deictic pointer becomes geographically false (e.g. *"above"* points to text that now follows).
  2. The intended antecedent changes to an unintended intervening provision, creating referential corruption.
- **Evaluation Rule**: Only Task A cases belong in the Order-Sensitive Dependency Benchmark.

#### Task B: Reference Integrity
- **Definition**: The verification that explicit numeric identifiers, defined terms, and schedule citations resolve to valid, unique, and existing anchors within the document.
- **Linguistic Markers**: *"pursuant to Section 4"*, *"as set forth in Section 1.10 of this Agreement"*, *"subject to Exhibit A"*.
- **Defect Criterion**: The referenced section does not exist (dangling pointer), is duplicated (ambiguous pointer), or was deleted.
- **Non-Defect Under Reordering**: If Section 4 is moved from page 5 to page 15, the reference *"pursuant to Section 4"* remains 100% resolvable. **Scoring order inversion of non-directional references as coherence failures conflates Task B with Task A.**

#### Task C: Content Consistency
- **Definition**: The detection of substantive contractual contradictions, incompatible covenants, or impossible conditions of satisfaction.
- **Examples**: Section 3.1 mandates delivery within 30 days, while Section 5.4 mandates cancellation if delivery is not made within 15 days; conflicting indemnification liability caps.
- **Non-Conflation**: A substantive contradiction is a legal conflict, not a broken discourse dependency.

#### Task D: Editorial Organization
- **Definition**: The evaluation of standard drafting conventions, section modularity, and customary contract layout.
- **Examples**: Front-loading the Definitions Article to the contract opening; swapping the order of Notices and Governing Law; placing dispute resolution upfront.
- **Non-Defect Under Law**: In commercial contracting, administrative covenants are commutative. Displacing them represents stylistic variation, not a structural or discourse defect.

---

### 4. Prohibition on Cross-Task Metric Conflation

1. **Success on Task B is NOT Success on Task A**: A model that detects deleted sections (Task B) has not proven any capability to detect order-sensitive discourse coherence (Task A).
2. **Success on Task D is NOT Coherence Auditing**: Flagging standard commercial reorderings (e.g. notices swapped with governing law) as defects reflects naive positional bias, not deep discourse comprehension.
3. **Purity of the Order-Sensitive Benchmark**:
   - In [verified_order_sensitive_cases.csv](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/design/ui_redesign/phase_04dda/verified_order_sensitive_cases.csv), **only genuine Task A cases** are admitted.
   - All 16 non-directional references from Phase 4D-D are explicitly classified as `NONDIRECTIONAL_REFERENCE_STILL_VALID` and excluded from Task A positive evaluation.
