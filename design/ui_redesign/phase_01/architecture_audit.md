# Architecture Audit & Current State Analysis — Phase 1

**Project:** Legal Contract Coherence Auditor ("LexAudit")  
**Module:** UI Redesign Program — Phase 1  
**Authors:** Senior LegalTech UX Architect, Senior Next.js/React Engineer, Integration Architect  
**Date:** October 10, 2026  
**Status:** COMPLETE (Read-Only Architectural Audit)  

---

## 1. Executive Summary

This architecture audit establishes the technical baseline of the **Legal Contract Coherence Auditor** across the frontend and backend boundaries. The application currently consists of a hardened Python/FastAPI backend and an academic research frontend built in Next.js 16. While the backend exhibits strong security, deterministic heuristics, dual-channel scoring, and explainability endpoints, the frontend remains a monolithic research dashboard with significant usability, aesthetic, and architectural limitations.

The objective of the UI Redesign Program is to elevate this academic prototype into an executive-grade, professional LegalTech contract intelligence platform ("LexAudit") while strictly preserving 100% of the backend functional architecture, cryptographic controls, and NLP models.

---

## 2. Actual Full-Stack Architecture

```text
┌────────────────────────────────────────────────────────────────────────┐
│                   NEXT.JS 16 RESEARCH FRONTEND                         │
│  - Framework: Next.js 16.4.0 (Turbopack, App Router)                   │
│  - View Engine: React 19.3.0, React-DOM 19.3.0                         │
│  - Language: TypeScript 5.x (Strict typing, no `any`)                  │
│  - Styling: Vanilla CSS (globals.css, 267 lines)                       │
│  - State & Lifecycle: Client-side React Hooks (useState, useEffect)    │
│  - Component Architecture: Monolithic page.tsx (772 lines)            │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ HTTP / REST (X-API-Key / Bearer)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                      FASTAPI HARDENED BACKEND                          │
│  - Framework: FastAPI 1.0.0 (Python 3.11.9, Starlette)                 │
│  - Concurrency & Runtime: Uvicorn Single-Worker (workers=1 required)   │
│  - Cryptography: Fernet AES-128-CBC + HMAC-SHA256 (STORAGE_ENCRYPTION) │
│  - Authentication: X-API-Key / Bearer with constant-time comparison    │
│  - In-Flight Storage: Process-local in-memory jobs store (_jobs dict)  │
│  - Data Retention: Automated 24h background artifact purge             │
│  - Persistence: SQLite / PostgreSQL for reviewer feedback              │
└───────────────────┬────────────────────┬────────────────────┬──────────┘
                    │                    │                    │
                    ▼                    ▼                    ▼
┌────────────────────────┐ ┌────────────────────────┐ ┌──────────────────┐
│  Segmentation & NLP    │ │ Dual-Channel Scoring   │ │ Deterministic    │
│  - Rule & spaCy Regex  │ │ - Channel A: Legal-BERT│ │ Rules            │
│  - Clause Chunking     │ │ - Channel B: Discourse │ │ - Reference Check│
│  - Tokenization        │ │ - Conformal Calibrator │ │ - Date Checker   │
└────────────────────────┘ └─────────────┬──────────┘ └──────────────────┘
                                         │
                                         ▼
                               ┌───────────────────┐
                               │ Explainability    │
                               │ - Integrated Grad │
                               │ - Sensitivity     │
                               └───────────────────┘
```

---

## 3. Frontend Architecture Inspection

### 3.1 Package Dependencies (`frontend/package.json`)
```json
{
  "name": "frontend",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "eslint"
  },
  "dependencies": {
    "next": "16.4.0",
    "react": "19.3.0",
    "react-dom": "19.3.0"
  },
  "devDependencies": {
    "@types/node": "^20",
    "@types/react": "^19",
    "@types/react-dom": "^19",
    "eslint": "^9",
    "eslint-config-next": "16.4.0",
    "typescript": "^5"
  }
}
```

**Key Finding:** There are currently **zero styling or UI component libraries** installed.
- No Tailwind CSS
- No Lucide / Heroicons (currently using raw Unicode emojis: ⚖️, 💾, 🔍)
- No Radix UI or headless primitives
- No charting library (currently using raw flexbox heatmaps)
- No CSS module adoption (page uses inline styles mixed with global utility classes)

