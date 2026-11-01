# Phase 4A implementation report — 2026-10-28

The native opt-in experimental obligation-binding component is implemented and tested within a
small explicit grammar. It returns MATCHED / DIFFERENT / UNCERTAIN / UNSUPPORTED with structured
fields, exact source/section evidence and reasons. Matching establishes potential comparability,
not conflicting deadlines or legal equivalence. There is no frontend redesign or new model.

## Delivered files and API

* New `src/obligations/{__init__,binding}.py`: bounded CPU extraction and conservative matching.
* `src/api/release_routes.py`: authenticated explicit opt-in route
  `POST /v1/experimental/obligation-bindings`, body `{ "job_id": "...", "experimental": true }`.
  It requires an existing owned completed analysis with original extracted source and inventory.
* `src/api/reports.py`: optional separately labelled binding section in PDF/DOCX after opt-in.
* New tests: `tests/test_obligation_binding.py` and `tests/test_obligation_integration.py`.
* Four required `docs/PHASE4A_*.md` reports and new reproducible Phase 4A evaluation directory.

Results persist separately as `metadata.obligation_binding`. No existing scorer, neural input,
reference/graph/date flag, total severity, analysis state or Phase 3 temporal metadata is changed.
Legacy saved records without original evidence return 409 rather than guessing source coordinates.
Strict false opt-in returns 400, string boolean returns 422, unauthenticated requests 401 and
other-owner requests 404. Oversized source returns 413 without saving a partial result.

## Audit, benchmark and scientific integrity

The Phase 3 confusion matrices reproduce. Its final raw review/unsupported rate is **40%**, not
the stale 42% previously reported; supported statement count is 96/118. An additive erratum was
reported before implementation. Historical reports and results remain unchanged.

Before binding code, the protocol and final benchmark hashes were frozen: 28 development and
30 reserved evaluation documents. A benchmark draft literal-field correction is retained in
`benchmark_draft/`. Production/test source was then frozen after native/development verification,
and the reserved split was evaluated once. No algorithm/source/label edits followed exposure.
Surface-document templates are separated, while ontology, authoring rules and some diagnostic
phrases are shared; this is not independent real-world family validation or expert annotation.

Post-exposure inspection found invalid type-vs-occurrence field gold for two recurring-case cells
per split. It is explicitly flagged without rewriting first-pass labels/scores. Sensitivity figures
are separate, labelled posthoc and do not replace the reserved results. The passive FN, joint-actor
field error and other extraction misses remain recorded. The standalone error audit is reproducible.

## Actual tests and verification

| Check | Result | Evidence relative to Phase 4A evaluation directory |
| --- | --- | --- |
| Initial development/unit tests | 39 passed, exit 0 | `development_v1.xml`, `.log` |
| Initial integration collection | exit 2; one import error | `integration_v1.xml`, `.log`; corrected local test import |
| Affected actual-model integration | 44 passed, exit 0; 54.76 s | `integration_v2.xml`, `.log` |
| **Final full native suite** | **440 passed, 0 failed, 2 skipped**, exit 0; 269.66 s; nine warnings | `full_native_v1.xml`, `.log` |
| Actual frozen neural results | 148/148 match | `preserved_output_verification.json` |
| Structure/reference/graph | 148/148 match each | same parity evidence |
| Temporal integration | 148/148 match direct unchanged checker; 38/38 match saved Phase 3 outputs | same evidence; method explicitly recorded |
| Frontend lint / production build | both exit 0 | `frontend_lint.log`, `frontend_build.log` |
| Frontend workflow / alignment | 20 passed / 17 passed, exit 0 | frontend test logs |
| Public-source probes | six exhibits × raw/normalized = 12 observations; exact spans pass; no labels | two public smoke JSON/log files |
| Docker | client present, Server=null, engine pipe absent; exit 1 | `docker_engine.log`; **BLOCKED** |

Affected tests overlap the full suite and are not summed. The two skips remain optional live CUAD
order-report existence/verdict tests. Starlette/httpx, tokenizer deprecations and small conformal
fixture warnings remain visible. No test or existing assertion was suppressed. A new test import
was fixed before the reserved evaluation; the failed collection is retained.

Native integration uses actual offline models and FastAPI TestClient. TXT, PDF and DOCX are actually
encoded/uploaded/parsed, analyzed, opted into binding, compared exactly to the pre-opt-in core
result, restored after clearing the memory job and exported. PDF/DOCX are parsed back to verify
experimental identity evidence and source hash. Missing/ambiguous data and bounded long inputs
are tested. This is local integration, not a browser audit, container run, full process-restart
test, external penetration test or independent legal validation.

## Measured result and remaining limitations

Development binary matching: 7 TP / 0 FP / 0 FN / 7 TN (n=14); reserved: **7 TP / 0 FP / 1 FN /
8 TN (n=16)**. Reserved precision 100%, recall 87.5%, F1 93.33%, FPR 0%, FNR 12.5%, with
**15/30 (50%) coverage and 15/30 abstention**. The two unknown/provisional strata are not invented
binary negatives. Full state and field denominators are in the evaluation report.

The unsupported passive positive is a genuine FN. The joint subject is represented incorrectly
despite its correct DIFFERENT pair state. Generic objects, recurrence instances, wider actions,
complex conditions, aliases and public legal wording remain outside reliable coverage. The
public substantive views yield eight partial records and eleven unsupported pairs, not evidence
of practical matching success. No legal accuracy percentage is established.

## Reproduce / use

From the repository root with the existing clean CPU environment:

```powershell
$env:HF_HUB_OFFLINE='1'
$env:TRANSFORMERS_OFFLINE='1'
$env:LEXAUDIT_ALLOW_MODEL_DOWNLOAD='0'
$env:OMP_NUM_THREADS='2'
$env:MKL_NUM_THREADS='2'
tmp/final-release/clean-env/Scripts/python.exe -m pytest tests -q
```

The existing backend launcher/configuration remains unchanged:

```powershell
tmp/final-release/clean-env/Scripts/python.exe scripts/run_server.py --port 8012
```

Configure local authentication/encryption as described in `INSTALL_AND_RUN.md`. Analyze a document
through the existing workflow, then submit the experimental POST with its job ID and the same
owner key. Keys must stay in local configuration or environment, never committed or placed in
public frontend variables. The new endpoint is available without any frontend redesign.

Evaluation reproduction instructions and artifact map are in the new evaluation README. Each
run directory is append-only. The reserved exposure file prevents pretending that another tuned
run is still untouched. Offline model paths, user storage and original research assets are preserved.
No existing user service was restarted or interrupted by this phase.

## Final recommendation

**NO-GO for Phase 4B automatic distant-clause contradiction detection.** The experimental explicit
matcher is useful for controlled research, but partial coverage, known actor/passive failures,
occurrence-label ambiguity, unsupported public pairs and absent expert/legal evaluation prevent
that expansion from being justified. Repair and annotate binding on exposed development cases,
then freeze a fresh evaluation protocol before reassessing. Human-review retrieval research can
remain an explicitly separate experiment; no additional large model is justified here.

Docker runtime, independent legal annotation, natural unseen-family evaluation and external
security validation remain blockers. No commit, push, deployment, historical rewrite or frozen
asset change was performed.

Final `final_verification.json` checks the 1,345-file pre-change snapshot: only the two intended
API/report integration files and the appended completion tracker changed among existing files.
There are no missing or unexpected changed files; model/cache, frozen source/benchmark and Git
HEAD checks pass. Exposed reproduction repeats all 58 archived document predictions identically,
without creating new independent examples or replacing the initial reserved score.
