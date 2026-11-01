# Install and run LexAudit

<!-- docker-validation-final -->
**Updated 2026-10-24: 24/24 application components COMPLETE (100/100).** The user-authorized local Docker deployment and restart/recreation persistence passed. Independent scientific, legal and external security validation remains outstanding. See [DOCKER_VALIDATION_REPORT.md](DOCKER_VALIDATION_REPORT.md) and [DOCKER_RUN_AND_VALIDATION.md](DOCKER_RUN_AND_VALIDATION.md) for actual evidence and launch commands.


Tested platform: Windows, Python 3.11.9, Node 24.13.1, npm 11.8.0. The frontend uses Next.js 16.4.3. CPU inference is the default; large model retraining is unnecessary. Preserve this checkout, the model checkpoints and fixtures.

## Install dependencies

In PowerShell, from the repository root:

```powershell
cd F:\projects\nlp\Legal-contract-coherence-auditor-
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install torch==2.13.0 --index-url https://download.pytorch.org/whl/cpu
python -m pip install -r requirements-release-lock.txt
cd frontend
npm ci
cd ..
```

The Windows dependency snapshot pins the verified isolated environment; bootstrap the CPU Torch wheel first as shown. The optional spaCy English model is excluded from the snapshot. For other platforms, use `requirements-release.txt` and verify the resulting environment. The release requirements add ReportLab, python-docx, defusedxml and the existing Streamlit-compatible Pillow bound, plus PyArrow 25.0.1 for compatibility with NumPy 1.26.4. The existing ML pins are preserved. The spaCy English model is optional: the reference checker supports a blank English pipeline fallback. A Unicode PDF font is required: Arial on Windows or DejaVu Sans on Linux (`fonts-dejavu-core`).

## Prepare local model assets

The checkout must retain `models/coherence_classifier.pt`, `fixtures/ledgar_centroids.npz` and the calibration fixture. The public Legal-BERT model must be present in the local Hugging Face cache. To populate it once, before processing any contracts:

```powershell
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('nlpaueb/legal-bert-base-uncased', device='cpu')"
```

That command downloads public model weights, not contract text. Normal application inference loads only local files, with offline flags enforced before Hugging Face libraries import. `LEXAUDIT_ALLOW_MODEL_DOWNLOAD=1` explicitly permits public-weight setup downloads; do not enable it during private document processing. No cloud LLM service is required. Preserve the existing cache and checkpoint; do not retrain or change frozen thresholds.

## Run the synthetic demonstration

Terminal 1, repository root:

```powershell
python scripts/run_server.py --demo --port 8010
```

Terminal 2:

```powershell
cd F:\projects\nlp\Legal-contract-coherence-auditor-\frontend
npm run dev -- --hostname 127.0.0.1
```

Open `http://127.0.0.1:3000`. Open **Settings**, enter the explicit public demo key `dev_auditor_key_12345` and choose **Connect engine**. The native address defaults to `http://127.0.0.1:8010`; other trusted addresses are under **Connection address**. In **New Audit**, acknowledge privacy consent, choose TXT/PDF/DOCX, select **Upload and preview**, then **Analyze document**. **Audit Results** contains findings, clause review, analytics, explanations and opt-in reference checks. **Reports & History** contains saved audits, PDF/DOCX downloads and reviewer feedback. Suggested positions remain available from clause review; optional **Research Tools** contains the model evaluation, compatibility map and robustness experiments. Reconnect after reload: access keys are retained only in page memory.

The demo profile uses public test credentials and a public test encryption key, prints its demo status and binds to loopback. Use synthetic documents. The model inference itself is real. Port 8010 was used during verification because another application occupied port 8000. Any free port can be selected with `--port`.

## Configure private local use

Create `.env` without overwriting an existing configuration. Configure `API_KEY` or `API_KEYS`, a separate `ADMIN_API_KEY` if maintenance is needed, and a stable `STORAGE_ENCRYPTION_KEY`. Generate secrets locally:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
python scripts/run_server.py --port 8010
```

Keep the encryption key stable to reopen encrypted documents after restart. Do not rotate it without a migration. Credentials remain in browser memory and are cleared by Sign out. Never put API keys in `NEXT_PUBLIC_*` variables. Configure `CORS_ORIGINS` with exact trusted frontend origins. `NEXT_PUBLIC_API_URL` / `NEXT_PUBLIC_BACKEND_URL` configure the initial browser API URL at build time; Settings can override it explicitly during the session. Changing identity or engine clears the active document; keys are never saved in browser storage.

The launcher loads `.env` without overwriting explicit environment variables and refuses unconfigured non-demo startup. `ENV=production` also makes encryption fail closed without a configured key. Do not blindly copy the example PostgreSQL URL unless that service is running: omitting `DATABASE_URL` selects local SQLite. Optional `LEXAUDIT_UPLOAD_DIR`, `LEXAUDIT_FEEDBACK_DB_PATH`, `LEXAUDIT_EMBEDDINGS_CACHE_DIR` and `LEXAUDIT_THRESHOLDS_PATH` support isolated local runs. Default storage remains compatible with the existing application.

## Limits and retained results

- Maximum file 10 MB; multipart body also bounded before parsing; no plaintext upload spooling within the accepted bound.
- PDF up to 100 pages; extracted text up to 250,000 characters; analysis up to 500 clauses.
- Scanned PDFs require external OCR before upload; encrypted/damaged documents return validation errors.
- Model operations run serially with a bounded waiting queue; analysis admission can return a busy response. Counterfactual and robustness routes retain their smaller existing limits.
- Completed results, filenames and contract content are encrypted. The latest completed analysis per document can be reopened after restart with the same key and storage directory.
- Retention defaults to 24 hours. Cleanup runs on startup, every five minutes and through the authenticated admin endpoint. Do not point synthetic tests at real user storage.
- HTTP jobs are in process memory while running. A restart interrupts unfinished jobs; reupload/reanalyze if no completed snapshot exists. Stale jobs show a failure after 15 minutes; a stuck native worker can require an API restart.

## Checks and optimized frontend

```powershell
python -m pytest tests -q
cd frontend
npm run lint
npx tsc --noEmit
npm run test:alignment
npm run test:workflow
npm run build
npm start -- --hostname 127.0.0.1
```

Tests automatically isolate feedback, threshold files and derived-vector caches from user data, and do not inherit an external database URL. In this session, optional export libraries were installed in `.release-deps` to preserve the existing environment; the launcher appends that directory if present. A normal installation through the documented release requirements does not need it. When testing that temporary arrangement, append it to `sys.path` instead of overriding the application's existing libraries.

Fresh-machine installation and Docker execution are recorded separately in the completion tracker; successful checks in the existing environment do not prove a clean setup. Docker was initially unavailable; subsequent safe host recovery, actual image builds and container workflow verification passed. Use DOCKER_RUN_AND_VALIDATION.md for the verified Compose deployment and private configuration.
