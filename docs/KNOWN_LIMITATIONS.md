# Known limitations

<!-- docker-validation-final -->
**Updated 2026-10-24: 24/24 application components COMPLETE (100/100).** The user-authorized local Docker deployment and restart/recreation persistence passed. Independent scientific, legal and external security validation remains outstanding. See [DOCKER_VALIDATION_REPORT.md](DOCKER_VALIDATION_REPORT.md) and [DOCKER_RUN_AND_VALIDATION.md](DOCKER_RUN_AND_VALIDATION.md) for actual evidence and launch commands.


## Validation boundaries

- The local application is decision support, not a legal correctness or enforceability service. Independent legal annotation, unseen-family evaluation and external security review remain external blockers.
- Historical research artifacts remain exploratory. Nine directional candidates and fifteen eligible negatives are development evidence only. No new accuracy or expert-verification claim is made.
- Two full-suite tests skip because the optional CUAD order-report artifact is absent. Existing research data was not regenerated merely to remove skips.
- Docker host startup initially failed on stale runtime sockets; reversible recovery succeeded and the default container deployment is now verified. The historical optional MinIO profile is not used by the API and remains outside the verified application path.

## Operational limits

- Authentication is API-key based; there is no separate account-registration/password-reset service. An API key identifies a storage owner. The Connection form and sign-in check implement this existing architecture.
- The public demo profile is for synthetic documents. Use unique private keys and a stable encryption key for private local use. Browser credentials and plaintext are kept in page memory, not browser local storage.
- Latest completed analysis per document is persisted, encrypted. Older jobs can remain accessible in memory until pruning, but only the latest completed snapshot survives restart. Unfinished jobs do not resume after restart; retry analysis.
- A 15 minute stale-job deadline reports failure; it cannot forcibly interrupt native model execution. Restart the API if a native worker remains busy. Model operations are serialized with a bounded queue; busy/time-out responses are explicit.
- Retention cleanup runs at startup and every five minutes, not at the exact expiry instant. Keep encryption keys stable for retained files. Ephemeral development keys cannot decrypt prior-session data.
- Limits: 10 MB files, bounded multipart bodies, 100 PDF pages, 250,000 extracted characters, 500 clauses. Counterfactual and robustness routes keep their smaller existing limits. These are practical application limits, not a certified sandbox for hostile parsers.
- Scanned PDFs need OCR before upload. Password-protected, damaged or unsupported documents are rejected. DOCX ingestion reads main-document paragraph/table text without running macros, relationships or embedded objects; headers, footnotes, images and layout are not preserved.
- Clause locations refer to normalized extracted text, not original PDF page coordinates or DOCX layout. The review UI verifies returned clause IDs and exact source offsets.
- The experimental graph supports explicit numeric section identities and narrowly defined direction markers. Ambiguous/duplicate targets, Roman identities and vague boundary antecedents require review. It is not a universal discourse or legal dependency parser.
- PDF font coverage depends on Arial/DejaVu Sans availability. Unsupported glyphs are rendered explicitly as Unicode code points instead of silent missing glyphs. Human review of unusual-script documents is required.
- Reports contain sensitive excerpts. The client explicitly downloads them; local download-folder retention is controlled by the user and browser, independently of server retention.
- The global shared Python environment has unrelated OpenCV versus NumPy constraints. LexAudit's successful application checks do not repair other applications' package constraints. Use an isolated environment with the documented requirements.
- Existing dependency deprecation warnings include Starlette/httpx TestClient, tokenizer construction and an insufficient-calibration-example warning in small synthetic tests. The clean frontend install also warns about the pinned ESLint major's support lifecycle. No unrelated major upgrade was performed.

See the completion tracker and test results for the final clean-install verification state and exact counted completion.
