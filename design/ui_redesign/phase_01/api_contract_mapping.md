# API Contract Mapping & Data Binding Specification — Phase 1

**Module:** UI Redesign Program — Phase 1  
**Authors:** Frontend/Backend Integration Architect & Security Reviewer  
**Date:** October 10, 2026  
**Status:** COMPLETE (API Contract Mapping)  

---

## 1. Verified FastAPI Endpoint Catalog

Every route documented below was verified directly against the active FastAPI implementation (`src/api/main.py`, `src/api/v1/router.py`, `src/api/schema.py`).

| Route & Method | Auth Header | Request Schema / Payload | Response Model | Error Codes | Frontend Consumer |
|---|:---:|---|---|:---:|---|
| `GET /health` | None | None | `{"status": "ok"}` | 500 | `HeaderBar` status badge |
| `GET /ready` | None | None | `{"status": "ready"}` | 503 | `HeaderBar` ready indicator |
| `GET /v1/privacy-policy` | None | None | `PrivacyPolicyResponse` | 500 | `PrivacyConsentModal` |
| `POST /v1/upload` | `X-API-Key` or `Bearer` | `multipart/form-data` (`file: UploadFile`) | `UploadResponse` (`doc_id`, `message`) | 400, 429, 500 | `DocumentUploader` |
| `POST /v1/analyze` | `X-API-Key` or `Bearer` | `AnalyzeRequest` (`{"doc_id": string}`) | `AnalyzeResponse` (`job_id`, `message`) | 404, 429, 500 | `DocumentUploader` |
| `GET /v1/jobs/{job_id}` | `X-API-Key` or `Bearer` | None (Path: `job_id`) | `JobStatusResponse` (`job_id`, `status`, `error`) | 404, 500 | `AnalysisProgress` (Polling) |
| `GET /v1/jobs/{job_id}/results` | `X-API-Key` or `Bearer` | None (Path: `job_id`) | `UnifiedAuditReportModel` | 400, 404, 500 | `SplitReviewer`, `Analytics` |
| `GET /v1/xai/attribution` | `X-API-Key` or `Bearer` | Query: `doc_id`, `clause_id` | `ExplanationResult` (with `ig_payload`) | 404, 500 | `XaiTokenViewer` |
| `GET /v1/xai/sensitivity` | `X-API-Key` or `Bearer` | Query: `doc_id`, `clause_id` | `ExplanationResult` (with `sensitivity_payload`) | 404, 500 | `SensitivityChart` |
| `POST /v1/feedback` | `X-API-Key` or `Bearer` | `FeedbackRequest` (JSON) | `FeedbackResponse` (`feedback_id`, `message`) | 404, 422, 500 | `FeedbackForm`, `FindingsInspector` |

---

## 2. Field-Level Binding Matrix

This matrix maps actual backend JSON properties to their corresponding TypeScript interfaces and visual presentation components without inventing fields.

### 2.1 Unified Audit Report (`GET /v1/jobs/{job_id}/results`)

| Backend JSON Path | TypeScript Field | Target UI Component | Display Label | Formatting / Presentation | Null / Missing Behavior |
|---|---|---|---|---|---|
| `doc_id` | `doc_id: string` | `HeaderBar`, `Inspector` | Document ID | Monospace chip (`doc_...`) | Fallback: `"Unknown Doc"` |
| `total_clauses` | `total_clauses: number` | `MetricCard` | Total Clauses | Integer (`5`) | Display `0` |
| `ml_anomaly_count` | `ml_anomaly_count: number` | `MetricCard` | Total Anomalies | Red/Amber integer badge | Display `0` |
| `high_severity_count` | `high_severity_count: number`| `MetricCard` | High Severity | Red pill with `🔴` pip | Display `0` |
| `rule_violation_count`| `rule_violation_count: number`| `MetricCard` | Rule Violations | Purple pill with `⚠️` pip | Display `0` |
| `scoring_result.mean_combined_score` | `mean_combined_score: number` | `MetricCard` | Mean Anomaly Score | `(val).toFixed(3)` (e.g. `0.341`) | Display `"0.000"` |
| `scoring_result.calibration_source` | `calibration_source: string` | `MetricCard` Subtitle | Calibration Source | Text chip (e.g., `SYNTHETIC_SHUFFLE`)| Display `"Uncalibrated"` |

### 2.2 Clause Scoring Model (`scoring_result.clauses[]`)

