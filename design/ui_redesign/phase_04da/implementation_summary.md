# Phase 4D-A Implementation Summary

**Program**: LexAudit Research Extension — Phase 4D-A  
**Date**: October 22, 2026  
**Auditor**: ML Research Auditor & Independent Verification Lead  
**Scope**: Structural Detection Validity, Scientific Metric Correction & Independent Evidence Audit  
**Overall Verdict**: **READY WITH DOCUMENTED SCIENTIFIC LIMITATIONS**  

---

## 1. Executive Summary

Phase 4D-A was commissioned to independently audit, validate, and scientifically correct the findings and metrics of the Phase 4D Self Red-Team Robustness Laboratory.

### Key Audit Accomplishments:
1. **Priority One Audit of Threshold `0.08`**: Source audit established verdict **`PHASE_4D_CRITERION_INCORRECT`**. The threshold `0.08` was an ad-hoc runner parameter (`max_affected_clause_b_delta >= 0.08`) applied to exploratory score shifts, completely absent from the production scoring pipeline (`src/config.py`, `src/scoring/severity.py`). Conflating score deltas with absolute anomaly thresholds represented a fundamental category error.
2. **Reconstruction of Production Detection Predicate**: Reconstructed the true production anomaly predicate governed by `SeverityRanker.assess_clause()` (composite score $S \ge 0.50$ or single-channel score $\ge 0.70$).
3. **Exact Numerical Re-Evaluation**: Evaluated all 6 structural cases (P1: 3, P2: 3) tracking both absolute anomaly scores and score deltas. Under the production pipeline, structural detection is **0/6 detected** because baseline synthetic contracts are in the `CLEAN` tier ($S \sim 0.3400$), and perturbations produce maximum score shifts of only $\Delta S_B = +0.0152$, resulting in perturbed scores of $\sim 0.3440 < 0.3500$, generating zero new anomalies.
4. **Mathematical Proof of Channel A Invariance**: Proven that Channel A OOD distance $A(c_i \mid D)$ is invariant under clause permutations ($A(c_i \mid D) = A(c_i \mid \pi(D))$). Empirically confirmed exact $\Delta S_A = 0.000000$ across all 66 clause comparisons.
5. **Decoupling of Conflated Benchmark Metrics**: Decoupled the heterogeneous Phase 4D combined matrix into 3 task-specific confusion matrices with valid integer denominators:
   - **Broken Cross-References**: TP=3, FP=0, FN=0, TN=2 ($N=5$). Precision=1.000, Recall=1.000.
   - **Date Chronology Inversions**: TP=2, FP=0, FN=0, TN=2 ($N=4$). Precision=1.000, Recall=1.000.
   - **Structural Perturbations (Strict)**: TP=0, FP=0, FN=5, TN=2 ($N=7$). Recall=0.000.
   - **Structural Perturbations (Broad)**: TP=0, FP=0, FN=6, TN=2 ($N=8$). Recall=0.000.
6. **Full Test Suite Verification**:
   - Backend pytest suite: **170 passed, 2 skipped, 0 failed in 117.67s** (exit code 0).
   - Frontend: `tsc --noEmit` (0 errors), `eslint` (0 errors), `npm run test:alignment` (17/17 passed), `npm run build` (compiled successfully).
7. **Complete 32-Check Browser Acceptance**: Executed all 32 checks live via Headless Chrome CDP on port 9222 against Next.js (port 3000) and FastAPI (port 8001): **32/32 CHECKS VERIFIED PASS (100.0%)**.

---

## 2. Source Audit: Semantics of Threshold `0.08`

| Property | Production Pipeline (`SeverityRanker`) | Red-Team Runner (`src/redteam/runner.py`) |
| :--- | :--- | :--- |
| **Source Location** | `src/config.py`, `src/scoring/severity.py` | `src/redteam/runner.py` (line 34) |
| **Variable / Field** | `SEVERITY_THRESHOLDS["ANOMALY_TIER_CUTOFF"] = 0.50` | `DEFAULT_STRUCTURAL_SHIFT_THRESHOLD = 0.08` |
| **Operates On** | Absolute combined score $S = 0.5 \cdot S_A + 0.5 \cdot S_B$ | Delta of Channel B score $\Delta S_B = S_B^{\text{pert}} - S_B^{\text{orig}}$ |
| **Assessment Domain** | Production anomaly severity (`CLEAN`, `LOW`, `MEDIUM`, `HIGH`) | Exploratory experimental sensitivity threshold |
| **Audit Verdict** | **Authoritative production ground truth** | **Category error to equate with production detection** |

---

## 3. Per-Clause Production Decisions for All Six Structural Cases

The structural anomaly detection conclusions derive strictly from **per-clause production decisions** (`SeverityRanker.assess_clause` across all 66 clauses), not from document-level mean scores or exploratory heuristics.

