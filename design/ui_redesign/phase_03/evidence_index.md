# Evidence Index — Phase 3
**Directory: `design/ui_redesign/phase_03/evidence/`**

## 1. Overview
All screenshots and verification records were generated using real headless/remote Chrome sessions executing against the live Next.js application on `http://localhost:3000` and FastAPI on `http://127.0.0.1:8000`. No mocked data or synthetic image generation was used.

---

## 2. Screenshot Manifest

| Filename | Description & Subject Matter | Viewport / Theme | File Size (Bytes) |
|---|---|---|---|
| **`01_desktop_1440x900_light_review.png`** | Primary 55/45 split-screen review workspace. Renders document viewer with continuous clauses on left, sequence risk heatmap bar at top, and findings inspector with coherence metrics on right. | 1440 × 900 (Default Light) | 137,619 |
| **`02_desktop_1440x900_dark_review.png`** | Dark theme review workspace. High-contrast accessible text, dark slate cards, vibrant severity indicators, and cohesive styling. | 1440 × 900 (Dark Mode) | 137,685 |
| **`03_laptop_1024x768_review.png`** | Adaptive split-screen review workspace on standard laptop display. Dual panels maintain readability with independent vertical scroll. | 1024 × 768 (Light) | 100,332 |
| **`04_tablet_768x1024_review.png`** | Responsive stacked tablet layout. Document viewer stacks cleanly above findings inspector without nested scroll clipping. | 768 × 1024 (Light) | 85,551 |
| **`05_mobile_390x844_review.png`** | Responsive single-column mobile view. Readable contract typography, 44px+ touch targets, and full findings visibility below document stream. | 390 × 844 (Light) | 43,420 |
| **`06_clause_02_selected_inspector.png`** | Interactive selection of Clause 2 (§ 1). Highlights left card and immediately populates right inspector with per-clause Legal-BERT and Markov metrics. | 1440 × 900 (Light) | 141,031 |
| **`07_search_filter_term.png`** | Text search active (`"Term"`). Document viewer filtered to 2 matching clauses with counter displaying `(filtered)` and visible clear button. | 1440 × 900 (Light) | 124,438 |
| **`08_search_zero_results.png`** | Zero-match query (`"XYZNonExistent..."`). Displays accessible empty state with search icon and `"Reset Search & Filters"` button. | 1440 × 900 (Light) | 118,065 |
| **`09_inspector_rule_findings_tab.png`** | Inspector switched to Rule Findings tab. Displays clean state notification (`"No deterministic rule violations were reported for this analysis."`). | 1440 × 900 (Light) | 122,189 |
| **`10_cross_workspace_xai_carryover.png`** | Cross-workspace navigation to Explainability (XAI) via inspector toolbar button. Carries selected clause ID (`doc_b6c220fb_1`) without URL parameters. | 1440 × 900 (Light) | 89,652 |
| **`11_cross_workspace_feedback_carryover.png`** | Cross-workspace navigation to Reviewer Feedback. Carries selected clause ID (`doc_b6c220fb_1`) into review feedback target selector. | 1440 × 900 (Light) | 89,362 |

---

## 3. Data & Matrix Artifacts

- **`field_level_value_comparison.csv`**: Ground-truth field-by-field CSV comparing backend `/v1/jobs/{job_id}/results` values against live DOM extractions.
- **`responsive_test_matrix.csv`**: Matrix validating layout behavior across desktop, laptop, tablet, and mobile viewports.
- **`frontend_test_results.json`**: Machine-readable output from `scripts/run_phase3_browser_verification.py`.
- **`backend_regression_results.json`**: Machine-readable output from `python -m pytest tests/ -v -ra`.
