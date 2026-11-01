# Phase 1 frozen detection baseline — 2026-10-26

**Complete evaluation phase; no detection changes. Exposed development diagnostic, not legal validation.**

70 unique cases: 59 mechanically labelled synthetic, 11 provisional human-review, zero independently
adjudicated. Corpus constructed after source audit; reused MSA/SLA fixtures remain exposed development
evidence. Read [PROTOCOL.md](PROTOCOL.md) before interpreting any number.

| Deliverable | State | Evidence |
| --- | --- | --- |
| Audit actual frozen detection pipeline | COMPLETE | `../../docs/DETECTION_CAPABILITY_MATRIX.md`, runtime metadata and source manifest |
| Separate, provenance-labelled development corpus | COMPLETE | `corpus.json`, 70 `cases/*.txt`, byte-identical regeneration |
| Run per-task baseline without tuning | COMPLETE | Two 148-analysis runs, per-clause and per-case evidence |
| Analyze misses, false alarms, parsing and abstention | COMPLETE | `../../docs/ERROR_ANALYSIS_AND_IMPROVEMENT_PLAN.md`, `results/evidence_index.json` |
| Document findings and verify preservation/regressions | COMPLETE | Three new docs, XML test reports, 1,040 existing files unchanged |
| Independent qualified legal adjudication | BLOCKED / external | No independent annotators or expert labels in session |
| Unseen-family scientific evaluation | BLOCKED / external | Must acquire and freeze new sources/labels before exposure |

This checklist tracks evaluation deliverables, not improved detection performance. The existing
application-completion tracker was preserved and does not become an accuracy score.

## Outputs

* `build_dataset.py`: deterministic, no detector imports, refuses to overwrite existing corpus.
* `corpus.json`, `cases/`: facts, task labels/provenance, interpretations, development-source lineage.
* `frozen_manifest.json`: pre-prediction input/source/checkpoint hashes; refuse source drift.
* `run_baseline.py`: actual API detector dependencies, actual offline models, TXT/PDF/DOCX ingestion;
  authored and segmented modes, parser probes, null undefined metrics, new run-directory requirement.
* `results/frozen_primary/` and `results/frozen_replication/`: full `predictions.jsonl`, clause CSV,
  decision CSV, metrics/coverage/error `summary.json`, runtime metadata, rejection probes and four
  synthetic PDF/four DOCX transport inputs each. These are NEW evaluation inputs, not private contracts.
* `analyze_results.py`, `results/evidence_index.json`: derived review evidence, no detector changes.
* `results/repeatability.json`: raw evidence order vs canonical scientific prediction equality.
  Only set-like target/sample/involved-ID lists are sorted; scores and clause sequences are retained.
* `preservation_before.json`, `verify_preservation.py`, `results/preservation_verification.json`:
  pre-existing dirty work/research/model preservation. Not a substitute for source manifest verification.
* `results/legalbert_cache_fingerprint.json`: supplementary post-run local encoder file fingerprint.
* `results/corpus_reproduction.json`: 71/71 regenerated input files byte-identical.
* `regression_tests.xml`, `regression_console.log`, `evaluation_tests.xml`: actual test evidence.
* `replication_console.log`: full repeated-run console evidence including model-load warnings.
* `execution_log.json`: commands, actual exits, initial interrupted/failed attempts and successful reruns.
* `runtime/` (ignored): isolated embedding/feedback scratch and corpus reproduction; never an artifact
  to publish. Nothing in runtime is scientific ground truth or a model retraining output.

## Reproduce on this local checkout (PowerShell)

Run from `F:\projects\nlp\Legal-contract-coherence-auditor-`. Existing clean CPU environment:

```powershell
$python = '.\tmp\final-release\clean-env\Scripts\python.exe'
$evaluation = '.\evaluations\phase1_detection_baseline_2026_10_26'
# Existing local Legal-BERT cache is required; run_baseline disables downloads.
# Use a NEW run ID each time. Existing output directories are never overwritten.
& $python "$evaluation\run_baseline.py" --run-id reproduction_01
& $python "$evaluation\verify_preservation.py"
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = '1'
$env:HF_HUB_OFFLINE = '1'
$env:TRANSFORMERS_OFFLINE = '1'
$env:LEXAUDIT_ALLOW_MODEL_DOWNLOAD = '0'
$env:OMP_NUM_THREADS = '2'
& $python -m pytest "$evaluation\test_evaluation_contract.py" -q
& $python -m pytest tests/test_rules.py tests/test_final_release.py tests/test_ensemble.py tests/test_severity.py tests/test_segmentation.py -q
```

TestClient needs permitted local socket communication; an initial restricted-sandbox regression
invocation stalled at the first HTTP case and was interrupted. An approved local run passed 43/43.
No internet or external database is needed. Test storage is isolated by existing `tests/conftest.py`.
Do not disable assertions or modify detector thresholds to make the diagnostic cases pass.

To independently regenerate just the corpus, choose a NEW scratch directory:

```powershell
& $python "$evaluation\build_dataset.py" --output "$evaluation\runtime\corpus_reproduction_02"
```

The original `--freeze` invocation already created the manifest BEFORE any detector predictions.
Do not regenerate that manifest to disguise changed input/source. For a future modified algorithm,
create a separately named evaluation with lineage and clearly retained development status.

## Result boundary

Main TXT results: reference presence P=.75/R=.3333/F1=.4615; graph direction P=1/R=.6667/F1=.8;
date chronology P=.75/R=.75/F1=.75. Neural B/ensemble order proxy P=.75/R=.3333/F1=.4615;
A OOD detected none of nine permutations. There is **no aggregate legal accuracy estimate**.
Read `../../docs/ACCURACY_BASELINE_AUDIT.md` for all counts, denominators, strata and limitations.
No UI changes, model retraining, recalibration, source fixes, Git writes or deployment occurred.
