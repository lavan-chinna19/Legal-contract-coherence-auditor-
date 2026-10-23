# Release checklist

<!-- docker-validation-final -->
**Updated 2026-10-24: 24/24 application components COMPLETE (100/100).** The user-authorized local Docker deployment and restart/recreation persistence passed. Independent scientific, legal and external security validation remains outstanding. See [DOCKER_VALIDATION_REPORT.md](DOCKER_VALIDATION_REPORT.md) and [DOCKER_RUN_AND_VALIDATION.md](DOCKER_RUN_AND_VALIDATION.md) for actual evidence and launch commands.


Readiness: **DEMO_READY_WITH_LIMITATIONS**. Counted completion: **24/24 COMPLETE = 100%**. Only COMPLETE counts; all counted application items are verified. The full per-feature ledger is `FINAL_COMPLETION_TRACKER.md`.

| Gate | State | Evidence |
| --- | --- | --- |
| A — Core application | PASS | TXT/PDF/DOCX upload, preview, real local inference, source-backed results; real browser workflows |
| B — Reports | PASS | Valid authenticated PDF/DOCX downloads, equivalent facts, empty/uncertain cases and rendered synthetic-page inspection |
| C — Reliability | PASS | Clean full regression 245 passed/2 documented skips; affected acceptance tests; lint/types/build and 28 live HTTP checks; publication results in RELEASE_PUBLICATION.md |
| D — Research integrity | PASS | Frozen scores preserved; deterministic graph separate and opt-in; development evidence not independent legal accuracy |
| E — Local reproducibility | PASS | Clean isolated CPU Python installation/checks and clean frontend npm installation/build; exact launch instructions |
| Container runtime validation | COMPLETE | Actual Compose build, four healthy services, inference/exports/history, image audit, restart/recreation and 20 Linux release tests |

## Final operational checks

- PASS — API-key owner checks cover preview, analysis, results and exports.
- PASS — Full UUID document identities and exact normalized clause evidence are retained.
- PASS — Original data and frozen checkpoints preserved. Git publication to the user-authorized release branch is documented separately in RELEASE_PUBLICATION.md; no destructive Git operation or external deployment is authorized.
- PASS — Report content uses actual saved results, never placeholder inference.
- PASS — Model-unavailable parsing and explicit analysis failure are tested.
- PASS — No-findings and review-required states are distinct from legal correctness.
- PASS — Installation constraints include the PyArrow/NumPy compatibility repair and Unicode report fonts.
- PASS — Temporary test storage and feedback/threshold files are isolated from existing user data.
- PASS — Historical benchmark outputs are not rewritten by test-report generation.
- PASS — Research validity and operational limitations are recorded separately.

## External validation blockers

- BLOCKED — Independent qualified legal annotation/adjudication.
- BLOCKED — Newly acquired unseen-family confirmatory evaluation under a protocol frozen before exposure.
- BLOCKED — External security validation and real deployment acceptance.

These are not claimed as completed by local application tests. No production-grade legal correctness or production-readiness certification is asserted.
