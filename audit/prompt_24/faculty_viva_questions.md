# Anticipated Faculty Viva Questions & Answers — Prompt 24

**Target Audience:** Candidate defending research prototype before faculty committee  
**Focus:** NLP theory, software architecture, security, and scientific integrity  

---

### Question 1: Why did you choose a dual-channel architecture instead of a single end-to-end language model?
**Answer:**  
"A single generative or sequence model tends to conflate semantic topicality with discourse flow. A clause might discuss an ordinary topic (like indemnification) but appear completely out of logical order, or conversely, have smooth transitions while introducing an unprecedented statutory clause. By separating Channel A (Semantic Out-of-Distribution scoring against LEDGAR centroids) from Channel B (Discourse Transition probabilities between adjacent clauses), we isolate topical deviations from structural sequence disorganization. This allows cross-channel agreement analysis and yields more granular diagnostic explanations for human auditors."

---

### Question 2: What are the theoretical foundations and limitations of your Conformal Prediction calibration?
**Answer:**  
"We apply inductive conformal prediction using nonconformity scores to produce valid 95% confidence intervals around anomaly scores without distributional assumptions. However, conformal guarantees require the *exchangeability* property between calibration and test samples. In our prototype, calibration was computed against synthetic clause shuffle permutations rather than real human contractual defect distributions. Therefore, we explicitly disclose that these intervals represent empirical bounds under synthetic perturbation assumptions, not certified guarantees on real commercial contracts."

---

### Question 3: How does your Integrated Gradients implementation work, and can a lawyer rely on it as legal reasoning?
**Answer:**  
"Integrated Gradients computes the Riemann approximation of path integrals of gradients along a linear interpolation from a baseline embedding to the input token representation. It satisfies the axioms of Completeness and Implementation Invariance. However, we explicitly warn users that token attributions represent *model-internal feature importance*, not legal statutory reasoning. A high attribution score on a token indicates that the word strongly influenced the model's vector projection, not that the clause violates legal doctrine."

---

### Question 4: Your tests report 116 passing tests. Does that mean your model has high accuracy?
**Answer:**  
"No, and this distinction is crucial to our research integrity. The 116 passing pytest tests verify software engineering correctness—such as encryption integrity, input validation, API routing, rate limiting, and component interfaces. Model performance, by contrast, is measured using NLP benchmark metrics like Kendall's Tau ($\tau = -0.0285$), which reflects how well discourse ordering is preserved. We do not conflate software regression test pass rates with machine learning classification accuracy, and we do not claim unsupported 95% accuracy."

---

### Question 5: How does your system handle state across workers, and why is it currently restricted to a single worker?
**Answer:**  
"Currently, job tracking (`_jobs`) and rate limiting run in process-local memory within the FastAPI application instance. In a multi-worker setup (such as Uvicorn or Gunicorn with multiple workers), a client polling `GET /v1/jobs/{job_id}` might hit a worker that did not ingest the job, resulting in an intermittent 404 error. To prevent race conditions in this research prototype, the deployment is strictly configured for a single worker (`--workers 1`). In our architectural roadmap, we have designed a Redis/Celery shared task broker for distributed scaling."

---

### Question 6: What security controls prevent unauthorized access or disclosure of sensitive contract text?
**Answer:**  
"We implement a multi-layered security model:
1. **Authentication:** All analysis, retrieval, and feedback endpoints require an `X-API-Key` header with constant-time verification.
2. **Encryption at Rest:** Uploaded documents are encrypted using Fernet (`AES-128-CBC` with `HMAC-SHA256`) before being written to disk.
3. **Data Retention:** An automated background retention purge deletes documents after 24 hours.
4. **Log Hygiene:** The logging framework scrubs contract plaintext and credential tokens to ensure zero confidential data leakage."

---

### Question 7: What happens when a reviewer submits feedback via the UI? Does the model immediately update its weights?
**Answer:**  
"No. The feedback loop records the reviewer's verdict (`CONFIRM_ANOMALY` or `REJECT_ANOMALY`), reviewer ID, and cryptographic provenance into a persistent SQLite/PostgreSQL database. It does not perform online parameter updates, which could destabilize the model or introduce adversarial poisoning. Instead, the collected feedback forms an auditable dataset intended for offline threshold recalibration and active learning."