| Backend JSON Path | TypeScript Field | Target UI Component | Display Label | Formatting / Presentation | Null / Missing Behavior |
|---|---|---|---|---|---|
| `clauses[i].clause_id` | `clause_id: string` | `ClauseCard` Header | Clause Identifier | Monospace (`clause_1`) | Required by schema |
| `clauses[i].sequence_idx` | `sequence_idx: number` | `ClauseCard` Pip | Section Index | `§ ${val}` (e.g. `§ 1`) | Fallback to array index |
| `clauses[i].text_preview` | `text_preview: string` | `ClauseCard` Body | Contract Clause Text | Full continuous text, 1.65 line height | Fallback: `"[Empty Text]"` |
| `clauses[i].severity` | `severity: string` | `SeverityBadge` | Severity Tag | Tag: `HIGH`, `MEDIUM`, `LOW` | Default to `LOW` |
| `clauses[i].combined_score` | `combined_score: number` | `FindingsInspector` | Combined Score | `(val).toFixed(3)` with gradient bar | Display `0.000` |
| `clauses[i].confidence_interval` | `confidence_interval: number[]` | `FindingsInspector` | 95% Conformal Bounds | `[min.toFixed(2), max.toFixed(2)]` | Display `"N/A"` |
| `clauses[i].channel_a_evidence.nearest_centroid_label` | `nearest_centroid_label: string` | `FindingsInspector` | Reference Cluster | Uppercase legal topic (e.g. `TERMINATION`) | Display `"Unknown"` |
| `clauses[i].channel_a_evidence.centroid_distance` | `centroid_distance: number` | `FindingsInspector` | Centroid Distance | `(val).toFixed(3)` | Display `"0.000"` |
| `clauses[i].channel_b_evidence.incoming_prob` | `incoming_prob?: number` | `FindingsInspector` | Transition Inflow | `(val * 100).toFixed(1) + "%"` | Display `"—"` if boundary |
| `clauses[i].channel_b_evidence.outgoing_prob` | `outgoing_prob?: number` | `FindingsInspector` | Transition Outflow | `(val * 100).toFixed(1) + "%"` | Display `"—"` if boundary |

### 2.3 Deterministic Rule Violations (`rule_flags[]`)

| Backend JSON Path | TypeScript Field | Target UI Component | Display Label | Formatting / Presentation | Null / Missing Behavior |
|---|---|---|---|---|---|
| `rule_flags[i].flag_id` | `flag_id: string` | `RuleFlagCard` Header | Rule Flag ID | Monospace chip (`flag_...`) | Required |
| `rule_flags[i].title` | `title: string` | `RuleFlagCard` Title | Violation Title | Bold header (e.g. `Dangling Reference`) | Fallback to category |
| `rule_flags[i].description` | `description: string` | `RuleFlagCard` Body | Description | Descriptive text with clause link | Fallback: `"No details"` |
| `rule_flags[i].clause_id` | `clause_id?: string` | `RuleFlagCard` Footer | Associated Clause | Interactive link to jump to clause | Omit if document-level |

### 2.4 Explainability Model (`GET /v1/xai/attribution` & `sensitivity`)

| Backend JSON Path | TypeScript Field | Target UI Component | Display Label | Formatting / Presentation | Null / Missing Behavior |
|---|---|---|---|---|---|
| `ig_payload.tokens` | `tokens: string[]` | `XaiTokenBadge` | WordPiece Token | Individual token chip (WordPiece `##` cleaned) | Show empty container |
| `ig_payload.attributions` | `attributions: number[]` | `XaiTokenBadge` Intensity | Attribution Weight | Green color saturation proportional to score | Default opacity `0.1` |
| `sensitivity_payload.score_delta` | `score_delta: number` | `SensitivityChart` | Sensitivity Delta ($\Delta$) | `+0.142` or `-0.081` with trend indicator | Display `"0.000"` |
| `claim_scope.what_this_shows` | `what_this_shows: string` | `ClaimScopeBox` | What This Shows | Descriptive scope paragraph | Show standard text |
| `claim_scope.what_this_does_not_show`| `what_this_does_not_show: string`| `ClaimScopeBox` | What This Does Not Show | Warning scope paragraph | Show standard text |

---

## 3. Documented Backend Limitations & UI Handlers

1. **No Persistent Contract List:** The backend does **not** provide a `GET /v1/contracts` endpoint. Audited document IDs exist in server memory for 24 hours. The redesigned UI must store the user's active session history in browser `sessionStorage`, rather than fabricating an unsupported API call.
2. **Strict Feedback Verdicts:** `POST /v1/feedback` strictly rejects any verdict other than `CONFIRM_ANOMALY` or `REJECT_ANOMALY` with HTTP 422. The frontend form will exclusively render these two options.
3. **Single File Support:** `POST /v1/upload` accepts plain UTF-8 text files (`.txt`). PDF parsing is not implemented in the backend; the UI upload zone must explicitly enforce `.txt` filtering.
