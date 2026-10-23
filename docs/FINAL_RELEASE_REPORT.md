# LexAudit final release report

<!-- docker-validation-final -->
**Updated 2026-10-24: 24/24 application components COMPLETE (100/100).** The user-authorized local Docker deployment and restart/recreation persistence passed. Independent scientific, legal and external security validation remains outstanding. See [DOCKER_VALIDATION_REPORT.md](DOCKER_VALIDATION_REPORT.md) and [DOCKER_RUN_AND_VALIDATION.md](DOCKER_RUN_AND_VALIDATION.md) for actual evidence and launch commands.


Date: 2026-10-23, Asia/Calcutta. Classification: **DEMO_READY_WITH_LIMITATIONS**.

The requested local application workflows and Docker deployment are implemented and verified. The unchanged checklist denominator now has **24 COMPLETE items out of 24: 100/100**. Independent scientific and external security validation remain separate blockers and are not claimed as completed application features.

## Verified application behavior

| Capability | Result |
| --- | --- |
| API-key sign in and owner isolation | PASS; documents, previews, jobs, results and exports are protected |
| TXT/PDF/DOCX parsing | PASS; real local parsers, validation errors and bounded uploads |
| Parse and preview before model execution | PASS; exact clauses and normalized locations shown, then the same document is analyzed |
| Local analysis and clause review | PASS; frozen Channel A/B outputs, authoritative clause IDs and source-span verification |
| Saved analyses | PASS; encrypted latest completed snapshot per document, including real restart recovery |
| Analytics and compatibility map | PASS; real current-document metrics and separately labelled frozen research artifact |
| Explanations | PASS; real Integrated Gradients tokens and neighbor sensitivity |
| Counterfactual workflow | PASS; ranked positions, explicit abstention, no automatic document changes |
| Robustness lab | PASS; opt-in experiments, real broken-reference evidence and negative-control invariants |
| Dependency graph | PASS; separate opt-in channel, exact source/target evidence and review/abstention states; ensemble unchanged |
| PDF and DOCX reports | PASS; equivalent factual content, real model results, evidence, counterfactuals where available and limitations |
| Reviewer feedback | PASS; authenticated persistence; self-reported provenance is not expert verification |
| Error and empty states | PASS; no findings, uncertain graph evidence, parser failure, model unavailable, busy operation and stale job states |
| Responsive keyboard interface | PASS in bounded acceptance; 390px review/preview/XAI and narrow robustness controls, native keyboard clause selection |
| Clean local setup | PASS; fresh isolated CPU Python environment and clean frontend dependency installation/build |
| Docker runtime | PASS; real build, four healthy services, workflow acceptance, image audit and restart/recreation persistence |

## Actual end-to-end verification

Chromium exercised sign in, synthetic upload, parsed-clause preview, analysis of that same document, source-backed review, token explanations, and PDF and DOCX download. The preview and result document IDs matched. The no-findings sample displayed ten parsed clauses and no configured detector flags, with an explicit statement that this does not establish legal correctness. Separate browser flows exercised PDF and DOCX uploads, analytics, the 66-category compatibility artifact, sensitivity, counterfactual abstention, broken-reference robustness, dependency evidence, feedback, history and unsupported-file errors.

The final live API script passed **28 HTTP checks** across all three document formats. Preview and analysis clause inventories matched exactly. Other-owner report access returned 404, missing authentication returned 401 in regression, and completed snapshots reopened after a real API restart with the same encryption key.

## Implemented repairs

