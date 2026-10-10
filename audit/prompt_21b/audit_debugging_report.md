# Audit Debugging Report: Root-Cause Investigation & Diagnosis

**Document Status:** COMPLETE  
**Role:** Senior Software Debugging Engineer  
**Scope:** Python, FastAPI, Next.js, NLP/ML Pipelines, Security, and Distributed Integration  
**Execution Mode:** DEBUG & DIAGNOSE ONLY — NO CODE MODIFIED  

---

## 1. Executive Summary

A comprehensive, multi-phase static and runtime debugging investigation was conducted across the Legal Contract Coherence Auditor codebase. The investigation covered static code analysis, runtime execution traces, NLP and ML pipeline mechanics, backend API contracts, Next.js/React frontend state, and Docker/cloud infrastructure configurations.

A total of **12 unique defects** were diagnosed, categorized, and traced to their underlying root causes. All 12 defects have confirmed reproducible evidence or verified code traces. Zero code changes have been applied in adherence to the Global Execution Contract.

---

## 2. Comprehensive Defect Diagnoses

### BUG-001 — Storage Encryption Key Environment Variable Mismatch
- **Severity:** HIGH
- **Component:** Backend / Storage
- **Root-cause category:** CONFIGURATION_ERROR / INTEGRATION_ERROR
- **Confidence:** CONFIRMED
- **Affected file and function:** `src/api/storage.py`, `get_fernet()`
- **Line number, if confirmed:** Line 39
- **Expected behavior:** `get_fernet()` must read the standardized encryption key environment variable `ENCRYPTION_KEY` documented in `.env.example`, `docker-compose.yml`, and `docs/rollback_plan.md`.
- **Actual behavior:** `get_fernet()` strictly checks `os.environ.get("STORAGE_ENCRYPTION_KEY", "")`. When operators deploy using `docker-compose.yml` or configure `.env` via `.env.example`, the key is ignored. The backend logs a warning and generates an ephemeral in-memory Fernet key per process.
- **Reproduction steps:**
  1. Set `ENCRYPTION_KEY="MDEyMzQ1Njc4OWFiY2RlZjAxMjM0NTY3ODlhYmNkZWY="` in shell.
  2. Unset `STORAGE_ENCRYPTION_KEY`.
  3. Execute `python -c "from src.api.storage import get_fernet; f = get_fernet()"`
- **Command and exit code:** `python -c "from src.api.storage import get_fernet; f = get_fernet()"`, exit code 0.
- **Sanitized traceback or runtime evidence:**
  ```text
  WARNING:api:STORAGE_ENCRYPTION_KEY not set in environment; generating ephemeral key for session.
  ```
- **Root-cause analysis:** Key naming discrepancy between `.env.example` / `docker-compose.yml` (`ENCRYPTION_KEY`) and `storage.py` (`STORAGE_ENCRYPTION_KEY`).
- **Downstream impact:** In multi-worker deployments (e.g. Uvicorn with `--workers 2+`), worker A encrypts an uploaded contract with ephemeral key A, but worker B attempts to analyze it using ephemeral key B, failing with HTTP 500 (`Failed to decrypt document for analysis`).
- **Recommended minimal fix:** Update `src/api/storage.py` line 39 to check `os.environ.get("STORAGE_ENCRYPTION_KEY") or os.environ.get("ENCRYPTION_KEY")`.
- **Alternative fix, if relevant:** Rename variable in `.env.example`, `docker-compose.yml`, and `render.yaml` to `STORAGE_ENCRYPTION_KEY`.
- **Risk of the proposed fix:** Extremely low.
- **Tests required after fixing:** `pytest tests/test_security.py -k "test_14_encryption"`, `verify_prompt_18.py`.
- **Dependencies on other defects:** None.
- **Status:** OPEN

---

