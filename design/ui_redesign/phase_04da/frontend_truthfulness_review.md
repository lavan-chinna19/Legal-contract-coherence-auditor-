# Frontend Truthfulness and Scientific UI Review

**Document ID**: `PHASE_04DA_FRONTEND_TRUTHFULNESS`  
**Auditor**: Frontend QA Engineer & Senior ML Evaluation Auditor  
**Scope**: UI Metric Display Parity, Label Accuracy, State Representations, and Scientific Truthfulness  

---

## 1. Executive Summary

A critical responsibility of legal audit software is ensuring that the user interface never misleads attorneys or auditors about what a model has detected, what thresholds mean, or what capabilities exist.

In Phase 4D, the Self Red-Team Robustness Laboratory displayed a card stating `Threshold: ≥ 0.0800` directly under `Max Channel B Shift (ΔSB)`. A legal reviewer viewing this UI would naturally infer that `0.0800` is the production anomaly threshold of LexAudit. As proven in the Priority One audit, this is false: LexAudit's production anomaly threshold is `0.50` (or `0.70` single channel), and `0.08` was an offline, exploratory research heuristic for differential score shifts.

This review implemented targeted, minimal corrections to ensure scientific truthfulness across the UI without destabilizing the existing Robustness Lab workspace.

---

## 2. UI Truthfulness Corrections Implemented

### A. Threshold Disambiguation on Metric Card
- **File**: [`frontend/src/components/redteam/DetectionOutcomePanel.tsx`](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/frontend/src/components/redteam/DetectionOutcomePanel.tsx#L104)
- **Before**: `Threshold: ≥ 0.0800`
- **After**: `Exploratory Cutoff: ≥ 0.0800 (Prod: ≥ 0.50)`
- **Impact**: The user is immediately alerted that `0.0800` is an exploratory research cutoff for score deltas, while the actual production severity threshold requires composite scores $\ge 0.50$.

### B. Unambiguous NOT_DETECTED Scientific Semantics
- **File**: [`frontend/src/components/redteam/DetectionOutcomePanel.tsx`](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/frontend/src/components/redteam/DetectionOutcomePanel.tsx#L25-L29)
- **Before**: `"Perturbation applied and oracle-valid, but existing detectors remained silent."`
- **After**: `"Perturbation applied and oracle-valid; production model remained in CLEAN tier (no new anomaly findings; ΔSB below 0.08 exploratory cutoff)."`
- **Impact**: Distinguishes "no new findings / CLEAN severity" from an indeterminate silence or crashed detector.

### C. Backend Diagnosis Sync
- **File**: [`src/redteam/runner.py`](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/src/redteam/runner.py#L380)
- **Before**: `"Channel B score delta fell below anomaly threshold (0.08)."`
- **After**: `"Channel B score delta fell below exploratory delta cutoff (0.08); production severity tier remained CLEAN (score < 0.35)."`
- **Impact**: Syncs the backend diagnosis text rendered inside the amber callout box with the corrected scientific definitions.

---

## 3. Review of Remaining UI Displays

### A. Absolute vs Differential Score Displays
- The UI maintains strict separation between absolute scores ($S^{\text{orig}}, S^{\text{pert}}$) and differential shifts ($\Delta S_B, \Delta \bar{S}$).
- In `DetectionOutcomePanel.tsx`:
  - Card 1 displays $\Delta \bar{S}$ alongside baseline $\to$ perturbed mean scores ($0.3403 \to 0.3408$).
  - Card 2 displays $\Delta S_B$ on the target clause.
  - Card 4 displays the integer delta in production anomaly flags ($0 \to 0$).

### B. Task-Specific Results and Unsupported States
- **Exact Duplication (P3)**: Correctly mounts `ExperimentLimitations.tsx` displaying the amber warning:
  `"DEDICATED_DUPLICATE_DETECTOR_UNAVAILABLE — LexAudit does not possess a dedicated duplicate clause rule checker. Channel B transition response measured descriptively."`
- **Clean Negative Control (P9)**: Correctly displays `NOT_APPLICABLE (DESCRIPTIVE / CLEAN)` with a green badge, indicating that 0 false positives were produced on clean controls.

### C. Original-versus-Perturbed Clause Identity
- In `OriginalVsPerturbedView.tsx`:
  - Clauses are rendered with stable clause badges (`c00`, `c01`, etc.).
  - When clauses are reordered, the visual diff tracks the clauses by their persistent IDs and displays their new slot indices without altering the original document state.

### D. Navigation & Cross-Workspace Integrity
- Lateral switching between the 5 primary workspaces (Contract Review, Analytics, Explainability / XAI, Reviewer Feedback, and Robustness Lab) operates smoothly without state loss or memory leaks.

---

## 4. Verification Verdict

**`FRONTEND_TRUTHFULNESS_VERIFIED`**

The UI faithfully reflects the true mathematical capabilities, separates exploratory deltas from production anomaly severity tiers, and clearly labels unsupported capabilities.
