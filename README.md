# Legal Contract Coherence Auditor

> **⚠️ RESEARCH PROTOTYPE — NOT LEGAL ADVICE**  
> This system is an academic research prototype evaluating structural and semantic coherence in legal contract text using dual-channel anomaly detection. Predictions and severity flags are model-generated research outputs and **DO NOT** constitute formal legal counsel, statutory advice, or document certification.

---

## 1. System Overview

The **Legal Contract Coherence Auditor** audits legal contracts for structural disorganization, out-of-distribution clauses, dangling references, and date inconsistencies. The architecture combines:

1. **Dual-Channel Scoring Core:**
   - **Channel A (Semantic OOD):** Measures semantic deviation from reference contract clause centroids derived from the LEDGAR corpus using Legal-BERT embeddings.
   - **Channel B (Discourse Transition Coherence):** Evaluates sequential transition probabilities between adjacent clauses using a trained discourse coherence model.
2. **Decision-Support Severity Ranking:** Categorizes clause findings into `HIGH`, `MEDIUM`, or `LOW` severity with cross-channel agreement analysis.
3. **Conformal Confidence Calibration:** Assigns empirical 95% confidence intervals to anomaly scores. *(Calibration Source: Synthetic shuffle permutations only).*
4. **Explainability & Evidence Layer (XAI):** Provides token-level Integrated Gradients attributions, neighbor perturbation sensitivities, and corpus nearest neighbors, with explicit claim-scoping documentation.
5. **Auxiliary Heuristic Checkers:** Identifies dangling internal section references, conflicting milestone dates, and missing boilerplate provisions.
6. **Hardened API & Security:** Authenticated FastAPI backend (`X-API-Key`), Fernet authenticated encryption at rest (AES-128-CBC + HMAC-SHA256), process-local rate limiting, zero plaintext logging, and automated 24-hour retention purge.
7. **Production Frontend:** Next.js 16 (App Router / TypeScript / Turbopack) dashboard with sequence coherence heatmap, mandatory pre-upload privacy notice acknowledgment, and reviewer feedback loop.
8. **Multi-Service Orchestration:** Docker Compose stack with PostgreSQL 16 and MinIO object storage.

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

---

## 3. Human-Feedback Loop Status

- **Architecture:** `POST /v1/feedback` persists reviewer verdicts in SQLite or PostgreSQL with audit logging.
- **Verification Status:** Tested with synthetic test fixtures (`SYNTHETIC_TEST`).
- **Research Integrity Disclosure:** In accordance with Global Contract Item 2, simulated feedback has **not** been presented as real reviewer validation. The feedback recalibration mechanism is mechanically complete and waiting on future professional human legal review.

---

## 4. Quickstart Guide

### Option A: Docker Compose (Recommended)

```bash
# 1. Copy environment template
cp .env.example .env

# 2. Build and launch all services (Postgres, MinIO, Backend, Frontend)
docker compose up --build -d

# 3. Access web dashboard
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000/docs
```

### Option B: Local Python Development

```bash
# 1. Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Or: .venv\Scripts\activate on Windows

# 2. Install dependencies & spaCy language model
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# 3. Set development API key
export API_KEY="dev_auditor_key_12345"

# 4. Start FastAPI backend
uvicorn src.api.main:app --host 0.0.0.0 --port 8000

# 5. Start Next.js frontend (in another terminal)
cd frontend
npm ci
npm run dev
# Or launch the companion Streamlit dashboard:
streamlit run src/ui/app.py
```

---

## 5. Automated Verification & Testing

```bash
# Run backend security & integration tests
pytest -v tests/test_security.py tests/test_api_integration.py

# Run security review checklist tests
pytest -v tests/test_security_review.py

# Run prompt verification gates
python verify_prompt_17.py
python verify_prompt_18.py
python verify_prompt_19.py

# Run stack smoke test
python smoke_test_compose.py
```

---

## 6. Repository Structure

```
├── .github/workflows/ci.yml       # GitHub Actions CI workflow
├── data/raw/sec_edgar/            # Clean SEC EDGAR Exhibit 10 contracts
├── docs/                          # Architecture, rollback, & security documentation
├── fixtures/                      # Verified evaluation benchmark results & claim matrix
├── frontend/                      # Next.js 16 production frontend (App Router)
├── scripts/
│   ├── backup_database.py         # Automated database backup script
│   ├── restore_database.py        # Automated database restore script
│   ├── migrate_sqlite_to_postgres.py # SQLite -> PostgreSQL migration
│   ├── monitor_health.py          # Uptime & health probe
│   └── run_load_test.py           # Multi-tier realistic load test
├── src/
│   ├── api/                       # Hardened FastAPI backend (auth, retention, encryption)
│   ├── coherence/                 # Discourse coherence models & registry
│   ├── embeddings/                # Legal-BERT embeddings & contrastive model
│   ├── feedback/                  # Hybrid SQLite / PostgreSQL feedback storage
│   ├── rules/                     # Reference and date consistency checkers
│   ├── scoring/                   # Dual-channel anomaly scoring pipeline
│   └── ui/app.py                  # Companion Streamlit dashboard
├── tests/                         # Full automated test suite
├── docker-compose.yml             # Local multi-service orchestration
├── Dockerfile.backend             # Multi-stage Python backend container
├── render.yaml                    # Render cloud deployment blueprint
└── railway.json                   # Railway cloud deployment manifest
```

---

## 7. Known Limitations

1. **Process-Local Rate Limiting:** Sliding-window rate limiting currently runs in-process. Clustered multi-worker deployments will require Redis or distributed key-value storage.
2. **Conformal Intervals:** Bounds are computed under exchangeability assumptions on synthetic shuffle permutations, not real human contractual defect distributions.
3. **Hardware Constraints:** Inference runs on CPU. High-throughput batch processing of 100+ page filings benefits from GPU acceleration.
