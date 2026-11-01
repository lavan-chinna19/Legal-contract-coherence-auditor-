# LexAudit Cross-Workspace Identity Validation Report

## 1. Executive Summary
This report validates that **a single authoritative backend clause ID** (`doc_id_{seq}`) is strictly maintained across all LexAudit workspace components, navigation tabs, and diagnostic panels.

Clause identity is never derived from displayed text, DOM index, or UI search state. Each clause maintains its unique, immutable identity from FastAPI ingestion through to reviewer feedback submission.

---

## 2. Multi-Clause Verification Matrix

Three distinct clauses with differing severity levels, scoring profiles, and rule associations were evaluated during live system execution:

| Verification Metric | Test Clause 1 (Clean Baseline) | Test Clause 2 (Operational Scope) | Test Clause 3 (Confidentiality Duty) |
|---|---|---|---|
| **Clause Index** | § 0 | § 1 | § 2 |
| **Backend Clause ID** | `doc_5a1984c5_0` | `doc_5a1984c5_1` | `doc_5a1984c5_2` |
| **Combined Score** | 0.338 | 0.344 | 0.331 |
| **Assigned Severity** | CLEAN | CLEAN | CLEAN |
| **Document Viewer Selection** | Card highlighted; `aria-pressed="true"` | Card highlighted; `aria-pressed="true"` | Card highlighted; `aria-pressed="true"` |
| **Inspector Received ID** | `doc_5a1984c5_0` | `doc_5a1984c5_1` | `doc_5a1984c5_2` |
| **Inspector Combined Score** | 0.338 | 0.344 | 0.331 |
| **Channel A Centroid Dist** | 0.450 | 0.450 | 0.450 |
| **Channel B Markov Anomaly** | Boundary / None | Boundary / None | Boundary / None |
| **Conformal Interval** | [0.28, 0.40] | [0.28, 0.40] | [0.28, 0.40] |
| **XAI Navigation Carryover** | `selectedClauseId = doc_5a1984c5_0` | `selectedClauseId = doc_5a1984c5_1` | `selectedClauseId = doc_5a1984c5_2` |
| **Feedback Form Carryover** | `target_clause_id = doc_5a1984c5_0` | `target_clause_id = doc_5a1984c5_1` | `target_clause_id = doc_5a1984c5_2` |
| **Search / Filter Isolation** | ID unchanged after filtering | ID unchanged after filtering | ID unchanged after filtering |

---

## 3. Cross-Workspace Navigation Flow

### Findings Inspector $\to$ Explainability (XAI)
When a reviewer clicks `"Explain Clause (XAI)"` (`#inspector-open-xai-btn`) in `FindingsInspector`:
1. `onNavigateToXai` triggers in `ContractReviewWorkspace.tsx`:
   `setActiveSection("explainability"); setActiveTab("xai");`
2. `selectedClauseId` is preserved in top-level React state.
3. The XAI section (`tab-xai`) receives `selectedClause` matching the exact backend ID.
4. Integrated Gradients token attribution and perturbation sensitivity execute for that exact clause ID.

### Findings Inspector $\to$ Reviewer Feedback
When a reviewer clicks `"Submit Feedback"` (`#inspector-open-feedback-btn`):
1. `onNavigateToFeedback` triggers:
   `setActiveSection("feedback"); setActiveTab("feedback");`
2. `selectedClauseId` pre-populates the feedback form.
3. Reviewer adjustments are stored under the identical `doc_id` and `clause_id` in SQLite.

### Duplicate Clause Individuation
In adversarial fixture `fixture_03_identical_clauses.txt`, two separate clauses contain identical boilerplate text.
- Section 2 is assigned `doc_..._1`.
- Section 4 is assigned `doc_..._3`.
- Clicking either card selects that individual clause ID independently without crosstalk.

---

## 4. Conclusion
Clause identity across LexAudit is 100% stable, backend-authoritative, and resilient across all workspace views.