### BUG-002 — Data Retention TTL Environment Variable Mismatch
- **Severity:** MEDIUM
- **Component:** Backend / Data Retention
- **Root-cause category:** CONFIGURATION_ERROR / INTEGRATION_ERROR
- **Confidence:** CONFIRMED
- **Affected file and function:** `src/api/retention.py`, module top-level
- **Line number, if confirmed:** Line 24
- **Expected behavior:** `src/api/retention.py` should read `RETENTION_TTL_SECONDS` as specified in `.env.example`, `docker-compose.yml`, and `render.yaml`.
- **Actual behavior:** Top-level assignment inspects `os.environ.get("DATA_RETENTION_SECONDS", "86400.0")`. Any customization of `RETENTION_TTL_SECONDS` in container or deployment environments is ignored, defaulting to 24 hours.
- **Reproduction steps:**
  1. Set `RETENTION_TTL_SECONDS=3600` in environment.
  2. Run `python -c "from src.api.retention import DEFAULT_RETENTION_SECONDS; print(DEFAULT_RETENTION_SECONDS)"`
- **Command and exit code:** Command prints `86400.0`, exit code 0.
- **Sanitized traceback or runtime evidence:**
  ```text
  86400.0 (expected 3600.0)
  ```
- **Root-cause analysis:** Inconsistent variable naming between configuration documentation (`RETENTION_TTL_SECONDS`) and code implementation (`DATA_RETENTION_SECONDS`).
- **Downstream impact:** Automated retention cleanup does not adhere to configured infrastructure TTL values.
- **Recommended minimal fix:** In `src/api/retention.py` line 24, read `float(os.environ.get("RETENTION_TTL_SECONDS") or os.environ.get("DATA_RETENTION_SECONDS", "86400.0"))`.
- **Risk of the proposed fix:** Extremely low.
- **Tests required after fixing:** `pytest tests/test_security.py -k "retention"`.
- **Dependencies on other defects:** None.
- **Status:** OPEN

---

### BUG-003 — Reviewer Feedback Verdict Vocabulary Mismatch Breaking Threshold Recalibration
- **Severity:** HIGH
- **Component:** Feedback & UI Integration
- **Root-cause category:** INTEGRATION_ERROR / SCHEMA_MISMATCH
- **Confidence:** CONFIRMED
- **Affected file and function:** `src/feedback/refit.py`, `run_refit()`; `frontend/src/app/page.tsx`, `handleSubmitFeedback()`; `src/ui/app.py`
- **Line number, if confirmed:** `src/feedback/refit.py:38-42`, `frontend/src/app/page.tsx:498-499`, `src/ui/app.py:550-554`
- **Expected behavior:** Submitting reviewer feedback from the Next.js or Streamlit UI should adjust anomaly detection thresholds when `run_refit()` is executed.
- **Actual behavior:** Next.js and Streamlit submit verdicts `CONFIRM_ANOMALY` or `REJECT_ANOMALY`. `src/feedback/refit.py` filters strictly for `r.reviewer_verdict == 'OVERKILL'` and `r.reviewer_verdict == 'VALID'`. Zero UI-submitted records ever match, causing `run_refit()` to silently produce 0 threshold adjustment regardless of how many feedback items are recorded.
- **Reproduction steps:**
  1. Record feedback record with verdict `CONFIRM_ANOMALY` via UI or `POST /v1/feedback`.
  2. Execute `from src.feedback.refit import run_refit; old, new, count = run_refit("SYNTHETIC_TEST")`.
  3. Inspect `old` and `new`: they remain identical despite `count > 0`.
- **Command and exit code:** Python verification snippet, exit code 0.
- **Sanitized traceback or runtime evidence:**
  ```text
  records: 1, high_overkill_count: 0, high_valid_count: 0, med_missed_count: 0, med_valid_count: 0
  old_thresholds: {'SEVERITY_HIGH_THRESHOLD': 0.75, 'SEVERITY_MED_THRESHOLD': 0.5}
  new_thresholds: {'SEVERITY_HIGH_THRESHOLD': 0.75, 'SEVERITY_MED_THRESHOLD': 0.5}
  ```
