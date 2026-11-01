# Phase 4D Combined-Perturbation Experimental Findings

## 1. Compound Scenario Evaluation
Following validation of single-perturbation categories P1–P9, compound scenarios were evaluated:
1. `SCEN_P10_01_COMBINED_DISP_AND_REF`:
   - Injected Conditions: Clause Displacement (Slot 1 moved to End) + Broken Internal Reference (Section 4 cites Section 99).
   - Observed Output: `CrossReferenceChecker` registered `DANGLING_SECTION_REFERENCE` on Slot 4. Channel B registered transition boundary shifts ($\Delta S_B = -0.0096$).
   - Attribution: Verified match on the broken reference clause.
2. `SCEN_P10_02_COMBINED_DATE_AND_DUP`:
   - Injected Conditions: Date Chronology Inversion (Termination set to 2020) + Exact Clause Duplication (Preamble copied to Slot 7).
   - Observed Output: `DateLogicChecker` registered 2 rule flags (`INVERTED_CONTRACT_TERM` and `EXECUTION_AFTER_TERMINATION`). Channel B registered transition shifts ($\Delta S_B = +0.0003$).

## 2. Interaction Effects & Non-Additivity
- Compound disturbances do not interfere destructively with deterministic rule checker execution.
- Neural score responses remain localized to perturbed transition boundaries without cascading artificial anomalies across unrelated sections.
