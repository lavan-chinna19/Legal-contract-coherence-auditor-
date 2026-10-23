# Legal Contract Coherence Auditor

**Verified local Docker deployment:** 24/24 application checklist components COMPLETE. See [Docker validation](docs/DOCKER_VALIDATION_REPORT.md) and [Docker launch guide](docs/DOCKER_RUN_AND_VALIDATION.md). Scientific/legal/security validation remains separate.


For the completed local release, use [Install and run](docs/INSTALL_AND_RUN.md), [completion tracker](docs/FINAL_COMPLETION_TRACKER.md) and [verified test results](docs/FINAL_RELEASE_TEST_RESULTS.md). Install `requirements-release.txt` for PDF/DOCX export and the compatible dependency constraints. The explicit synthetic demo launcher is `python scripts/run_server.py --demo --port 8010`.

> **⚠️ RESEARCH PROTOTYPE — NOT LEGAL ADVICE**  
> This system is an academic research prototype evaluating structural and semantic coherence in legal contract text using dual-channel anomaly detection. Predictions and severity flags are model-generated research outputs and **DO NOT** constitute formal legal counsel, statutory advice, or document certification.

---

## 1. System Overview

The **Legal Contract Coherence Auditor** audits legal contracts for structural disorganization, out-of-distribution clauses, dangling references, and date inconsistencies. The architecture combines:

1. **Dual-Channel Scoring Core:**
   - **Channel A (Semantic OOD):** Measures semantic deviation from reference contract clause centroids derived from the LEDGAR corpus using Legal-BERT (`nlpaueb/legal-bert-base-uncased`) embeddings.
   - **Channel B (Discourse Transition Coherence):** Evaluates sequential transition probabilities between adjacent clauses using a trained discourse coherence model.
2. **Decision-Support Severity Ranking:** Categorizes clause findings into `HIGH`, `MEDIUM`, or `LOW` severity with cross-channel agreement analysis.
3. **Conformal Confidence Calibration:** Assigns empirical 95% confidence intervals to anomaly scores. *(Calibration Source: Synthetic shuffle permutations only).*
4. **Explainability & Evidence Layer (XAI):** Provides token-level Integrated Gradients attributions, neighbor perturbation sensitivities, and corpus nearest neighbors, with explicit claim-scoping documentation.
5. **Auxiliary Heuristic Checkers:** Identifies dangling internal section references, conflicting milestone dates, and missing boilerplate provisions.
6. **Hardened API & Security:** Authenticated FastAPI backend (`X-API-Key`), Fernet authenticated encryption at rest (AES-128-CBC + HMAC-SHA256), process-local rate limiting, zero plaintext logging, and automated 24-hour retention purge.
7. **Research Frontend:** Next.js 16 (App Router / TypeScript) dashboard with sequence coherence heatmap, mandatory pre-upload privacy notice acknowledgment, Integrated Gradients token viewer, and reviewer feedback loop.
8. **Multi-Service Orchestration:** Docker Compose stack with PostgreSQL 16 and MinIO object storage.

### Reconciled API Workflow

```text
POST /v1/upload
      ↓
POST /v1/analyze
      ↓
GET  /v1/jobs/{job_id}            (polling until status: completed)
      ↓
GET  /v1/jobs/{job_id}/results
      ↓
GET  /v1/xai/attribution          (Integrated Gradients token importance)
GET  /v1/xai/sensitivity          (Channel B perturbation delta)
      ↓
POST /v1/feedback                 (Record reviewer verdict to SQLite / PostgreSQL)
```

---

## 2. Empirical Benchmark Results (Prompt 14 Evidence)

In accordance with our Global Execution Contract, all performance metrics are reported honestly without cherry-picking. Evidence is backed by reproducible runs stored in `fixtures/claim_evidence_matrix.json` and `fixtures/evaluation_benchmark_results.json`:

| Metric Axis | Evaluation Dataset | Measured Value | 95% Confidence Interval | Provenance / Notes |
|---|---|---|:---:|---|
| **Kendall's Tau (Rank Correlation)** | LEDGAR Test Split (`test.jsonl`) | $\tau = -0.0285$ ($p = 0.6225$) | $[-0.1254, 0.0730]$ | Evaluated on 200 clauses over 5 permutations. |
| **False Positive Rate (High Severity)** | 50 Clean SEC EDGAR Contracts | $\text{FPR}_{\text{High}} = 1.18\%$ (7/595 clauses) | $[0.57\%, 2.41\%]$ | Wilson score binomial interval. |
| **False Positive Rate (Med + High)** | 50 Clean SEC EDGAR Contracts | $\text{FPR}_{\text{Med+High}} = 44.54\%$ (265/595) | $[40.59\%, 48.55\%]$ | Mean combined anomaly score: $0.3726$. |
| **CUAD Generalization** | CUAD Commercial Agreements | Mean Combined Anomaly = $0.3922$ | $[0.3697, 0.4178]$ | Out-of-distribution transfer test. |
| **Baseline: Linear Classifier** | Identical Test Split | Accuracy = $55.0\%$, F1 = $0.6087$ | $\tau = +0.0816$ | Linear logistic regression baseline. |
| **Baseline: Dual-Channel System** | Identical Test Split | Accuracy = $50.0\%$, F1 = $0.00$ | $\tau = -0.2100$ | Targets structural discourse shifts. |

