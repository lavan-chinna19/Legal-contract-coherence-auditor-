# Production Deployment & Rollback Strategy (Prompt 19)

This document outlines the deployment architecture, configuration steps, and emergency rollback procedures for the Legal Contract Coherence Auditor on PaaS providers (Render and Railway).

---

## 1. Cloud Architecture Overview

- **Compute - Backend:** FastAPI ASGI web service (`uvicorn src.api.main:app`), auto-provisioned from `Dockerfile.backend` or Native Python 3.11 environment.
- **Compute - Frontend:** Next.js 16 standalone Node.js web service running in `frontend/`.
- **Database:** Managed PostgreSQL 16 add-on hosting the feedback schema (`feedback` table).
- **Object Storage:** Cloudflare R2 / S3-compatible bucket for encrypted contract uploads.
- **Health Checks:** Native platform polling against `/health` (backend) and `/` (frontend) with automatic restart-on-failure.

---

## 2. Secrets & Environment Management

All credentials are injected via platform secrets management; zero secrets are committed to the Git repository.

| Secret Key | Description | Target Service |
|---|---|---|
| `API_KEY` | Master API Key for endpoint authentication | Backend, Frontend |
| `DATABASE_URL` | PostgreSQL connection string | Backend |
| `ENCRYPTION_KEY` | Fernet 32-byte URL-safe base64 key | Backend |
| `S3_ENDPOINT_URL` | Cloudflare R2 or S3 API endpoint | Backend |
| `S3_ACCESS_KEY` | Storage Access Key | Backend |
| `S3_SECRET_KEY` | Storage Secret Key | Backend |
| `S3_BUCKET_NAME` | Name of encrypted storage bucket | Backend |

---

## 3. Automated Platform Rollback Procedures

### A. Render Rollback Procedure
1. Navigate to the **Render Dashboard** -> Select `legal-contract-auditor-api`.
2. Open the **Events** or **Deploys** tab.
3. Locate the last known good deployment commit.
4. Click the three dots menu (`...`) next to the commit -> Select **"Rollback to this deploy"**.
5. Render immediately stops traffic routing to the degraded instance and redirects traffic to the previous healthy container artifact (Instant Rollback, < 30s).
6. Repeat for `legal-contract-auditor-ui` if frontend regression occurred.

### B. Railway Rollback Procedure
1. Open the **Railway Dashboard** -> Select your project service.
2. Go to the **Deployments** panel.
3. Find the previous stable deployment in the history list.
4. Click **Redeploy** or **Rollback**.
5. Railway initiates an atomic zero-downtime container switchover once healthchecks pass.

---

## 4. Database Schema Rollback

The feedback schema is non-destructive (additive columns, idempotent `ON CONFLICT` updates).
If a database rollback is required:
1. Connect via `psql $DATABASE_URL`.
2. Inspect table state: `SELECT COUNT(*) FROM feedback;`.
3. If necessary, execute table recreation or backup restore via `scripts/restore_postgres.py`.

---

## 5. Post-Rollback Validation Checklist

After executing a rollback:
1. Query `/health` -> Confirm HTTP 200 `{"status": "ok"}`.
2. Query `/ready` -> Confirm HTTP 200 `{"status": "ready"}`.
3. Run live smoke test: `python smoke_test_compose.py --backend-url <LIVE_URL> --api-key <API_KEY>`.
4. Inspect security audit log to confirm zero error spikes.
