# Phased Implementation & Migration Plan — Phases 2 to 6

**Module:** UI Redesign Program — Phase 1  
**Authors:** Senior Next.js/React Engineer & Full-Stack QA Lead  
**Date:** October 10, 2026  
**Status:** COMPLETE (Migration Plan)  

---

## 1. Migration Strategy & Phase Gate Model

To prevent regressions, maintain continuous testability, and protect the existing working codebase, the UI redesign executes through a strictly serialized 5-phase migration. Each phase defines concrete file changes, tests, rollback procedures, and a mandatory human authorization boundary.

```text
Phase 1 (Complete)  ──►  Phase 2             ──►  Phase 3             ──►  Phase 4             ──►  Phase 5             ──►  Phase 6
Architecture Audit       Foundation & Shell       Contract Reviewer        Analytics & XAI          Feedback & Polish        Release & QA
[Design Only]            [Theme, Shell, Nav]      [Split Workspace]        [Heatmap, Tokens]        [Verdicts, A11y]         [Full Regression]
      │                        │                        │                        │                        │                        │
      ▼                        ▼                        ▼                        ▼                        ▼                        ▼
[STOP / Approval]       [STOP / Approval]        [STOP / Approval]        [STOP / Approval]        [STOP / Approval]        [STOP / Release]
```

---

## 2. Phase-by-Phase Execution Roadmap

### Phase 2 — Foundation, Theme System & Application Shell
- **Primary Goal:** Implement the dual-theme token system (`globals.css`), hydration-safe theme provider, and the persistent application shell with lateral navigation.
- **Components Created:** `AppShell`, `HeaderBar`, `SidebarNav`, `ThemeToggle`, `StatusBadge`.
- **Files Modified:**
  - `frontend/src/app/globals.css` (Replace dark-only variables with light/dark semantic token classes).
  - `frontend/src/app/layout.tsx` (Add pre-hydration theme script and metadata).
  - New directory: `frontend/src/components/layout/`.
- **Functionality Preserved:** Existing application views remain functional; backend API routes untouched.
- **Required Verification:**
  - `npm run build` exits with code 0.
  - `npx eslint src/` exits with code 0.
  - Browser theme toggle switches themes instantly without page reload or FOUC.
- **Rollback Strategy:** Revert changes to `globals.css` and `layout.tsx`; remove `src/components/layout/`.
- **Authorization Boundary:** Stop for human review before proceeding to Phase 3.

---

### Phase 3 — Ingestion Workflow & Split-Screen Contract Reviewer
- **Primary Goal:** Build the flagship split-screen review workspace, continuous numbered clause document viewer, and asynchronous upload/polling pipeline.
- **Components Created:** `DocumentUploader`, `PrivacyConsentModal`, `AnalysisProgress`, `SplitReviewer`, `ClauseDocViewer`, `ClauseCard`, `FindingsInspector`.
- **Files Modified:**
  - New directory: `frontend/src/components/reviewer/`.
  - New directory: `frontend/src/components/upload/`.
  - `frontend/src/app/page.tsx` (Refactor review view to use new modular components).
- **Functionality Preserved:** Encrypted storage (`POST /v1/upload`), job polling (`/v1/jobs/{id}`), results retrieval (`/v1/jobs/{id}/results`).
- **Required Verification:**
  - Drag-and-drop `.txt` file upload succeeds.
  - Privacy checkbox guard disables submission until checked.
  - Polling completes in ~3 seconds.
  - Clicking a clause highlights it and updates the findings panel bidirectionally.
- **Rollback Strategy:** Git revert of `src/components/reviewer/` and `src/components/upload/`.
- **Authorization Boundary:** Stop for human review before proceeding to Phase 4.

---

### Phase 4 — Analytics Dashboard & Explainability Workspace (XAI)
- **Primary Goal:** Implement executive KPI cards, sequence coherence heatmap, deterministic rule cards, and Integrated Gradients token attribution chips.
- **Components Created:** `KPIGrid`, `MetricCard`, `SequenceHeatmap`, `RuleFlagCard`, `XaiTokenViewer`, `SensitivityChart`, `ClaimScopeBox`.
- **Files Modified:**
  - New directory: `frontend/src/components/analytics/`.
  - New directory: `frontend/src/components/xai/`.
  - `frontend/src/app/page.tsx` (Wire analytics and XAI views to modular components).
- **Functionality Preserved:** `/v1/xai/attribution`, `/v1/xai/sensitivity`, rule violation rendering.
- **Required Verification:**
  - Integrated Gradients token badges render with proportional green shading.
  - Hovering on a badge displays attribution score tooltip.
  - Heatmap bar accurately visualizes all clauses with click-to-navigate.
- **Rollback Strategy:** Remove `src/components/analytics/` and `src/components/xai/`.
- **Authorization Boundary:** Stop for human review before proceeding to Phase 5.

---

### Phase 5 — Reviewer Feedback Loop & UX Hardening
- **Primary Goal:** Implement inline and dedicated feedback forms with supported verdicts (`CONFIRM_ANOMALY` / `REJECT_ANOMALY`), accessible keyboard listeners, and mobile drawer transitions.
- **Components Created:** `FeedbackForm`, `QuickFeedbackBar`, `ErrorAlert`, `EmptyState`.
- **Files Modified:**
  - New directory: `frontend/src/components/feedback/`.
  - New directory: `frontend/src/components/common/`.
  - `frontend/src/app/page.tsx` (Final modular integration and removal of legacy code).
- **Functionality Preserved:** `POST /v1/feedback` SQLite persistence, zero plaintext logging.
- **Required Verification:**
  - Submitting feedback writes to `data/processed/feedback.sqlite` (table `feedback`).
  - Keyboard shortcuts (`j`/`k`, `ArrowDown`/`ArrowUp`) navigate clauses fluidly.
  - Responsive layout adapts cleanly across 1440px, 1024px, 768px, and 390px.
- **Rollback Strategy:** Revert `src/components/feedback/` and restore Phase 4 page state.
- **Authorization Boundary:** Stop for human review before proceeding to Phase 6.

---

### Phase 6 — Full-Stack Acceptance & Production Release
- **Primary Goal:** Execute full automated test suite, end-to-end browser reproduction, and prepare release commit packaging.
- **Testing Battery:**
  - `python -m pytest tests/ -v -ra` (116 passed, 2 skipped, 0 failed).
  - `npx eslint src/` (0 errors, 0 warnings).
  - `npm run build` (0 errors, production static compilation).
  - `python scripts/reproduce_browser_evidence.py` (All browser workflows pass via Chrome CDP).
- **Deliverables:** Updated audit packages under `audit/ui_redesign/` and explicit-path Git commit manifest.
- **Authorization Boundary:** Stop for human approval before `git commit` or `git push`.
