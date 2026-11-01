# Ten-Minute Technical Demonstration Script — Prompt 24

**Target Duration:** 10 minutes  
**Format:** Technical Viva / Architecture Deep Dive  
**Audience:** Faculty Committee, NLP Researchers, Software Architects  

---

## Technical Agenda

| Minute Range | Segment | Focus Area |
|:---:|---|---|
| **0:00 – 2:00** | System Architecture & Security Posture | Next.js 16, FastAPI, Fernet AES encryption, rate limiting |
| **2:00 – 4:30** | NLP Dual-Channel Pipeline & Mathematical Model | Legal-BERT embeddings, clause centroids, transition probabilities |
| **4:30 – 6:30** | Live Execution & Deterministic Heuristics | Real contract audit, async job polling, regex/date validation |
| **6:30 – 8:30** | Explainability (XAI) & Conformal Calibration | Integrated Gradients, perturbation sensitivity, exchangeability bounds |
| **8:30 – 10:00** | Human Feedback Loop & Architectural Limitations | SQLite/Postgres persistence, single-worker process model, future work |

---

## Detailed Section-by-Section Guidance

### 1. System Architecture & Security Posture (Min 0:00 – 2:00)
- **Architecture Overview:** Decoupled architecture combining a Next.js 16 App Router UI (TypeScript, Turbopack) with a Python 3.11 FastAPI backend.
- **Data Protection:**
  - Ingress documents are stored with Fernet authenticated encryption at rest (`AES-128-CBC` + `HMAC-SHA256`).
  - Strict 24-hour retention purge worker deletes temporary blobs.
  - Zero plaintext logging: contract contents and API credentials are never written to standard logs.
  - Rate limiting protects endpoints against denial-of-service bursts.

### 2. NLP Dual-Channel Scoring Pipeline (Min 2:00 – 4:30)
- **Channel A (Semantic OOD):**
  - Contracts are segmented into numbered clauses via rule-based and spaCy parsing (`en_core_web_sm`).
  - Each clause is mapped into dense 768-dimensional vector space using Legal-BERT (`nlpaueb/legal-bert-base-uncased`).
  - Cosine distance is measured against cluster centroids pre-computed from the LEDGAR corpus.
- **Channel B (Discourse Transition Coherence):**
  - Sequential pairwise transitions $(C_i, C_{i+1})$ are scored using a transition coherence classifier to detect structural disorganization or abrupt context switches.
- **Severity Ranking:** Combines Channel A and B scores into `HIGH`, `MEDIUM`, or `LOW` severity flags with cross-channel agreement analysis.

### 3. Live Execution & Deterministic Heuristics (Min 4:30 – 6:30)
- **Demonstration:**
  - Submit the verified demo fixture `valid_multiclause.txt` (SHA256: `55558d95947bb2050782035de4f7a9f938d29c5b3d0b8e53014cf22c8c085825`) via UI.
  - Show developer tools network tab: observe `POST /v1/upload`, `POST /v1/analyze`, and polling `GET /v1/jobs/{job_id}` until `status == "completed"`.
  - Point out rule checkers: Reference Checker verifies internal pointers (e.g., "Section 4.2" pointing to non-existent clauses); Date Checker parses ISO/standard dates to catch inverted commencement/termination dates.
  - *Observed Metrics Note:* For this specific 5-clause sample, the pipeline observes 2 anomalies, 2 high-severity flags, and a mean combined anomaly score of 0.341. Note that these are sample-specific empirical findings for the fixture, not guaranteed constants across different contracts.

### 4. Explainability & Conformal Calibration (Min 6:30 – 8:30)
- **Integrated Gradients Token Attribution:**
  - Calculates path integrals of gradients along a straight line from a baseline embedding (zero vector or padding tokens) to the input clause embedding:
    $$IG_i(x) = (x_i - x'_i) \times \int_{0}^{1} \frac{\partial F(x' + \alpha(x - x'))}{\partial x_i} d\alpha$$
  - Display the resulting 26 token badges with attribution intensities for Clause 1.
- **Conformal Prediction:**
  - Shows 95% empirical confidence bounds calculated via inductive conformal prediction (`crepes`).
  - *Integrity Note:* Emphasize that calibration nonconformity scores are derived from synthetic shuffle permutations, not human ground truth.

### 5. Reviewer Feedback & Limitations (Min 8:30 – 10:00)
- **Reviewer Feedback:**
  - Submit verdict via UI to `POST /v1/feedback` using supported API options: `CONFIRM_ANOMALY` or `REJECT_ANOMALY`.
  - Show SQLite database entry in `data/processed/feedback.sqlite` (table `feedback`).
  - Explain that recorded feedback supports future offline active learning / threshold recalibration and does not perform live parameter updates.
- **Architectural Limitations:**
  - Process-local job queue requires single-worker deployment (`--workers 1`).
  - CPU inference latency on large 100-page filings.
  - Disclose that software test pass rate (116 passing tests) validates code implementation, not legal validity.
