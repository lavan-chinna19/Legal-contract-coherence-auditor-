# Phase 4D-D-A Dataset Validity and Reconciliation Audit Summary
## Rigorous Reclassification, Label Auditing, and Exact Count Reconciliation

### 1. Executive Summary

Phase 4D-D-A completes a comprehensive, evidence-grounded semantic audit of all 72 cases generated during Phase 4D-D.

**Key Findings**:
1. **Positive Ground-Truth Correction**: Out of the 30 purported positives in Phase 4D-D, only **9 cases** represent genuine, defensible **Order-Sensitive Violations (Task A)** where directional pointers (*"above"*) are contradicted and anaphoric introduction is inverted. The remaining 21 cases were invalidly categorized:
   - 16 cases featured non-directional section references (*"pursuant to Section 4"*) that remain 100% resolvable regardless of document order (`NONDIRECTIONAL_REFERENCE_STILL_VALID`).
   - 3 cases were redundant duplicate extractions from the same clause (`INVALID_TRANSFORMATION`).
   - 2 cases were false mappings to filing page headers rather than contract sections (`UNRESOLVED_SOURCE_MAPPING`).
2. **Negative Ground-Truth Correction**: Out of the 30 negatives, **15 cases** are verified order-sensitive or commutative preservations with zero external cross-reference side-effects. The remaining 15 cases require caution:
   - 9 cases contain external cross-references that require full document dependency graph validation (`PROVISIONAL_NEGATIVE_EXTERNAL_DEPENDENCY_AUDIT`).
   - 6 cases represent editorial/customary order variations (Task D) rather than discourse invariants (`EDITORIAL_REORDERING_NON_DEFECTIVE`).
3. **Eligible Order-Sensitive Dataset**: Exactly **24 verified cases** (9 positive violations, 15 clean negative preservations) are admitted to [verified_order_sensitive_cases.csv](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/design/ui_redesign/phase_04dda/verified_order_sensitive_cases.csv).
4. **Unresolved / Excluded Queue**: Exactly **48 cases** are isolated in [unresolved_cases.csv](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/design/ui_redesign/phase_04dda/unresolved_cases.csv).

---

### 2. Comprehensive Reconciliation Ledger ($N = 72$)

```
                                [Original Phase 4D-D Benchmark: 72 Cases]
                                                    │
        ┌───────────────────────────────────────────┼───────────────────────────────────────────┐
        │                                           │                                           │
  [30 Positives]                              [30 Negatives]                              [12 Ambiguous]
        │                                           │                                           │
  ├── 9 Verified Violations                   ├── 11 Verified Preservations               ├── 4 Deictic Conflicts
  │   (Task A - Eligible)                     │    (Task A - Eligible)                    │   (Task A - Provisional)
  ├── 16 Nondirectional Valid                 ├── 4 Commutative Reorderings               ├── 3 Unresolved Discourse
  │   (Task B - Excluded)                     │    (Task A - Eligible)                    │   (Task A - Provisional)
  ├── 3 Duplicate Invalids                    ├── 9 Provisional External Audits           ├── 3 Subsection Moves
  │   (Data Quality - Excluded)               │    (Task A - Provisional)                 │   (Task D - Provisional)
  └── 2 False Header Mappings                 └── 6 Editorial Reorderings                 └── 2 Cross-Article Moves
      (Data Quality - Excluded)                    (Task D - Excluded)                        (Task D - Provisional)
```

---

### 3. Detailed Label Reconciliation Table

| Original Category | Original Label | Record Count | Revised Phase 4D-D-A Classification | Revised Task Scope | Benchmark Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Positives** | `VERIFIED_POSITIVE` | **9** | `VERIFIED_ORDER_SENSITIVE_VIOLATION` | Task A: Order-Sensitive Dependency | **ELIGIBLE** |
| **Positives** | `VERIFIED_POSITIVE` | **16** | `NONDIRECTIONAL_REFERENCE_STILL_VALID` | Task B: Reference Integrity | **EXCLUDED** |
| **Positives** | `VERIFIED_POSITIVE` | **3** | `INVALID_TRANSFORMATION` | Data Quality (Duplicate Extractions) | **EXCLUDED** |
| **Positives** | `VERIFIED_POSITIVE` | **2** | `UNRESOLVED_SOURCE_MAPPING` | Data Quality (False Page Header '2') | **EXCLUDED** |
| **Negatives** | `VERIFIED_NEGATIVE` | **11** | `VERIFIED_ORDER_SENSITIVE_PRESERVATION` | Task A: Order-Sensitive Dependency | **ELIGIBLE** |
| **Negatives** | `VERIFIED_NEGATIVE` | **4** | `VERIFIED_COMMUTATIVE_REORDERING` | Task A: Order-Sensitive Dependency | **ELIGIBLE** |
| **Negatives** | `VERIFIED_NEGATIVE` | **9** | `PROVISIONAL_NEGATIVE_EXTERNAL_DEPENDENCY_AUDIT` | Task A: Provisional Graph Audit | **PROVISIONAL** |
| **Negatives** | `VERIFIED_NEGATIVE` | **6** | `EDITORIAL_REORDERING_NON_DEFECTIVE` | Task D: Editorial Organization | **EXCLUDED** |
| **Ambiguous** | `AMBIGUOUS` | **4** | `AMBIGUOUS_REQUIRES_EXPERT_ADJUDICATION` | Task A: Deictic Directional Conflict | **PROVISIONAL** |
| **Ambiguous** | `AMBIGUOUS` | **3** | `AMBIGUOUS_REQUIRES_EXPERT_ADJUDICATION` | Task A: Unresolved Boundary Discourse | **PROVISIONAL** |
| **Ambiguous** | `AMBIGUOUS` | **5** | `AMBIGUOUS_REQUIRES_EXPERT_ADJUDICATION` | Task D: Editorial / Subsection Structure | **PROVISIONAL** |
| **Totals** | — | **72** | — | — | **24 Eligible / 48 Excluded or Provisional** |

---

### 4. Mathematical and Invariant Verification

1. **Denominators Reconciled**:
   - $9 + 16 + 3 + 2 = 30$ Positive cases reconciled.
   - $11 + 4 + 9 + 6 = 30$ Negative cases reconciled.
   - $4 + 3 + 5 = 12$ Ambiguous cases reconciled.
   - $30 + 30 + 12 = 72$ Total benchmark cases reconciled.
   - $24 \text{ Eligible} + 48 \text{ Unresolved/Excluded} = 72$ Cases reconciled.
2. **Purity of the Eligible Benchmark**:
   - 100% of the 9 admitted positive cases feature proven directional pointers (*"above"*) that become physically false under displacement, accompanied by inverted anaphoric introduction of operative terms.
   - 100% of the 15 admitted negative cases are verified clean of external cross-reference side effects.
3. **Zero History Rewriting**:
   - The original Phase 4D-D files in `research/dependency_ground_truth_phase_04dd/` remain completely untouched.
   - All Phase 4D-D-A corrections are preserved in versioned audit manifests in `design/ui_redesign/phase_04dda/`.
