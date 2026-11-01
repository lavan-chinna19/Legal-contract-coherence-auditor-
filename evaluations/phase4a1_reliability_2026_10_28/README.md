# Phase 4A.1 — three repairs and focused applicability evidence

This directory preserves the actual original Phase 4A matcher, exposed before/after results,
separate annotation corrections and descriptive evidence from three authentic SEC contracts.
No independent expert labels, unseen test claim or legal accuracy claim is made. See the single
required report `docs/PHASE4A1_RELIABILITY_AND_FEASIBILITY_REPORT.md` for counts and NO-GO decision.

## Evidence map

* `preservation_before.json`: 1,416 existing-file hashes and original Git HEAD, including dirty work.
* `baseline_snapshot/binding.py`: byte-exact Phase 4A frozen module, verified against its manifest.
* `original_count_audit.json`: selected-pair/document/binary/abstention definitions and reconciliation.
* `PROTOCOL.md`, `focused_cases.json`, `focused_input_manifest.json`, `build_focused_cases.py`:
  20 authored mechanical cases, frozen before repairs; exposed development evidence only.
* `results/baseline_v1/`: actual old implementation predictions; 58/58 archived outputs reproduced,
  plus the 20 new cases and six public source-view observations.
* `results/comparison_v1/`: initial repair predictions; preserved definitional-subject actor bug.
* **`results/comparison_v2/`**: final paired synthetic/public predictions, source manifest, summary,
  every changed labelled state and verification. Source/extraction views and evidence are retained.
* `annotation_overlay.json`: four explicit recurrence field corrections, separate original/raw and
  corrected-overlay metrics for both implementations. Original labels/predictions/pair gold unchanged.
* `public_applicability_audit.json`: URLs, filings, hashes, source spans, limited candidate examples,
  parsing versus grammar versus ambiguity distinctions, and the unrepaired inline-body blocker.
* `affected_v1.xml/.log`: 63 initial targeted passes. `affected_v2.xml/.log`: 73 final affected
  integration passes. **`full_native_v1.xml/.log`: 468 passed, 0 failed, 2 optional skips**.
* `verify_core.py`, `preserved_output_verification.json`: reuse of historical core verifier with
  output redirected here; 148 neural/structure/reference/graph/direct-date and 38 saved-date matches.
* `docker_engine.log`: unavailable engine, exit1; no container runtime validation.
* `execution_log.json`: actual commands/exits and limits. `final_verification.json`: preservation,
  model/cache, source/input baseline hashes and parsed native test totals.

## Reproduce

From the repository root, use the existing clean Python and offline model flags documented in
the report. `python run_comparison.py --run-id <new-id>` repeats the exposed paired run using the
saved actual old baseline. `--baseline --run-id <another-new-id>` reruns the exact frozen old module.
All run IDs must be new. The scripts refuse to overwrite evidence. Full native tests isolate user
storage and require permitted local HTTP communication. No Git mutation or user-service restart.

Raw/public normalized views are six observations of three contracts, not six independent documents.
The former reserved set is already exposed. Corrections and new authored cases must never be
renamed as an independently unseen holdout. No further algorithm expansion is part of this phase.
