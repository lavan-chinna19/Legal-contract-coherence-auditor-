# Final release publication

Publication target authorized by the user: `origin/lexaudit-final-release`, based on
`23dbcf536f2fb3dce1611e2d2ae71e9ca8c86f55`. Publication does not authorize a merge to
`main`, a force push, an external deployment or a GitHub Release/tag.

## Included and preserved files

The release includes the application source, UI components, public aggregate
compatibility matrix, Docker definitions, dependency specifications, synthetic
regression tests, verification tools and installation/validation documentation.
An explicit file manifest is reviewed before staging. Existing tracked research
history and pretrained assets remain unchanged. The unrelated existing working
change to `fixtures/load_test_results.json` is preserved locally and excluded.

Private `.env` files, contract uploads, databases, caches, installed dependencies,
generated reports, screenshots, logs and raw Docker validation evidence remain
local. `.env.example` contains empty credential fields, with instructions to
generate private values. Public synthetic/demo credentials in tests and the
explicit `--demo` profile are not private deployment credentials.

The existing tracked `models/coherence_classifier.pt` is 3,218,819 bytes. Its Git
blob remains `c1b9ab0738c58b6409913c172017d3315e65d81c`; the centroid fixture remains
`2d316e3703f8044832bc087a6896ee41e9303d4e`. No selected file requires Git LFS.
The public Legal-BERT cache (approximately 881 MB locally), experimental C2
checkpoint (5,464,777 bytes), virtual environments and temporary build output are
excluded. Download the public model using the documented setup command; do not
add its cache to Git. No LFS migration or history rewrite is performed.

## Verification boundaries

The complete local checkout and a separate application-release snapshot are
tested independently. The snapshot contains only proposed Git files, retaining
the unchanged baseline load-test fixture. It contains no local research corpus,
private configuration or experimental checkpoint. Actual results are recorded
below. Raw logs and XML remain in ignored
`tmp/release-publish`.

Seven previously untracked historical test/helper files remain local with their
datasets and audit records: `test_benchmark_consistency.py`,
`test_phase_04dca_audit.py`, `test_phase_04dd_dataset.py`,
`test_phase_04dda_audit.py`, `test_redteam_metric_consistency.py`,
`test_structural_coherence_model.py` and `test_xai_numerical_validation.py`.
They require local research artifacts or optional experimental model assets and
are not represented as portable application regression tests. They are neither
deleted nor rewritten; the full-checkout regression still exercises the
collectable tests. No tracked test is removed or disabled.

The fresh snapshot additionally lacks the optional EDGAR sample used by one
legacy integration test. The release acceptance suite independently exercises
real local model inference using synthetic inputs. Missing optional research
artifacts are reported as skips, never passes.

| Final publication check | Actual result | Exit code |
| --- | --- | --- |
| Full local backend regression | 245 passed, 0 failed, 2 skipped; 167.87 s | 0 |
| Publication-only backend regression | 190 passed, 0 failed, 3 skipped; 101.49 s | 0 |
| Frontend lint | Passed | 0 |
| Frontend TypeScript | Passed | 0 |
| Frontend alignment checks | 17 passed | 0 |
| Production frontend build from reviewed source and matching clean-install lockfile | Passed | 0 |
| Fresh snapshot fixture helper and actual TXT/PDF/DOCX parsing | 3 format checks passed | 0 |
| Compose configuration and existing four-service health | Passed; all healthy | 0 |

The full local suite has two missing optional CUAD-report skips. The application
snapshot additionally skips the legacy EDGAR-sample integration test because
its optional local corpus is excluded. The synthetic release acceptance tests
pass with actual local models. The 54 other collectable historical checks belong
to the local research tests described above and are covered by the full local
run; their inputs are not silently bundled into the application release.

Two initial sandboxed backend runs stalled without results. Only their test
processes were stopped; the completed runs above used normal local access with
test-storage isolation and offline models. A helper verification initially used
an unavailable optional `pypdf` module; it was rerun successfully through the
application's installed parsers. No dependency was added to hide this harness
error. The final index whitespace check and content audit passed: 180 changed
files, 419 total Git files, no private-secret findings, no added runtime artifacts
and no file requiring LFS. The frozen asset hashes match the baseline. Only
blank/comment-line whitespace and documentation changed after the
reported regression runs; application behavior is unchanged.

These are local verification results. The existing GitHub workflow triggers on
`main` pushes and pull requests; publishing this separate branch alone does not
establish a successful GitHub Actions run.

Previously completed Docker verification: 103 HTTP/runtime assertions, 14
image/storage assertions, 10 browser assertions and 20 Linux-image release tests
passed. These overlap other suites and must not be summed as unique tests.
Before publication, Compose configuration passed again and backend, frontend,
gateway and PostgreSQL were all healthy.

Application completion remains 24/24 COMPLETE. Demo readiness is
`DEMO_READY_WITH_LIMITATIONS`. Independent scientific/legal annotation,
unseen-family evaluation and external security validation remain outstanding.
