# Phase 4D Detector Capability Audit

## 1. Subsystem Investigation & Grounding
Before designing the red-team perturbation benchmark, the active implementations of all LexAudit detectors were inspected:
1. `src/scoring/channel_a.py`: Computes Mahalanobis / Euclidean distance to LEDGAR centroid embeddings.
   - **Properties**: Position-invariant bag-of-clauses semantic distance.
   - **Perturbation Reaction**: Unaltered by clause permutations ($\Delta S_A = 0.0$ for P1/P2). Sensitive only to lexical additions/substitutions (P4).
2. `src/scoring/channel_b.py`: Frozen RoBERTa/Legal-BERT adjacent pair classifier scoring $P(c_{i+1} \text{ follows } c_i)$.
   - **Properties**: Strictly local discourse transition coherence.
   - **Perturbation Reaction**: Sensitive to boundary disruption ($\Delta S_B$). Does not identify why a boundary was broken.
3. `src/rules/reference_checker.py`: spaCy dependency parsing and regex matching for internal section citations (`Section \d+`) and exhibits (`Exhibit [A-Z]`).
   - **Properties**: Exact-match inventory lookup against declared section numbers.
   - **Perturbation Reaction**: Flags `DANGLING_SECTION_REFERENCE` if citation targets undeclared section. Unsupported for informal or cross-document external citations.
4. `src/rules/date_checker.py`: `dateparser` regex and relation extraction between Effective, Expiration, and Termination dates.
   - **Properties**: Chronological order verification ($T_{\text{effective}} \le T_{\text{termination}}$).
   - **Perturbation Reaction**: Flags `CHRONOLOGICAL_INVERSION` if termination precedes effective date. Requires explicit temporal role headings or phrasing.
5. `UnifiedAuditor` (`src/rules/unified_pipeline.py`): Ensemble combining Channel A, Channel B, and deterministic rule violations into severity ratings.

## 2. Unsupported Capabilities & Explicit Exclusions
- **Duplicate Clause Detector**: The current system has **no dedicated duplicate detector**. Duplicates only affect adjacent Channel B discourse scores and aggregate contract length. Labeled as `DEDICATED_DUPLICATE_DETECTOR_UNAVAILABLE`.
- **Arbitrary Clause Deletion**: Deleting an arbitrary boilerplate clause creates no detectable rule anomaly unless the clause was the target of an active internal reference. Labeled as `DELETION_OCCURRED` without `DETECTABLE_CONSEQUENCE_PRESENT`.
- **External Exhibit Inventories**: If exhibits are referenced but neither declared nor attached in the contract body, `CrossReferenceChecker` only catches explicit `Exhibit [A-Z]` forms.

The complete capability mapping is formalized in `detector_capability_matrix.csv`.
