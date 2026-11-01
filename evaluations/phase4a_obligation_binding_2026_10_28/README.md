# Phase 4A obligation/event binding — retained evidence

All labels are author-constructed mechanical labels or explicitly provisional interpretations.
Independent expert annotation: zero. The source and inputs were frozen before the first reserved
evaluation; production code was not tuned afterward. No legal accuracy or natural-family holdout
claim is made. See the four `docs/PHASE4A_*.md` reports for the actual scope, limits and NO-GO decision.

## Artifact map

* `preservation_before.json`: hashes of 1,345 existing source/frontend/research/evaluation files and Git HEAD.
* `audit_phase3.py`, `phase3_audit_verified.json`: recomputed matrices/metrics and additive Phase 3
  report errata (40% review union, 96/118 statements). `phase3_audit.json` is an intermediate check
  that repeated the stale interpretation and is explicitly superseded, not deleted.
* `PROTOCOL.md`: pre-implementation task/state/field/metric definitions and preservation rules.
* `build_benchmark.py`, `development.json`, `evaluation.json`, `benchmark_frozen_manifest.json`:
  input generation, labels, construction provenance and hashes before binding code.
* `benchmark_draft/`: original draft before literal unsupported-field correction, retained before
  implementation. Do not regenerate frozen inputs; hashes identify the exact final benchmark.
* `development_v1.xml/.log`: initial 39-pass unit suite. `integration_v1.xml/.log`: initial collection
  error from a local test import, retained; `integration_v2.xml/.log`: 44-pass corrected affected suite.
* `implementation_frozen.json`: exact production/tests/evaluator/protocol hashes before reserved exposure.
* `evaluation_exposure.json`: the single first reserved evaluation run, never an unseen rerun.
* `results/development_v1/`: original development predictions, fields, metrics, errors and ablation.
* **`results/evaluation_first_pass/`**: unchanged first reserved predictions with source evidence,
  summary, field errors and guard-ablation changes. One passive positive is FN; joint actor is wrong.
* `analyze_errors.py`, `post_evaluation_error_audit.json`: post-exposure errors and two invalid
  occurrence/type label cells per split. Posthoc sensitivity is separate; initial labels/scores stay intact.
* `full_native_v1.xml/.log`: **440 passed, 0 failed, 2 optional skips**, exit 0, 269.66 s, nine warnings.
* `verify_existing_outputs.py`, `preserved_output_verification.json`: 148 neural/structural/reference/
  graph matches; 148 direct unchanged date checks and 38 exact historical Phase 3 date matches.
* `public_smoke.py`, `public_source_smoke.json`, `public_substantive_smoke.json`: six existing SEC
  exhibits, raw and declared normalized extraction views; no legal labels. The substantive normalized
  probes yield eight partial modal records and eleven unsupported pairs. Logs omit contract content;
  source-backed public excerpts stay in the saved observation evidence only.
* `frontend_*.log`, `frontend_results.json`: lint/build, 20 workflow and 17 alignment passes.
* `docker_engine.log`: client available, engine named pipe missing; runtime BLOCKED.
* `reproduce_frozen.py`: deterministic exposed reproduction, never a second untouched score.
* `final_verification.json`: preservation, final source/input freeze, parsed test counts and metrics audit.
* `execution_log.json`: actual commands/exits/failures. Runtime embeddings/SQLite caches are ignored.

## Reproduce in PowerShell from the repository root

```powershell
$env:HF_HUB_OFFLINE='1'
$env:TRANSFORMERS_OFFLINE='1'
$env:LEXAUDIT_ALLOW_MODEL_DOWNLOAD='0'
$env:OMP_NUM_THREADS='2'
$env:MKL_NUM_THREADS='2'
tmp/final-release/clean-env/Scripts/python.exe -m pytest tests -q
tmp/final-release/clean-env/Scripts/python.exe evaluations/phase4a_obligation_binding_2026_10_28/reproduce_frozen.py --run-id your_new_reproduction_id
```

Each run ID must be new. The initial `evaluate.py --split evaluation` intentionally refuses a
second initial exposure. Use `reproduce_frozen.py` to repeat the frozen predictions as exposed
reproduction; it verifies source/input hashes and does not alter reserved metrics. Development
evaluation can use `evaluate.py --split development --run-id <new-id>` without touching reserved
data. Never rerun the benchmark builder over these preserved inputs. New tuning requires a new
protocol, fresh evaluation and clear development exposure accounting.

Tests isolate private user storage and use local actual models. Local HTTP communication must be
permitted. Existing frontend build needs its configured font access; no frontend edits were made.
The new endpoint and native launch/configuration are in the implementation report. No running user
service was interrupted; no commit/push/deployment/reset/prune/model edit occurred.
