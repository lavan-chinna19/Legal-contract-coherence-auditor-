# Final release test results

<!-- docker-validation-final -->
**Updated 2026-10-24: 24/24 application components COMPLETE (100/100).** The user-authorized local Docker deployment and restart/recreation persistence passed. Independent scientific, legal and external security validation remains outstanding. See [DOCKER_VALIDATION_REPORT.md](DOCKER_VALIDATION_REPORT.md) and [DOCKER_RUN_AND_VALIDATION.md](DOCKER_RUN_AND_VALIDATION.md) for actual evidence and launch commands.


All fixtures created for live release acceptance are synthetic. Tests isolate uploads, feedback and threshold files from existing user data. No results below are invented; source logs/XML are retained under the ignored `tmp/final-release` directory and root `tmp-release-*.log` files.

| Check | Actual result | Exit code |
| --- | --- | --- |
| Latest completed full clean backend suite `pytest tests -q` | 245 passed, 2 skipped; 167.87 s, including the concurrent-initialization regression | 0 |
| Final security/retention suite in reversed order | 32 passed; 92.03 s | 0 |
| Final release/isolation acceptance | 19 passed; 37.17 s | 0 |
| Clean isolated Python pip check | No broken requirements | 0 |
| Compose configuration validation (no build/run) | Passed; obsolete version warning | 0 |
| Final report-layout affected tests | 2 passed; 66.28 s | 0 |
| Preview/report acceptance before final retention addition | 18 passed; 64.74 s | 0 |
| Additional model-unavailable preview | 1 passed; 55.60 s | 0 |
| Installed dependency snapshot dry-run | Consistent; optional spaCy model excluded | 0 |
| Final graph/model/attribution affected suite | 26 passed; 131.66 s | 0 |
| Final severity/security/parser/report affected suite | 43 passed; 123.14 s | 0 |
| Authorization and release race-fix suite | 31 passed; 191.20 s | 0 |
| Initial new release acceptance rerun | 16 passed; 130.03 s | 0 |
| Frontend lint | Passed | 0 |
| TypeScript `tsc --noEmit` | Passed | 0 |
| Frontend production build, Next 16.4.3 | Passed | 0 |
| Existing clause alignment script | 17/17 passed | 0 |
| Live API acceptance | 28 real HTTP checks passed | 0 |
| Production npm audit after targeted patch | 0 reported vulnerabilities | 0 |
| Clean frontend `npm ci` | 347 packages installed from lockfile | 0 |
| Clean frontend production build | Passed from copied current source and new node_modules | 0 |
| Release requirements dry-run | Resolved additions without changing global environment | 0 |
| Shared Python `pip check` | OpenCV packages require NumPy >=2; existing LexAudit NumPy pin is 1.26.4 | 1 |
| Docker engine checks | Initially unavailable; final startup socket crash; final bounded probe timed out | 1 initially; final timeout |

The test suites overlap; their pass counts must not be added into a fictitious count of unique tests. The latest full-suite total is 247 collected tests, with 245 passes and two skips. The skips are `tests.test_cuad_order.test_live_cuad_order_report_exists` and `test_live_cuad_report_has_verdict`, both missing the optional CUAD order-report artifact. Publication checks, including a separate snapshot without local research data, are recorded in [RELEASE_PUBLICATION.md](RELEASE_PUBLICATION.md).

## Browser acceptance actually exercised

Real Chromium tools exercised API-key sign-in, synthetic TXT/PDF/DOCX file selection and upload, real analysis, clause review and source identity, analytics, the frozen compatibility map, signed attribution tokens, Channel B neighbor sensitivity, counterfactual ranked positions and abstention, a synthetic broken-reference robustness scenario, reviewer feedback, both report-download buttons, explicit dependency opt-in and evidence, saved-analysis reopening, unsupported-file error, a narrow viewport and Enter-key clause selection. The browser showed no critical application error in these successful flows. This is a bounded acceptance pass, not exhaustive visual testing or accessibility certification.

Live HTTP acceptance independently exercised all three document formats, parsed-clause previews, analysis/results, graph, both reports per format, attribution, sensitivity, counterfactuals, robustness negative control, other-owner export denial and saved-document listing. A real API restart was followed by successful retrieval of an encrypted completed analysis.

## Reports

Both downloads were reopened and checked using PDF text extraction and DOCX XML/package parsing. Shared report construction supplies equivalent factual results. Empty and uncertain results are tested. Generated reports were rendered and inspected: PDF through PDFium; DOCX through an installed separate Microsoft Word instance after the LibreOffice helper reported that LibreOffice was unavailable. No clipping, missing glyphs or margin overflow was observed in the synthetic report pages. Final pagination changes keep anomaly explanations together; the final three-page PDF and Word-rendered DOCX samples were inspected again and the two affected layout tests passed.

## Failures encountered and corrected

