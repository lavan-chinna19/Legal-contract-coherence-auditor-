# Selection, Bidirectional Navigation & Cross-Workspace Validation
**LexAudit Phase 3 UI Redesign Program**

## 1. Overview
The contract review workspace requires synchronized, bidirectional selection between document clauses, inspector findings, sequential navigation buttons, macro heatmap blocks, and cross-workspace tabs (Explainability and Feedback).

---

## 2. Test Execution & Verified Behaviors

### 2.1 Initial Clause Selection
- **Expected**: First valid clause (§ 0, ID `doc_xxxxxxxx_0`) is selected automatically upon workspace mount.
- **Observed**: Card 0 renders with `.selected` class, `aria-pressed="true"`, and accent border indicator.
- **Inspector State**: `FindingsInspector` title renders `Clause § 0`, ID pill renders `doc_b6c220fb_0`.
- **Verdict**: PASS.

### 2.2 Direct Click Selection
- **Action**: User clicks on Clause 2 card (`#clause-card-doc_b6c220fb_1`).
- **Observed**:
  - Clause 2 card gains `.selected`.
  - Previous card deselects cleanly.
  - `FindingsInspector` updates immediately to `Clause § 1`, Combined Score `0.343`, Centroid Distance `0.119`.
  - Document scroll context is preserved without unexpected page jumping.
- **Verdict**: PASS.

### 2.3 Macro Heatmap Block Selection
- **Action**: User clicks on block 3 in `.sequence-heatmap-bar`.
- **Observed**: Clause 3 card becomes selected, scrolls into view in the document viewer, and inspector updates to Clause § 2.
- **Verdict**: PASS.

### 2.4 Sequential Prev / Next Stepper (`ClauseNavigator`)
- **Forward Traversal**:
  - Clicking `#next-clause-btn` advances selection from § 1 to § 2.
  - Active card updates, inspector updates.
- **Backward Traversal**:
  - Clicking `#prev-clause-btn` decrements selection from § 2 back to § 1.
- **Boundary Handling**:
  - At § 0 (first clause): `#prev-clause-btn` has `disabled={true}`, preventing underflow.
  - At § 4 (final clause): `#next-clause-btn` has `disabled={true}`, preventing overflow.
- **Verdict**: PASS.

### 2.5 Cross-Workspace Selection Carryover
- **To Explainability (XAI)**:
  - While Clause 2 (§ 1) is selected, user clicks `#inspector-open-xai-btn` ("Explain Clause (XAI)").
  - Workspace navigates to Tab 3 (`#tab-xai.active`).
  - Selected clause ID `doc_b6c220fb_1` is retained in React state and automatically populated in the XAI clause dropdown.
  - Screenshot captured: `design/ui_redesign/phase_03/evidence/10_cross_workspace_xai_carryover.png`.
- **To Reviewer Feedback**:
  - While Clause 2 is selected, user clicks `#inspector-open-feedback-btn` ("Submit Feedback").
  - Workspace navigates to Tab 4 (`#tab-feedback.active`).
  - Selected clause ID `doc_b6c220fb_1` is retained and populated in the feedback target clause selector.
  - Screenshot captured: `design/ui_redesign/phase_03/evidence/11_cross_workspace_feedback_carryover.png`.
- **Return to Review**:
  - User clicks Tab 2 (`#tab-results`).
  - Contract review workspace re-renders with Clause 2 (§ 1) still selected. No re-analysis triggered.
- **Verdict**: PASS.