For each of the six original P1/P2 structural cases:
- Production predicate: Clause is anomaly $\iff S \ge 0.50$ (or $\max(S_A, S_B) \ge 0.70$).
- Baseline synthetic MSA has 11 clauses, all with $S < 0.35$ (`CLEAN` tier, `is_anomaly = False`).
- Across all 66 perturbed clauses, no clause crossed the $0.35$ threshold (max observed combined score was $0.3449$).

| Scenario ID | Perturbation Description | Max Combined ($S$) [Orig $\to$ Pert] | Max Channel A ($S_A$) [Orig $\to$ Pert] | Max Channel B ($S_B$) [Orig $\to$ Pert] | Severity Classifications [Orig $\to$ Pert] | `is_anomaly` Flags [Orig $\to$ Pert] | Prod Detection |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **SCEN_P1_01_DISP_DISTANT** | Section 2 (Scope) slot $1 \to 10$ | $0.3449 \to 0.3449$ | $0.0000 \to 0.0000$ | $0.6898 \to 0.6898$ | 100% `CLEAN` $\to$ 100% `CLEAN` | 0/11 $\to$ 0/11 False | **NOT DETECTED** |
| **SCEN_P1_02_DISP_MODERATE** | Section 6 (Term) slot $5 \to 2$ | $0.3449 \to 0.3449$ | $0.0000 \to 0.0000$ | $0.6898 \to 0.6898$ | 100% `CLEAN` $\to$ 100% `CLEAN` | 0/11 $\to$ 0/11 False | **NOT DETECTED** |
| **SCEN_P1_03_DISP_SUBTLE** | Section 4 (IP) slot $3 \to 4$ | $0.3449 \to 0.3449$ | $0.0000 \to 0.0000$ | $0.6898 \to 0.6898$ | 100% `CLEAN` $\to$ 100% `CLEAN` | 0/11 $\to$ 0/11 False | **NOT DETECTED** |
| **SCEN_P2_01_SWAP_ADJACENT** | Preamble $\leftrightarrow$ Scope (slots $0 \leftrightarrow 1$) | $0.3449 \to 0.3449$ | $0.0000 \to 0.0000$ | $0.6898 \to 0.6898$ | 100% `CLEAN` $\to$ 100% `CLEAN` | 0/11 $\to$ 0/11 False | **NOT DETECTED** |
| **SCEN_P2_02_SWAP_DISTANT** | Payment $\leftrightarrow$ Gov Law (slots $2 \leftrightarrow 8$) | $0.3449 \to 0.3449$ | $0.0000 \to 0.0000$ | $0.6898 \to 0.6898$ | 100% `CLEAN` $\to$ 100% `CLEAN` | 0/11 $\to$ 0/11 False | **NOT DETECTED** |
| **SCEN_P2_03_SWAP_SUBTLE** | Conf $\leftrightarrow$ Indemn (slots $4 \leftrightarrow 6$) | $0.3449 \to 0.3449$ | $0.0000 \to 0.0000$ | $0.6898 \to 0.6898$ | 100% `CLEAN` $\to$ 100% `CLEAN` | 0/11 $\to$ 0/11 False | **NOT DETECTED** |

**Direct Clause Target Breakdown**:
- `SCEN_P1_01`: Scope clause $S_B$ shifted from $0.6842 \to 0.6746$ ($\Delta S_B = -0.0096$). Combined $S$ shifted from $0.3421 \to 0.3373$.
- `SCEN_P1_02`: Term clause $S_B$ shifted from $0.6849 \to 0.6812$ ($\Delta S_B = -0.0037$). Combined $S$ shifted from $0.3424 \to 0.3406$.
- `SCEN_P1_03`: IP clause $S_B$ shifted from $0.6762 \to 0.6847$ ($\Delta S_B = +0.0085$). Combined $S$ shifted from $0.3381 \to 0.3423$.
- `SCEN_P2_01`: Preamble shifted $0.6728 \to 0.6880$ ($\Delta S_B = +0.0152$, largest single shift); Scope shifted $0.6842 \to 0.6794$. Both remain `CLEAN`.
- `SCEN_P2_02`: Gov Law shifted $0.6731 \to 0.6831$ ($\Delta S_B = +0.0100$); Payment shifted $0.6842 \to 0.6846$. Both remain `CLEAN`.
- `SCEN_P2_03`: Indemnification shifted $0.6794 \to 0.6827$ ($\Delta S_B = +0.0033$); Confidentiality shifted $0.6849 \to 0.6846$. Both remain `CLEAN`.

---

## 4. Root Cause of Structural Non-Detection

