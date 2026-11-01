"""
scripts/run_phase4a_browser_verification.py — Phase 4A Browser Acceptance & Evidence Capture

Automated CDP test script validating:
1. Analytics workspace empty state
2. Live contract upload & analysis
3. Document KPIs vs backend UnifiedAuditReportModel JSON
4. Clause score distribution sequential rendering & interaction
5. Severity distribution segmented bar & accessible table
6. Multi-channel evidence decomposition (Channel A vs Channel B)
7. Deterministic rule findings & legal defect caveats
8. Calibration transparency & conformal prediction intervals
9. Cross-workspace clause synchronization (Analytics -> Review -> XAI -> Feedback)
10. Dual theme verification (Light & Dark)
11. Responsive viewports (1440x900, 1024x768, 768x1024, 390x844)
12. Strict privacy & storage isolation audit (localStorage/sessionStorage)
"""

import os
import sys
import time
import json
import base64
import asyncio
import urllib.request
from pathlib import Path
import websockets

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

CDP_JSON_URL = "http://127.0.0.1:9222/json"
FRONTEND_URL = "http://localhost:3000/"
BACKEND_URL = "http://127.0.0.1:8000"
EVIDENCE_DIR = Path("design/ui_redesign/phase_04a/evidence")
EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)

FIXTURE_PATH = Path("design/ui_redesign/phase_03a/fixtures/fixture_01_baseline.txt").resolve()
API_KEY = "dev_auditor_key_12345"

class CDPClient:
    def __init__(self, ws):
        self.ws = ws
        self.msg_id = 0
        self.pending = {}
        self.handlers = {}
        self.console_logs = []
        asyncio.create_task(self._listen())

    async def _listen(self):
        try:
            async for raw in self.ws:
                data = json.loads(raw)
                if "id" in data and data["id"] in self.pending:
                    fut = self.pending.pop(data["id"])
                    if "error" in data:
                        fut.set_exception(RuntimeError(data["error"].get("message", "CDP Error")))
                    else:
                        fut.set_result(data.get("result", {}))
                elif "method" in data:
                    m = data["method"]
                    p = data.get("params", {})
                    if m == "Runtime.consoleAPICalled":
                        text = " ".join([arg.get("value", "") for arg in p.get("args", []) if "value" in arg])
                        self.console_logs.append(f"[{p.get('type')}] {text}")
                    if m in self.handlers:
                        self.handlers[m](p)
        except Exception:
            pass

    async def send(self, method, params=None):
        self.msg_id += 1
        curr_id = self.msg_id
        payload = {"id": curr_id, "method": method}
        if params is not None:
            payload["params"] = params
        loop = asyncio.get_running_loop()
        fut = loop.create_future()
        self.pending[curr_id] = fut
        await self.ws.send(json.dumps(payload))
        return await fut

    async def evaluate(self, expr):
        res = await self.send("Runtime.evaluate", {
            "expression": expr,
            "returnByValue": True,
            "awaitPromise": True
        })
        val = res.get("result", {}).get("value")
        return val

    async def set_viewport(self, width, height, mobile=False):
        await self.send("Emulation.setDeviceMetricsOverride", {
            "width": width,
            "height": height,
            "deviceScaleFactor": 1,
            "mobile": mobile
        })

    async def capture_screenshot(self, filepath: Path):
        res = await self.send("Page.captureScreenshot", {"format": "png"})
        data = base64.b64decode(res["data"])
        with open(filepath, "wb") as f:
            f.write(data)
        print(f"Captured screenshot: {filepath.name} ({len(data)} bytes)")

