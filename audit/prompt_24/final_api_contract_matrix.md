# Final API Contract Matrix — Prompt 24

**Audit Date:** October 10, 2026  
**Auditor:** FastAPI Integration Engineer & Release QA Lead  
**Scope:** Reconciled API routes between Next.js frontend, Python FastAPI backend, and test suites  

---

## 1. Reconciled Route Matrix

| Route Path | HTTP Method | Auth Required | Request Body / Query | Response Model / Payload | Status Code | Verified In |
|---|:---:|:---:|---|---|:---:|:---:|
| `/health` | `GET` | No | None | `{"status": "healthy", "version": "1.0.0"}` | 200 | CDP, Pytest |
| `/ready` | `GET` | No | None | `{"status": "ready"}` | 200 | CDP, Pytest |
| `/v1/upload` | `POST` | Yes (`X-API-Key`) | `multipart/form-data` (`file`) | `{"doc_id": "...", "filename": "...", "size_bytes": int, "retention_expires_at": "..."}` | 200 | CDP, Pytest |
| `/v1/analyze` | `POST` | Yes (`X-API-Key`) | `{"doc_id": "..."}` | `{"job_id": "...", "status": "queued", "doc_id": "..."}` | 202 | CDP, Pytest |
| `/v1/jobs/{job_id}` | `GET` | Yes (`X-API-Key`) | Path parameter: `job_id` | `{"job_id": "...", "status": "completed"\|"processing"\|"queued", "progress": float}` | 200 | CDP, Pytest |
| `/v1/jobs/{job_id}/results` | `GET` | Yes (`X-API-Key`) | Path parameter: `job_id` | `AnalysisResultResponse` (KPIs, clauses, anomalies, rules, calibration) | 200 | CDP, Pytest |
| `/v1/xai/attribution` | `GET` | Yes (`X-API-Key`) | Query: `doc_id`, `clause_idx` | `{"attributions": float[], "tokens": str[], "baseline_score": float}` | 200 | CDP, Pytest |
| `/v1/xai/sensitivity` | `GET` | Yes (`X-API-Key`) | Query: `doc_id`, `clause_idx` | `{"score_delta": float, "perturb_method": str, "details": dict}` | 200 | CDP, Pytest |
| `/v1/feedback` | `POST` | Yes (`X-API-Key`) | `FeedbackSubmission` (doc_id, clause_idx, reviewer_verdict, notes, etc.) | `{"feedback_id": "...", "status": "recorded", "timestamp": "..."}` | 200 | CDP, Pytest |

---

## 2. Invalid / Non-Existent Routes Catalog (Verified Omitted)

The following routes were previously suspected or incorrectly cited in earlier prompt drafts. They have been verified **omitted** from both frontend calls and backend definitions:
- ❌ `/v1/audit/contracts` — Does NOT exist; replaced by `/v1/analyze`.
- ❌ `/v1/feedback/verdicts` — Does NOT exist; replaced by `/v1/feedback`.
- ❌ `/v1/contracts/{id}/anomalies` — Does NOT exist; anomalies are provided directly in `/v1/jobs/{job_id}/results`.

---

## 3. Pydantic Model vs. TypeScript Interface Alignment

### 3.1 Job Results Contract
- **FastAPI / Pydantic:** `AnalysisResultResponse`
  - `total_clauses: int`
  - `anomalies_detected: int`
  - `high_severity_count: int`
  - `rule_violations_count: int`
  - `overall_coherence_score: float`
  - `clauses: List[ClauseAnomaly]`
  - `calibration_metrics: CalibrationMetrics`
- **Next.js TypeScript:** `AnalysisResults`
  - Exactly maps all fields with matching scalar types and optional conformal intervals.

### 3.2 Feedback Contract
- **FastAPI / Pydantic:** `FeedbackRequest` (`src/api/schema.py`)
  - `doc_id: str`
  - `clause_id: str`
  - `original_severity: str`
  - `reviewer_verdict: str` (validated in router to `CONFIRM_ANOMALY` or `REJECT_ANOMALY`)
  - `reviewer_id: str`
  - `provenance: str = "REAL"`
- **Next.js TypeScript:** Payload sent via `fetch(`${backendUrl}/v1/feedback`, ...)` matches these exact field names:
  `{ doc_id, clause_id, original_severity, reviewer_verdict, reviewer_id, provenance, model_version: "v1" }`.
- **Persistence:** Saved into SQLite (`data/processed/feedback.sqlite`, table `feedback`), confirmed by direct inspection.
