# Phase 2 Evidence Index & Screenshot Manifest

**Project:** Legal Contract Coherence Auditor (`LexAudit`)  
**Directory:** `design/ui_redesign/phase_02/evidence/`  
**Total Screenshots:** 14 files  
**Total Data Logs:** 1 file  

---

## 1. Verified Screenshot Evidence Files

| Filename | Dimensions | File Size | Description & Test Step |
|---|:---:|:---:|---|
| `viewport_01_desktop_1440x900_light.png` | 1440x900 | 101,066 B | Desktop default light theme layout, LexAudit sidebar brand, and global disclaimer |
| `theme_01_dark_mode_1440x900.png` | 1440x900 | 100,394 B | Desktop dark theme mode after clicking `#theme-btn-dark` |
| `theme_02_reload_persistence_dark.png` | 1440x900 | 100,379 B | Page reload with zero-flicker dark theme persistence from `localStorage` |
| `viewport_02_laptop_1024x768.png` | 1024x768 | 99,380 B | Laptop layout with 200px compact sidebar and fluid content area |
| `viewport_03_tablet_768x1024.png` | 768x1024 | 74,560 B | Tablet layout with collapsible off-canvas navigation and hamburger menu toggle |
| `viewport_04_mobile_390x844.png` | 390x844 | 58,180 B | Smartphone layout with responsive stacked cards and 0px horizontal overflow |
| `nav_01_contract_review_empty.png` | 1440x900 | 85,396 B | Contract Review empty state: "No Active Contract in Review" with CTA button |
| `nav_02_explainability_empty.png` | 1440x900 | 86,094 B | Explainability empty state: "Explainability Unavailable" with CTA button |
| `nav_03_feedback_empty.png` | 1440x900 | 83,477 B | Reviewer Feedback empty state: "Feedback Interface Inactive" with CTA button |
| `nav_04_transparency_benchmarks.png` | 1440x900 | 98,985 B | Transparency & Benchmarks empirical evaluation table and Kendall's Tau metric cards |
| `workflow_01_results_view.png` | 1440x900 | 110,642 B | Active contract results: KPI cards, sequence coherence heatmap, and clause findings list |
| `workflow_02_xai_attribution.png` | 1440x900 | 113,361 B | Explainability Integrated Gradients token attribution highlights with color weights |
| `workflow_03_xai_sensitivity.png` | 1440x900 | 96,825 B | Explainability perturbation sensitivity score delta for masked neighbor position |
| `workflow_04_feedback_success.png` | 1440x900 | 92,799 B | Reviewer feedback submission confirmation with live server feedback ID |

---

## 2. Machine-Readable Evidence Data

- `browser_verification_results.json`: JSON output containing execution timestamps, gate evaluations, and screenshot metadata.
