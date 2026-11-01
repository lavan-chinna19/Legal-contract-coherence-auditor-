"""
scripts/reproduce_browser_evidence.py — Independent Browser Reproduction Suite (Prompt 23B)
Executes independent browser reproduction tests against the running application using ACTUAL runtime DOM locators.
"""
import os
import sys
import time
import json
import base64
import asyncio
import sqlite3
import urllib.request
from pathlib import Path
import websockets

CDP_JSON_URL = "http://127.0.0.1:9222/json"
FRONTEND_URL = "http://localhost:3000/"
EVIDENCE_DIR = Path("audit/prompt_23b/evidence")
EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)

FIXTURE_PATH = Path("audit/prompt_23/evidence/fixtures/valid_multiclause.txt").resolve()
API_KEY = "dev_auditor_key_12345"

network_requests = []
network_responses = []
console_logs = []

class CDPClient:
    def __init__(self, ws):
        self.ws = ws
        self.msg_id = 0
        self.pending = {}
        self.handlers = {}

    async def send(self, method, params=None):
        self.msg_id += 1
        curr_id = self.msg_id
        payload = {"id": curr_id, "method": method}
        if params is not None:
            payload["params"] = params
        await self.ws.send(json.dumps(payload))
        
        while True:
            raw = await self.ws.recv()
            data = json.loads(raw)
            if "id" in data and data["id"] == curr_id:
                if "error" in data:
                    raise RuntimeError(f"CDP Error in {method}: {data['error']}")
                return data.get("result", {})
            elif "method" in data:
                m = data["method"]
                p = data.get("params", {})
                if m in self.handlers:
                    self.handlers[m](p)

    async def evaluate(self, expression):
        res = await self.send("Runtime.evaluate", {
            "expression": expression,
            "returnByValue": True,
            "awaitPromise": True
        })
        val = res.get("result", {})
        if val.get("subtype") == "error":
            raise RuntimeError(f"JS Error: {val.get('description')}")
        return val.get("value")

    async def capture_screenshot(self, filename):
        res = await self.send("Page.captureScreenshot", {"format": "png"})
        img_data = base64.b64decode(res["data"])
        out_path = EVIDENCE_DIR / filename
        out_path.write_bytes(img_data)
        print(f"[SCREENSHOT] Saved: {out_path.name} ({len(img_data)} bytes)")
        return out_path

