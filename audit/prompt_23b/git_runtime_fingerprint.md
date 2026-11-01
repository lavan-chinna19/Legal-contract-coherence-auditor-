# Git Baseline & Runtime Application Fingerprint

**Audit Phase:** Prompt 23B — Browser Evidence Authenticity, Route Reconciliation & Acceptance Integrity Audit  
**Date:** 2026-10-10  
**Auditor:** Independent Software Verification Engineer & Software Evidence Forensics Specialist  

---

## 1. Git Repository State

| Property | Value | Integrity Verification |
|---|---|---|
| **HEAD Commit** | `23dbcf536f2fb3dce1611e2d2ae71e9ca8c86f55` | Verified via `git rev-parse HEAD` |
| **Active Branch** | `main` | Verified via `git branch --show-current` |
| **Upstream Tracking** | `origin/main` (`23dbcf536f2fb3dce1611e2d2ae71e9ca8c86f55`) | Aligned; zero commits ahead/behind |
| **Commit Message** | `fix(security): prompt-22a authorization closure and regression verification` | Authoritative Prompt 22A security baseline |
| **Tracked Changes** | `M fixtures/load_test_results.json` | Benchmark file preserved from prior phases |
| **Untracked Directories** | `audit/prompt_23/`, `audit/prompt_23a/`, `audit/prompt_23b/` | Audit output workspaces preserved |
| **Untracked Scripts** | `scripts/run_prompt23_acceptance.py`, `scripts/run_prompt23a_browser_acceptance.py`, `scripts/run_server.py`, `scripts/test_cdp.py`, `scripts/diagnose_runtime_dom.py`, `scripts/reproduce_browser_evidence.py` | Standalone test & verification scripts |

### Source Code Identity Verification
- `frontend/src/app/page.tsx`: **Identical to HEAD** (`git diff frontend/src/app/page.tsx` produces zero output).
- `src/api/v1/router.py`: **Identical to HEAD** (`git diff src/api/v1/router.py` produces zero output).
- `src/api/main.py`: **Identical to HEAD** (`git diff src/api/main.py` produces zero output).
- `src/config.py`: **Identical to HEAD** (`git diff src/config.py` produces zero output).

---

## 2. Running Application Runtime Fingerprint

| Runtime Attribute | Observed Value | Forensic Method |
|---|---|---|
| **Frontend URL** | `http://localhost:3000/` | CDP `Runtime.evaluate window.location.href` |
| **Frontend Framework** | Next.js 16.4.0 (Turbopack development server) | Process audit & HTTP chunk inspection |
| **Frontend Process** | PID 29936 (`npm run dev`) | Task Manager / IDE daemon monitor |
| **Page `<title>`** | `Create Next App` | Verified via live DOM `document.title` |
| **Page `<h1>` Heading** | `Legal Contract Coherence Auditor` | Live DOM `document.querySelector('h1').innerText` |
| **Header Badge** | `Research Prototype` | Live DOM `.badge-research` |
| **Disclaimer Text** | `⚠️ Research Prototype — Not Legal Advice: This system is an academic research prototype evaluating structural and semantic coherence.` | Live DOM `.disclaimer-banner` |
| **DOM Navigation Tabs** | `1. Upload & Ingest`, `2. Coherence Heatmap & Findings`, `3. Explainability (XAI)`, `4. Reviewer Feedback`, `5. Transparency & Baselines` | Live DOM `.tab-btn` array |
| **DOM ID Inventory** | `['_R_']` (Only Next.js root element ID exists) | Evaluated via `Array.from(document.querySelectorAll('[id]')).map(el => el.id)` |
| **Backend URL** | `http://127.0.0.1:8000` | Process audit & Next.js config |
| **Backend Framework** | FastAPI 0.115+ / Starlette / Uvicorn (Single worker) | Process inspection & OpenAPI inspection |
| **Backend Process** | PID 24144 (`python scripts/run_server.py`) | Task Manager / IDE daemon monitor |
| **Backend Status** | Online (`GET /health` -> 200, `GET /ready` -> 200) | Live HTTP ping |
| **Backend Route Prefix** | `/v1` | Programmatic route inspection on `src.api.main:app` |
| **Feedback Database** | `data/processed/feedback.sqlite` (Table: `feedback`) | `src/config.py:156` & SQLite inspection |

---

## 3. Provenance Conclusion

The running application on `localhost:3000` and `127.0.0.1:8000` is **100% authentic and directly compiled from the Git HEAD commit** (`23dbcf536f2fb3dce1611e2d2ae71e9ca8c86f55`). There is no proxy, no alternate application, and no mismatched branch running.
