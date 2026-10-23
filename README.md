# LexAudit — Legal Contract Coherence Auditor

LexAudit is a local legal-NLP research application. **24/24 application components
are implemented and workflow-verified (100/100).** This is application completion,
not proof of legal accuracy or scientifically validated production readiness.
Outputs are research decision support, not legal advice.

Personal repository: [GoutamNandhen/NLP_](https://github.com/GoutamNandhen/NLP_).
The [original collaborative repository](https://github.com/lavan-chinna19/Legal-contract-coherence-auditor-)
and its contributor history are preserved. See [team credits](CONTRIBUTORS.md).

## Features

- API-key sign-in, per-client document ownership and protected downloads.
- TXT, PDF and DOCX ingestion, bounded parsing, clause preview and consistent
  clause identities/source spans.
- Real local CPU inference: frozen Legal-BERT embeddings, LEDGAR-derived semantic
  centroids (Channel A), learned adjacent-clause compatibility (Channel B),
  severity ranking and synthetic-shuffle conformal calibration.
- Encrypted saved analyses, history reopening, clause review, analytics and an
  aggregate pretrained clause-pair compatibility map.
- Token-level Integrated Gradients explanations and neighbor sensitivity.
- Counterfactual position suggestions with evidence and abstention; suggestions
  do not apply edits or establish legal improvement.
- Opt-in Robustness Lab with synthetic perturbations and negative controls.
- Independent experimental dependency graph with explicit directional-reference
  evidence and abstention on ambiguous targets; frozen model scores stay separate.
- Authenticated PDF/DOCX reports generated from actual saved results, including
  empty and uncertain outcomes.
- Reviewer feedback, retention cleanup, bounded job queues, safe errors and
  responsive keyboard navigation.
- Verified four-service Docker deployment with persistent storage, plus native
  development and an explicit synthetic-demo profile.

The [completion tracker](docs/FINAL_COMPLETION_TRACKER.md) records all 24 counted
components. [Research validity](docs/RESEARCH_VALIDITY_STATUS.md) and
[known limitations](docs/KNOWN_LIMITATIONS.md) describe the evidence boundaries.

## Technology stack

| Area | Technologies |
| --- | --- |
| Backend | Python 3.11, FastAPI, Uvicorn, Pydantic, python-multipart, HTTPX |
| NLP / ML | CPU PyTorch 2.13.0, Transformers 5.15.1, sentence-transformers 6.0.0, Legal-BERT, spaCy, scikit-learn, NumPy, SciPy |
| Explainability / calibration | Captum, MAPIE, crepes, frozen coherence head and centroids |
| Documents | pdfplumber, defusedxml, python-docx, ReportLab, Unicode fonts |
| Frontend | Next.js 16.4.3 App Router, React 19.3, TypeScript 5, CSS, lucide-react, ESLint 9 |
| Privacy / storage | cryptography/Fernet, encrypted snapshots, SQLite for native feedback, PostgreSQL 16 for Docker feedback |
| Containers | Docker Compose, Python 3.11 Debian images, Node 24.13.1 Alpine, Nginx 1.28, named volumes |
| Verification | pytest, TypeScript, alignment assertions, real HTTP/browser acceptance and Linux-image tests |

Exact dependencies are in `requirements-release.txt`,
`requirements-release-lock.txt` (verified Windows CPU snapshot) and
`frontend/package-lock.json`. Legacy Streamlit, MinIO and cloud definitions remain
available; they are not counted as verified release deployments.

## Installation

Clone with an account that has access to this private repository:

```powershell
git clone https://github.com/GoutamNandhen/NLP_.git
cd NLP_
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install torch==2.13.0 --index-url https://download.pytorch.org/whl/cpu
python -m pip install -r requirements-release-lock.txt
cd frontend
npm ci
cd ..
```

On Linux/macOS, use `source .venv/bin/activate` and install
`requirements-release.txt` after the CPU Torch bootstrap instead of the Windows
snapshot. Linux PDF exports require `fonts-dejavu-core`; Windows uses Arial.
The spaCy English model is optional because reference checking supports a blank
English fallback. See [Install and run](docs/INSTALL_AND_RUN.md).

Prepare the public model cache once, before processing documents:

```powershell
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('nlpaueb/legal-bert-base-uncased', device='cpu')"
```

This downloads public weights; application inference subsequently uses local
files and offline settings. Retain the included `models/coherence_classifier.pt`,
`fixtures/ledgar_centroids.npz` and calibration fixture unchanged. No retraining
is needed. Raw datasets and upstream weight caches are not stored in Git.
Review [model and dataset terms](docs/THIRD_PARTY_NOTICES.md).

## Native launch

Start the backend from the repository root for synthetic demonstrations:

```powershell
python scripts/run_server.py --demo --port 8010
```

In a separate terminal:

```powershell
cd frontend
npm run dev -- --hostname 127.0.0.1
```

Open `http://127.0.0.1:3000`. In **Connection**, set
`http://127.0.0.1:8010` and the public synthetic-demo key
`dev_auditor_key_12345`. Sign in, acknowledge the privacy notice, upload, preview
and analyze a document. Review, explanations, counterfactuals, Robustness Lab
and report downloads use the saved results.

For private use, create a Git-ignored `.env` from the empty-field template and
configure unique API keys, trusted browser origins and a stable Fernet key.
Run `python scripts/run_server.py --port 8010` without `--demo`.
Do not use public demo credentials for sensitive files or place keys in
`NEXT_PUBLIC_*`. Follow the private configuration instructions in the install guide.

## Docker launch

After dependency and public-model setup, with Docker Desktop's Linux engine or
a Linux Docker engine running:

```powershell
python scripts/initialize_docker_env.py
docker compose --env-file .env.docker.local -p lexaudit-release config --quiet
docker compose --env-file .env.docker.local -p lexaudit-release --progress plain build
docker compose --env-file .env.docker.local -p lexaudit-release --profile tools run --rm --no-deps model-setup
docker compose --env-file .env.docker.local -p lexaudit-release up -d --wait --wait-timeout 300
docker compose --env-file .env.docker.local -p lexaudit-release ps
```

Open `http://127.0.0.1:3001`; the API gateway is `http://127.0.0.1:8011`.
Enter your private `API_KEY` from `.env.docker.local` in Connection. The initializer
preserves existing keys and prints no secrets. Protect that file: losing the
stable encryption key makes retained history unreadable.

Frontend, gateway, backend and PostgreSQL form the default deployment. Backend
and database use an internal network; host ports bind only to loopback. Non-root
application containers use readiness checks. Named volumes retain encrypted
history, feedback, vectors and the public model cache. Images exclude private
files, databases and host caches. MinIO is an unused optional legacy profile.

See [Docker instructions](docs/DOCKER_RUN_AND_VALIDATION.md) and
[verified Docker results](docs/DOCKER_VALIDATION_REPORT.md). To stop these services
while retaining containers and volumes:

```powershell
docker compose --env-file .env.docker.local -p lexaudit-release stop
```

## Tests and verified results

```powershell
python -m pytest tests -q
cd frontend
npm run lint
npx tsc --noEmit
npm run test:alignment
npm run build
```

Completed full local regression: **245 passed, zero failed, two optional CUAD
report skips**. A separate publication-only snapshot passed **190 tests, zero
failed, three optional-data skips**. Its extra skip is the legacy EDGAR-sample
integration test; real synthetic-input inference acceptance passes. Frontend
lint, types, 17 alignment assertions and production build passed.

Docker verification separately passed 103 HTTP/runtime assertions, 14
image/storage checks, 10 browser assertions and 20 Linux-image release tests,
including exports and restart/recreation persistence. Counts overlap; do not
sum them as unique tests. These are recorded completed runs, not newly executed
results for a documentation-only publication.

[Release test results](docs/FINAL_RELEASE_TEST_RESULTS.md) and
[publication boundaries](docs/RELEASE_PUBLICATION.md) distinguish application
regression from local-only historical research audits. Tests isolate user data;
raw logs, generated reports and Docker evidence remain local. The retained legacy
GitHub Actions workflow is separate and has not been certified for a new private
repository run.

## Project layout

```text
src/api/         authentication, ingestion, jobs, history and reports
src/embeddings/  local embeddings and model loading
src/coherence/   frozen coherence models
src/scoring/     anomaly scoring, severity and counterfactual positions
src/rules/       reference/date checks and experimental dependency graph
src/xai/         attribution and sensitivity
src/redteam/     perturbations, oracles and robustness workflows
src/research/    experimental benchmark, ground-truth and coherence modules
src/feedback/    reviewer feedback persistence
src/deployment/ offline model-cache setup
frontend/       complete Next.js application and alignment checks
tests/          portable application and synthetic regression tests
scripts/        launch, setup, synthetic fixtures and validation tools
deploy/         Nginx gateway configuration
models/         existing small frozen coherence head
fixtures/       frozen centroids, calibration and historical results
docs/           installation, completion, reports, limitations and governance
```

## Limitations and readiness

- **DEMO_READY_WITH_LIMITATIONS**. The 100/100 checklist is not a model accuracy
  percentage or an independently validated production-readiness claim.
- Qualified legal annotation, unseen-family confirmatory evaluation and external
  security assessment remain outstanding. Historical exploratory metrics and
  compromised preregistration are documented without new accuracy claims.
- Model scores and synthetic conformal bounds are exploratory signals, not
  calibrated probabilities of legal defects. A graph conflict is textual
  evidence, not a legal ruling; no findings does not establish correctness.
- One API worker is required: running jobs and rate limits are process-local.
  Completed encrypted results survive restart; unfinished jobs may need retry.
- CPU processing can be slow. File, text, page and clause limits apply. Scanned
  PDFs need external OCR; malformed or encrypted documents are rejected.
- Font/layout, hostile-parser security and browser coverage are bounded by the
  recorded tests. Legacy interfaces and external deployments are not certified.

## Team credits and licensing

Contributors in the preserved Git history are
[GoutamNandhen](https://github.com/GoutamNandhen) and
[lavan-chinna19](https://github.com/lavan-chinna19). Original authors, commit
messages and parent history remain intact. Personal publication does not claim
sole authorship. See [CONTRIBUTORS.md](CONTRIBUTORS.md).

No project-wide `LICENSE` file is declared. This private publication adds no new
license to contributor-owned code or assets. Legal-BERT's upstream model card
lists **CC BY-SA 4.0**, not MIT. Dataset and derived-asset rights need their own
provenance review; public filing access is not blanket redistribution permission.
See [third-party notices](docs/THIRD_PARTY_NOTICES.md) and
[data governance](docs/data_governance.md). Private contracts, raw research data,
caches and optional experimental weights remain local.
