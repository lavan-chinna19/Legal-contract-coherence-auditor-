# Phase 4D Perturbation Engine Specification

## 1. Engine Core Principles
The perturbation engine (`src/redteam/`) is designed with the following scientific guarantees:
1. **Purity**: Transformations are deterministic functions `f(doc, params, seed) -> (new_doc, affected_ids, meta)`.
2. **Immutability**: Source clause text and source order are never modified in-place.
3. **Id Preservation**: Existing clauses retain their immutable `clause_id`. Injected duplicates or variants receive distinct IDs with traceable prefixes (`dup_` or `variant_`).
4. **Reversibility**: Every permutation has an inverse mapping allowing full reconstruction of the original sequence.

## 2. Taxonomy Implementation Summary (P1–P10)

| Code | Scenario | Pure Transformation Function | Parameters | Expected Semantic Condition | Target Detector |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **P1** | Clause Displacement | `apply_clause_displacement` | `source_slot`, `target_slot` | `SYNTHETIC_DISPLACEMENT` | Channel B Discourse |
| **P2** | Clause Swapping | `apply_clause_swap` | `slot_a`, `slot_b` | `PAIRWISE_CLAUSE_SWAP` | Channel B Discourse |
| **P3** | Exact Duplication | `apply_exact_duplication` | `source_slot`, `insert_slot` | `EXACT_DUPLICATION` | Descriptive (Unavailable) |
| **P4** | Near-Duplicate Variant | `apply_near_duplication` | `source_slot`, `insert_slot`, `substitution_mode` | `NEAR_DUPLICATE_VARIANT` | Channel A OOD |
| **P5** | Broken Cross-Reference | `apply_broken_reference` | `source_slot`, `old_target`, `new_target` | `DANGLING_INTERNAL_REFERENCE` | CrossReferenceChecker |
| **P6** | Missing Exhibit Citation | `apply_missing_exhibit` | `source_slot`, `exhibit_symbol` | `MISSING_EXHIBIT_REFERENCE` | CrossReferenceChecker |
| **P7** | Chronology Inversion | `apply_date_inversion` | `source_slot`, `inversion_pattern`, `contradictory_date` | `CHRONOLOGICAL_INVERSION` | DateLogicChecker |
| **P8** | Clause Deletion | `apply_clause_deletion` | `source_slot` | `DEPENDENCY_DELETION` | CrossReferenceChecker |
| **P9** | Clean Negative Control | `apply_negative_control` | None | `CLEAN_NEGATIVE_CONTROL` | None (Expect 0 Flags) |
| **P10** | Compound Perturbation | `apply_combined_perturbation` | `perturbation_list` | Multi-Condition Tuple | Multi-Detector Ensemble |
