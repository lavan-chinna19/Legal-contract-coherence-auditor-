# Prompt 23A — Evidence Artifact Index

This catalog indexes all 20 verified evidence artifacts generated during Prompt 23A real browser automation testing. All files are located in `audit/prompt_23a/evidence/` and are directly accessible on disk.

| Artifact Filename | Type | Size (Bytes) | Workflow / Phase Proven | Description & Verification Details |
|---|---|---|---|---|
| `initial_state_1440x900.png` | PNG | 69,463 | Phase B1 (Privacy) | Browser view of application initial state at 1440x900 desktop viewport. Shows disabled "Analyze Contract" button prior to consent. |
| `initial_state.png` | PNG | 116,722 | Phase A (Inventory) | Full-height capture of initial Audit tab showing all controls, privacy banner, and contract input fields. |
| `privacy_acknowledged_1440x900.png` | PNG | 68,256 | Phase B1 (Privacy) | Browser view after checking privacy consent checkbox. Demonstrates dynamic UI state change. |
| `privacy_acknowledged.png` | PNG | 114,951 | Phase B1 (Privacy) | Full-height capture showing checked privacy consent state. |
| `file_selected_ready.png` | PNG | 68,510 | Phase B2 (Upload) | Browser view with `valid_multiclause.txt` attached via file input and valid API key entered. Analyze button is active. |
| `analysis_running.png` | PNG | 69,758 | Phase B3 (Analysis) | Real-time loading indicator and status spinner during active contract analysis polling. |
| `results_view_desktop.png` | PNG | 76,196 | Phase C (Results) | Browser view of completed analysis results. Displays KPI cards (5 clauses, 2 anomalies, 0.341 coherence) and clause table. |
| `rendered_kpi_values.json` | JSON | 141 | Phase C (Metrics) | Machine-readable dump of DOM `.kpi-value` text parsed during browser test session. |
| `xai_attribution_view.png` | PNG | 49,671 | Phase D (Explainability) | Browser view of Tab 3 showing 26 token attribution badges generated via Integrated Gradients. |
| `xai_sensitivity_view.png` | PNG | 59,840 | Phase D (Explainability) | Browser view of Tab 3 showing sensitivity perturbation delta (+0.0752) and context comparison table. |
| `feedback_view_before_submit.png` | PNG | 56,437 | Phase E (Feedback) | Browser view of Tab 4 showing clause selection dropdown and CONFIRM_ANOMALY verdict button selected. |
| `feedback_submitted_success.png` | PNG | 60,205 | Phase E (Feedback) | Browser view of Tab 4 showing green success confirmation banner following POST /v1/feedback/verdicts. |
| `transparency_tab.png` | PNG | 117,126 | Phase A (Tabs) | Browser view of Tab 5 ("Transparency") displaying system model architectures, weights provenance, and compliance disclaimers. |
| `desktop_1440x900.png` | PNG | 76,196 | Phase F (Viewports) | Desktop viewport (1440x900) layout verification. |
| `laptop_1024x768.png` | PNG | 66,509 | Phase F (Viewports) | Laptop viewport (1024x768) layout verification. |
| `tablet_768x1024.png` | PNG | 68,946 | Phase F (Viewports) | Tablet viewport (768x1024 portrait) layout verification. |
| `mobile_390x844.png` | PNG | 45,918 | Phase F (Viewports) | Mobile viewport (390x844 portrait) layout verification. |
| `browser_console_events.json` | JSON | 10,822 | Phase H (Console) | Full log of Chrome DevTools Protocol console events captured during browser automation. |
| `browser_network_requests.json` | JSON | 4,565 | Phase H (Network) | Sanitized HTTP request log across all browser user journeys (37 requests). |
| `browser_network_responses.json` | JSON | 4,460 | Phase H (Network) | Sanitized HTTP response status and header log across all browser user journeys. |

---

## Verification Statement

All 20 artifacts listed above were captured directly from the live browser session running against FastAPI (`http://127.0.0.1:8000`) and Next.js (`http://localhost:3000`) via Google Chrome DevTools Protocol WebSocket. No placeholder or simulated images are present.