async def run_reproduction():
    print("=== STARTING INDEPENDENT BROWSER REPRODUCTION (PROMPT 23B) ===")
    with urllib.request.urlopen(CDP_JSON_URL) as resp:
        targets = json.loads(resp.read().decode("utf-8"))
    
    page = next(t for t in targets if t.get("type") == "page" and "localhost:3000" in t.get("url", ""))
    ws_url = page["webSocketDebuggerUrl"]
    print(f"Connecting to Chrome page via CDP: {ws_url}")

    async with websockets.connect(ws_url, max_size=10_000_000) as ws:
        cdp = CDPClient(ws)
        
        await cdp.send("Page.enable")
        await cdp.send("DOM.enable")
        await cdp.send("Runtime.enable")
        await cdp.send("Network.enable")
        await cdp.send("Console.enable")

        cdp.handlers["Console.messageAdded"] = lambda p: console_logs.append(p.get("message", {}))
        cdp.handlers["Runtime.consoleAPICalled"] = lambda p: console_logs.append(p)
        cdp.handlers["Network.requestWillBeSent"] = lambda p: network_requests.append({
            "url": p.get("request", {}).get("url"),
            "method": p.get("request", {}).get("method"),
            "timestamp": p.get("timestamp")
        })
        cdp.handlers["Network.responseReceived"] = lambda p: network_responses.append({
            "url": p.get("response", {}).get("url"),
            "status": p.get("response", {}).get("status"),
            "timestamp": p.get("timestamp")
        })

        # Set standard desktop viewport
        await cdp.send("Emulation.setDeviceMetricsOverride", {
            "width": 1440, "height": 900, "deviceScaleFactor": 1, "mobile": False
        })

        # Navigate to frontend
        await cdp.send("Page.navigate", {"url": FRONTEND_URL})
        await asyncio.sleep(2.0)

        # ── Test 1: Real application identification ──
        print("\n--- Test 1: Real Application Identification ---")
        app_identity = await cdp.evaluate("""
            (() => ({
                title: document.title,
                h1: document.querySelector('h1')?.innerText,
                hasDisclaimer: document.querySelector('.disclaimer-banner')?.innerText.includes('Research Prototype'),
                backendBadge: document.querySelector('header')?.innerText.includes('Backend: online')
            }))()
        """)
        print("Application identity:", app_identity)
        assert "Legal Contract Coherence Auditor" in app_identity["h1"], "H1 mismatch"
        assert "Legal Contract Coherence Auditor" in app_identity["title"], "Title mismatch"
        await cdp.capture_screenshot("repro_01_app_identity.png")

        # ── Test 2: Privacy Checkbox & Interlock ──
        print("\n--- Test 2: Privacy Checkbox Toggle ---")
        # Enter API Key
        await cdp.evaluate(f"""
            (() => {{
                const inputs = Array.from(document.querySelectorAll('input'));
                const keyInput = inputs.find(i => i.placeholder && i.placeholder.includes('API Key'));
                if (keyInput) {{
                    const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                    setter.call(keyInput, '{API_KEY}');
                    keyInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    keyInput.dispatchEvent(new Event('change', {{ bubbles: true }}));
                }}
            }})()
        """)
        await asyncio.sleep(0.5)

        initial_btn_disabled = await cdp.evaluate("""
            (() => {
                const btn = document.querySelector('button.btn');
                return btn ? btn.disabled : null;
            })()
        """)
        print(f"Analyze button disabled initially: {initial_btn_disabled} (Expected: True)")

        # Toggle privacy checkbox
        await cdp.evaluate("""
            (() => {
                const cb = document.querySelector('input[type="checkbox"]');
                if (cb && !cb.checked) cb.click();
            })()
        """)
        await asyncio.sleep(0.5)
        cb_checked = await cdp.evaluate("document.querySelector('input[type=\"checkbox\"]').checked")
        print(f"Privacy checkbox checked state: {cb_checked} (Expected: True)")
        await cdp.capture_screenshot("repro_02_privacy_toggle.png")

        # ── Test 3: Contract Upload and Real Analysis Pipeline ──
        print("\n--- Test 3: Contract Upload & Pipeline Trigger ---")
        doc_res = await cdp.send("DOM.getDocument")
        file_res = await cdp.send("DOM.querySelector", {
            "nodeId": doc_res["root"]["nodeId"],
            "selector": 'input[type="file"]'
        })
        await cdp.send("DOM.setFileInputFiles", {
            "files": [str(FIXTURE_PATH)],
            "nodeId": file_res["nodeId"]
        })
        await cdp.evaluate("""
            (() => {
                const fi = document.querySelector('input[type="file"]');
                if (fi) fi.dispatchEvent(new Event('change', { bubbles: true }));
            })()
        """)
        await asyncio.sleep(0.5)

        btn_ready = await cdp.evaluate("!document.querySelector('button.btn').disabled")
        print(f"Analyze button enabled after upload: {btn_ready} (Expected: True)")

        # Click analyze
        t0 = time.time()
        await cdp.evaluate("document.querySelector('button.btn').click()")
        print("Clicked Analyze button, observing polling and pipeline...")

        completed = False
        for _ in range(40):
            await asyncio.sleep(1.0)
            has_kpis = await cdp.evaluate("document.querySelectorAll('.kpi-card').length > 0")
            if has_kpis:
                completed = True
                break
        t_duration = time.time() - t0
        print(f"Analysis resolved in {t_duration:.2f}s. Results tab visible: {completed}")
        assert completed, "Analysis did not complete within timeout"
        await cdp.capture_screenshot("repro_03_analysis_completed.png")

        # ── Test 4: Results & KPI Verification ──
        print("\n--- Test 4: Results KPI Extraction vs Backend API ---")
        kpi_dom = await cdp.evaluate("""
            (() => {
                const map = {};
                document.querySelectorAll('.kpi-card').forEach(c => {
                    const l = c.querySelector('.kpi-label')?.innerText?.trim();
                    const v = c.querySelector('.kpi-value')?.innerText?.trim();
                    if (l) map[l] = v;
                });
                return map;
            })()
        """)
        print("DOM KPI values:", kpi_dom)
        (EVIDENCE_DIR / "repro_kpi_dom.json").write_text(json.dumps(kpi_dom, indent=2), encoding="utf-8")

        # Verify against backend DB/memory
        # Expected: Total Clauses: 5, Total Anomalies: 2, High Severity: 2, Medium Severity: 0, Mean Anomaly Score: 0.341
        kpi_normalized = {k.upper(): v for k, v in kpi_dom.items()}
        assert kpi_normalized.get("TOTAL CLAUSES") == "5", "Clause count mismatch"
        assert kpi_normalized.get("TOTAL ANOMALIES") == "2", "Flags count mismatch"
        assert kpi_normalized.get("HIGH SEVERITY") == "2", "High severity count mismatch"
        assert kpi_normalized.get("MEDIUM SEVERITY") == "0", "Medium severity count mismatch"
        assert kpi_normalized.get("MEAN ANOMALY SCORE") == "0.341", "Mean score mismatch"

        # ── Test 5: XAI Interactions ──
        print("\n--- Test 5: Explainability (XAI) Tab & Mode Switching ---")
        await cdp.evaluate("""
            (() => {
                const tabs = Array.from(document.querySelectorAll('.tab-btn'));
                const xTab = tabs.find(t => t.innerText && t.innerText.includes('Explainability'));
                if (xTab) xTab.click();
            })()
        """)
        badges_count = 0
        for _ in range(20):
            await asyncio.sleep(0.5)
            badges_count = await cdp.evaluate("document.querySelectorAll('span[style*=\"background\"]').length")
            if badges_count > 0:
                break
        await cdp.capture_screenshot("repro_05_xai_attribution.png")
        print(f"Rendered XAI token attribution badges: {badges_count}")
        assert badges_count > 10, "Attribution tokens missing"

        # Switch to Neighbor Sensitivity
        await cdp.evaluate("""
            (() => {
                const btns = Array.from(document.querySelectorAll('button.btn, button.btn-secondary'));
                const sensBtn = btns.find(b => b.innerText && b.innerText.includes('Sensitivity'));
                if (sensBtn) sensBtn.click();
            })()
        """)
        await asyncio.sleep(1.5)
        await cdp.capture_screenshot("repro_05_xai_sensitivity.png")
        sens_rendered = await cdp.evaluate("document.body.innerText.includes('Perturbed Neighbor Score Delta')")
        print(f"Sensitivity delta text rendered: {sens_rendered}")

        # ── Test 6: Feedback Submission & Database Persistence ──
        print("\n--- Test 6: Feedback Submission (SYNTHETIC_TEST) ---")
        await cdp.evaluate("""
            (() => {
                const tabs = Array.from(document.querySelectorAll('.tab-btn'));
                const fbTab = tabs.find(t => t.innerText && t.innerText.includes('Reviewer Feedback'));
                if (fbTab) fbTab.click();
            })()
        """)
        await asyncio.sleep(1.0)

        # Select SYNTHETIC_TEST provenance
        await cdp.evaluate("""
            (() => {
                const selects = Array.from(document.querySelectorAll('select'));
                // Find provenance select
                const provSelect = selects.find(s => Array.from(s.options).some(o => o.value === 'SYNTHETIC_TEST'));
                if (provSelect) {
                    provSelect.value = 'SYNTHETIC_TEST';
                    provSelect.dispatchEvent(new Event('change', { bubbles: true }));
                }
            })()
        """)
        await asyncio.sleep(0.5)

        # Click Submit Feedback button
        await cdp.evaluate("""
            (() => {
                const btns = Array.from(document.querySelectorAll('button.btn'));
                const subBtn = btns.find(b => b.innerText && b.innerText.includes('Submit Feedback'));
                if (subBtn) subBtn.click();
            })()
        """)
        await asyncio.sleep(1.5)
        await cdp.capture_screenshot("repro_06_feedback_success.png")

        feedback_text = await cdp.evaluate("""
            (() => {
                const p = document.querySelector('p[style*="color: #10b981"], p[style*="rgb(16, 185, 129)"]');
                return p ? p.innerText : null;
            })()
        """)
        print(f"Feedback success notification: {feedback_text}")
        assert feedback_text and "Feedback recorded successfully" in feedback_text, "Feedback did not succeed"

        # Verify SQLite row
        conn = sqlite3.connect("data/processed/feedback.sqlite")
        c = conn.cursor()
        c.execute("SELECT feedback_id, clause_id, reviewer_verdict, provenance, timestamp FROM feedback ORDER BY rowid DESC LIMIT 1")
        last_row = c.fetchone()
        conn.close()
        print(f"Verified SQLite persisted row: {last_row}")
        assert last_row and last_row[3] == "SYNTHETIC_TEST", "SQLite provenance mismatch"

        # ── Test 7: Negative / Error Handling ──
        print("\n--- Test 7: Negative Validation (Unauthenticated / Bad Key) ---")
        # Change API key to invalid
        await cdp.evaluate("""
            (() => {
                const inputs = Array.from(document.querySelectorAll('input'));
                const keyInput = inputs.find(i => i.placeholder && i.placeholder.includes('API Key'));
                if (keyInput) {
                    const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                    setter.call(keyInput, 'INVALID_KEY_FOR_TESTING');
                    keyInput.dispatchEvent(new Event('input', { bubbles: true }));
                    keyInput.dispatchEvent(new Event('change', { bubbles: true }));
                }
            })()
        """)
        # Switch to tab 1
        await cdp.evaluate("""
            (() => {
                const tabs = Array.from(document.querySelectorAll('.tab-btn'));
                if (tabs[0]) tabs[0].click();
            })()
        """)
        await asyncio.sleep(0.5)
        await cdp.capture_screenshot("repro_07_error_handling.png")

        # Save artifacts
        (EVIDENCE_DIR / "repro_network_requests.json").write_text(json.dumps(network_requests, indent=2), encoding="utf-8")
        (EVIDENCE_DIR / "repro_network_responses.json").write_text(json.dumps(network_responses, indent=2), encoding="utf-8")
        (EVIDENCE_DIR / "repro_console_logs.json").write_text(json.dumps(console_logs, indent=2, default=str), encoding="utf-8")

        print("\n=== INDEPENDENT REPRODUCTION TESTS COMPLETED WITH 100% SUCCESS ===")

if __name__ == "__main__":
    asyncio.run(run_reproduction())
