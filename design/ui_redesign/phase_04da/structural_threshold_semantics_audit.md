# Structural Detection Threshold Semantics Audit (Priority One)

**Document ID**: `PHASE_04DA_THRESHOLD_AUDIT`  
**Evaluation Scope**: Priority One — Meaning and Operational Validity of the Reported "0.08" Structural Anomaly Threshold  
**Auditor Conclusion**: `PHASE_4D_CRITERION_INCORRECT`  

---

## 1. Executive Summary

Phase 4D reported that 0 out of 6 structural perturbations (clause displacement and clause swapping) were detected under a reported threshold of `0.08`, stating:
> *"Channel B score delta (0.0152) fell below anomaly threshold (0.08)."*

An exhaustive, line-by-line source code inspection across the entire LexAudit codebase reveals that **this comparison is scientifically and operationally incorrect**.

1. **`0.08` does not exist anywhere in LexAudit's production scoring configuration.**
   It is not in `src/config.py`, not in `src/scoring/severity.py`, not in `src/scoring/pipeline.py`, nor in any calibrated checkpoint file.
2. **Production anomaly detection operates on absolute composite scores ($S \ge 0.50$), not on differential score shifts ($\Delta S$).**
   In production, a clause is marked as an anomaly (`is_anomaly=True`) if and only if its ensembled combined score satisfies $S_i \ge 0.50$ (Medium Severity) or $S_i \ge 0.65$ (High Severity), or if a single channel breach occurs ($A_i \ge 0.70$ or $B_i \ge 0.70$).
3. **The `0.08` threshold was an unverified, ad-hoc research parameter introduced exclusively in the test runner.**
   It was defined as a default keyword argument `structural_anomaly_threshold: float = 0.08` in `src/redteam/runner.py` (Line 50) and applied to `max_affected_clause_b_delta`.
4. **Conflating an absolute anomaly threshold with a differential score change is a category error.**
   Comparing $\Delta S_B = S_B^{\text{perturbed}} - S_B^{\text{orig}}$ against an absolute severity tier threshold ($0.08$ vs $0.50$) misrepresents how LexAudit functions. Under production rules, the synthetic benchmark contracts had baseline scores $\sim 0.34$ (CLEAN tier, $0$ anomalies), and after displacement/swap, scores shifted by at most $+0.0152$ to $\sim 0.344$, remaining firmly in the CLEAN tier ($0$ anomalies).

---

## 2. Line-by-Line Code Grounding

