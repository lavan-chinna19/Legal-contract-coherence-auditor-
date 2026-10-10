# Audit Evidence Index

This document catalogs the evidence collected during the PROMPT 21B Regression Audit.
All evidence files are stored in `audit/prompt_21b/`.

### 1. Test & Baseline Evidence
- `pytest_raw.log`: Pytest suite output (95 passed, 2 skipped).
- `verify_17.txt`: Verification output for Prompt 17 frontend components.
- `verify_18.txt`: Verification output for Prompt 18 containerization.
- `verify_19.txt`: Verification output for Prompt 19 deployment configs.
- `verify_20.txt`: Verification output for Prompt 20 workflow automation.
- `frontend_build.txt`: Next.js `npm run build` static analysis output.

### 2. Defect Reproduction Evidence
The script `collect_evidence.ps1` generated the following local files:
- `BUG-001_evidence.txt`: Demonstrates fallback to ephemeral encryption key.
- `BUG-002_evidence.txt`: Demonstrates default TTL despite custom environment var.
- `BUG-003_evidence.txt`: Contains extracted AST comparison showing mismatch between frontend UI `CONFIRM_ANOMALY` and backend `VALID`/`OVERKILL` filter.
- `BUG-004_evidence.txt`: Confirms `127.0.0.1` hardcoded state in frontend component.
- `BUG-005_evidence.txt`: Search demonstrating absence of XAI API endpoints.
- `BUG-006_evidence.txt`: Search demonstrating `jobs.py` calls `DualChannelScorer` directly instead of `UnifiedAuditor`.
- `BUG-007_evidence.txt`: Static excerpt showing slicing before stripping logic.
- `BUG-008_evidence.txt`: Static excerpt showing `.npz` caching without locking.
- `BUG-009_evidence.txt`: Static excerpt showing omission of `method='higher'` in quantile fallback.
- `BUG-010_evidence.txt`: Static excerpt of unbounded `JOB_STORE` dictionary.
- `BUG-011_evidence.txt`: `Test-Path` output proving `.dockerignore` is missing.
- `BUG-012_evidence.txt`: Static excerpt showing discarded rate limit HTTP headers.

**Note:** All defects have been diagnosed in strictly static analysis or non-mutating runtime tests. No code was altered.
