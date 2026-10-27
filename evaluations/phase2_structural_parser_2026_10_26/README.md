# Phase 2 source-preserving structural parser — 2026-10-26

**Native scope verified; Docker NOT VERIFIED. Exposed development comparison, no legal accuracy claim.**

Read `PROTOCOL.md`, `INTERFACES_BEFORE.md` and the five `../../docs/PHASE2_*.md` deliverables.
The Phase 1 corpus/predictions remain unchanged. Old modules were copied BEFORE implementation
and re-executed against the same actual frozen local models; no mock, retraining or recalibration.

## Authoritative final evidence

`results/paired_v4/` is the final evaluated source revision. Both old and new implementations ran
148 analyses over the same 70 documents (authored/TXT and eight format probes). Old predictions
reproduced Phase 1 148/148; old/new neural outputs, date-rule flags, exact structural source and
offset checks matched 148/148. Final pre-prediction source manifest still matches current source.

Main TXT metrics, document-level only:

| Task | Old P/R/F1 | New P/R/F1 | Old → new TP/FP/FN/TN |
| --- | --- | --- | --- |
| Missing target, n=28 | .75/.3333/.4615 | 1/1/1 | 3/1/6/18 → 9/0/0/19 |
| Numeric direction, n=15 | 1/.6667/.8 | 1/1/1 | 4/0/2/9 → 6/0/0/9 |

All original 13 canonical directional examples remain correct. No newly introduced errors in those
labelled subsets. These 100% development values are **not** overall contract accuracy. The corpus
has 59 mechanical/11 provisional cases and zero independent adjudications; it is already exposed.

## Files

* `legacy_snapshot/`: exact pre-change reference checker, graph, unified pipeline, segmenter and
  ingestion modules, verified against pre-change hashes.
* `run_paired.py`: executes both implementations, actual parsers/models, and parity gates; requires
  a NEW run directory. Refuses altered frozen neural/input/Phase 1 files. Source hashes are captured
  before predictions and checked afterward. No production algorithm branches on case IDs/labels.
* `results/paired_v4/paired_predictions.jsonl`: full old/new prediction, source and parity evidence.
* `results/paired_v4/case_comparison.json` and `.csv`: all cases/modes, original/new predictions,
  label/provenance, changes/reasons, corrected/regressed tasks and source evidence. Provisional
  legal correctness remains NOT_ASSESSED, never an invented TN.
* `comparison.json`, old/new decisions and summary JSON/CSV under that run: defined task metrics,
  including unchanged date and neural order proxies, with original denominators/strata.
* `coverage.json`: resolver states and explicit review counts; unsupported silence is not a success.
* `parity.json`, `verification.json`, `source_manifest_before_predictions.json`: numerical/input/
  source evidence and exact evaluated source identity.
* `summarize_phase2.py`: generates derived comparisons and preservation/test summaries; no scoring.
* `preservation_before.json`, `results/preservation_verification.json`: allowed source/tracker
  changes distinguished from 1,104 unchanged existing files; Phase 1, model/frontend/research hashes,
  local encoder fingerprint, 51 raw research inputs and Git HEAD verified. Existing parity test
  modification is separately documented because tests were outside the initial hash-root selection.
* `full_native_verified.xml` / console: **298 passed, 0 failed, 2 optional CUAD-report skips**.
  This includes 49 structural grammar tests and four new real format/review HTTP integration tests.
* Frontend logs: lint/build exit 0, 20 workflow tests, 17 alignment checks. Source unchanged.
* `docker_engine_check.log`: exit 1; desktop-linux server absent, named engine pipe not found.
* `execution_log.json`: actual command/exit history, retained unsuccessful attempts and fixes.
* `runtime/` is ignored scratch embeddings/storage, not a dataset to publish.

## Reproduction (PowerShell, repository root)

Use the already-installed clean CPU environment and existing local encoder cache:

```powershell
$python = '.\tmp\final-release\clean-env\Scripts\python.exe'
$phase2 = '.\evaluations\phase2_structural_parser_2026_10_26'
& $python "$phase2\run_paired.py" --run-id reproduction_01
# Derives/validates the authoritative final run without changing frozen Phase 1 outputs:
& $python "$phase2\summarize_phase2.py"
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = '1'
$env:HF_HUB_OFFLINE = '1'
$env:TRANSFORMERS_OFFLINE = '1'
$env:LEXAUDIT_ALLOW_MODEL_DOWNLOAD = '0'
$env:OMP_NUM_THREADS = '2'
& $python -m pytest tests -q
```

TestClient needs permitted local socket communication. Test storage is isolated by existing
`tests/conftest.py`. Model downloads are disabled in the evaluator. Future changed algorithms must
use a new named comparison rather than overwrite these outputs or Phase 1's source manifest.
The original Phase 1 evaluator rightly refuses changed source in the live checkout; this Phase 2
runner reproduces old behavior with its saved exact modules and unchanged shared model components.

Frontend verification from `frontend/`: `npm run lint`, `npm run build`, `npm run test:workflow`,
`npm run test:alignment`. Build includes TypeScript checks. No installation, UI editing or deployment.
Docker runtime must be independently retested after the host engine is available; no reset/prune/
volume/WSL action was taken here.

## Retained unsuccessful attempts

Initial grammar XML retains two failures (parenthesized-direction bug and ambiguous bare-marker
specimen). Paired_v1 retains a loader failure before predictions. Paired_v2 retains a failed tuple/
JSON-array comparison gate with successful numeric outputs, fixed without dropping evidence.
Paired_v3 retains the first successful full parity run and four unnecessary title-noun review notices;
paired_v4 corrects those through a general grammar rule/test. Initial full regression XMLs retain
the raw-source omission and CRLF input-parity failures. Final assertions were strengthened, not removed.

No Git writes, publication, deployment, deletion of research, modification of frozen neural assets
or temporal-logic change occurred. Phase 3 may proceed on the verified native source/evidence layer;
independent annotation and unseen-family/legal/security validation remain outstanding.