- Added in-memory PDF/DOCX ingestion, signatures/archive validation, UTF-8 handling and clear errors. Multipart bytes are bounded before framework parsing and accepted files remain below the in-memory spool threshold.
- Added an authenticated parser preview route that does not load model weights, a preview UI and analysis of an already parsed document. The combined upload-and-analyze action remains functional.
- Added encrypted analysis snapshots and encrypted filenames, authenticated history and exports, atomic snapshot writes, snapshot write serialization and restored-job caching. New document IDs use full UUIDs; existing IDs remain valid.
- Added local report generation with a shared factual source for both formats. Reports include metadata, model/checkpoint provenance, summaries, inventories, excerpts, locations, grouped candidates, score interpretation, graph/counterfactual evidence and a technical appendix. Font fallback is explicit and headings/explanations are kept together.
- Added a conservative explicit-reference dependency graph. Numeric identities, direction and explicit immediate-predecessor checks are independent of existing scores. Duplicate/unresolved targets, unsupported Roman identities and vague antecedents require review. Self-contained antecedents are preserved under movement.
- Added serialized model operations with a bounded queue, CPU defaults, explicit missing-model errors and stale-job failure reporting. Attribution batches are bounded. Heavy explanation, counterfactual and robustness work leaves the HTTP event loop responsive.
- Added stable configuration loading, an explicit public synthetic-demo profile, private configured startup checks, exact CORS origins, no-store response headers and periodic retention, including per-document derived-vector cache cleanup. Removed legacy model-loader safety bypasses; local loading uses the installed framework's normal checks. Offline environment guards are set before model-library imports to prevent incidental model-metadata requests.
- Removed the browser's embedded demo credential default. Sign-out and connection changes clear active document state. Downloads and experimental actions have visible progress/error states.
- Corrected misleading neural-model, severity-threshold, ensemble-weight, calibration-guarantee and negative-control labels. Clause severity distributions now count clause classifications separately from rule candidates.
- Patched Next.js and its matching lint package from 16.4.0 to 16.4.3 after a real registry security audit. The final production dependency audit reports zero advisories.
- Added a PyArrow 25.0.1 compatibility pin after a fresh install exposed PyArrow 26's runtime incompatibility with the preserved NumPy 1.26.4 stack.
- Isolated legacy destructive feedback tests and redirected test-generated reports away from historical research artifacts.

## Tests and evidence

The latest complete clean-environment regression passed **245 tests, skipped two, failed zero**, in 167.87 seconds, exit 0, including the concurrent-initialization regression. The earlier release/isolation acceptance suite passed **19 tests**, exit 0; the additional model-unavailable preview check passed, exit 0. Publication-only snapshot results are recorded in `RELEASE_PUBLICATION.md`. Earlier affected suites and failures are recorded in `FINAL_RELEASE_TEST_RESULTS.md`; overlapping counts are not added together.

Frontend lint, TypeScript and optimized Next.js 16.4.3 builds passed, exit 0. The existing alignment suite passed 17/17. A separate clean `npm ci` installed 347 packages and built successfully. The fresh Python dependency check reports no broken requirements. The original shared Python environment still has unrelated OpenCV/NumPy constraint warnings; it was not broadly upgraded.

Both report packages were reopened and their content validated. Synthetic pages were rendered with PDFium and Microsoft Word and visually inspected. This is real bounded visual QA, not universal font/layout certification. Chromium was used; the UI was not merely inferred from HTTP responses.

The CPU path was used, with two OpenMP threads by default. No isolated peak-memory or whole-application latency benchmark was conducted. One shared-host snapshot showed a Node process around 609 MB and a Python process around 586 MB working set; these are instantaneous observations, not peak RAM or a capacity certification.

## Files changed for this release

The working tree already contained extensive uncommitted work at entry. The list below identifies files this release edited or added; it does not attribute earlier changes in those files to this session.

