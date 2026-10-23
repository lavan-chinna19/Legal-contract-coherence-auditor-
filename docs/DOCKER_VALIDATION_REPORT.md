# Docker validation and final application completion

**Application completion: 24/24 COMPLETE = 100/100. Demo classification: DEMO_READY_WITH_LIMITATIONS. Production scientific/legal/security readiness: not independently validated.**

This result follows actual Dockerized acceptance; it is not awarded for writing container files. The native full regression previously passed 244 tests with two documented optional-CUAD skips. The Linux image separately passed the 20 release acceptance tests; these counts overlap and are not added together.

| Verification | Actual result |
| --- | --- |
| Docker host recovery | Engine 29.6.1 responds after reversible runtime-socket quarantine |
| Compose build and configuration | Exit 0 |
| Backend/frontend/gateway/PostgreSQL | All healthy |
| Real HTTP/runtime checks | 103 PASS |
| Image/storage checks | 14 PASS |
| Browser assertions | 10 PASS |
| Release tests inside offline Linux image | 20 passed, exit 0 |
| Authentication and owner isolation | Missing/invalid keys rejected; other owner preview/export denied |
| TXT/PDF/DOCX | Actual upload, preview, local inference and exports passed |
| History and persistence | Exact saved scores/evidence survive restart and fresh application-container recreation |
| PostgreSQL feedback | Actual synthetic feedback survives database restart and application recreation |
| PDF/DOCX reports | Packages reopen; required factual content and protected-download headers verified before/after restart/recreation |
| Local inference/privacy | CPU Torch; offline settings; blocked external routing; read-only public model mount |
| Image contents | Frozen checksums match; no uploaded documents, saved databases, private env files or cache baked into images |

## Host issue and safe recovery

Docker Desktop 4.82.0 failed before LexAudit ran: inaccessible zero-byte AF_UNIX reparse points at `Docker/run/dockerInference`, then `docker-secrets-engine/engine.sock`. The logs show the Inference manager error predating this release. WSL checks passed. With Docker stopped, only these runtime directories were renamed to timestamped sibling backups. A clean start restored the engine. No factory reset, WSL unregister, volume removal, prune or software upgrade occurred. Backups are retained as documented in DOCKER_RUN_AND_VALIDATION.md.

## Deployment corrections

Required Dockerfiles exist and the canonical frontend/backend images actually built. Image contexts are allowlisted. The backend copies only source and three frozen runtime assets; user data is never copied. Frontend uses Node 24.13.1, receives the public API URL during build and runs as a non-root user. The backend runs as UID 10001, one CPU worker, with bounded resources and readiness-based health checks. API/database/encryption keys are generated in Git-ignored `.env.docker.local`; retain that file for history. A read-only named volume exposes only the seeded public Legal-BERT cache; the one-shot setup copies from a read-only host mount without downloads. A non-root Nginx gateway connects loopback ingress to the private backend; request buffering and access logging are disabled. Named volumes retain encrypted uploads/snapshots, vectors, file-based configuration and PostgreSQL data. MinIO is preserved as an optional legacy profile and is not used by the API or claimed as verified.

## Exact launch and verification commands

```powershell
python scripts/initialize_docker_env.py
docker compose --env-file .env.docker.local -p lexaudit-release config --quiet
docker compose --env-file .env.docker.local -p lexaudit-release --progress plain build
docker compose --env-file .env.docker.local -p lexaudit-release --profile tools run --rm --no-deps model-setup
docker compose --env-file .env.docker.local -p lexaudit-release up -d --wait --wait-timeout 300
python scripts/validate_docker_release.py
python scripts/audit_docker_images.py
python scripts/test_docker_release_image.py
```

Frontend: `http://127.0.0.1:3001`; backend: `http://127.0.0.1:8011`. Copy your private API_KEY from `.env.docker.local` into Connection. Existing native services on 3000/8010 were not replaced. The Compose project is `lexaudit-release`; no pre-existing project volumes were present when validation began. Use the documented installed Python environment for the scripts.

## Evidence and limits

`tmp/docker-validation` retains initial/recovered host diagnostics, reversible recovery records, real build output, actual command arguments/exit codes, service health, redacted logs, acceptance JSON, report packages, image audit and Linux test output. The first PyTorch download experienced network/TLS interruptions, then resumed with certificate verification intact; no TLS bypass was used.

Local functional completion does not establish legal correctness or model generalization. Independent annotation/adjudication, unseen-family confirmatory evaluation and external security validation remain external blockers. Two native optional research-artifact tests remain skipped. Font/layout coverage, hostile-parser security and operational reliability are bounded by the documented tests, not universally certified. No model retraining, dataset relabeling, frozen-result modification or external deployment was performed. Git publication was not part of the Docker validation stage; the subsequent user-authorized release branch and final regression are documented in RELEASE_PUBLICATION.md.

## Encountered failures and verified corrections

- The first container run was healthy internally but host connections failed: Docker did not publish ports on the internal-only network. A separate ingress network and local gateway corrected this while preserving backend egress isolation. The failed run is retained in `first-network-failure.json`/`.log`.
- Slow Windows cache reads exposed overlapping lazy initialization during readiness. Model construction is now serialized; the public cache is seeded once into a persistent Linux volume and mounted read-only by the API. No weights were retrained or changed.
- During planned backend maintenance the already-running gateway became unhealthy; Compose's immediate wait observed that old state before its next probe recovered. The runner now uses a finite health-recovery wait. `cold-start-health-failure.json`/`.log` retains that failed attempt; the final acceptance rerun passes all 103 checks.
- Five native embedding/concurrency checks passed (96.10 seconds, exit 0). Twenty release tests passed inside the offline Linux image (54.36 seconds, exit 0). The earlier full native run remains 244 passed/two skipped; it predates the additional concurrency test and is not represented as a fresh full run after that change.
- The historical optional MinIO image manifest probe returned registry access denied. Source has no S3/MinIO integration; that preserved optional profile is not started or claimed as verified. The required application deployment is frontend, gateway, backend and PostgreSQL.
- Browser export helpers could not directly save a snapshot to the workspace through their file-path option. The actual masked snapshot was read and saved with the authorized workspace file tool instead. Browser workflow assertions themselves passed.

All three pages of a Docker-generated PDF were rendered and visually inspected. Both PDF and DOCX factual package checks passed before and after restart/recreation. The final Chromium flow signed in, uploaded synthetic text, previewed four clauses, analyzed the same document, downloaded both reports and reopened the saved analysis without a user-facing error.

Final postflight confirmed the exact newly created feedback ID is present after restart/recreation. Container pip check exited 0 (no broken requirements). Final frontend, health and readiness endpoints returned 200; all four services remained healthy. Evidence: final-postflight.json, container-pip-check.log, final-live-services.json and final-live-http.json under tmp/docker-validation.
