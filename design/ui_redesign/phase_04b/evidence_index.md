# Phase 4B — Evidence Index & Artifact Catalog

**Project:** Legal Contract Coherence Auditor (LexAudit)  
**Phase:** 4B — Learned Clause-Pair Compatibility Map & Professional Explainability  
**Date:** 2026-10-14  
**Author:** Independent QA Lead & Senior ML Validation Specialist  

---

## 1. Browser Acceptance Screenshots (`evidence/`)

| File Name | Dimensions | Format | Size (Bytes) | Verification Description |
| :--- | :--- | :--- | :--- | :--- |
| `01_flow_compatibility_map_light.png` | 1440x900 | PNG | 142,756 | Learned clause-pair compatibility heatmap in Light Theme with Core Commercial (12) preset active. |
| `02_flow_compatibility_map_dark.png` | 1440x900 | PNG | 142,720 | Learned compatibility heatmap in Dark Theme verifying token contrast and cell styling. |
| `03_explainability_attribution_light.png` | 1440x900 | PNG | 131,776 | Professional Explainability workspace displaying 25 signed Integrated Gradients token attributions. |
| `04_explainability_token_inspector.png` | 1440x900 | PNG | 133,116 | Token Detail Panel displaying subword decomposition, sum attribution, and peak magnitude. |
| `05_explainability_sensitivity.png` | 1440x900 | PNG | 134,922 | Channel B perturbation sensitivity card with baseline, perturbed, and delta scores. |
| `06_cross_workspace_sync_feedback.png` | 1440x900 | PNG | 93,344 | Reviewer Feedback interface pre-selected to Clause 1 after navigating from Explainability. |
| `07_responsive_1024x768.png` | 1024x768 | PNG | 106,640 | Desktop standard viewport showing responsive layout without horizontal overflow. |
| `08_responsive_390x844_mobile.png` | 390x844 | PNG | 56,315 | Mobile viewport (iPhone 12/13/14) showing responsive stacking without horizontal overflow. |

---

## 2. Numerical Validation CSVs

| File Name | Records | Size (Bytes) | Key Validation Content |
| :--- | :--- | :--- | :--- |
| `matrix_numerical_validation.csv` | 10 rows | 993 | 10 sampled matrix cells compared to fresh frozen-checkpoint inference; max delta `0.000000`. |
| `signed_attribution_validation.csv` | 30 rows | 2,126 | Exact token strings, signed attributions, and sign classifications for Clause 0 and Clause 1. |
| `sensitivity_numerical_validation.csv` | 2 rows | 357 | Baseline score, perturbed score, delta, neighbor position, and method for Clause 0 and Clause 1. |
| `responsive_test_matrix.csv` | 4 rows | 304 | Viewport dimensions, device categories, overflow checks, and associated screenshot evidence. |
| `defect_register.csv` | 8 rows | 1,420 | Comprehensive defect register tracking 8 scientific, model, and UI resolutions. |

---

## 3. Test & Audit Result JSONs

| File Name | Size (Bytes) | Verification Content |
| :--- | :--- | :--- |
| `browser_verification_results.json` | 1,180 | Programmatic CDP test outcomes for 15 acceptance checks, storage audit, and console errors. |
| `wordpiece_grouping_test_results.json` | 7,169 | Complete input/output traces for 12 WordPiece subword grouping unit test cases (100% pass). |
| `frontend_test_results.json` | 980 | Results for TypeScript compile, ESLint, Next.js production build, and alignment suite. |
| `backend_regression_results.json` | 1,150 | PyTest regression summary (120 passed, 2 skipped, 0 failed in 69.04s). |
| `artifact_provenance_manifest.json` | 2,450 | SHA-256 hashes, sizes, architectures, and provenance details for all frozen artifacts. |
