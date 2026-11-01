# Phase 4D Experimental Protocol

## 1. Protocol Architecture
Every red-team experiment executes under a strict five-step protocol:
1. **Pre-flight Validation**: Verify source document integrity and baseline cleanliness.
2. **Deterministic Transformation**: Apply pure in-memory transformation $T(D, \theta, s) \to D'$.
3. **Independent Oracle Check**: Pass $D$ and $D'$ to `IndependentGroundTruthOracle.validate_transformation()` to evaluate transformation correctness without calling any pipeline detector.
4. **Frozen Auditor Evaluation**: Execute unchanged production `UnifiedAuditor` on both $D$ and $D'$. Extract real output fields:
   - Channel A scores ($S_A$)
   - Channel B discourse transition anomaly scores ($S_B$)
   - Unified combined scores ($S$) and severity classifications
   - `CrossReferenceChecker` finding flags
   - `DateLogicChecker` finding flags
5. **Differential Accounting & Failure Attribution**:
   - Compute $\Delta \bar{S}$, $\Delta S_B^{\max}$, $\Delta \text{Rules}$.
   - Check if the injected target condition was flagged by the relevant subsystem.
   - If undetected, assign an evidence-grounded failure classification.

## 2. Threshold Discipline
- Production anomaly threshold remains frozen at $\tau = 0.0800$.
- Experimental repair abstention threshold remains frozen at $\epsilon = 0.0050$.
- Zero thresholds were adjusted or post-hoc calibrated to artificially inflate detection metrics.
