# Final release baseline

Inspected 2026-10-23. Authoritative checkout at that time: HEAD `23dbcf5`. Existing uncommitted frontend, API, tests, research, data and audit work is preserved. At baseline inspection, no Git staging, reset, commit, push or deployment was authorized. Subsequent explicit authorization to publish a separate release branch is recorded in RELEASE_PUBLICATION.md.

| Feature | Baseline |
| --- | --- |
| Authentication | API-key authentication and per-client ownership implemented; regression verification pending |
| Upload | UTF-8 text only; PDF/DOCX missing; unbounded file read |
| Segmentation | Existing deterministic v1 segmenter; HTML normalization means offsets refer to normalized text |
| Analysis | Existing local Legal-BERT embeddings, frozen centroids and neural coherence head; live verification pending |
| Results and analytics | Existing UI and typed API; result jobs only in process memory |
| Explanations | Attribution and sensitivity routes and workspace implemented; verification pending |
| Counterfactual | Opt-in reposition API and UI implemented; verification pending |
| Robustness lab | Opt-in synthetic and active-document experiments implemented; verification pending |
| Reports | No PDF/DOCX routes or download controls |
| Dependency graph | Research data and semantic audit tests only; independent opt-in channel missing |
| Retention | Startup and admin cleanup, encrypted uploads; runtime cleanup and saved results need review |
| Installation | Python requirements and npm lock present; report libraries absent from application interpreter |

## Research status

Phase 4D-C-A withdraws confirmatory claims: exploratory benchmark, compromised preregistration and invalid order transformations. Phase 4D-D-A isolates 9 directional candidates and 15 eligible negatives, with further annotation required. These are development evidence, not independent validation. Historical checkpoints, thresholds, datasets and predictions must remain intact.

## Existing launch commands

From repository root: `python scripts/run_server.py`. Frontend, in a separate terminal: `cd frontend` then `npm run dev -- --hostname 127.0.0.1`. Existing launcher hardcodes public demo credentials and encryption configuration; replace with explicit configuration while preserving compatibility. Frontend uses `NEXT_PUBLIC_API_URL`, then `NEXT_PUBLIC_BACKEND_URL`, then `http://localhost:8000`.