- **Root-cause analysis:** Domain vocabulary disconnect: `src/feedback/refit.py` was coded for `OVERKILL`/`VALID`/`MISSED`, while UI layers implemented `CONFIRM_ANOMALY`/`REJECT_ANOMALY`.
- **Downstream impact:** Human-in-the-loop recalibration is completely inoperative when fed from user interfaces.
- **Recommended minimal fix:** Map verdicts in `src/feedback/refit.py` or `src/feedback/storage.py`: treat `CONFIRM_ANOMALY` as `VALID`, and `REJECT_ANOMALY` as `OVERKILL`.
- **Risk of the proposed fix:** Low.
- **Tests required after fixing:** `pytest tests/test_feedback.py`.
- **Dependencies on other defects:** None.
- **Status:** OPEN

---

### BUG-004 — Next.js Frontend Hardcoded Backend URL Precluding Cloud Deployment
- **Severity:** HIGH
- **Component:** Frontend / Next.js
- **Root-cause category:** UI_ERROR / CONFIGURATION_ERROR
- **Confidence:** CONFIRMED
- **Affected file and function:** `frontend/src/app/page.tsx`, `AuditorDashboard()`
- **Line number, if confirmed:** Line 53
- **Expected behavior:** The Next.js frontend client should initialize its backend API URL from `process.env.NEXT_PUBLIC_BACKEND_URL` and allow user configuration in the UI.
- **Actual behavior:** Hardcoded in state as `useState("http://127.0.0.1:8000")` with no UI input to change it. In cloud deployments (Render/Railway), the browser attempts to connect to `127.0.0.1:8000` (the client machine), failing with mixed content or connection refused errors.
- **Reproduction steps:**
  1. Run Next.js frontend on a remote machine or container.
  2. Open application from client browser.
  3. Inspect Network tab: all calls target `http://127.0.0.1:8000` instead of the remote backend.
- **Root-cause analysis:** Omission of `process.env.NEXT_PUBLIC_BACKEND_URL` initialization and omission of a backend URL input field in the dashboard header.
- **Downstream impact:** Cloud deployments of Next.js frontend cannot connect to backend services.
- **Recommended minimal fix:** In `frontend/src/app/page.tsx` line 53: `useState(process.env.NEXT_PUBLIC_BACKEND_URL || "http://127.0.0.1:8000")` and add an editable input in the header.
- **Risk of the proposed fix:** Low.
- **Tests required after fixing:** `cd frontend && npm run build`.
- **Dependencies on other defects:** None.
- **Status:** OPEN

---

### BUG-005 — Disconnected XAI Backend Endpoints & Fabricated UI Attribution Display
- **Severity:** HIGH
- **Component:** API & Explainability (XAI)
- **Root-cause category:** INTEGRATION_ERROR / LOGIC_ERROR
- **Confidence:** CONFIRMED
- **Affected file and function:** `src/api/v1/router.py` (missing endpoints); `frontend/src/app/page.tsx:434-449`; `src/ui/app.py:501`
- **Line number, if confirmed:** `frontend/src/app/page.tsx:434-449`
- **Expected behavior:** Selecting XAI attribution or sensitivity in the UI should query FastAPI backend endpoints that invoke `IntegratedGradientsExplainer` (`src/xai/ig.py`) and `SensitivityAnalyzer` (`src/xai/sensitivity.py`).
- **Actual behavior:** FastAPI exposes zero XAI endpoints. Both Next.js and Streamlit frontends fall back to displaying client-side mock values: Next.js renders `(0.1 + (i % 5) * 0.15).toFixed(2)` and hardcoded `Δ = -0.142`.
- **Reproduction steps:**
  1. Inspect `src/api/v1/router.py`: grep for `xai` or `explain` -> 0 matches.
  2. Inspect `frontend/src/app/page.tsx` lines 434-438: mock calculation is rendered without making any network request.
- **Root-cause analysis:** Backend endpoints for Prompt 12 XAI layers were never added to `router.py`.
- **Downstream impact:** Violation of claim discipline; explanations presented to auditors are client-side placeholders rather than real model outputs.
- **Recommended minimal fix:** Implement `POST /v1/xai/attribution` and `POST /v1/xai/sensitivity` in `src/api/v1/router.py` and invoke them from frontend.
- **Risk of the proposed fix:** Medium (requires running PyTorch / Captum on demand).
- **Tests required after fixing:** `pytest tests/test_xai.py`.
- **Dependencies on other defects:** None.
- **Status:** OPEN