### A. Origin and Definition of `0.08`
- **File**: [`src/redteam/runner.py`](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/src/redteam/runner.py#L46-L55)
- **Class**: `RedTeamExperimentRunner`
- **Lines 46–55**:
  ```python
  def __init__(
      self,
      auditor: Optional[UnifiedAuditor] = None,
      oracle: Optional[IndependentGroundTruthOracle] = None,
      structural_anomaly_threshold: float = 0.08  # <-- Uncalibrated runner parameter
  ):
      self.auditor = auditor or UnifiedAuditor()
      self.oracle = oracle or IndependentGroundTruthOracle()
      self.structural_anomaly_threshold = structural_anomaly_threshold
  ```
- **File**: [`src/redteam/reporting.py`](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/src/redteam/reporting.py#L228-L231)
- **Lines 228–231**:
  ```python
  for th in [0.02, 0.04, 0.06, 0.08, 0.10, 0.12, 0.15]:
      det = sum(1 for c in struct_cases if c.max_affected_clause_b_delta >= th or c.delta_anomaly_count > 0)
  ```

### B. The Evaluation Predicate in Phase 4D
- **File**: [`src/redteam/runner.py`](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/src/redteam/runner.py#L370-L381)
- **Lines 370–381**:
  ```python
  # Case 3: Structural Perturbations (P1 Displacement, P2 Swap)
  if ptype in (PerturbationType.P1_DISPLACEMENT, PerturbationType.P2_SWAP):
      # Evaluate Channel B discourse transition anomaly response
      if max_affected_b_delta >= self.structural_anomaly_threshold or delta_anomalies > 0:
          return DetectionStatus.DETECTED, True, None, None
      else:
          return (
              DetectionStatus.NOT_DETECTED,
              False,
              "WEAK_TRANSITION_SCORE_RESPONSE",
              f"Channel B score delta ({max_affected_b_delta:.4f}) fell below anomaly threshold ({self.structural_anomaly_threshold})."
          )
  ```

### C. The Actual Production Anomaly Predicate
- **File**: [`src/config.py`](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/src/config.py#L158-L163)
  ```python
  CHANNEL_A_OOD_THRESHOLD: float = 0.5
  CHANNEL_B_COHERENCE_THRESHOLD: float = 0.5
  ENSEMBLE_ALPHA: float = 0.5
  SEVERITY_HIGH_THRESHOLD: float = 0.75  # (Overridden to 0.65 in SeverityRanker)
  SEVERITY_MED_THRESHOLD: float = 0.50
  ```
- **File**: [`src/scoring/severity.py`](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/src/scoring/severity.py#L54-L175)
  - `SeverityRanker` sets:
    - `high_threshold = 0.65`
    - `high_single_threshold = 0.85`
    - `med_threshold = 0.50`
    - `med_single_threshold = 0.70`
    - `low_threshold = 0.35`
  - Predicate for `is_anomaly = True`:
    ```python
    is_anomaly = (
        (combined_score >= 0.65 and agreement_type == "CONCORDANT_ANOMALY")
        or (combined_score >= 0.75)
        or (max(channel_a_score, channel_b_score) >= 0.85 and combined_score >= 0.60)
        or (ci_lower is not None and ci_lower >= 0.40 and combined_score >= 0.60)
        or (combined_score >= 0.50)
        or (channel_a_score >= 0.70)
        or (channel_b_score >= 0.70)
    )
    ```

---

## 3. Discrepancy Analysis: Production vs Phase 4D

| Property | Actual Production Scorer | Phase 4D Red-Team Runner |
| :--- | :--- | :--- |
| **Input Variable** | Absolute clause scores ($S_A, S_B, S$) | Score change ($\Delta S_B = S_B^{\text{pert}} - S_B^{\text{orig}}$) |
| **Comparison Target** | `med_threshold = 0.50`, `med_single = 0.70` | `structural_anomaly_threshold = 0.08` |
| **Output Type** | Discrete severity tier (`HIGH`, `MEDIUM`, `LOW`, `CLEAN`) | Binary detection status (`DETECTED` / `NOT_DETECTED`) |
| **Document Context** | Evaluates document in isolation | Requires differential comparison against unperturbed baseline |
| **Anomaly Decision** | `is_anomaly = True` (severity $\in \{\text{HIGH}, \text{MEDIUM}\}$) | $\Delta S_B \ge 0.08$ OR $\Delta \text{anomalies} > 0$ |
| **Baseline Sensitivity** | Absolute scores must breach 0.50 | Any delta $\ge 0.08$ triggers detection regardless of tier |

---

## 4. Impact on Previously Reported Results

1. **Why Phase 4D Reported 0/6**:
   - The synthetic contracts (`SYNTH_DOC_01_MSA` and `SYNTH_DOC_02_SLA`) consist of well-formed legal text.
   - Channel A distance to LEDGAR centroids was $0.0000$ (clean standard language).
   - Channel B transition anomalies averaged $\sim 0.6800$.
   - Ensembled combined scores were $S = 0.5(0.0) + 0.5(0.6800) = 0.3400 < 0.3500$, categorizing all clauses as `CLEAN` (`is_anomaly=False`, $0$ document anomalies).
   - When clauses were displaced or swapped:
     - Perturbed Channel B scores shifted between $-0.0096$ and $+0.0152$.
     - Perturbed combined scores shifted between $-0.0048$ and $+0.0076$ (ending at $\sim 0.3440 < 0.3500$).
     - Perturbed clauses remained `CLEAN` (`is_anomaly=False`).
     - Document anomaly count did not increase ($\Delta \text{anomalies} = 0$).
     - The maximum affected Channel B delta ($+0.0152$) was far below the ad-hoc cutoff ($0.08$).
2. **Scientific Reinterpretation**:
   - The numerical outcome ($0/6$) was **reproducible**, but its scientific characterization was **incorrect**.
   - Phase 4D portrayed 0/6 as a failure of Channel B to reach its "anomaly threshold (0.08)".
   - In truth, the production detector did not flag the perturbations because:
     1. The synthetic baseline scores were deep within the `CLEAN` tier ($\sim 0.34 \ll 0.50$).
     2. The coherence model's transition dynamic range was severely compressed (all transitions produced probabilities $\sim 0.31 - 0.34$).
     3. Channel A dilution halved the transition score contribution ($0.5 \times B$).
     4. Neither the production anomaly predicate ($\text{combined} \ge 0.50$ or $B \ge 0.70$) nor the exploratory delta heuristic ($\Delta B \ge 0.08$) was triggered.

---

## 5. Audit Verdict

**`PHASE_4D_CRITERION_INCORRECT`**

*Justification*: The reported criterion compared a differential score delta ($\Delta S_B$) against an ad-hoc runner parameter (`0.08`), erroneously characterizing it as the production coherence anomaly threshold. Evaluated under the true production predicate (`SeverityRanker`), structural detection is $0/6$ because all perturbed clauses remained in the `CLEAN` severity tier. Evaluated under the exploratory score-delta heuristic, structural detection is $0/6$ because the maximum observed $\Delta S_B$ was $0.0152 < 0.08$. Both outcomes must be explicitly separated and documented under their respective definitions.