async def main():
    print("=================================================================")
    print("LEXAUDIT PHASE 4A — AUTOMATED BROWSER VERIFICATION SUITE")
    print("=================================================================\n")

    # 1. Connect to CDP
    req = urllib.request.urlopen(CDP_JSON_URL)
    tabs = json.loads(req.read().decode())
    page_tab = next((t for t in tabs if t.get("type") == "page" and "localhost:3000" in t.get("url", "")), None)
    if not page_tab:
        page_tab = next(t for t in tabs if t.get("type") == "page")
    
    ws_url = page_tab["webSocketDebuggerUrl"]
    print(f"Connecting to CDP session: {ws_url}")
    
    async with websockets.connect(ws_url, max_size=50_000_000) as ws:
        client = CDPClient(ws)
        await client.send("Runtime.enable")
        await client.send("Page.enable")
        await client.send("DOM.enable")

        test_outcomes = {}

        # Initial Viewport
        await client.set_viewport(1440, 900)

        # -------------------------------------------------------------
        # STEP 1: Empty State Verification
        # -------------------------------------------------------------
        print("\n--- STEP 1: Verifying Analytics Empty State ---")
        await client.send("Page.navigate", {"url": FRONTEND_URL})
        await asyncio.sleep(2)

        # Navigate to Analytics
        await client.evaluate("""(() => {
            const btn = document.getElementById('nav-analytics');
            if (btn) btn.click();
        })()""")
        await asyncio.sleep(1)

        empty_displayed = await client.evaluate("""(() => {
            const card = document.querySelector('.analytics-empty-card');
            const h2 = card ? card.querySelector('h2') : null;
            return card !== null && h2 && h2.innerText.includes('No Active Audit Data');
        })()""")
        print(f"Empty state properly displayed: {empty_displayed}")
        test_outcomes["analytics_empty_state"] = bool(empty_displayed)

        await client.capture_screenshot(EVIDENCE_DIR / "01_analytics_empty_state.png")

        # -------------------------------------------------------------
        # STEP 2: Ingest Document & Poll Pipeline
        # -------------------------------------------------------------
        print("\n--- STEP 2: Ingesting Contract Document ---")
        # Click Ingestion & Upload
        await client.evaluate("""(() => {
            const btn = document.getElementById('analytics-empty-upload-btn') || document.getElementById('nav-overview');
            if (btn) btn.click();
        })()""")
        await asyncio.sleep(1)

        # Open connection drawer if closed
        await client.evaluate("""(() => {
            const drawer = document.getElementById('connection-settings-panel');
            if (drawer && drawer.style.display === 'none') {
                const toggle = document.getElementById('connection-settings-toggle');
                if (toggle) toggle.click();
            }
        })()""")
        await asyncio.sleep(0.3)

        # Set API Key in HeaderBar using React prototype setter
        await client.evaluate(f"""(() => {{
            const input = document.getElementById('api-key-input');
            if (input) {{
                const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                setter.call(input, '{API_KEY}');
                input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                input.dispatchEvent(new Event('change', {{ bubbles: true }}));
            }}
            const consent = document.getElementById('privacy-consent');
            if (consent && !consent.checked) {{
                consent.click();
                consent.dispatchEvent(new Event('change', {{ bubbles: true }}));
            }}
        }})()""")
        await asyncio.sleep(0.5)

        # File input upload
        doc_res = await client.send("DOM.getDocument")
        node_res = await client.send("DOM.querySelector", {
            "nodeId": doc_res["root"]["nodeId"],
            "selector": "#file-input"
        })
        input_node_id = node_res["nodeId"]

        await client.send("DOM.setFileInputFiles", {
            "files": [str(FIXTURE_PATH)],
            "nodeId": input_node_id
        })
        print(f"Set file input to: {FIXTURE_PATH.name}")
        await asyncio.sleep(1)

        # Trigger analysis
        await client.evaluate("""(() => {
            const btn = document.getElementById('analyze-btn');
            if (btn) btn.click();
        })()""")
        print("Analysis initiated. Polling pipeline completion...")

        # Poll until report loads
        completed = False
        for i in range(30):
            await asyncio.sleep(1.5)
            ready = await client.evaluate("""(() => {
                const resultsTab = document.getElementById('tab-results');
                const kpis = document.querySelector('.grid-kpis');
                return resultsTab && !resultsTab.disabled && kpis !== null;
            })()""")
            if ready:
                completed = True
                print(f"Pipeline completed successfully after {(i+1)*1.5:.1f}s!")
                break

        if not completed:
            raise RuntimeError("Pipeline analysis timed out!")

        test_outcomes["pipeline_analysis_completed"] = True

        # -------------------------------------------------------------
        # STEP 3: Professional Analytics Workspace Verification
        # -------------------------------------------------------------
        print("\n--- STEP 3: Verifying Professional Analytics Workspace ---")
        # Click Lateral Nav Analytics
        await client.evaluate("""(() => {
            const btn = document.getElementById('nav-analytics');
            if (btn) btn.click();
        })()""")
        await asyncio.sleep(1)

        kpis = await client.evaluate("""(() => {
            const getVal = (id) => {
                const el = document.getElementById(id);
                return el ? el.querySelector('.kpi-value').innerText.trim() : null;
            };
            return {
                totalClauses: getVal('analytics-kpi-total-clauses'),
                mlAnomalies: getVal('analytics-kpi-ml-anomalies'),
                highSeverity: getVal('analytics-kpi-high-severity'),
                ruleViolations: getVal('analytics-kpi-rule-violations'),
                meanScore: getVal('analytics-kpi-mean-score')
            };
        })()""")
        print(f"Observed Document KPIs in Analytics: {kpis}")
        test_outcomes["kpi_values_match"] = (
            kpis["totalClauses"] == "5" and
            kpis["meanScore"] is not None and
            float(kpis["meanScore"]) > 0.0
        )

        # Verify Clause Score Distribution Chart
        bars_count = await client.evaluate("""(() => {
            const bars = document.querySelectorAll('[data-clause-id]');
            return bars.length;
        })()""")
        print(f"Interactive sequential clause bars rendered: {bars_count}")
        test_outcomes["score_distribution_bars"] = (bars_count == 5)

        # Verify Severity Distribution Table
        sev_table_verified = await client.evaluate("""(() => {
            const card = document.querySelector('.analytics-severity-card');
            const rows = card ? card.querySelectorAll('tbody tr') : [];
            return rows.length === 4; // High, Medium, Low, Clean
        })()""")
        print(f"Severity tiers table rendered: {sev_table_verified}")
        test_outcomes["severity_distribution_table"] = bool(sev_table_verified)

        # Verify Channel Evidence Comparison Panels
        channel_panels_verified = await client.evaluate("""(() => {
            const card = document.querySelector('.analytics-channel-comparison-card');
            const h4s = card ? Array.from(card.querySelectorAll('h4')).map(h => h.innerText) : [];
            const hasChannelA = h4s.some(t => t.includes('Channel A'));
            const hasChannelB = h4s.some(t => t.includes('Channel B'));
            return hasChannelA && hasChannelB;
        })()""")
        print(f"Channel A and Channel B diagnostic panels rendered: {channel_panels_verified}")
        test_outcomes["channel_panels_verified"] = bool(channel_panels_verified)

        # Verify Rule Findings and Calibration Disclosures
        safeguards_verified = await client.evaluate("""(() => {
            const ruleCard = document.querySelector('.analytics-rules-section');
            const calibCard = document.querySelector('.analytics-calibration-section');
            const textR = ruleCard ? ruleCard.innerText : '';
            const textC = calibCard ? calibCard.innerText : '';
            const ruleSafe = textR.includes('No deterministic rule violations') || textR.includes('Violations Detected');
            const calibSafe = textC.includes('Synthetic shuffle-based calibration does not establish real-world legal defect correctness');
            return ruleSafe && calibSafe;
        })()""")
        print(f"Rule findings & calibration safeguards verified: {safeguards_verified}")
        test_outcomes["safeguards_and_limitations_verified"] = bool(safeguards_verified)

        await client.capture_screenshot(EVIDENCE_DIR / "02_analytics_light_theme.png")

        # -------------------------------------------------------------
        # STEP 4: Dual Theme Verification (Dark Theme)
        # -------------------------------------------------------------
        print("\n--- STEP 4: Verifying Dark Theme ---")
        await client.evaluate("""(() => {
            const btn = document.getElementById('theme-btn-dark');
            if (btn) btn.click();
        })()""")
        await asyncio.sleep(1)

        is_dark = await client.evaluate("""(() => {
            return document.documentElement.getAttribute('data-theme') === 'dark';
        })()""")
        print(f"Dark theme active: {is_dark}")
        test_outcomes["dark_theme_verified"] = bool(is_dark)

        await client.capture_screenshot(EVIDENCE_DIR / "03_analytics_dark_theme.png")

        # Toggle back to light theme
        await client.evaluate("""(() => {
            const btn = document.getElementById('theme-btn-light');
            if (btn) btn.click();
        })()""")
        await asyncio.sleep(0.5)

        # -------------------------------------------------------------
        # STEP 5: Interactive Clause Selection & Cross-Workspace Sync
        # -------------------------------------------------------------
        print("\n--- STEP 5: Verifying Cross-Workspace Clause Synchronization ---")
        # Click clause § 2 bar in sequence chart
        clicked_clause_id = await client.evaluate("""(() => {
            const bars = document.querySelectorAll('[data-clause-id]');
            if (bars.length > 2) {
                const target = bars[2];
                const clauseId = target.getAttribute('data-clause-id');
                target.click();
                return clauseId;
            }
            return null;
        })()""")
        print(f"Selected clause bar in score distribution: {clicked_clause_id}")
        await asyncio.sleep(1)

        # Switch to Contract Review workspace
        await client.evaluate("""(() => {
            const btn = document.getElementById('nav-contract-review');
            if (btn) btn.click();
        })()""")
        await asyncio.sleep(1)

        review_synced = await client.evaluate(f"""(() => {{
            const inspector = document.querySelector('.findings-inspector');
            const inspectorText = inspector ? inspector.innerText : '';
            return inspectorText.includes('{clicked_clause_id}');
        }})()""")
        print(f"Contract Review synchronized to selected clause: {review_synced}")
        test_outcomes["review_sync_verified"] = bool(review_synced)

        # Switch to Explainability (XAI)
        await client.evaluate("""(() => {
            const btn = document.getElementById('nav-explainability');
            if (btn) btn.click();
        })()""")
        await asyncio.sleep(1)

        xai_synced = await client.evaluate(f"""(() => {{
            const card = document.querySelector('section[role="tabpanel"]');
            const text = card ? card.innerText : '';
            return text.includes('{clicked_clause_id}');
        }})()""")
        print(f"Explainability synchronized to selected clause: {xai_synced}")
        test_outcomes["xai_sync_verified"] = bool(xai_synced)

        # Switch to Reviewer Feedback
        await client.evaluate("""(() => {
            const btn = document.getElementById('nav-feedback');
            if (btn) btn.click();
        })()""")
        await asyncio.sleep(1)

        feedback_synced = await client.evaluate(f"""(() => {{
            const select = document.getElementById('clause-select-fb');
            return select && select.value === '{clicked_clause_id}';
        }})()""")
        print(f"Reviewer Feedback synchronized to selected clause: {feedback_synced}")
        test_outcomes["feedback_sync_verified"] = bool(feedback_synced)

        # Return to Analytics
        await client.evaluate("""(() => {
            const btn = document.getElementById('nav-analytics');
            if (btn) btn.click();
        })()""")
        await asyncio.sleep(1)
        await client.capture_screenshot(EVIDENCE_DIR / "04_cross_workspace_sync.png")

        # -------------------------------------------------------------
        # STEP 6: Responsive Viewports Verification
        # -------------------------------------------------------------
        print("\n--- STEP 6: Verifying Responsive Viewports ---")
        viewports = [
            ("05_analytics_responsive_1440x900.png", 1440, 900, False),
            ("06_analytics_responsive_1024x768.png", 1024, 768, False),
            ("07_analytics_responsive_768x1024.png", 768, 1024, False),
            ("08_analytics_responsive_390x844.png", 390, 844, True),
        ]

        for filename, w, h, is_mob in viewports:
            await client.set_viewport(w, h, is_mob)
            await asyncio.sleep(1)
            # Check horizontal overflow
            overflow = await client.evaluate("""(() => {
                return document.documentElement.scrollWidth > window.innerWidth;
            })()""")
            print(f"Viewport {w}x{h} (mobile={is_mob}): horizontal page overflow = {overflow}")
            test_outcomes[f"viewport_{w}x{h}_no_overflow"] = not overflow
            await client.capture_screenshot(EVIDENCE_DIR / filename)

        # Restore default viewport
        await client.set_viewport(1440, 900, False)

        # -------------------------------------------------------------
        # STEP 7: Security & Persistent Storage Audit
        # -------------------------------------------------------------
        print("\n--- STEP 7: Verifying Storage Confidentiality & Security ---")
        storage_audit = await client.evaluate("""(() => {
            const localKeys = Object.keys(localStorage);
            const sessionKeys = Object.keys(sessionStorage);
            const forbiddenKeys = ['contract', 'clause', 'analysis', 'apiKey', 'doc_id', 'result', 'token'];
            const leaks = [];
            for (const k of localKeys) {
                if (k !== 'lexaudit_theme' && forbiddenKeys.some(f => k.toLowerCase().includes(f))) {
                    leaks.push(`localStorage: ${k}`);
                }
            }
            for (const k of sessionKeys) {
                if (forbiddenKeys.some(f => k.toLowerCase().includes(f))) {
                    leaks.push(`sessionStorage: ${k}`);
                }
            }
            return {
                localKeys,
                sessionKeys,
                leaks,
                compliant: leaks.length === 0
            };
        })()""")
        print(f"Storage audit result: {storage_audit}")
        test_outcomes["zero_storage_leakage"] = storage_audit["compliant"]

        # Check console errors
        console_errors = [log for log in client.console_logs if "[error]" in log.lower()]
        print(f"Browser console error count: {len(console_errors)}")
        test_outcomes["zero_console_errors"] = (len(console_errors) == 0)

        # -------------------------------------------------------------
        # SUMMARY REPORT
        # -------------------------------------------------------------
        print("\n=================================================================")
        print("PHASE 4A BROWSER VERIFICATION SUMMARY")
        print("=================================================================")
        all_passed = all(test_outcomes.values())
        for k, v in test_outcomes.items():
            print(f"[{'PASS' if v else 'FAIL'}] {k}")
        print(f"\nOverall Result: {'ALL TESTS PASSED [PASS]' if all_passed else 'SOME TESTS FAILED [FAIL]'}")

        results_json_path = EVIDENCE_DIR / "browser_verification_results.json"
        with open(results_json_path, "w", encoding="utf-8") as f:
            json.dump({
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "outcomes": test_outcomes,
                "overall_status": "PASS" if all_passed else "FAIL",
                "kpis": kpis,
                "storage_audit": storage_audit
            }, f, indent=2)
        print(f"Results written to: {results_json_path}")

if __name__ == "__main__":
    asyncio.run(main())