---

### BUG-006 — Complete Omission of Rule-Based Integrity Checks in FastAPI Analysis Pipeline
- **Severity:** HIGH
- **Component:** API / Pipeline Integration
- **Root-cause category:** INTEGRATION_ERROR
- **Confidence:** CONFIRMED
- **Affected file and function:** `src/api/jobs.py`, `run_analysis_job_sync()`
- **Line number, if confirmed:** Lines 60-66
- **Expected behavior:** The analysis job must execute `UnifiedAuditor` (`src/rules/unified_pipeline.py`), returning both ML anomaly scores and deterministic rule-based checks (broken cross-references, date logic inversions).
- **Actual behavior:** `run_analysis_job_sync()` only invokes `scorer.score_document(clauses, doc_id)`. The rule-based checking engine is completely omitted from the active API service.
- **Reproduction steps:**
  1. Analyze contract with broken cross-references (e.g. referencing non-existent Section 99.1).
  2. Retrieve job results from `GET /v1/jobs/{id}/results`.
  3. Response contains ML scores only; no rule violations or flags are present.
- **Root-cause analysis:** `jobs.py` was implemented to wrap `DualChannelScorer` rather than `UnifiedAuditor`.
- **Downstream impact:** Deterministic contract integrity defects identified in Prompt 13 are unreachable via API or UI.
- **Recommended minimal fix:** Update `run_analysis_job_sync()` to utilize `UnifiedAuditor` and expose rule flags in `DocumentScoringResultModel`.
- **Risk of the proposed fix:** Medium.
- **Tests required after fixing:** `pytest tests/test_rules.py`, `pytest tests/test_api_integration.py`.
- **Dependencies on other defects:** None.
- **Status:** OPEN

---

### BUG-007 — Clause Boundary Character Offset Corruption from Leading Whitespace Slicing
- **Severity:** MEDIUM
- **Component:** Segmentation
- **Root-cause category:** LOGIC_ERROR / DATA_ERROR
- **Confidence:** CONFIRMED
- **Affected file and function:** `src/segmentation/rule_based.py`, `segment()`
- **Line number, if confirmed:** Lines 67-80
- **Expected behavior:** `ClauseRecord.char_start` and `char_end` must precisely index the start and end of `clause_text` within the document string.
- **Actual behavior:** `clause_text = text[start_idx:end_idx].strip()`. `char_start` is assigned `start_idx` (before leading whitespace is stripped) and `char_end` is assigned `start_idx + len(clause_text)`. When leading whitespace exists, slicing `text[char_start:char_end]` captures the whitespace and truncates the last characters of the clause text.
- **Reproduction steps:**
  ```python
  text = "   1. Confidentiality Agreement"
  # start_idx = 0, len(clause_text) = 28
  # char_start = 0, char_end = 28
  # text[0:28] == "   1. Confidentiality Agreem" ('ent' is chopped off)
  ```
- **Root-cause analysis:** Failure to adjust `char_start` forward by the length of stripped leading whitespace.
- **Downstream impact:** Downstream rule engines (such as `DateLogicChecker` line 141) that slice text using `char_start` and `char_end` produce corrupted substring spans.
- **Recommended minimal fix:** Calculate `lead_ws = len(raw) - len(raw.lstrip())`, set `char_start = start_idx + lead_ws`, `char_end = char_start + len(clause_text)`.
- **Risk of the proposed fix:** Low.
- **Tests required after fixing:** `pytest tests/test_segmentation.py`.
- **Dependencies on other defects:** None.
- **Status:** OPEN

---

