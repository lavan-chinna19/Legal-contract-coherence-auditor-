# Phase 4D-C Annotation Guidelines

## Overview
These annotation guidelines govern the labeling of legal contract structural coherence in the Phase 4D-C independent benchmark. All labeling must follow objective, linguistically verifiable discourse and cross-reference criteria without circular dependence on model heuristics.

## Scope of Evaluated Coherence Tasks
1. **Task A — Textual Discourse Coherence**: Focuses on anaphoric discourse presuppositions. A clause that explicitly refers to preceding discourse (e.g., "the preceding provision", "the foregoing", "as defined above") requires its antecedent to appear earlier in the linear sequence. If reordered such that the antecedent appears after the referent, it constitutes a `VERIFIED_DISCOURSE_DEPENDENCY_VIOLATION`.
2. **Task B — Explicit Structural Dependencies**: Verifies whether numbered cross-references (e.g. "pursuant to Section 2.1") remain valid under sequence displacement.
3. **Task C — Content-Level Legal Logic**: Covers contradictory covenants (out of scope for pure sequence ordering).
4. **Task D — Conventional Document Organization**: Descriptive ordering conventions (e.g. title -> recitals -> covenants -> boilerplate -> execution). Deviation from conventional organization without broken discourse dependencies is labeled `VALID_NONCANONICAL_ORDER`.
5. **Task E — Position Recovery**: Measures ranking recovery of displaced provisions.

## Ground-Truth Assignment Rules
- **Rule 1 (Canonical Stability)**: Original, author-drafted SEC EDGAR contracts are labeled `VALID_CANONICAL_ORDER`.
- **Rule 2 (Discourse Defect Verification)**: Displacements that strand explicit backward discourse markers are labeled `VERIFIED_DISCOURSE_DEPENDENCY_VIOLATION`.
- **Rule 3 (Commutative Swaps)**: Swapping independent covenants with no shared discourse references is labeled `VALID_NONCANONICAL_ORDER`.
- **Rule 4 (Hard Negatives)**: Front-loaded dispute resolution or definitions are standard commercial drafting options and must be labeled `VALID_NONCANONICAL_ORDER`.
- **Rule 5 (Conservative Exclusion)**: Any permutation where discourse impact is disputed or indeterminate must be labeled `AMBIGUOUS` and excluded from binary detection metrics.