- Configuration/build: `.env.example`, `.gitignore`, `Dockerfile.backend`, `README.md`, `requirements-release.txt`, `requirements-release-lock.txt`, `frontend/package.json`, `frontend/package-lock.json`.
- Backend: `src/__init__.py`, `src/config.py`, `src/embeddings/frozen.py`, `src/xai/ig.py`, `src/scoring/severity.py`, `src/rules/dependency_graph.py`, `src/api/ingestion.py`, `src/api/upload_limits.py`, `src/api/dependencies.py`, `src/api/jobs.py`, `src/api/main.py`, `src/api/privacy.py`, `src/api/retention.py`, `src/api/storage.py`, `src/api/reports.py`, `src/api/release_routes.py`, `src/api/v1/router.py`.
- Frontend: `frontend/src/app/page.tsx`, `frontend/src/app/globals.css`, `frontend/src/components/ReleaseTools.tsx`, `frontend/src/components/review/types.ts`, `frontend/src/components/review/ContractReviewWorkspace.tsx`, `ClauseDocumentViewer.tsx`, `ScoreEvidencePanel.tsx`, `frontend/src/components/explainability/ExplainabilityWorkspace.tsx`, `ClauseExplanationHeader.tsx`, `frontend/src/components/analytics/AnalyticsWorkspace.tsx`, `AnalyticsEmptyState.tsx`, `SeverityDistribution.tsx`, `ClauseScoreDistribution.tsx`, `CalibrationTransparency.tsx`, `RuleFindingsSummary.tsx`, `frontend/src/components/redteam/PerturbationSelector.tsx`, `RedTeamEmptyState.tsx`, `ChannelResponseComparison.tsx`, `frontend/src/components/layout/HeaderBar.tsx`.
- Tests/tools: `tests/conftest.py`, `tests/test_final_release.py`, `tests/test_security.py`, `tests/test_security_review.py`, `tests/test_wordpiece_grouping.py`, `frontend/scripts/test_alignment_suite.ts`, `scripts/run_server.py`, `scripts/create_release_fixtures.py`, `scripts/verify_release_http.py`.
- Handoff: `docs/FINAL_RELEASE_BASELINE.md`, `FINAL_COMPLETION_TRACKER.md`, `FINAL_RELEASE_REPORT.md`, `FINAL_RELEASE_TEST_RESULTS.md`, `INSTALL_AND_RUN.md`, `KNOWN_LIMITATIONS.md`, `RESEARCH_VALIDITY_STATUS.md`, `RELEASE_CHECKLIST.md`.

Checkpoints and centroids match their original Git objects: `c1b9ab0738c58b6409913c172017d3315e65d81c` and `2d316e3703f8044832bc087a6896ee41e9303d4e`, respectively. Historical predictions, labels and research datasets were not rewritten. The implementation baseline was `23dbcf5`; subsequent user-authorized Git publication to `lexaudit-final-release` is documented in RELEASE_PUBLICATION.md. No destructive Git operation or external deployment is authorized. The authorized local Docker deployment was verified.

## Launch

From the repository root, after following the dependency installation in `INSTALL_AND_RUN.md` and preparing the documented local model cache:

```powershell
python scripts/run_server.py --demo --port 8010
```

In another terminal:

```powershell
cd F:\projects\nlp\Legal-contract-coherence-auditor-\frontend
npm run dev -- --hostname 127.0.0.1
```

Open `http://127.0.0.1:3000`, set Connection's API URL to `http://127.0.0.1:8010`, enter the public synthetic-demo key `dev_auditor_key_12345`, and sign in. For private use, follow `INSTALL_AND_RUN.md` and configure unique keys; do not use the demo profile.

## Remaining limits and release decision

Docker runtime verification now passes; all 24 counted application items are COMPLETE. Two optional CUAD research tests skip because their corpus artifact is absent. PostgreSQL feedback persistence and the four-service Compose deployment were verified. Optional legacy MinIO and the separate Streamlit interface were not promoted as verified release paths. No external deployment was attempted.

Independent human legal annotation, a genuine unseen-family confirmatory evaluation and external security validation are still required before scientifically validated production claims. The system remains a local decision-support demonstration with honest uncertainty and explicit experimental channels.

## Final readiness and live state

**Demo: DEMO_READY_WITH_LIMITATIONS. Production: not validated for production.** The native frontend/API remain available on 3000/8010; the verified local Docker deployment uses 3001/8011. Fresh health/readiness and owner-history calls return 200; Chromium reopened a saved ten-clause analysis after the final API restart. Both report downloads were exercised through the optimized frontend.

Docker Desktop startup failed in its Inference manager socket initialization (`dockerInference`: file inaccessible / invalid filename syntax), as shown in the user's screenshot. A 15-second engine check timed out, the waiting startup CLI was interrupted, and no further Docker starts were attempted. No factory reset was performed. The socket-only directories were subsequently preserved and engine recovery succeeded. The 24th component is now COMPLETE, backed by the Docker validation report. Independent annotation, unseen-family evaluation and external security validation remain separate production-readiness blockers. No known unresolved critical local-workflow bug was observed in the bounded checks; this is not exhaustive certification.
