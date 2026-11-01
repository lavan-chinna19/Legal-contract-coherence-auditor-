# Phase 3 implementation report — 2026-10-28

Native Phase 3 implementation and verification are complete within the bounded supported grammar.
The system now preserves source-backed temporal roles, actors/actions/triggers, agreement/phase/
section/party context, dates/durations/bases/operators, conditions, exact spans and explicit
uncertainty. It distinguishes supported deterministic conflicts, potential differences, reviews,
consistent checks and unsupported syntax. Ambiguous relationships are not invented.

This is **native application integration with exposed development evidence**, not independently
validated legal production readiness. Docker runtime verification is BLOCKED by the unavailable
host engine. No UI redesign, neural retraining, threshold change, Git commit/push or deployment
was performed. Existing uncommitted frontend work was preserved and checked for compatibility.

## Delivered source and integration

* New `src/temporal/{extraction,analysis}.py` and package export implement bounded extraction,
  scoped relation checking and evidence-preserving abstention.
* `src/rules/date_checker.py` retains its public two-value compatibility facade and adds richer
  analysis. The exact old checker and its before-change predictions are preserved separately.
* `src/rules/unified_pipeline.py` reuses the Phase 2 structural document for temporal analysis
  while retaining the original neural clause inventory and thresholds.
* `src/api/jobs.py` persists additive temporal metadata and uses uncertainty to require review.
* `src/api/reports.py` includes temporal categories, source evidence and interpretation in the
  common PDF/DOCX pipeline; review priority is explicitly separate from legal certainty.
* `tests/test_temporal_reasoning.py` and `tests/test_temporal_integration.py` cover arithmetic,
  binding, source spans, negatives, uncertainty, limits and actual authenticated document flows.
  The NO_FINDINGS specimen in `tests/test_final_release.py` is now explicitly unambiguous;
  the old MSA retains separate zero-alert/review-state coverage. No test was suppressed.

Earlier paused work already contained some integration changes; the current checkout's Git diff
alone is therefore not a complete Phase 3 file inventory. The pre-change preservation manifest
and final evaluation manifests identify the actual files. The repository already contained a
Phase 2 commit when work resumed; that existing history was not reset or rewritten.

## Actual verification results

| Check | Result | Retained evidence |
| --- | --- | --- |
| Final full native suite | **395 passed, 0 failed, 2 skipped**, exit 0; 63.09 s; nine warnings | `full_native_v2.xml`, `full_native_v2.log` |
| Final affected real-model/API suite | 117 passed, 0 failed, exit 0; 18.71 s | `affected_v2.xml`, `affected_v2.log` |
| Initial affected suite | 144 passed, exit 0 | `affected_v1.xml`, `affected_v1.log` |
| First full native suite | 391 passed, **1 failed**, 2 skipped; exit 1 | `full_native_v1.xml`, `full_native_v1.log` |
| Original legacy baseline reproduction | 38/38 observations reproduce | `results/paired_v3/verification.json` |
| Frozen neural clause-result parity | 148/148 | `results/paired_v3/parity.json` |
| Structure / references / dependency-graph parity | 148/148 for each | same parity JSON |
| Exact temporal source/date spans | Verified on all 108 paired observations; zero parser exceptions | paired predictions and verification JSON |
| Frontend lint | exit 0 | `frontend_lint.log` |
| Frontend production build / TypeScript | exit 0 on permitted-network retry | `frontend_build_retry.log` |
| Frontend workflow / alignment | 20 passed / 17 passed, both exit 0 | frontend test logs |
| Docker engine | exit 1; Server=null; `dockerDesktopLinuxEngine` pipe absent | `docker_engine.log` |

Counts from overlapping test runs are not added together. The two skips are the optional live
CUAD order-report existence/verdict tests; historical reports were not regenerated to erase them.
Warnings are retained: Starlette/httpx and tokenizer deprecations, plus deliberately small
conformal calibration fixtures. No warning is turned into evidence of legal accuracy.

TXT, PDF and DOCX real-format workflow tests perform actual upload parsing, actual offline model
analysis, source/section checks, owner authentication and other-owner rejection, saved encrypted
history restoration after clearing the job's memory entry, and both exports. Exports are parsed
back to check conflict categories, relation, source hash and deadline evidence. This is local HTTP
TestClient integration, not a new browser UX audit, OS-process restart test or penetration test.
The unsupported-deadline and original MSA workflows prove review state survives persistence.

