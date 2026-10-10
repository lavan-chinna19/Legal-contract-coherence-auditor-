# System Card: Legal Contract Coherence Auditor (Prompt 20)

## 1. Model & System Details
- **System Name:** Legal Contract Coherence Auditor
- **Version:** 1.0.0 (Research Prototype)
- **Model Type:** Dual-Channel Structural and Semantic Discourse Anomaly Detector
- **Primary Architectures:**
  - `nlpaueb/legal-bert-base-uncased` (frozen & contrastive fine-tuned representations)
  - Discourse Coherence Transition Classifier (bi-directional clause sequence classifier)
  - Conformal Prediction Calibration (`crepes` / `MAPIE` split conformal)

## 2. Intended Use
- **Primary Intended Use:** Academic and research evaluation of contract structure, clause order anomalies, missing standard terms, and dangling internal references.
- **Out-of-Scope / Prohibited Uses:**
  - Automated contract execution or autonomous legal advisory decisions.
  - Replacement for licensed attorney review.
  - Enforceability certification or statutory compliance auditing.

## 3. Training & Evaluation Data
- **LEDGAR Dataset:** ~60,000 clause provisions from SEC EDGAR filings for clause classification and semantic centroid baseline.
- **SEC EDGAR Exhibit 10:** 50 clean, executed commercial agreements for false positive rate estimation.
- **CUAD (Contract Understanding Atticus Dataset):** Out-of-distribution evaluation corpus.

## 4. Empirical Performance Summary (Measured vs. Target)
- **Kendall's Tau:** Measured $-0.0285$ ($p = 0.6225$, 95% CI: $[-0.125, +0.073]$) on shuffled LEDGAR provisions. Target for specialized contiguous document models: $\tau > 0.35$.
- **False Positive Rate:** Measured $1.18\%$ at High Severity ($95\%$ CI: $[0.57\%, 2.41\%]$); $44.54\%$ at Med+High Severity ($95\%$ CI: $[40.59\%, 48.55\%]$).
- **Out-of-Distribution Generalization:** Mean anomaly score of $0.3922$ on CUAD agreements.

## 5. Security & Privacy Safeguards
- **Data Encryption:** Fernet symmetric authenticated encryption at rest for all contract uploads.
- **Retention:** Hard 24-hour time-to-live automatic purge for encrypted storage and memory jobs.
- **Audit Logging:** Anonymized client IDs via SHA-256 digests; zero contract plaintext or API secrets recorded in logs.
