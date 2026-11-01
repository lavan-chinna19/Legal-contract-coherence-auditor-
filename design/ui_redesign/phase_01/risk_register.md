# Risk Register & Architectural Safeguards — Phase 1

**Module:** UI Redesign Program — Phase 1  
**Authors:** Senior LegalTech UX Architect, Integration Architect & Security Reviewer  
**Date:** October 10, 2026  
**Status:** COMPLETE (Risk Register)  

---

## 1. Risk Matrix Overview

| Risk ID | Risk Domain | Severity | Likelihood | Impact Description | Architectural Safeguard |
|:---:|---|:---:|:---:|---|---|
| **RSK-01** | Backend Schema Drift | **HIGH** | Medium | Frontend assumes non-existent endpoints (e.g., `GET /v1/contracts`) | Explicit API contract mapping; session-only history stored in `sessionStorage` |
| **RSK-02** | React 19 Hydration FOUC | **MEDIUM** | High | Flash of wrong theme or React 19 hydration mismatch on first paint | Synchronous inline `<script>` in `layout.tsx` `<head>` sets `data-theme` prior to render |
| **RSK-03** | CPU Inference Latency | **HIGH** | Medium | Large contracts require 10–30s on CPU; users perceive frozen UI | Progress bar with active polling (`GET /v1/jobs/{id}`) and elapsed timer |
| **RSK-04** | Rate Limit Burst Exhaustion | **MEDIUM** | Low | Overly aggressive polling triggers 429 Too Many Requests | Fixed 1.0s polling interval; max 60 attempts (60s timeout); exponential backoff on retry |
| **RSK-05** | Legal Text Reformatting | **HIGH** | Low | CSS truncation or re-wrapping alters legal contract interpretation | Continuous full-text viewer with `white-space: pre-wrap` and `overflow-wrap: anywhere` |
| **RSK-06** | Secret / API Key Leakage | **HIGH** | Low | API keys exposed in browser console, URL query params, or DOM | Password-masked inputs (`type="password"`), zero plaintext logging, headers only |
| **RSK-07** | Client Ownership 404s | **MEDIUM** | Medium | Polling with mismatched API key yields confusing 404 | Error boundary catches 404 and guides user to check API Key authentication |
| **RSK-08** | Feedback Verdict Invalidation| **HIGH** | Low | Frontend submits unsupported verdict string, causing HTTP 422 | Hardcoded dropdown options strictly locked to `CONFIRM_ANOMALY` / `REJECT_ANOMALY` |
| **RSK-09** | React 19 Library Incompatibility| **MEDIUM** | High | Installing component libraries with React 18 peer dependency conflicts | Use native React 19 code, Vanilla CSS variables, and zero heavy UI framework bloat |
| **RSK-10** | Single-Worker Multi-Tab Race | **MEDIUM** | Low | Multiple tabs triggering concurrent jobs on in-memory backend | Distinct `job_id` per document; single-worker deployment documented in README |

---

## 2. In-Depth Risk Analysis & Mitigations

### 2.1 RSK-01: Backend Schema Drift & Invented History
- **Hazard:** Designers frequently assume that an application dashboard includes a "Contract History" or "Recent Audits" server endpoint.
- **Current Backend Reality:** The backend operates as a privacy-first, stateless audit pipe: documents are encrypted and purged after 24 hours. There is no `GET /v1/contracts` endpoint.
- **Mitigation:** The redesigned Overview Dashboard strictly uses **session-based in-memory history** (`sessionStorage`). When the tab is closed, recent history is cleared. No unsupported server requests are made.

### 2.2 RSK-02: React 19 / Next.js 16 Theme Hydration Flash
- **Hazard:** When using `localStorage` in Next.js Server Components, reading theme state inside `useEffect` causes a white flash if dark mode is preferred, or throws a React hydration mismatch error.
- **Mitigation:** In `layout.tsx`, an inline blocking script runs before React hydration:
  ```html
  <script>
    (function(){
      var t = localStorage.getItem('lexaudit_theme') || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
      document.documentElement.setAttribute('data-theme', t);
    })();
  </script>
  ```
  CSS styles are bound to `html[data-theme="light"]` and `html[data-theme="dark"]`, guaranteeing 0ms flicker.

### 2.3 RSK-05: Document Alteration and Legal Integrity
- **Hazard:** Text truncation (e.g. `text.slice(0, 100) + '...'`), automated capitalization, or improper line-breaking can alter the legal meaning of liability caps or covenants.
- **Mitigation:** The `ClauseDocViewer` presents the verbatim clause text extracted by the NLP segmentation engine. No client-side text alteration or truncation is permitted in the document stream.

### 2.4 RSK-08: Reviewer Feedback Protocol
- **Hazard:** Submitting legacy verdict names like `ACCEPT` or `REJECT` causes HTTP 422 validation failure in `src/api/v1/router.py`.
- **Mitigation:** The `FeedbackForm` component defines an explicit TypeScript enum:
  ```typescript
  type SupportedVerdict = "CONFIRM_ANOMALY" | "REJECT_ANOMALY";
  ```
  The UI form strictly binds to this type, preventing arbitrary string submission.

### 2.5 RSK-09: Dependency Bloat vs. React 19 Compatibility
- **Hazard:** Popular component libraries (older versions of shadcn, Mantine, or Material UI) often have peer dependency conflicts with `react@19.3.0` and `react-dom@19.3.0`.
- **Mitigation:** Phase 1 recommends building on Next.js 16 and Vanilla CSS with CSS custom properties (`globals.css`), avoiding third-party component libraries that introduce dependency bloat or breaking peer dependency conflicts.
