# Final Staging Commands — Prompt 24A

**Author:** Principal Release Engineer  
**Audit Phase:** Prompt 24A (Final Release Corrections & Verification)  
**Date:** October 10, 2026  

---

## 1. Explicit Staging Commands (Awaiting Human Approval)

The following explicit-path commands are proposed for staging the release assets.
In accordance with strict security hygiene, no bulk shortcuts (`git add .` or `git add -A`) are used, and all sensitive or non-portable files are excluded.

```powershell
# 1. Stage verified source code modifications
git add -- README.md
git add -- frontend/src/app/layout.tsx
git add -- frontend/src/app/page.tsx

# 2. Stage independent browser reproduction test suite
git add -- scripts/reproduce_browser_evidence.py

# 3. Stage verified audit evidence packages
git add -- audit/prompt_23/
git add -- audit/prompt_23a/
git add -- audit/prompt_23b/
git add -- audit/prompt_24/
git add -- audit/prompt_24a/
```

---

## 2. Proposed Commit Message

```text
chore(release): finalize research prototype demonstration, verified evidence and release packaging
```

---

## 3. Explicitly Excluded Files & Directories

The following files will **NOT** be staged:
1. `data/` — Contains runtime operational SQLite databases (`feedback.sqlite`, `jobs.sqlite`) and encrypted document blobs (`data/uploads/`).
2. `.env` — Contains local environment secret configurations.
3. `scripts/run_server.py` — Excluded due to hardcoded test encryption key and admin secret.
4. `scripts/run_prompt23a_browser_acceptance.py` — Excluded due to obsolete synthesized DOM selectors.
5. `scripts/diagnose_runtime_dom.py` — Ephemeral selector diagnostic tool superseded by `reproduce_browser_evidence.py`.
6. `scripts/run_prompt23_acceptance.py` — Historical HTTP test runner superseded by pytest suite.
7. `scripts/test_cdp.py` — Scratch CDP connectivity probe.
8. `frontend/AGENTS.md` — Machine-generated Next.js dev server file.
9. `fixtures/load_test_results.json` — Pre-existing unstaged test artifact preserved in working tree.
