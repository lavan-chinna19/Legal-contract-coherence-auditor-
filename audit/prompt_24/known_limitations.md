# Known Limitations & Operating Boundaries — Prompt 24

**Audit Phase:** Prompt 24 (Final Release Preparation)  
**System:** Legal Contract Coherence Auditor (Research Prototype)  

---

## 1. Architectural & Deployment Limitations

### 1.1 Process-Local Job Queue & Single-Worker Requirement
- **Mechanism:** Asynchronous audit jobs are stored in an in-memory dictionary (`_jobs` in `src/api/main.py`).
- **Limitation:** In a multi-worker production environment (e.g., Uvicorn or Gunicorn with `workers > 1`), polling `GET /v1/jobs/{job_id}` across different worker processes will result in intermittent `404 Not Found` errors.
- **Requirement:** The backend must be run with a single worker (`--workers 1`). Distributed scaling requires external task queuing (Redis/Celery).

### 1.2 Process-Local Rate Limiting
- **Mechanism:** Sliding-window IP rate limiting is tracked in Python memory.
- **Limitation:** Rate limits are not synchronized across clustered nodes. Clustered deployments must integrate Redis.

---

## 2. Machine Learning & Statistical Limitations

### 2.1 Conformal Prediction Exchangeability Assumptions
- **Mechanism:** Conformal coverage bounds (95% empirical confidence intervals) are calibrated using `crepes`.
- **Limitation:** Calibration was generated on synthetic shuffle permutations of clean legal contracts, not real human-annotated contractual defects. The exchangeability assumption may not hold on real-world malformed documents.

### 2.2 CPU Inference Latency
- **Mechanism:** Embedding extraction and transformer gradient computations default to CPU execution.
- **Limitation:** Analyzing long commercial filings (100+ pages) requires several minutes on standard laptop CPUs. GPU acceleration is recommended for batch processing.

---

## 3. Legal & Domain Scope Limitations

### 3.1 Decision Support Only (Not Legal Advice)
- **Scope:** The system produces heuristic and statistical signals indicating potential structural disorganization or anomalous phrasing.
- **Limitation:** Model outputs do not establish legal validity, enforceability, or compliance with any state or federal jurisdiction.

### 3.2 Unmeasured Performance Metrics
- **Scope:** The system has been validated for software regression correctness (116 passing tests).
- **Limitation:** Real-world legal precision, recall, and expert human agreement have not been measured on live legal proceedings and are marked **NOT ESTABLISHED**.