### 3.2 Source File Structure
- `frontend/src/app/layout.tsx` (30 lines): App Router root layout with updated prototype metadata.
- `frontend/src/app/page.tsx` (772 lines): Single client-side monolithic component containing all state, network calls, tab routing, rendering, and modals.
- `frontend/src/app/globals.css` (267 lines): Global CSS defining a dark-only theme with 12 CSS variables and glassmorphic card classes.

---

## 4. Current Frontend UX & Engineering Deficiencies

| Deficiency Area | Current State | Technical Impact | UX & LegalTech Impact |
|---|---|---|---|
| **Layout & Architecture** | Single monolithic 772-line component | Any state update re-renders large DOM subtrees; difficult to maintain | Navigation feels sluggish; code cannot be scaled cleanly across features |
| **Document Navigation** | Tab-based navigation without deep-linking or routing | State is lost on refresh; no URL bookmarks for specific findings | Legal auditors cannot share or link specific audit findings with colleagues |
| **Review Experience** | Isolated clause cards with 150-char previews | User cannot see full contract context or adjacent clauses | Disconnected from legal workflow; lawyers need to see the entire agreement |
| **Theme & Aesthetics** | Dark-only theme with glassmorphism (`backdrop-filter`) | Difficult to read extended legal text; no light mode available | Fails professional legal standards where clean light surfaces are required |
| **Information Density** | Oversized KPI cards and loose spacing | Requires extensive scrolling to view 5+ clauses | High cognitive fatigue when auditing complex agreements |
| **Visual Charts** | Basic HTML flexbox divs (`.heatmap-bar`) | Cannot display multi-series trends, confidence intervals, or tooltips | Cannot intuitively visualize sequence flow or conformal intervals |
| **Explainability (XAI)** | Inline badges below cards with raw float tooltips | Badges are disconnected from the actual legal clause context | Explanations appear disjointed from the legal text they analyze |
| **Feedback Loop** | Dropdown with submit button in separate tab | Reviewer must switch tabs away from the contract to submit feedback | High friction; review should happen directly alongside the clause |
| **Accessibility & Contrast**| Hardcoded dark badge backgrounds | Dark-on-dark contrast can drop below 4.5:1 on low-gamma monitors | Does not strictly adhere to WCAG 2.2 Level AA requirements |
| **Mobile & Tablet** | Vertical stack collapsing into long page | Two-column tables overflow horizontally or wrap illegibly | Unusable on tablet and mobile viewports |

---

## 5. Preserved Backend Capabilities & Contract Boundaries

The redesign **MUST strictly preserve** the existing backend interfaces and operational characteristics:

1. **Reconciled REST Workflow:**
   - `POST /v1/upload` (multipart/form-data `file`) → `UploadResponse(doc_id, message)`
   - `POST /v1/analyze` (JSON `{doc_id}`) → `AnalyzeResponse(job_id, message)`
   - `GET /v1/jobs/{job_id}` → `JobStatusResponse(job_id, status, error)`
   - `GET /v1/jobs/{job_id}/results` → `UnifiedAuditReportModel`
   - `GET /v1/xai/attribution?doc_id=...&clause_id=...` → `ExplanationResult`
   - `GET /v1/xai/sensitivity?doc_id=...&clause_id=...` → `ExplanationResult`
   - `POST /v1/feedback` → `FeedbackResponse(feedback_id, message)`
   - `GET /v1/privacy-policy` → `PrivacyPolicyResponse`
   - `GET /health` & `GET /ready`
2. **Process-Local Concurrency:**
   - The backend runs with single-worker execution (`workers=1`) due to in-memory job coordination (`_jobs` dictionary).
   - The frontend must gracefully poll `GET /v1/jobs/{job_id}` at 1.0-second intervals until status is `COMPLETED` or `FAILED`.
3. **Cryptographic Storage:**
   - Raw contracts are encrypted with Fernet AES-128-CBC at rest. The frontend never receives persistent file paths, only authenticated `doc_id` references.
4. **Strict Feedback Validation:**
   - Only `CONFIRM_ANOMALY` and `REJECT_ANOMALY` are permitted by the backend router.
5. **Session-Only Contract History:**
   - The backend does **not** provide a `GET /v1/contracts` history list endpoint.
   - Any recent analysis cards in the redesigned UI must rely on client-side session state (`sessionStorage` or local memory), never an invented backend endpoint.
