# Perturbation Scenario Taxonomy

| Category | Identifier | Target Detector | Ground Truth Condition | Evaluability Mode |
|---|---|---|---|---|
| P1 | Clause Displacement | Channel B (Discourse Transition) | SYNTHETIC_DISPLACEMENT | Strict ML Sensitivity |
| P2 | Clause Swapping | Channel B (Discourse Transition) | CLAUSE_SWAP | Strict ML Sensitivity |
| P3 | Exact Clause Duplication | Channel B / None | EXACT_DUPLICATION | Descriptive Only (`DEDICATED_DUPLICATE_DETECTOR_UNAVAILABLE`) |
| P4 | Near-Duplicate Clause | Channel A / B | NEAR_DUPLICATION | Exploratory Evaluation |
| P5 | Broken Internal Cross-Reference | CrossReferenceChecker | DANGLING_INTERNAL_REFERENCE | Strict Rule Verification |
| P6 | Missing Exhibit Reference | CrossReferenceChecker | DANGLING_EXHIBIT_REFERENCE | Strict Rule Verification |
| P7 | Date Chronology Inversion | DateLogicChecker | CHRONOLOGICAL_INVERSION | Strict Rule Verification |
| P8 | Clause Deletion | CrossReferenceChecker / None | CLAUSE_DELETION | Strict only if surviving dependency exists; else Descriptive |
| P9 | Clean Negative Control | Full Unified Pipeline | CLEAN_NEGATIVE_CONTROL | Strict False-Positive Evaluation |
| P10 | Combined Perturbations | Multi-Detector Ensemble | COMBINED_MULTI_PERTURBATION | Strict Compound Evaluation |
