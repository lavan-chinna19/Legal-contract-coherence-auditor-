# Phase 2 — structural parser implementation report

2026-10-26. **Native implementation/evaluation verified. Docker integration NOT VERIFIED.**
No UI redesign, model retraining, recalibration, date-logic modification, commit, push or deployment.

## Completed scope

| Component | Status | Actual verification |
| --- | --- | --- |
| Record old interfaces/consumers/schemas | COMPLETE | Pre-change inventory, hashes and five exact legacy modules |
| Source-preserving structure and hierarchy | COMPLETE | Exact text/offset/unit, nested/parent/duplicate, Unicode/CRLF and bounded-parser tests |
| Reference resolver and abstention states | COMPLETE | Singular/plural/ranges, nested identity, sentence-start/punctuation/preposed direction, ambiguity/unsupported tests |
| Reference checker / graph integration | COMPLETE | Shared structural parser, existing flag/response compatibility, 13 canonical controls retained |
| Frozen neural and date behavior | COMPLETE | 148/148 identical neural clause outputs and date-rule flags; source/model hashes unchanged |
| Paired exposed development evaluation | COMPLETE | Old and new 148 analyses each; exact old predictions reproduce Phase 1; all-case comparison/coverage retained |
| Real TXT/PDF/DOCX preview/analysis/evidence | COMPLETE | Authenticated HTTP integration with actual local models and source assertions |
| Reports and saved reopening | COMPLETE | Real PDF/DOCX render/parse assertions, encrypted snapshot reopen and saved graph evidence |
| Security/ownership/native full regression | COMPLETE | 298 passed / 0 failed / 2 documented optional skips |
| Frontend compatibility | COMPLETE | Lint, production build/TypeScript, 20 workflow and 17 alignment checks; source unchanged |
| Five design/spec/results/error/report documents | COMPLETE | Required files created; evaluation scripts/results in separate Phase 2 directory |
| Docker runtime integration | NOT VERIFIED | docker version exit 1; host desktop-linux engine pipe absent; no reset or volume operation |
| Independent legal / unseen-family / external security validation | EXTERNAL / unavailable | Not performed, not implied by application tests |

This is a scoped engineering completion statement, not 100% real-world legal accuracy. Docker is
outside the verified runtime boundary for this revision; prior historical Docker success is not reused.

## Implementation inventory

New production package: `src/structure/__init__.py`, `parser.py`, `resolver.py`.

Existing production integrations changed: `src/rules/reference_checker.py`, `dependency_graph.py`,
`unified_pipeline.py`, `src/api/jobs.py`, `release_routes.py`, `reports.py`. The legacy reference
helper and two-value interface remain compatible; source-aware APIs add optional fields/arguments.
New structures preserve exact extracted source while the old neural/date input path remains frozen.
No dependency installation or large model work was necessary.

Tests added: `tests/test_structural_parser.py` (49 final grammar/source/resource cases) and
`tests/test_structural_integration.py` (four real API cases, three formats plus review-state behavior).
Existing `tests/test_api_integration.py` retains all its parity expectations and now supplies the
same upload-decoded original source, with three additional source/inventory assertions. Earlier
failures from omitted source/CRLF conversion and their fixes are documented, not suppressed.

New evaluation: `evaluations/phase2_structural_parser_2026_10_26/`, including protocol, legacy
snapshots, original preservation hashes, reproducible paired runner, comparison/coverage/source
evidence, test XML/console logs, failures and final verification. The Phase 1 directory was never
rewritten; its manifest correctly describes the old source and is not regenerated for new code.

## Final measured result

| TXT task | Old precision / recall / F1 | New precision / recall / F1 | Final confusion |
| --- | --- | --- | --- |
| Missing target, n=28 | 75% / 33.33% / 46.15% | 100% / 100% / 100% | 9 TP, 0 FP, 0 FN, 19 TN |
| Directional graph, n=15 | 100% / 66.67% / 80% | 100% / 100% / 100% | 6 TP, 0 FP, 0 FN, 9 TN |

Six reference misses, one reference false alarm and two directional misses were corrected in
unique TXT cases; no new labelled errors were introduced. R16's extraneous heading flag also
disappeared without being double-counted as a new document TP. These values apply only to the
small exposed development subsets, not overall legal correctness. All 70 documents retain their
original mechanical/provisional labels; there are zero independently adjudicated examples.

Final paired_v4 verification: 148/148 legacy predictions reproduced; 148/148 old/new neural outputs
identical; 148/148 date outputs identical; 148/148 exact source and structural-offset checks pass.
The final run checked 156 frozen input/scoring/research files before evaluation and verified its
source manifest after predictions. It recorded 19 corrected decisions across repeated input modes,
not 19 independent legal defects. Main table denominators are never inflated with format repetitions.

Reference reviews retain duplicate/uncertain/unsupported cases; the graph reviews all 12 predefined
TXT review-policy cases. Native absence/direction improvements do not solve the old date-scope,
role-window, numeric-locale, invalid-date or neural reasoning limitations.

## Final tests and runtime evidence

* Full native: **298 passed, 0 failed, 2 skipped**, exit 0, 131.15 seconds, 9 retained warnings.
  `full_native_verified.xml` and `full_native_verified_console.log` are authoritative. Skips:
  `test_live_cuad_order_report_exists` and `test_live_cuad_report_has_verdict`, because the optional
  CUAD order report is absent. Historical research was not regenerated to remove those skips.
* Earlier affected integration run: 79 passed, exit 0, 30.74 seconds. This overlaps full native;
  do not add it to the final native count. Initial partial grammar/full native failures remain saved.
* Frontend: `npm run lint` exit 0; `npm run build` exit 0, including TypeScript/static generation;
  `npm run test:workflow` 20 passed; `npm run test:alignment` 17 passed. No frontend source was edited.
* Real format workflows tested uploads, exact extraction preview, nested extraction/resolution,
  source-backed missing/directional evidence, actual model analysis, PDF/DOCX exports, saved
  reopening, unauthenticated denials and other-owner denials. This is real local HTTP TestClient
  integration, not a new browser usability audit or external security penetration test.
* Docker: `docker version --format '{{json .}}'`, exit 1, client 29.6.1, Server=null.
  `dockerDesktopLinuxEngine` named pipe was not found. Log: `docker_engine_check.log`.
  No container build/run or runtime claim for this revision; no factory reset, WSL/volume deletion,
  prune or other recovery was attempted.

Tests used the existing clean CPU Python environment, offline model loading and isolated temporary
uploads/feedback/threshold storage. TestClient execution used permitted local communication; no
external model service, external database or production credentials were needed.

## Preservation and handoff

`results/preservation_verification.json` verifies existing frontend work, all Phase 1 evidence,
snapshotted historical research/results and model assets against the pre-change snapshot; raw
research inputs are additionally checked against the Phase 1 snapshot. The six intended
production integration files and appended completion-tracker entry are explicitly allowed changes.
Legacy snapshots match their pre-change hashes. The local Legal-BERT cache files also match the
Phase 1 fingerprint. Git HEAD and historical attribution remain unchanged.

The existing application tracker receives an additive Phase 2 note, not a replacement of historical
results or a new Docker award. Full commands, artifacts and execution failures are recorded in the
evaluation README and execution log. Restart the native backend normally to load new source into
any previously running process; this task did not interrupt existing user services.

**Phase 3 may proceed with scope-aware temporal reasoning on the verified native path.** Keep its
baseline separate and continue explicit abstention/provenance practices. Docker revalidation and
independent legal/unseen-family/security validation remain outstanding and must not be represented
as solved by development metrics.
