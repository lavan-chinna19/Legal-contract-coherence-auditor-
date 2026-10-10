# Manual Acceptance Readiness Assessment

**Phase:** Prompt 22A
**Date:** 2026-10-10
**Overall Readiness Verdict:** **READY FOR MANUAL ACCEPTANCE TESTING**

---

## 1. Readiness Summary

The **Legal Contract Coherence Auditor** has completed all automated verification gates, regression test suites, security closures, and frontend production builds.

- **Automated Regression:** 116 passed, 2 skipped, 0 failed across all 20 historical development phases.
- **Security Closures:** Object-level authorization and administrative endpoint protection verified.
- **Pipeline Integration:** Unified auditor, explainability (XAI), and reviewer feedback verified end-to-end.
- **Frontend Build:** Next.js production build succeeded with 0 TypeScript/compilation errors.

---

## 2. Manual Testing Instructions for QA / Release Auditor

### Step 1: Environment Setup
1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
2. Set isolated client and admin keys in `.env`:
   ```ini
   API_KEY=client_alice_secret_123
   API_KEYS=client_alice_secret_123,client_bob_secret_456
   ADMIN_API_KEY=admin_super_secret_999
   STORAGE_ENCRYPTION_KEY=
   ```
   *(Note: Leave `STORAGE_ENCRYPTION_KEY` blank for development ephemeral encryption, or generate a 32-byte Fernet key).*

### Step 2: Start the Backend Service
In terminal 1:
```bash
uvicorn src.api.main:app --host 127.0.0.1 --port 8000 --reload
```
Verify readiness:
```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/ready
```

### Step 3: Start the Next.js Frontend
In terminal 2:
```bash
cd frontend
npm run dev
```
Open browser to `http://localhost:3000`.

### Step 4: Full User Journey Verification (Client Alice)
1. **API Key Input:** Enter `client_alice_secret_123` in the API Key configuration field.
2. **Privacy Notice:** Observe the Privacy and Data Retention Policy disclosure. Confirm the "Analyze Contract" button is disabled until the checkbox "I have reviewed and acknowledge the Data Retention and Privacy Notice" is checked.
3. **Upload Contract:** Upload a real contract file (e.g. from `data/raw/edgar/` or a custom text contract).
4. **Trigger Analysis:** Click "Analyze Contract".
5. **View Results:** Observe:
   - Total Clauses, ML Anomalies, and Rule Flags cards.
   - Sequence Coherence Heatmap with per-clause Channel A, Channel B, and Combined anomaly scores.
   - 95% Conformal Confidence Intervals with `synthetic_shuffle_only` calibration source label.
   - Deterministic rule violation table (cross-reference and date entity findings).
6. **Explainability Tab:** Click the "Explainability" tab. Select a clause and verify token-level Integrated Gradients attributions and neighborhood perturbation scores are computed and displayed.
7. **Submit Reviewer Feedback:** Submit a verdict (`CONFIRM_ANOMALY` or `REJECT_ANOMALY`) on a clause. Confirm the feedback ID is recorded.

### Step 5: Multi-Tenant Isolation Verification (Client Bob vs Alice)
1. Open an incognito browser window or a second tab.
2. Configure API key as `client_bob_secret_456`.
3. Attempt to fetch or analyze Client Alice's `doc_id` or `job_id`:
   ```bash
   curl -H "X-API-Key: client_bob_secret_456" http://127.0.0.1:8000/v1/jobs/<ALICE_JOB_ID>
   ```
4. Verify response is `404 Not Found` (`{"detail": "Job not found."}`).

### Step 6: Administrative Cleanup Verification
1. Attempt cleanup with Alice's key:
   ```bash
   curl -X POST -H "X-API-Key: client_alice_secret_123" http://127.0.0.1:8000/v1/maintenance/cleanup
   ```
   Verify response is `403 Forbidden` (`{"detail": "Administrative privileges required."}`).
2. Attempt cleanup with Admin key:
   ```bash
   curl -X POST -H "X-API-Key: admin_super_secret_999" http://127.0.0.1:8000/v1/maintenance/cleanup
   ```
   Verify response is `200 OK` (`{"status": "cleanup_complete", "result": ...}`).

### Step 7: Legal Disclaimer and Claim Discipline Verification
1. Confirm that every page/view contains the prominent disclaimer:
   > *"Academic Research Prototype — Not Legal Advice"*
2. Confirm the UI copy strictly avoids prohibited marketing terms ("production-ready", "100% accuracy", "enterprise-grade").

---

## 3. Known Boundaries and Operator Notes

1. **Job Retention Across Server Restarts:**
   The process-local job store holds active jobs in memory. If the Uvicorn process restarts while a job is running or before results are polled, querying the job returns 404. Uploaded contracts persist on disk in encrypted form.
2. **CPU Model Inference Latency:**
   Transformer zero-shot inference (BART-MNLI and Legal-BERT) on CPU averages 8–14 seconds per full contract. The polling progress indicator properly keeps the UI responsive during processing.
