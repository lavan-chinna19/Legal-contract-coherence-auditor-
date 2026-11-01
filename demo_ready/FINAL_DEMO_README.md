# LexAudit — Final Faculty Demo Quick-Start & Operation Guide

**Application Status:** `DEMO_READY_WITH_LIMITATIONS`  
**Active Environment:** Docker Compose Release Profile (`lexaudit-release`)  
**Deployment Date:** October 2026  
**Audience:** Faculty Review Committee, Project Evaluators, Engineering Demonstration  

---

## 1. Quick Access Information

| Component | Target URL | Underlying Service | Status |
| :--- | :--- | :--- | :--- |
| **Frontend UI** | [http://127.0.0.1:3001](http://127.0.0.1:3001) | Next.js 14 Production Server (`lexaudit-release-frontend-1`) | **ONLINE (Healthy)** |
| **Backend API Gateway** | [http://127.0.0.1:8011](http://127.0.0.1:8011) | Nginx 1.28 Ingress Reverse Proxy (`lexaudit-release-gateway-1`) | **ONLINE (Healthy)** |
| **Backend Core API** | Internal (routed via `:8011`) | FastAPI Uvicorn Server (`lexaudit-release-backend-1`) | **ONLINE (Healthy)** |
| **Database** | Internal (`5432`) | PostgreSQL 16 Alpine (`lexaudit-release-postgres-1`) | **ONLINE (Healthy)** |

> [!IMPORTANT]
> **Authentication Credential:**
> The active Docker deployment uses the private API key configured in `.env.docker.local` (variable `API_KEY`).
> In accordance with security protocol, this key is masked (`type="password"`) in the UI and must **never** be projected or committed to version control.
> *(For native `--demo` runs on port 8010, the public key `dev_auditor_key_12345` is used instead).*

---

## 2. Directory Contents & Demo Assets (`demo_ready/`)

All necessary synthetic contracts, reports, and rehearsal evidence are stored locally in `demo_ready/` (available at both `F:\projects\nlp\demo_ready` and `F:\projects\nlp\Legal-contract-coherence-auditor-\demo_ready`):

```
demo_ready/
├── FINAL_DEMO_README.md                 <-- This operational guide
├── FACULTY_DEMO_SCRIPT.md               <-- Timed speaking script with click sequence
├── DEMO_VERIFICATION_REPORT.md          <-- Senior QA end-to-end verification report
├── LexAudit_Clean_Synthetic_Contract.txt <-- 6-clause synthetic baseline contract
├── LexAudit_Broken_Directional_Reference.txt <-- Synthetic contract with directional defect ("Section 4 above")
├── synthetic-contract.txt               <-- Multi-format ingestion fixture (TXT)
├── synthetic-contract.pdf               <-- Multi-format ingestion fixture (PDF)
├── synthetic-contract.docx              <-- Multi-format ingestion fixture (DOCX)
├── LexAudit_Clean_Report.pdf            <-- Real generated PDF audit report (Clean contract)
├── LexAudit_Clean_Report.docx           <-- Real generated DOCX audit report (Clean contract)
├── LexAudit_Broken_Ref_Report.pdf       <-- Real generated PDF audit report (Broken reference + finding)
├── LexAudit_Broken_Ref_Report.docx      <-- Real generated DOCX audit report (Broken reference + finding)
└── screenshots/                         <-- High-resolution walkthrough captures
    ├── 01_overview_and_connection.png
    ├── 02_contract_review_workspace.png
    ├── 03_explainability_xai.png
    ├── 04_analytics_dashboard.png
    ├── 05_robustness_lab.png
    ├── 06_transparency_benchmarks.png
    ├── 07_dependency_graph_and_reports.png
    ├── 08_reviewer_feedback_submitted.png
    └── 09_saved_documents_reopened.png
```

---

## 3. Step-by-Step Demonstration Sequence

### Step 1: Open Application & Verify Health
1. Open browser to [http://127.0.0.1:3001](http://127.0.0.1:3001).
2. Observe top-right status badge: **"online"** (green indicator).
3. In **Connection** (top header bar):
   - **API URL:** `http://127.0.0.1:8011`
   - **API Key:** Enter key from `.env.docker.local` (masked input).
4. Under **Session and reports**, click **"Sign in / Refresh saved documents"**.
   - Status updates: *"Signed in. Saved documents refreshed."*

### Step 2: Ingest & Parse Clean Synthetic Contract
1. In `1. Upload & Ingest`:
   - Check the privacy consent box: *"I acknowledge that documents are processed locally and encrypted at rest."*
   - Click **Choose File** and select `demo_ready/LexAudit_Clean_Synthetic_Contract.txt`.
2. Click **"Parse and preview clauses"**.
   - Notice: Contract splits cleanly into 6 numbered clauses with exact character offsets.
3. Click **"Analyze this parsed document"**.
   - Analysis executes locally in ~2–4 seconds on CPU.
   - UI automatically transitions to `2. Coherence Heatmap & Findings`.

### Step 3: Contract Review Workspace & KPIs
1. Observe header metrics:
   - **Total Clauses:** `6`
   - **Review Flags:** `0` (clean synthetic baseline)
   - **Risk Level:** `CLEAN / Low Risk` (mean combined score ~`0.340`).
2. Click through Clauses 1 to 6 in the clause list:
   - View normalized clause text, dual-channel scoring breakdown (Channel A Centroid + Channel B Adjacent Transition), and calibration justification.

### Step 4: Explainability (XAI) & Counterfactual Repositioning
1. Click **`3. Explainability (XAI)`** in the secondary navigation:
   - **Token Attribution:** View highlighting indicating words influencing coherence.
   - **Neighbor Sensitivity:** View impact of surrounding clauses.
2. In the clause detail panel, locate the **Counterfactual Repositioning** section:
   - Evaluates alternative sequence positions without modifying the source contract.

### Step 5: Analytics Dashboard
1. Click **`Analytics & Findings`** in the left sidebar navigation:
   - View score distribution charts, risk categorization breakdown, and statistical dispersion metrics.

### Step 6: Export Structured Reports
1. In the **Session and reports** card:
   - Click **"Download PDF report"** (downloads `LexAudit-<job_id>.pdf`).
   - Click **"Download DOCX report"** (downloads `LexAudit-<job_id>.docx`).
2. Show downloaded files: Contains metadata, clause scores, calibration notes, and audit provenance.

### Step 7: Broken Reference & Dependency Graph Detection
1. Click **`Overview`** in sidebar (`1. Upload & Ingest`).
2. Ensure privacy checkbox is ticked.
3. Select `demo_ready/LexAudit_Broken_Directional_Reference.txt`.
4. Click **"Parse and preview clauses"**, then **"Analyze this parsed document"**.
5. In **Session and reports**, expand **"Experimental dependency graph"**:
   - Check: *"I opt in to experimental dependency checks"*
   - Click **"Run dependency checks"**
6. Highlight observed finding:
   - **Status:** `FINDING`
   - **Reference:** `"Section 4 above"`
   - **Result:** `VERIFIED_TEXTUAL_CONFLICT`
   - **Reason:** *"Explicit directional reference contradicts the target's location."* (Section 4 appears after Section 2).

### Step 8: Reviewer Feedback Submission
1. Click **`4. Reviewer Feedback`** in the sidebar.
2. Verify / configure fields:
   - **Verdict:** `CONFIRM_ANOMALY`
   - **Reviewer Signature ID:** `faculty_demo_qa`
   - **Provenance:** `SYNTHETIC_TEST`
3. Click **"Submit Feedback to API"**.
   - Status confirmation appears with generated UUID `Feedback ID`.

### Step 9: Reopen Saved Document History
1. In **Session and reports**, expand **"Saved documents"**.
2. Locate any prior completed document and click **"Reopen analysis"**.
3. Observe: The workspace reloads immediately from encrypted storage without re-running inference.

---

## 4. Verified Capabilities vs. Limitations

| Feature / Domain | Verified Capability | Documented Limitation |
| :--- | :--- | :--- |
| **Document Ingestion** | UTF-8 TXT, DOCX, text PDF up to 10 MB and 500 clauses. | Scanned PDFs require separate OCR; encrypted PDFs not supported. |
| **NLP Inference** | Dual-channel scoring using local `nlpaueb/legal-bert-base-uncased` embeddings on CPU. | Scores represent *review prioritization*, not legal advice or certification. |
| **Directional References** | Deterministic detection of `"Section X above/below"` conflicts. | Purely rule-based text position check; does not semantically interpret legal cross-conditions. |
| **Reviewer Feedback** | Cryptographic storage of feedback records with provenance. | Feedback is collected for offline auditing; does **not** dynamically retrain weights in real time. |
| **Privacy & Security** | Fernet encryption-at-rest; zero data transmitted externally; no token logging. | Single-host deployment; session tokens stored in browser page memory only. |

---

## 5. Troubleshooting Matrix

| Symptom | Probable Cause | Action |
| :--- | :--- | :--- |
| Backend indicator says `offline` | Docker gateway or backend process stopped | Check `docker compose -p lexaudit-release ps`. Services should show `Up (healthy)`. |
| Sign-in rejected (401 / 403) | Key mismatch | Ensure API key entered matches `API_KEY` in `.env.docker.local`. |
| Parse / Analyze buttons disabled | Missing prerequisite | Ensure (1) privacy checkbox is ticked, (2) file is selected, (3) signed in with valid key. |
| Dependency check button disabled | Missing opt-in | Tick *"I opt in to experimental dependency checks"* checkbox before clicking button. |
| Inference slow | First-run cold start | Wait ~5–10 seconds for initial model tensor loading into memory. |
