# Demo Environment Setup Guide — Prompt 24

**Audience:** Faculty Evaluator, Demonstration Operator, Release Engineer  
**Target Environment:** Windows 10/11 Laptop with Python 3.11+ and Node.js 18+  
**Tested Stack:** FastAPI, Next.js 16 (App Router / Turbopack), spaCy `en_core_web_sm`, PyTorch / Transformers  

---

## 1. Prerequisites Checklist

Ensure the following tools are available in your Windows PowerShell environment:
- **Python:** `python --version` (3.11.x recommended)
- **Node.js:** `node -v` (v18.x or v20.x+)
- **NPM:** `npm -v` (v9.x or v10.x+)
- **Git:** `git --version`

---

## 2. Step-by-Step Operator Startup Sequence

### Step 1: Open Terminal 1 — Backend Startup
Open a Windows PowerShell terminal at the repository root `F:\projects\nlp\Legal-contract-coherence-auditor-`:

```powershell
# 1. Activate virtual environment
.\.venv\Scripts\Activate.ps1

# 2. Set required runtime environment variables using canonical variables
$env:API_KEY = "dev_auditor_key_12345"

# Generate canonical 32-byte Fernet key locally (never hardcode secrets in source or docs):
$env:STORAGE_ENCRYPTION_KEY = python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
# NOTE: In persistent deployments, store this key securely outside Git and supply the SAME key across restarts so previously encrypted documents remain decryptable.

# 3. Start FastAPI backend with single-worker configuration
# IMPORTANT: Single-worker is mandatory for in-memory job coordination
python -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000 --workers 1
```

**Verification:** In your browser or curl, navigate to `http://127.0.0.1:8000/health`. Expected response:
```json
{"status": "healthy", "version": "1.0.0"}
```

---

### Step 2: Open Terminal 2 — Frontend Startup
Open a second Windows PowerShell terminal:

```powershell
# Navigate to the frontend directory
cd frontend

# Start the Next.js development server
npm run dev
```

**Verification:** In your browser, navigate to `http://localhost:3000`. Expected page title:
`Legal Contract Coherence Auditor | Research Prototype`

---

### Step 3: Verified Nonconfidential Demonstration Contract
The demonstration utilizes a verified nonconfidential, synthetic demonstration fixture located at:
`audit/prompt_23/evidence/fixtures/valid_multiclause.txt`  
(SHA256: `55558d95947bb2050782035de4f7a9f938d29c5b3d0b8e53014cf22c8c085825`, Size: 597 bytes)

**Fixture Content:**
```text
1. Term and Duration. This Agreement commences on January 15, 2026 and terminates on January 14, 2027.
2. Confidentiality Obligations. The Receiving Party agrees to protect Confidential Information as defined in Section 1.
3. Intellectual Property Rights. All patent, copyright, and trade secret rights shall remain the sole property of the Discloser.
4. Termination for Convenience. Either party may terminate this Agreement pursuant to Section 1 upon thirty (30) days notice.
5. Dispute Resolution. All disputes arising under this Agreement shall be resolved via arbitration in New York, NY.
```

**Observed Metric Output (for this specific fixture):**
- Total Clauses: 5
- Total Anomalies: 2 (Clause 1 and Clause 5)
- High Severity Count: 2
- Medium Severity Count: 0
- Mean Anomaly Score: 0.341
- Integrated Gradients Attribution: 26 token badges for Clause 1

*(Note: These numbers reflect empirical execution on this fixture under current frozen checkpoints; other contracts will naturally produce different results).*

**Feedback Interface Options:**
When testing the feedback loop, the UI offers supported API verdict options:
- `CONFIRM_ANOMALY` (True positive anomaly)
- `REJECT_ANOMALY` (False positive alarm)

---

## 3. Teardown / Reset
To stop services after the demonstration:
- In Terminal 1: Press `Ctrl + C` to stop FastAPI.
- In Terminal 2: Press `Ctrl + C` to stop Next.js.
- Local feedback database persists in `data/processed/feedback.sqlite` (table `feedback`) and can be inspected with SQLite CLI or DB Browser for SQLite.
