# Component Inventory & Architecture — Phase 1

**Module:** UI Redesign Program — Phase 1  
**Authors:** Senior Next.js/React Engineer & Design System Engineer  
**Date:** October 10, 2026  
**Status:** COMPLETE (Component Architecture Inventory)  

---

## 1. Inventory Summary

This inventory catalogs every reusable component in the redesigned **LexAudit** architecture, contrasting the current monolithic implementation with the proposed modular hierarchy.

```text
┌────────────────────────────────────────────────────────────────────────┐
│                              AppShell                                  │
│  ┌───────────────┐  ┌───────────────────────────────────────────────┐  │
│  │  SidebarNav   │  │  HeaderBar (Brand | Status | ThemeToggle)     │  │
│  │               │  ├───────────────────────────────────────────────┤  │
│  │ - Overview    │  │                                               │  │
│  │ - Reviewer    │  │              VIEW CONTAINER                   │  │
│  │ - Analytics   │  │  (SplitReviewer / Analytics / XAI / Feedback) │  │
│  │ - Explain (XAI│  │                                               │  │
│  │ - Feedback    │  │                                               │  │
│  └───────────────┘  └───────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Detailed Component Specification Catalog

| # | Component Name | Classification | Current State | Redesigned Purpose | Backend Dependency | Key Interactions |
|:---:|---|:---:|---|---|---|---|
| **1** | `AppShell` | Layout | Monolithic container | Root application layout holding lateral sidebar, responsive drawer, and header | None | Collapsible sidebar, viewport adapt |
| **2** | `HeaderBar` | Layout | Inline `<header>` | Top bar displaying branding, research disclaimer, backend status, and theme toggle | `GET /health` | Click theme switch, open API modal |
| **3** | `SidebarNav` | Navigation | Inline `.tab-nav` | Lateral persistent navigation bar with 5 primary sections and badge counters | None | Route / view switching with active state |
| **4** | `ThemeToggle` | Control | Non-existent | Dark/Light mode toggle switch with persistent browser preference | None | Toggle theme, system preference sync |
| **5** | `PrivacyConsentModal` | Security / Gate | Raw inline checkbox | Dedicated modal surfacing `/v1/privacy-policy` retention terms before document submission | `GET /v1/privacy-policy` | Checkbox toggle, modal dismiss |
| **6** | `DocumentUploader` | Action | Native `<input type="file">` | Accessible drag-and-drop upload zone for `.txt` files with size and UTF-8 validation | `POST /v1/upload` | File drop, file select, clear file |
| **7** | `AnalysisProgress` | Feedback | Plain text status string | Visual progress bar with elapsed timer and asynchronous job polling status | `GET /v1/jobs/{job_id}` | Polling status listener, cancel action |
| **8** | `SplitReviewer` | Workspace | Monolithic tab | Flagship 2-panel review workspace coordinating document stream and findings | `GET /v1/jobs/{id}/results` | Bidirectional selection coordinator |
| **9** | `ClauseDocViewer` | Document Panel | Text cards | Left panel: continuous numbered contract text stream with severity pips | `DocumentResult.clauses` | Scroll sync, clause click selection |
| **10**| `ClauseCard` | Document Atom | Raw `<div>` | Individual clause container showing `§` sequence number, full text, and pip | `ClauseScoringResultModel` | Click to focus, keyboard focus |
| **11**| `FindingsInspector`| Findings Panel | Monolithic card | Right panel: detailed inspector for selected clause (Scores, XAI, Rules) | `ClauseScoringResultModel` | Next/Prev clause, trigger XAI |
| **12**| `SeverityBadge` | Data Display | Inline `.severity-tag`| Accessible severity tag combining color, text, and non-color geometric icon | `severity` string | Tooltip trigger for justification |
| **13**| `MetricCard` | Analytics | `.kpi-card` | Modular KPI card displaying metric value, title, tooltip, and confidence bounds | `scoring_result` | Hover tooltip for scientific definition |
| **14**| `SequenceHeatmap` | Analytics | Basic flexbox row | High-resolution interactive visual bar mapping clauses 1..N by anomaly score | `clauses` array | Click cell to jump to clause in reviewer |
| **15**| `RuleFlagCard` | Findings | Raw text string | Specialized card detailing broken internal pointers or chronological date inversions | `RuleFlagModel` | Link to involved clause index |
| **16**| `XaiTokenBadge` | Explainability | Inline `<span>` badges | Token attribution chip with color intensity mapped to attribution value | `ExplanationResult.tokens` | Hover tooltip with raw float attribution |
| **17**| `SensitivityChart` | Explainability | Raw delta text | Bar comparison showing baseline score vs. neighbor-perturbed score delta | `SensitivityExplanation` | Position selector (`prev` / `next`) |
| **18**| `ClaimScopeBox` | Scientific Disclosure | Hardcoded JSX text | Standardized bounded claim disclosure box (What this shows vs. does not show) | `ClaimScope` schema | Informational display |
| **19**| `FeedbackForm` | Form | Monolithic tab | Quick-action verdict submission interface (`CONFIRM_ANOMALY` / `REJECT_ANOMALY`) | `POST /v1/feedback` | Verdict select, provenance, submit |
| **20**| `EmptyState` | Feedback | Non-existent | Structured graphic and guidance message when no document or finding is active | None | Action button to upload |
| **21**| `ErrorAlert` | Feedback | Native browser `alert()` | Dismissible, accessible inline banner presenting structured API error messages | None | Dismiss, retry button |

---

## 3. Data Flow & State Binding Architecture

```text
[ DocumentUploader ]
        │ (POST /v1/upload & POST /v1/analyze)
        ▼
[ AnalysisProgress ] ─── Polling (GET /v1/jobs/{job_id})
        │
        ▼ (GET /v1/jobs/{job_id}/results)
┌───────────────────────────────────────────────────────────────┐
│                  Application Document State                   │
│  - docId: string                                              │
│  - totalClauses: number                                       │
│  - clauses: ClauseScoringResultModel[]                        │
│  - selectedClauseId: string (Unified Global Selection)        │
└──────────────┬────────────────────────────────┬───────────────┘
               │                                │
               ▼                                ▼
     [ ClauseDocViewer ]              [ FindingsInspector ]
     (Highlights selected)            (Inspects selected)
               │                                │
               └──────── Bidirectional ─────────┘
                         Sync Event
```

**Selection Invariance Principle:**  
When the user selects Clause $K$ in the `ClauseDocViewer`, that identical clause ID remains selected across the `FindingsInspector`, the `ExplainabilityWorkspace`, and the `FeedbackForm`. Navigating between views preserves the user's active focus without requiring re-selection.
