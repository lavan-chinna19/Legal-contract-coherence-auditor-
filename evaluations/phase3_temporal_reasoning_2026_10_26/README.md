# Phase 3 temporal reasoning: reproducible exposed development evidence

Started October 26; completed native verification October 28, 2026. Independent adjudication: zero.
No unseen holdout or external legal/security validation is claimed. See `PROTOCOL.md` and the four
`docs/PHASE3_*.md` reports for design, metrics, coverage, failures, limitations and handoff.

## Evidence map

* `preservation_before.json`: pre-change existing-file hashes (includes dirty user work).
* `legacy_snapshot/date_checker.py`: exact pre-change checker, never edited.
* `run_old_baseline.py`, `old_baseline/`: checker executed before new implementation, 38 records.
* `build_dataset.py`, `new_cases.json`, `new_cases.sha256`: 50 new mechanical and eight provisional
  examples with construction-rule provenance. Generator refuses to overwrite inputs.
* `challenge_cases.json`: twelve separately labelled post-implementation mechanical diagnostics.
  `challenge_initial_predictions.json` retains five initial false positives and two misses.
* `initial_inspection.json`, `initial_regression.xml`: initial development outputs, not final scores.
* `run_evaluation.py`: actual frozen-neural parity on all 148 Phase 2 modes, then paired temporal
  inference on 38 original modes and 70 new/challenge/provisional cases. Each run ID must be new.
* `results/paired_v1/`: failed reproduction gate; only unordered legacy involved-ID ordering differed.
* `results/paired_v2/`: successful intermediate run before the MSA negative-control fix.
* **`results/paired_v3/`**: authoritative final source manifest, full predictions, summary,
  every labelled change, 148-way parity and verification. No parser exceptions were suppressed.
* `full_native_v1.*`: actual 391-pass / one-failure / two-skip run that discovered the MSA bug.
* **`full_native_v2.*`**: final 395-pass / zero-failure / two-optional-skip native result.
* `affected_v1.*`: first 144-pass affected suite; `affected_v2.*`: final 117-pass targeted/API suite.
  Suites overlap; never sum them into a total. `integration_v1.log` is an interrupted sandbox HTTP
  run without a completed total, not a pass or a collection of invented failures.
* `msa_diagnostic.json`: raw pre-fix diagnostic console (text followed by JSON), not pure JSON input.
* `frontend_*.log`: actual lint/build/workflow/alignment commands; restricted font fetch failed,
  permitted-network `frontend_build_retry.log` passed. Workflow 20, alignment 17.
* `docker_engine.log`: Docker client present, engine named pipe absent; no container verification.
* `verify_preservation.py`, `final_verification_2026_10_28.json`: post-change preservation, model
  cache/checkpoint, historical input and source-manifest evidence, plus parsed native test totals.
* `execution_log.json`: commands, actual exit codes, failures and outcomes. `runtime/` is ignored;
  derived embeddings and SQLite files there are disposable evaluation state, not research evidence.

The old/new original-case task is a chronology candidate screen, retaining the original labels.
New mechanical tasks test explicit constructed conflicts; old flags against these labels are only
an alert proxy. Eight provisional interpretation cases have null gold and no confusion classification.
Metrics count TXT documents once; PDF/DOCX and authored modes are reproducibility probes, not
additional independent ground truth. Exact source/date spans and every decision are retained.

## Commands (PowerShell, repository root)

```powershell
$env:HF_HUB_OFFLINE='1'
$env:TRANSFORMERS_OFFLINE='1'
$env:LEXAUDIT_ALLOW_MODEL_DOWNLOAD='0'
$env:OMP_NUM_THREADS='2'
$env:MKL_NUM_THREADS='2'
tmp/final-release/clean-env/Scripts/python.exe -m pytest tests -q
tmp/final-release/clean-env/Scripts/python.exe evaluations/phase3_temporal_reasoning_2026_10_26/run_evaluation.py --run-id your_new_run_id
cd frontend
npm run lint
npm run build
npm run test:workflow
npm run test:alignment
```

The test suite isolates user storage and removes inherited external database settings. Local
FastAPI TestClient communication must be permitted. Existing Next font configuration needs
Google Fonts access to build; model loading stays offline. For native launch/configuration use
`docs/INSTALL_AND_RUN.md` and the Phase 3 implementation report. Existing user services were not
interrupted. No commit, push, deployment, reset, prune, retraining or historical-result rewrite.
