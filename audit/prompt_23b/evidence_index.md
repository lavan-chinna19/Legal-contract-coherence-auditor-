# Evidence Artifact Index — Prompt 23B

This index catalogs all verified forensic artifacts captured during the independent Prompt 23B browser reproduction and route reconciliation audit. All artifacts are stored under `audit/prompt_23b/evidence/`.

| Artifact Name | Type | Size (Bytes) | Provenance / Workflow Proven | Description & Verification Details |
|---|---|---|---|---|
| `repro_01_app_identity.png` | PNG | 69,463 | Test 1 (App Identity) | Real browser capture confirming page title, H1 heading "Legal Contract Coherence Auditor", disclaimer banner, and online backend status badge. |
| `repro_02_privacy_toggle.png` | PNG | 68,226 | Test 2 (Privacy Interlock) | Real browser capture confirming the Analyze button's disabled state toggles to enabled upon checking privacy consent. |
| `repro_03_analysis_completed.png` | PNG | 76,503 | Test 3 & 4 (Pipeline & Results) | Real browser capture showing completed analysis results for `valid_multiclause.txt`: 4 KPI cards and sequence findings table. |
| `repro_05_xai_attribution.png` | PNG | 75,384 | Test 5 (XAI Attribution) | Real browser capture showing 26 Integrated Gradients token attribution badges rendered with color highlighting. |
| `repro_05_xai_sensitivity.png` | PNG | 59,821 | Test 5 (XAI Sensitivity) | Real browser capture showing neighbor perturbation sensitivity delta badge (`Δ = +0.075`) and transition explanation. |
| `repro_06_feedback_success.png` | PNG | 61,119 | Test 6 (Feedback Persistence) | Real browser capture showing green confirmation banner with feedback ID after submitting `SYNTHETIC_TEST` review verdict. |
| `repro_07_error_handling.png` | PNG | 68,244 | Test 7 (Error Handling) | Real browser capture validating error handling and UI stability under invalid credential input. |
| `repro_network_requests.json` | JSON | 5,428 | Network Audit | Sanitized chronological log of all outgoing HTTP requests issued by the browser during independent reproduction (zero secret leakage). |
| `repro_network_responses.json` | JSON | 5,345 | Network Audit | Sanitized chronological log of all HTTP response status codes returned to the browser during independent reproduction. |
| `repro_console_logs.json` | JSON | 10,823 | Console Audit | Browser console messages confirming 0 React hydration errors and 0 unhandled promise rejections. |
| `repro_kpi_dom.json` | JSON | 141 | DOM Data Dump | Extracted JSON representation of DOM `.kpi-card` labels and values confirming exact numerical match with backend API. |

---

## Verification Statement
All artifacts listed above were captured directly from the live Google Chrome session via native DevTools Protocol WebSocket against `http://localhost:3000` and `http://127.0.0.1:8000`. No synthetic or simulated assets were created.
