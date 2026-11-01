# Phase 4D Independent Ground-Truth Oracle Validation

## 1. Oracle Separation and Circularity Prevention
To ensure rigorous adversarial testing, the Ground-Truth Oracle (`src/redteam/oracle.py`) is strictly decoupled from the system under test:
- **No Circularity**: The Oracle does **NOT** call `CrossReferenceChecker`, `DateLogicChecker`, or `UnifiedAuditor`.
- **Independent Verification Mechanics**:
  - For Displacement (P1) and Swap (P2): The Oracle inspects permutation lists and sequence indices directly.
  - For Duplication (P3/P4): The Oracle performs string hash checks and clause ID counting.
  - For Dangling References (P5/P6): The Oracle parses section headings via standard regex (`r"(?i)Section\s+(\d+)"`) and checks if the cited target exists in the document's section inventory.
  - For Date Inversion (P7): The Oracle parses explicit ISO dates using Python's standard `datetime` module and independently confirms whether $T_{\text{term}} < T_{\text{eff}}$.
  - For Deletion (P8): The Oracle confirms both the removal of the clause and the existence of surviving references in other clauses that target the removed section.
  - For Clean Negative Controls (P9): The Oracle validates that zero perturbations were introduced and all references and dates remain valid.

## 2. Oracle Rejection & Abstention Discipline
If a scenario parameter configuration fails independent validation (e.g., target section already exists, date inversion does not result in an earlier date, or no-op move), the Oracle rejects the scenario with `valid_transformation=False` and marks it `INVALID_SCENARIO`, disqualifying it from strict evaluation.