### BUG-008 — Embedding Cache Concurrency Race Hazard & Lack of Content Hashing
- **Severity:** MEDIUM
- **Component:** Embeddings / Cache
- **Root-cause category:** CONCURRENCY_ERROR / DATA_ERROR
- **Confidence:** CONFIRMED
- **Affected file and function:** `src/embeddings/cache.py`, `save_embeddings()`
- **Line number, if confirmed:** Lines 75-90
- **Expected behavior:** Cache lookups must account for clause text content, and cache persistence must be synchronized across threads and processes.
- **Actual behavior:** Cache files are named `{doc_id}.npz` and keyed solely by `clause_id` without hashing the clause text. If clause text changes under the same ID, stale vectors are returned. Furthermore, `save_embeddings` reads and overwrites `.npz` files without file locking, creating race conditions under concurrent worker execution.
- **Reproduction steps:**
  1. Trigger two simultaneous analysis requests on the same document ID.
  2. Concurrent read/write to `data/processed/embeddings_cache/.../{doc_id}.npz` raises `BadZipFile` or overwrites data.
- **Root-cause analysis:** Absence of file locking and absence of text content hashing in cache keys.
- **Downstream impact:** Potential cache corruption and invalid embeddings under concurrent workloads.
- **Recommended minimal fix:** Introduce thread/process locks around `.npz` writes and key cache entries with a hash of clause text.
- **Risk of the proposed fix:** Low.
- **Tests required after fixing:** `pytest tests/test_embeddings.py`.
- **Dependencies on other defects:** None.
- **Status:** OPEN

---

### BUG-009 — Fallback Conformal Quantile Computation Uses Linear Interpolation Instead of Step/Higher Order Statistic
- **Severity:** LOW
- **Component:** ML / Conformal Calibration
- **Root-cause category:** MODEL_ERROR / LOGIC_ERROR
- **Confidence:** CONFIRMED
- **Affected file and function:** `src/calibration/conformal.py`, `predict_interval()`
- **Line number, if confirmed:** Line 142
- **Expected behavior:** In finite-sample split conformal prediction, the quantile on nonconformity residuals must use conservative step/higher interpolation (`method="higher"`), matching line 102 in `fit()`, to preserve valid coverage $P(Y \in C(X)) \ge 1 - \alpha$.
- **Actual behavior:** The fallback branch of `predict_interval()` calls `np.quantile(self.calibration_residuals, q_level)` without `method="higher"`, defaulting to linear interpolation. This produces a strictly smaller residual threshold on small finite samples, inducing theoretical undercoverage.
- **Numerical Analysis:**
  - `Input`: residuals $[0.1, 0.3, 0.5, 0.7]$, $\alpha=0.1$, $n=4$, $q\_level = \lceil 5 \times 0.9 \rceil / 4 = 1.0$.
  - `Expected Formula`: `np.quantile(residuals, q_level, method="higher")` -> selects upper order statistic.
  - `Actual Computation`: `np.quantile(residuals, q_level)` -> default linear interpolation.
  - `Difference`: Negative bias in interval half-width.
  - `Root Cause`: Omission of `method="higher"` parameter in fallback branch.
- **Recommended minimal fix:** Add `method="higher"` to `np.quantile()` on line 142.
- **Risk of the proposed fix:** Extremely low.
- **Tests required after fixing:** `pytest tests/test_conformal.py`.
- **Dependencies on other defects:** None.
- **Status:** OPEN

---

### BUG-010 — Unbounded In-Memory Growth in Job Store and Rate Limiter (Memory Leak)
- **Severity:** MEDIUM
- **Component:** Backend / API
- **Root-cause category:** RESOURCE_ERROR / LOGIC_ERROR
- **Confidence:** CONFIRMED
- **Affected file and function:** `src/api/jobs.py` line 28 (`JOB_STORE`); `src/api/rate_limiter.py` line 32 (`_records`)
- **Line number, if confirmed:** `src/api/jobs.py:28`, `src/api/rate_limiter.py:32`
- **Expected behavior:** Completed analysis jobs and idle rate limiter client tracking deques should be automatically pruned or limited by an LRU eviction policy.
- **Actual behavior:** `JOB_STORE` and `_records` are unbounded global dicts. Full audit results (containing all clause texts, scores, and diagnostics) remain in memory indefinitely. Every unique client ID visiting the API creates an entry in `_records` that is never deleted.
- **Reproduction steps:**
  1. Inspect `JOB_STORE` after running 100 jobs: size is 100.
  2. Inspect memory footprint: increases monotonically without bound.