- One pre-existing frontend test-script `any` type failed lint; replaced with the actual fixture field type.
- Oversize byte parameters produced an enormous Windows pytest test ID and exceeded the environment-variable size limit; explicit short IDs fixed the harness without dropping assertions.
- An interrupted local Pillow replacement made a temporary dependency overlay incomplete; the launcher/test runner append optional libraries after the established application packages instead of shadowing them. Fresh installs use the constrained release requirements.
- The first complete backend run had 240 passes, two skips and one explanation busy-response failure. A bounded model-operation queue fixed the race; subsequent affected and full suites pass.
- Registry audit identified critical advisories for Next 16.4.0. Only Next and its matching lint packages were patched to 16.4.3. Large npm downloads required a bounded direct official-registry package download and lockfile reconciliation; final clean npm installation and build pass.
- Initial browser/server attempts were blocked by sandbox networking and a separate app occupying port 8000. LexAudit verification used dedicated port 8010 without stopping the other app.
- Narrow-screen robustness controls overflowed. Bounded selectors, scrollable tables and responsive grid sizing fixed page overflow; keyboard clause selection was also verified.

## Exact session commands

The established environment's optional export directory was appended for Python tests:

```powershell
$env:HF_HUB_OFFLINE='1'
$env:OMP_NUM_THREADS='2'
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'
python -u -c "import sys; sys.path.append('.release-deps'); import pytest; raise SystemExit(pytest.main(['tests','-q','--tb=short','--junitxml=tmp/final-release/final-regression.xml']))"
python scripts/verify_release_http.py --url http://127.0.0.1:8010
cd frontend
npm run lint
npx tsc --noEmit
npm run test:alignment
npm run build
npm audit --omit=dev --json
```

A fresh isolated CPU Python installation completed successfully. Its dependency check passed, and its complete backend suite passed 244 tests with two skips. The initial clean import failed because PyArrow 26 requires NumPy 2; pinning the already-working PyArrow 25.0.1 repaired compatibility without upgrading NumPy. The additional no-findings test initially exposed a fixture-factory call and shared rate-bucket issue in the test harness; both were fixed while retaining the production rate limit and all assertions. The subsequent clean suite passes. This verifies a clean local environment with the documented existing public model cache, not a clean operating-system installation.

## Final safeguards and current verification

A legacy end-to-end security test left its analysis worker running after its identity fixture ended, causing a later test to observe a real busy response in reversed test order. It now waits for completion and asserts matching actual results; the reversed security/retention suite passes 32/32. Test uploads are forced into an isolated directory even if a live upload path is inherited. Final release/isolation acceptance passed 19 tests in 37.17 seconds, exit 0. The final complete suite after this guard and offline model-import safeguards passed 244 tests with two documented skips in 161.73 seconds, exit 0 (`final-offline-regression.log` and XML).

The first dependency-snapshot dry-run attempted to resolve an installed optional spaCy model's direct GitHub URL and failed because networking was unavailable. The optional model is now excluded from the snapshot, consistent with the existing supported fallback; the installed-environment dry-run passes. This check is not a fresh install from the snapshot. The clean environment itself was built and tested using the constrained release requirements.

The final live service check received HTTP 200 from frontend `/`, backend `/health`, and model `/ready`. Chromium opened the optimized production frontend at 390px and reopened the same saved ten-clause analysis after the final API restart. Fresh readiness loaded local weights without the previously observed model-metadata requests; no contract text was included in those earlier requests. Latest frontend lint, types and 17 alignment assertions passed again, all exit 0 (`final-frontend-*.log`).

Docker Desktop was installed but not running. A bounded startup attempt produced the user-visible Inference manager `dockerInference` socket error (file inaccessible / invalid filename syntax). A separately timed engine probe timed out after 15 seconds. The waiting startup CLI was interrupted and further Docker startup attempts stopped. This initial host failure was later recovered without data deletion. Container build/runtime, acceptance, image audits and restart/recreation checks now pass; no factory reset or external deployment occurred.

## Verified Docker follow-up

Compose build/configuration and all command checks exited 0. Real acceptance: 103 passing HTTP/runtime assertions; image/storage audit: 14 passes; Chromium: 10 passing assertions; release tests inside the Linux image: 20 passed, exit 0. Docker health checks show backend/frontend/gateway/PostgreSQL healthy. Exact snapshots and PostgreSQL feedback survive restart and application-container recreation. Counts overlap prior native coverage and are not summed. The Docker validation report links the retained actual logs and evidence.

The Docker follow-up also ran 5 targeted native embedding/concurrency checks (exit 0). The earlier 244-pass full-native result predates the new concurrency case; the subsequent publication full run passed 245 tests with two skips as recorded above. The current Linux release suite contains 20 tests. Initial host-routing and maintenance-health failures were corrected and their artifacts retained. See DOCKER_VALIDATION_REPORT.md for exact boundaries and all final evidence.

Final container dependency check: exit 0, no broken requirements. Exact feedback-ID persistence postflight: pass.