## Retained failures and corrections

The first paired run failed only its legacy reproduction gate because the old checker serializes
an unordered involved-ID set. `paired_v1` remains intact; the runner now sorts only that field for
comparison. `paired_v2` passed before the final MSA fix; **paired_v3 is authoritative** and freezes
the final source before prediction. No historical output is overwritten.

The first full suite exposed a real false confirmation from modal term-endpoint/actor binding.
The generic binding fix, direct negative tests and separate original-MSA API regression correct it.
The final full suite passes. Details and exact examples are in `PHASE3_FALSE_POSITIVE_ANALYSIS.md`.

The first restricted HTTP integration attempt stalled and was interrupted; it has no completed
test total and is not counted as passed. The full reruns used permitted localhost communication
and isolated temporary storage. The first frontend build failed fetching its already-configured
Google Fonts in restricted networking; a permitted-network retry passed without frontend edits.
No new model downloads or external inference service were used.

## Evaluation and meaning of the result

Original exposed chronology-screen metrics improve from P/R/F1 75% and FPR 33.33% to P/R/F1 100%
and FPR 0% on **14** mechanically labelled TXT documents. Two false alarms and two misses are
corrected; no labelled final regression remains. This task includes arithmetic candidate warnings,
not only confirmed conflicts. All original labels/provenance remain unchanged.

The new 50-case mechanical confirmation screen has 13 TP / 0 FP / 0 FN / 37 TN; twelve separate
post-implementation challenges have 2 TP / 0 FP / 0 FN / 10 TN. Eight provisional examples have
no accuracy label. The baseline old alert proxy and full coverage/abstention denominators are in
`PHASE3_BEFORE_AFTER_EVALUATION.md`. Only 22/50 new mechanical documents receive a supported
relational decision; 21/50 retain review/unsupported evidence. Perfect synthetic screens are
not a generalization or legal-accuracy estimate. Candidate alerts actually increase from nine
to 17 on those new cases because four compatible-deadline differences are surfaced as potential.

## Reproduce and run

From the repository root in PowerShell, use the existing clean environment:

```powershell
$env:HF_HUB_OFFLINE='1'
$env:TRANSFORMERS_OFFLINE='1'
$env:LEXAUDIT_ALLOW_MODEL_DOWNLOAD='0'
$env:OMP_NUM_THREADS='2'
$env:MKL_NUM_THREADS='2'
tmp/final-release/clean-env/Scripts/python.exe -m pytest tests -q
tmp/final-release/clean-env/Scripts/python.exe evaluations/phase3_temporal_reasoning_2026_10_26/run_evaluation.py --run-id your_new_run_id
```

Every run ID must be new; the runner refuses to overwrite evidence. Its runtime caches/SQLite
files stay in an ignored evaluation runtime directory, separate from user data. The original
`run_old_baseline.py` is retained for provenance and refuses to overwrite its before-change output.

Use the project's existing installation/authentication configuration, then launch native services:

```powershell
tmp/final-release/clean-env/Scripts/python.exe scripts/run_server.py --port 8012
# In another terminal:
cd frontend
$env:NEXT_PUBLIC_API_URL='http://127.0.0.1:8012'
npm run dev -- --port 3002
```

These are launch instructions, not a claim this phase restarted any existing user service.
Restart an already-running backend normally to load new code. Frontend lint/build and the workflow/
alignment scripts are reproducible with their existing npm commands. Model assets remain local.

## Readiness and Phase 4 recommendation

Native temporal decision support is ready for a supervised demonstration with its limitations
visible. Docker verification requires the user to start/recover Docker Desktop safely and retest;
no reset, prune, WSL deletion or volume mutation occurred. Independent legal annotation, unseen
document-family evaluation and external security validation remain external blockers.

Phase 4 should first establish expert-labelled actor/action/event-instance and conditional-scope
examples with hard negatives and an untouched evaluation split. Improve evidence-backed binding
and retrieval before broadening to distant-clause contradiction candidates. A limited experimental
graph with abstention is defensible; general legal contradiction accuracy, production scientific
validation or large-model retraining is not supported by the current evidence.