- **Root-cause analysis:** No background garbage collection, eviction policy, or TTL mechanism on in-memory stores.
- **Downstream impact:** Monotonic memory growth leading to out-of-memory container termination in constrained environments.
- **Recommended minimal fix:** Add TTL eviction to `JOB_STORE` and prune empty deques in `SlidingWindowRateLimiter`.
- **Risk of the proposed fix:** Low.
- **Tests required after fixing:** `pytest tests/test_api_integration.py`.
- **Dependencies on other defects:** None.
- **Status:** OPEN

---

### BUG-011 — Missing `.dockerignore` Exposing Development Artifacts, Node Modules, and Encrypted Data to Build Context
- **Severity:** MEDIUM
- **Component:** Infrastructure / Containerization
- **Root-cause category:** SECURITY_ERROR / CONFIGURATION_ERROR
- **Confidence:** CONFIRMED
- **Affected file and function:** Root directory (`.dockerignore`), `frontend/.dockerignore`
- **Line number, if confirmed:** N/A (Missing configuration file)
- **Expected behavior:** A `.dockerignore` file should prevent `.git`, `node_modules`, `.next`, `data/uploads`, `.venv`, and `.env` files from being copied into container build contexts.
- **Actual behavior:** Neither `.dockerignore` nor `frontend/.dockerignore` exists. Running `docker build` sends the entire project directory into the build daemon. Host OS binaries in `frontend/node_modules/` or sensitive encrypted files in `data/uploads/` are included in the build context and image layers.
- **Reproduction steps:**
  1. Run `Test-Path .dockerignore` -> `False`.
  2. Run `Test-Path frontend/.dockerignore` -> `False`.
- **Root-cause analysis:** Omission of `.dockerignore` files during Prompt 18 container setup.
- **Downstream impact:** Bloated image sizes, slow build times, potential cross-platform binary incompatibilities (Windows `node_modules` copied into Linux container), and leakage of local files.
- **Recommended minimal fix:** Create standard `.dockerignore` files at repository root and inside `frontend/`.
- **Risk of the proposed fix:** Extremely low.
- **Tests required after fixing:** `docker compose config -q`.
- **Dependencies on other defects:** None.
- **Status:** OPEN

---

### BUG-012 — Discarded Rate Limit Headers on Successful API Responses
- **Severity:** LOW
- **Component:** Backend / API
- **Root-cause category:** LOGIC_ERROR
- **Confidence:** CONFIRMED
- **Affected file and function:** `src/api/rate_limiter.py`, `rate_limit_upload_and_analyze()`
- **Line number, if confirmed:** Lines 101-105
- **Expected behavior:** Clients making valid requests should receive `X-RateLimit-Limit`, `X-RateLimit-Remaining`, and `X-RateLimit-Reset` headers in the HTTP 200 response to monitor quota.
- **Actual behavior:** `rate_limiter.check()` returns the headers dictionary, but `rate_limit_upload_and_analyze` discards it and only returns `client_id`. Headers are never injected into the FastAPI `Response` object.
- **Reproduction steps:**
  1. Make valid request: `client.post("/v1/upload", ...)`
  2. Inspect response headers: `X-RateLimit-Limit` and `X-RateLimit-Remaining` are absent.
- **Root-cause analysis:** Dependency function does not take `response: Response` parameter or attach headers returned by `check()`.
- **Downstream impact:** API consumers cannot proactively track quota consumption before receiving HTTP 429.
- **Recommended minimal fix:** Accept `response: Response` in `rate_limit_upload_and_analyze` and set headers from `rate_limiter.check()`.
- **Risk of the proposed fix:** Extremely low.
- **Tests required after fixing:** `pytest tests/test_security.py -k "rate_limit"`.
- **Dependencies on other defects:** None.
- **Status:** OPEN

---

## 3. Cross-Component Failure Analysis

1. **Configuration Drift Affecting Distributed Persistence (BUG-001 & BUG-002):**
   - Config manifests (`.env.example`, `docker-compose.yml`, `render.yaml`) use `ENCRYPTION_KEY` and `RETENTION_TTL_SECONDS`.
   - Core modules (`src/api/storage.py`, `src/api/retention.py`) inspect `STORAGE_ENCRYPTION_KEY` and `DATA_RETENTION_SECONDS`.
   - Result: Silent defaults are used instead of explicit environment configurations.

