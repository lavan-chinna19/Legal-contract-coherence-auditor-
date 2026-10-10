# Remaining Issues & Technical Debt Register

**Phase:** Prompt 22A
**Date:** 2026-10-10

---

## 1. Issue Severity Classification

| Issue ID | Severity | Category | Description | Status / Impact | Proposed Remediation |
|---|---|---|---|---|---|
| **ISSUE-01** | `CRITICAL` | Security / Secrets | No critical vulnerabilities found. | **NONE** | N/A |
| **ISSUE-02** | `HIGH` | Authorization | No high vulnerabilities found. All object-level and admin authorizations enforced. | **NONE** | N/A |
| **ISSUE-03** | `MEDIUM` | Architecture | **Process-Local In-Memory Job Store:** The current job queue (`JOB_STORE`) resides in process memory. In a multi-worker deployment (`uvicorn --workers > 1`), worker processes cannot read each other's jobs. Process restarts drop in-flight jobs. | Fails safely (HTTP 404), but restricts deployment to single-worker processes or external queue (Celery/Redis). | In a future infrastructure update, migrate `JOB_STORE` to Redis or PostgreSQL job queue table if multi-worker scaling is required. |
| **ISSUE-04** | `MEDIUM` | Git Hygiene | **Scratch Files in Git Index:** Commit `e242452` included PowerShell redirection logs (`demo.out`, `demo2.out`, `demo_fast.out`) and scratch utilities (`quick_test.py`, `create_handoff*.py`). | No secrets leaked, but causes repository bloat. | In Prompt 23 / release commit, run `git rm --cached` on these files and ignore `*.out` in `.gitignore`. |
| **ISSUE-05** | `LOW` | Test Suite | **CUAD Order Live Tests Skipped:** Two tests in `tests/test_cuad_order.py` are skipped because raw CUAD dataset is not downloaded in CI/local environment. | Normal behavior (gated by live dataset availability). Synthetic CUAD tests pass. | Documented as expected conditional skip. |
| **ISSUE-06** | `LOW` | Dependencies | **Ecosystem Deprecation Warnings:** 4 warnings in pytest suite: Hugging Face WordPiece deprecation (`WordPiece.from_file`) and Starlette TestClient warning (`httpx2`). | Non-blocking; does not affect runtime correctness. | Upgrade `transformers` and `starlette` dependencies during scheduled dependency refresh. |
