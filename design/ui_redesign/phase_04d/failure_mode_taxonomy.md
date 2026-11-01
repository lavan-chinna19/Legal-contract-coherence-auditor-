# Phase 4D Failure Mode Taxonomy & Root Cause Analysis

## 1. Failure Categories & Root Cause Classification

| Failure Class | Frequency | Scenario Types | Proven Subsystem | Scientific Root Cause |
| :--- | :--- | :--- | :--- | :--- |
| **Weak Transition Score Response** | 6 cases | P1 (Displacement), P2 (Swap) | Channel B Scorer | Observed $\Delta S_B$ ($+0.0152$ to $-0.0096$) is smaller than the static anomaly threshold $\tau = 0.0800$. |
| **Dedicated Detector Unavailable** | 2 cases | P3 (Exact Duplication) | Detector Inventory | LexAudit has no duplicate detection component. Correctly classified as `NOT_APPLICABLE`. |
| **Exploratory / Unbound Semantic Variation** | 1 case | P4 (Near-Duplicate) | Channel A OOD | Lexical synonym substitution produces small embedding shifts that do not cross OOD thresholds. |
| **Descriptive Deletion (No Dependency)** | 1 case | P8 (Arbitrary Deletion) | Completeness Detector | Removing an independent section creates no syntactic broken reference. |

## 2. Research Implications
A negative robustness result is not an implementation failure; it is vital empirical insight into system boundaries. These results confirm that:
1. Static absolute thresholds designed for synthetic shuffle calibration are under-sensitive to subtle single clause displacements.
2. Rule checkers provide robust precision on targeted syntax, while neural coherence models provide continuous transition estimates that require differential calibration to flag isolated transpositions.