1. **Channel A Invariance**: Channel A distance $A(c_i \mid D) = \|e_i - \mu_{\text{LEDGAR}}\|_2$ depends solely on clause $c_i$ and static corpus centroids. Because clause text is preserved under permutations, Channel A produces an exact $\Delta S_A = 0.000000$ for all clauses.
2. **Channel B Logit Compression**: The fine-tuned Legal-BERT binary classification head outputs coherence probabilities compressed into $[0.3102, 0.3389]$ (anomaly scores $[0.6611, 0.6898]$). Across all 60 transition edges evaluated, total score spread was only $0.0287$, and the maximum single-transition delta was $+0.0152$.
3. **Weight Dilution & Tier Thresholds**: Combined score $S = 0.5 \cdot S_A + 0.5 \cdot S_B$ halves the $+0.0152$ Channel B shift to $+0.0076$. Since baseline synthetic contracts reside at $S \sim 0.3400$ (`CLEAN` tier, cutoff $0.3500$), perturbed scores reach $\sim 0.3440 < 0.3500$, remaining cleanly below the production anomaly cutoff ($0.50$).

---

## 5. Decoupled Confusion Matrices & Eligibility Tiers

### Three-Tier Eligibility Distinction
1. **Strict Five-Case Eligibility ($N=5$)**:
   - Includes `SCEN_P1_01`, `SCEN_P1_02`, `SCEN_P1_03`, `SCEN_P2_01`, `SCEN_P2_02`.
   - **Rationale**: Excludes `SCEN_P2_03_SWAP_SUBTLE` because swapping standard covenants (Confidentiality and Indemnification) represents an ambiguous ordering with no objective legal drafting standard or defect.
   - **Performance**: 0/5 detected (Recall = 0.0%, 95% Wilson CI **$[0.0000, 0.4345]$**).
2. **Six Original P1/P2 Transformations ($N=6$)**:
   - Includes all 6 structural permutations in the benchmark catalog.
   - **Performance**: 0/6 detected (Recall = 0.0%, 95% Wilson CI **$[0.0000, 0.3903]$**).
3. **Broader Analysis Including Deletion ($N=7$ or $N=8$)**:
   - Includes `SCEN_P8_01_DELETION_WITH_CONSEQUENCE` (where deleting Section 2 triggers a `DANGLING_SECTION_REFERENCE` symbol rule on surviving Section 4).
   - **Rationale**: Deletion alters contract content (token set) and is flagged by the symbolic reference resolver, NOT by neural coherence transition detection. It must not be conflated with discourse sequence sensitivity.

### Task-Specific Confusion Matrices Summary

#### Task 1: Broken Cross-Reference Detection ($N=5$)
- **Denominators**: Condition Positives $P=3$ (`P5_01`, `P5_02`, `P6_01`), Condition Negatives $N=2$ (`P9_01`, `P9_02`).
- **Confusion Matrix**: TP = 3, FP = 0, FN = 0, TN = 2.
- **Metrics**: Precision = 1.000, Recall = 1.000, F1 = 1.000, Accuracy = 1.000.
- **Wilson 95% CI for Recall**: **$[0.4385, 1.0000]$**.

#### Task 2: Date Chronology Inversion Detection ($N=4$)
- **Denominators**: Condition Positives $P=2$ (`P7_01`, `P7_02`), Condition Negatives $N=2$ (`P9_01`, `P9_02`).
- **Confusion Matrix**: TP = 2, FP = 0, FN = 0, TN = 2.
- **Metrics**: Precision = 1.000, Recall = 1.000, F1 = 1.000, Accuracy = 1.000.
- **Wilson 95% CI for Recall**: **$[0.3424, 1.0000]$**.

#### Task 3: Structural Perturbation Detection
- **Strict Scope ($0/5$ Positives, $2$ Negatives)**: TP = 0, FP = 0, FN = 5, TN = 2. Recall = 0.0% ($0/5$), Wilson 95% CI **$[0.0000, 0.4345]$**.
- **Broad Scope ($0/6$ Positives, $2$ Negatives)**: TP = 0, FP = 0, FN = 6, TN = 2. Recall = 0.0% ($0/6$), Wilson 95% CI **$[0.0000, 0.3903]$**.

---

## 6. Real Browser 32-Check Matrix Summary

- **Total Checks Defined**: 32
- **Checks Executed**: 32 (100.0%)
- **Passed Checks**: 32 (100.0%)
- **Failed Checks**: 0 (0.0%)
- **Unexecuted Checks**: 0 (0.0%)
- **Evidence Archive**: 13 PNG screenshots archived in `design/ui_redesign/phase_04da/evidence/`.
- **Full Report**: [browser_acceptance_report.md](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/design/ui_redesign/phase_04da/browser_acceptance_report.md).

---

## 7. Audit Commitments & Compliance
- **Zero Git Mutations**: Zero git commits created; zero files staged (`git add`); zero branches switched.
- **Preserved Pipeline Integrity**: Zero model weights, scoring formulas, or production thresholds altered.
- **Preserved User Environment**: User process PID 31904 (`http.server 8000`) untouched.
