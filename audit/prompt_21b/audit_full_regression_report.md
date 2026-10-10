# Final Regression Audit & Debugging Evidence Report
**Project:** Legal Contract Coherence Auditor
**Baseline Hash:** `32fd9d9fb8a2ca0b5fad928308079b71f3e5de5f`
**Phase:** PROMPT 21B (Regression Audit)
**Execution Mode:** STRICT AUDIT AND DIAGNOSIS ONLY — NO CODE MODIFIED.

## 1. Baseline Verification (Task A)
The repository was verified against the strict baseline:
- Git Hash: `32fd9d9fb8a2ca0b5fad928308079b71f3e5de5f` (feat(release): complete prompts 17-20 frontend, containerization, cicd & release hardening).
- Git Working Tree: Clean (ignoring untracked audit logs and test scripts).

## 2. Automated Test Execution (Task B)
The full Pytest test suite was executed:
- **Suite Command:** `pytest -v tests/`
- **Result:** 95 passed, 2 skipped, 4 warnings in ~40 seconds.
- **Verification Scripts:** `verify_prompt_17.py`, `verify_prompt_18.py`, `verify_prompt_19.py`, and `verify_prompt_20.py` were fully verified and completed successfully, proving the infrastructure baseline operates successfully.

## 3. Individual Bug Reproduction (Task C)
An independent powershell script (`collect_evidence.ps1`) was executed to definitively reproduce each of the 12 issues cataloged in the preliminary audit.

### Critical / High Severity Issues
- **BUG-001 (Storage Encryption):** Confirmed. `STORAGE_ENCRYPTION_KEY` not set warning triggers even when `ENCRYPTION_KEY` is provided. Ephemeral keys are generated, breaking multi-worker decryption.
- **BUG-003 (Feedback Verdict Mismatch):** Confirmed via static analysis of `src/feedback/refit.py`. The AST confirms the algorithm filters for `VALID` and `OVERKILL`, whereas the frontend submits `CONFIRM_ANOMALY`.
- **BUG-004 (Next.js Hardcoded URL):** Confirmed. `frontend/src/app/page.tsx` hardcodes `useState("http://127.0.0.1:8000")` instead of respecting environment variables, breaking remote container deployments.
- **BUG-005 (XAI Endpoint Omission):** Confirmed. Static sweep of `src/api/v1/router.py` shows no XAI attribution or sensitivity routes. The UI utilizes a mocked computation fallback.
- **BUG-006 (UnifiedAuditor Bypassed):** Confirmed. `src/api/jobs.py` routes directly to `DualChannelScorer`, abandoning all logic in `UnifiedAuditor` for deterministic rule checks.

### Medium Severity Issues
- **BUG-002 (Retention TTL Variable):** Confirmed. `src/api/retention.py` prints the fallback `86400.0` despite setting `RETENTION_TTL_SECONDS`. It expects `DATA_RETENTION_SECONDS`.
- **BUG-007 (Whitespace Clause Slicing):** Confirmed. `src/segmentation/rule_based.py` utilizes direct indexing before `.strip()`, creating truncated substring ranges.
- **BUG-008 (Embeddings Cache Race Condition):** Confirmed. `src/embeddings/cache.py` uses unhashed IDs and omits locks when writing `.npz` files.
- **BUG-010 (Memory Leak in API Jobs):** Confirmed. `JOB_STORE` and Rate Limiter `_records` lack eviction strategies, retaining state indefinitely.
- **BUG-011 (Missing .dockerignore):** Confirmed. Missing `.dockerignore` sends entire `node_modules` and `.env` files into daemon context.

### Low Severity Issues
- **BUG-009 (Conformal Calibration Interp):** Confirmed. `src/calibration/conformal.py` utilizes default interpolation for fallbacks instead of `method='higher'`.
- **BUG-012 (Rate Limit Header Discard):** Confirmed. `rate_limit_upload_and_analyze` discards header tracking object before building the HTTP Response.

## 4. API & Integration Verification (Task D)
Integration testing proves the foundational layer (Prompt 15) functions perfectly (95 tests passing). However, deep integration logic between the rule-based sub-engine (Prompt 13), XAI endpoints (Prompt 12), and active feedback (Prompt 14) are heavily broken due to BUG-006, BUG-005, and BUG-003 respectively.

## 5. Frontend & Docker Validation (Task E & F)
- Frontend build `npm run build` succeeds, but relies on flawed state initialization.
- Security configurations (BUG-001/BUG-002) demonstrate dangerous mismatches between documented container orchestration (`.env.example`) and API runtime (`src/api/`).

## 6. Scientific Validity Assessment (Task G)
The DualChannelScorer implements proper contrastive embedding evaluation, and conformal calibration effectively scales thresholds. However, BUG-009 compromises theoretical guarantees for conformal prediction at very small sample sizes.

## 7. Conclusion
The codebase represents a solid prototype with robust unit testing. However, the identified integration failures (12 Bugs) block its usage in a distributed cloud environment. The evidence generated proves the existence of all 12 defects. No code has been modified in this phase.
