# Ground Truth Taxonomy for Contract Structural Coherence

## Taxonomy of Structural Conditions

### 1. Ground Truth Labels
- `VERIFIED_DISCOURSE_DEPENDENCY_VIOLATION`: The clause reordering creates an objective textual defect by displacing an explicit anaphoric referent (e.g. "the preceding paragraph", "subject to the immediately preceding") to precede its antecedent.
- `VERIFIED_EXPLICIT_STRUCTURAL_VIOLATION`: An explicit numbered section reference or schedule attachment relationship is severed or inverted.
- `VERIFIED_CONTENT_LOGIC_VIOLATION`: Mutually contradictory substantive obligations (content-level reasoning).
- `VALID_CANONICAL_ORDER`: Author-drafted intact contract from official SEC filings.
- `VALID_NONCANONICAL_ORDER`: Reordered contract where provisions are placed unconventionally but all legal and textual discourse relationships remain intact and interpretable.
- `SYNTHETIC_REORDERING_ONLY`: Arbitrary reordering without verified legal meaning alteration.
- `AMBIGUOUS`: Permutations where legal or discourse coherence is disputed, ambiguous, or lacks qualified legal expert consensus.
- `INSUFFICIENT_EVIDENCE`: Indeterminate context due to missing exhibits or redactions.
- `INVALID_TRANSFORMATION`: Perturbation failed programmatic validation (e.g. text loss or index misalignment).
- `ANNOTATION_PENDING`: Awaiting qualified independent human legal adjudication.

### 2. Task Category Mapping
| Task Code | Description | Eligible Anomaly Labels |
| :--- | :--- | :--- |
| `TASK_A` | Textual Discourse Coherence | `VERIFIED_DISCOURSE_DEPENDENCY_VIOLATION` |
| `TASK_B` | Explicit Structural Cross-References | `VERIFIED_EXPLICIT_STRUCTURAL_VIOLATION` |
| `TASK_C` | Substantive Contract Logic | `VERIFIED_CONTENT_LOGIC_VIOLATION` |
| `TASK_D` | Customary Document Layout | *Descriptive Only (Non-Anomaly)* |
| `TASK_E` | Displaced Clause Recovery | *Ranking MRR / Top-k* |