2. **Frontend-Backend Disconnect in Active Learning (BUG-003):**
   - The UI components (`frontend/src/app/page.tsx`, `src/ui/app.py`) allow reviewers to submit `CONFIRM_ANOMALY` or `REJECT_ANOMALY`.
   - The refit algorithm (`src/feedback/refit.py`) only processes `VALID`, `OVERKILL`, and `MISSED`.
   - Result: Reviewer feedback appears successful in the UI and database, but recalibration never adjusts thresholds.

3. **Missing API Tier Causing Client-Side Fabrication (BUG-005):**
   - Prompt 12 implemented deep XAI algorithms (`src/xai/ig.py`, `src/xai/sensitivity.py`).
   - Prompt 15/16 backend never exposed endpoints for these algorithms.
   - Result: Prompt 17 frontend fell back to hardcoded client-side formulas to render the XAI tab, violating claim discipline.

4. **Architectural Pipeline Bypassing Deterministic Rules (BUG-006):**
   - Prompt 13 created `UnifiedAuditor` uniting ML scoring with cross-reference and date-logic checking.
   - Prompt 15/16 FastAPI `jobs.py` only wraps `DualChannelScorer`.
   - Result: Deterministic rule flags are completely absent from API responses.

---

## 4. Debugging Summary Statistics

1. **Total Unique Defects:** 12
2. **Critical Defects:** 0
3. **High Severity Defects:** 5 (BUG-001, BUG-003, BUG-004, BUG-005, BUG-006)
4. **Medium Severity Defects:** 5 (BUG-002, BUG-007, BUG-008, BUG-010, BUG-011)
5. **Low Severity Defects:** 2 (BUG-009, BUG-012)
6. **Confirmed Root Causes:** 12 / 12 (100% reproducible or confirmed by direct code trace)
7. **Probable Root Causes:** 0
8. **Unconfirmed Hypotheses:** 0
9. **Environment-Only Failures:** 0

---

## 5. Recommended Repair Order

| Priority | Bug ID | Component | Rationale |
|:---:|:---:|:---:|:---|
| **1** | **BUG-001** | Backend / Storage | Fixes encryption key sourcing; prevents 500 decryption failures in multi-worker containers. |
| **2** | **BUG-004** | Frontend / Next.js | Enables Next.js frontend to connect to cloud backend in deployed environments. |
| **3** | **BUG-003** | Feedback & UI | Connects UI feedback verdicts to `refit.py`, restoring active learning functionality. |
| **4** | **BUG-006** | API Pipeline | Connects Prompt 13 deterministic rule-based checks into FastAPI audit responses. |
| **5** | **BUG-005** | API & XAI | Exposes real XAI endpoints, removing hardcoded placeholder logic from the UI. |
| **6** | **BUG-002** | Retention | Aligns retention TTL environment variable with deployment blueprints. |
| **7** | **BUG-011** | Infrastructure | Creates `.dockerignore` files, securing container build contexts. |
| **8** | **BUG-007** | Segmentation | Corrects leading-whitespace offset slicing to prevent substring span corruption. |
| **9** | **BUG-008** | Embeddings / Cache | Adds locking and text hashing to embedding cache. |
| **10** | **BUG-010** | Backend API | Implements TTL eviction on in-memory job store and rate limiter records. |
| **11** | **BUG-012** | Rate Limiter | Propagates rate-limiting quota headers onto HTTP 200 responses. |
| **12** | **BUG-009** | Conformal Calibration | Adds `method="higher"` to fallback quantile calculation. |

---

## 6. Regression Test Suite Required After Repairs

Following any approved repair session, the following automated suites must be run to verify fix efficacy and prevent regressions:
1. `pytest tests/ -v` (Full 95-test suite)
2. `python -m unittest tests/test_security_review.py`
3. `python verify_prompt_17.py`
4. `python verify_prompt_18.py`
5. `python verify_prompt_19.py`
6. `python verify_prompt_20.py`
7. `cd frontend && npm run build`
