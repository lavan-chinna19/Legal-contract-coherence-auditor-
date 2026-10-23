# Local Docker deployment and validation

This guide applies to the existing CPU FastAPI/Next.js application. Independent scientific, legal and external security validation remain separate. The container completion component is not COMPLETE until the real acceptance and image/storage audit results pass.

## Host recovery performed

Initial host: Docker Desktop 4.82.0, Docker client 29.6.1, Compose 5.3.0, WSL 2.7.10.0. `wsl --status`, `wsl -l -v` and `wsl --version` succeeded. Ubuntu and docker-desktop were installed as WSL 2 distributions and stopped. `docker version` and `docker info` initially failed because the Linux-engine pipe did not exist. Docker logs showed the Inference manager error on October 10 as well as this session; this was a host startup fault before any LexAudit container ran.

The zero-byte `dockerInference` reparse point was inaccessible (Windows error 1920). With the GUI/backend stopped, the exact runtime directory was renamed to a sibling backup. Startup advanced to a second inaccessible socket, `docker-secrets-engine/engine.sock`. That directory contained only the socket. With Docker stopped again, both socket directories were preserved under timestamped sibling backup names. Docker Desktop then started and `docker info` returned server 29.6.1. No settings, volumes, WSL distributions, images or research files were deleted; no factory reset or software upgrade was performed.

Preserved directories:

- `C:\Users\gowth\AppData\Local\Docker\run.lexaudit-backup-20261023-231834`
- `C:\Users\gowth\AppData\Local\Docker\run.lexaudit-backup-20261023-232055`
- `C:\Users\gowth\AppData\Local\docker-secrets-engine.lexaudit-backup-20261023-232055`

These are retained diagnostic socket directories, not model or volume backups. Do not restore them over a running Docker instance. [Docker's matching issue](https://github.com/docker/desktop-feedback/issues/448) describes this failure class; a reported workaround is not a universal fix. Microsoft documents the inspected [WSL commands](https://learn.microsoft.com/en-us/windows/wsl/basic-commands).

## Start the application

Use the documented Python environment, which includes cryptography and the report/test dependencies. Prepare the existing public Legal-BERT cache as described in INSTALL_AND_RUN; never mount a private contract folder as a model cache.

```powershell
cd F:\projects\nlp\Legal-contract-coherence-auditor-
python scripts/initialize_docker_env.py
docker compose --env-file .env.docker.local -p lexaudit-release config --quiet
docker compose --env-file .env.docker.local -p lexaudit-release --progress plain build
docker compose --env-file .env.docker.local -p lexaudit-release --profile tools run --rm --no-deps model-setup
docker compose --env-file .env.docker.local -p lexaudit-release up -d --wait --wait-timeout 300
docker compose --env-file .env.docker.local -p lexaudit-release ps
```

The initializer creates `.env.docker.local` exclusively and preserves an existing file. It generates unique API/admin/database keys and a stable encryption key without printing them. The file is Git-ignored and excluded from build contexts. Preserve it; replacing the encryption key makes retained encrypted documents unreadable. Protect a private backup outside the repository.

Open `http://127.0.0.1:3001`. In Connection, set `http://127.0.0.1:8011` and copy `API_KEY` from your local `.env.docker.local` into the key field. Credentials remain in page memory. Ports are loopback-only and separate from the native release on 3000/8010. `LEXAUDIT_FRONTEND_PORT` and `LEXAUDIT_BACKEND_PORT` in that file can select other free ports; rebuild the frontend after changing its browser API URL.

## Services and storage

- Frontend: existing Next.js app, Node 24.13.1, non-root, telemetry disabled; the public API URL is supplied at build time. Private credentials are runtime inputs to the API, never frontend build arguments.
- Backend: existing API, CPU-only Torch, one worker/two OpenMP threads, non-root. Health checks use `/ready` so missing model assets cannot count as a healthy inference service.
- PostgreSQL 16: feedback database on `postgres_data`; not exposed on the host. Analysis history is an encrypted per-document snapshot in `uploads_data`, independently of feedback storage.
- `embeddings_data` retains derived vectors; `feedback_files` retains file-based threshold overrides. Existing volumes are not removed by the validation scripts.
- The one-shot model-setup helper copies only the public Legal-BERT files from the explicit read-only host cache into model_cache. The API mounts this persistent Linux volume read-only; subsequent starts reuse it without downloads. The image contains only the existing frozen coherence head, centroids and calibration fixture. No raw datasets, uploads, databases, `.env` files or host caches are copied into image contexts.
- The backend/database network is internal. A non-root read-only Nginx gateway and the frontend use a separate ingress network for loopback host ports; the gateway forwards requests only to the private backend. Gateway request buffering and access logging are disabled. Runtime inference does not need internet access; image building downloads public packages. HF offline flags and the explicit no-download setting apply inside the API.
- The historical MinIO definition is preserved under the optional `legacy-object-storage` profile. The API's encrypted local document storage does not call it. MinIO is not part of the default deployment or counted as a verified application integration. An explicit manifest probe of its historical image returned registry access denied; that optional service was not started or marked verified. Repository source contains no MinIO/S3 application calls.

## Acceptance and evidence

```powershell
python scripts/validate_docker_release.py
python scripts/audit_docker_images.py
python scripts/test_docker_release_image.py
```

Acceptance uses synthetic TXT/PDF/DOCX inputs. It verifies authentication/owner isolation, actual inference, source identity, history, PDF/DOCX packages and content, PostgreSQL feedback, read-only model mounts, CPU/offline settings, blocked internet egress, restart persistence and new-container recreation persistence. It restarts/recreates only the `lexaudit-release` application containers and restarts that project's PostgreSQL; it never removes volumes.

The image audit checks actual image users, secret exclusion, frozen-asset checksums, empty image data/cache directories, live mounts and encrypted persisted files. Runtime recreation does not prove resilience to disk/key loss or independent security certification.

Evidence is retained under `tmp/docker-validation`: host diagnostics, reversible recovery records, build output, acceptance JSON, exact commands/exit codes, service health and sanitized logs. Configuration outputs containing secrets are not printed. Do not publish private environment files or raw Docker inspect environment output.

To stop only this deployment while retaining its containers and volumes:

```powershell
docker compose --env-file .env.docker.local -p lexaudit-release stop
```

No factory reset, WSL unregister, volume deletion or system prune is needed for normal application use.

Cold-start hardening serializes model construction and uses the Linux model volume to avoid slow repeated Windows bind-mount metadata reads. A temporary gateway health failure during planned backend maintenance is awaited with a bounded health-poll sequence in the acceptance runner. Failed attempts are retained alongside the passing final evidence. The release suite inside the Linux image now contains 20 tests, including concurrent lazy initialization.