> **Scientific Integrity Notice:** Software test pass rates (e.g., 116 passing unit/integration tests) indicate code correctness and regression stability, NOT machine learning accuracy. No unsupported 95% classification accuracy is claimed.

---

## 3. Human-Feedback Loop Status

- **Architecture:** `POST /v1/feedback` persists reviewer verdicts in SQLite (`data/processed/feedback.sqlite`) or PostgreSQL with audit logging.
- **Verification Status:** Tested with synthetic test fixtures (`SYNTHETIC_TEST`).
- **Research Integrity Disclosure:** Simulated feedback has **not** been presented as real reviewer validation. The feedback recalibration mechanism is mechanically complete and waiting on future professional human legal review.

---

## 4. Quickstart Guide

### Option A: Local Development (Windows PowerShell)

```powershell
# 1. Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. Install dependencies & spaCy language model
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# 3. Set development API key & generate local storage encryption key
$env:API_KEY = "dev_auditor_key_12345"
# Generate a new 32-byte url-safe base64 Fernet key locally:
$env:STORAGE_ENCRYPTION_KEY = python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
# Note: Persistent deployments must store this key securely outside Git and keep it stable across restarts.

# 4. Start FastAPI backend (SINGLE WORKER REQUIRED FOR LOCAL JOB QUEUE)
python -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000 --workers 1

# 5. Start Next.js frontend (in another PowerShell window)
cd frontend
npm ci
npm run dev
# Frontend will be live at: http://localhost:3000
```

### Option B: Local Development (Linux / macOS Bash)

```bash
# 1. Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate

# 2. Install dependencies & spaCy language model
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# 3. Set environment variables
export API_KEY="dev_auditor_key_12345"
export STORAGE_ENCRYPTION_KEY=$(python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
# Note: Persistent deployments must store this key securely outside Git and keep it stable across restarts.

# 4. Start FastAPI backend (single worker)
python -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000 --workers 1

# 5. Start Next.js frontend
cd frontend
npm ci
npm run dev
```

### Option C: Docker Compose

```bash
# Copy environment template
cp .env.example .env

# Build and launch all services (PostgreSQL, MinIO, Backend, Frontend)
docker compose up --build -d

# Frontend: http://localhost:3000
# Backend API Docs: http://localhost:8000/docs
```

---

## 5. Automated Verification & Testing

```powershell
# Run full backend regression test suite
python -m pytest tests/ -v -ra

# Run frontend build verification
cd frontend
npm run build

# Run frontend ESLint check (0 errors, 0 warnings expected)
npx eslint src/
```

---

## 6. Repository Structure

```
├── .github/workflows/ci.yml       # GitHub Actions CI workflow
├── audit/                         # Audit verification artifacts & evidence handoffs
├── data/raw/sec_edgar/            # Clean SEC EDGAR Exhibit 10 contracts
├── docs/                          # Architecture, rollback, & security documentation
├── fixtures/                      # Verified evaluation benchmark results & claim matrix
├── frontend/                      # Next.js 16 research frontend (App Router / TypeScript)
├── scripts/                       # Maintenance, backup, load test, and browser reproduction scripts
├── src/
│   ├── api/                       # Hardened FastAPI backend (auth, retention, encryption)
│   ├── coherence/                 # Discourse coherence models & registry
│   ├── embeddings/                # Legal-BERT embeddings & contrastive model
│   ├── feedback/                  # SQLite / PostgreSQL feedback storage
│   ├── rules/                     # Reference and date consistency checkers
│   ├── scoring/                   # Dual-channel anomaly scoring pipeline
│   └── ui/app.py                  # Companion Streamlit dashboard
├── tests/                         # Full automated test suite (116 passing tests)
├── docker-compose.yml             # Local multi-service orchestration
├── Dockerfile.backend             # Multi-stage Python backend container
├── render.yaml                    # Render cloud deployment blueprint
└── railway.json                   # Railway cloud deployment manifest
```

---

## 7. Known Limitations & Architectural Bounds

1. **Process-Local Job State & Single-Worker Requirement:**
   Contract analysis jobs are tracked in an in-memory dictionary (`_jobs` in `src/api/main.py`). The application must run with a single worker (`--workers 1`). Multi-worker deployments (e.g. `gunicorn -w 4`) will cause intermittent `404 Not Found` responses when polling `GET /v1/jobs/{job_id}` across different worker processes. A shared task broker (Redis/Celery) is planned for future work.
2. **Process-Local Rate Limiting:**
   Sliding-window IP rate limiting runs in-process memory. Clustered deployments require distributed Redis coordination.
3. **Conformal Confidence Bounds:**
   Confidence bounds are computed under exchangeability assumptions using synthetic shuffle permutations, not real human contractual defect distributions.
4. **Hardware Constraints:**
   Embedding and scoring models run on CPU by default. Processing long contracts (100+ pages) requires several minutes on CPU and benefits from GPU acceleration.
5. **Research Prototype Scope:**
   Outputs from this system are for academic research exploration only. They are not legal advice, do not guarantee compliance, and must not replace professional legal counsel.
