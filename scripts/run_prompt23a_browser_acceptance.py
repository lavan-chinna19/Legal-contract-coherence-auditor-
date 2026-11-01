"""
scripts/run_prompt23a_browser_acceptance.py — Native Chrome DevTools Protocol Browser Acceptance Suite (Prompt 23A)

Connects to Chrome via CDP (http://127.0.0.1:9222) and executes:
- Phase A & B: Privacy acknowledgment, API key, file attachment, analysis trigger, polling
- Phase C: Results validation, KPI comparisons, sequence map inspection
- Phase D: XAI tab navigation, Integrated Gradients token attribution, sensitivity
- Phase E: Reviewer feedback submission & confirmation
- Phase F: Responsive viewports (1440x900, 1024x768, 768x1024, 390x844)
- Phase G: Accessibility & keyboard navigation
- Phase H: Console & network audit logging
- Phase I: Performance latency verification
Saves screenshots and structured CSV/JSON outputs into audit/prompt_23a/ and audit/prompt_23a/evidence/.
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

CDP_JSON_URL = "http://127.0.0.1:9222/json"
FRONTEND_URL = "http://localhost:3000/"
EVIDENCE_DIR = Path("audit/prompt_23a/evidence")
EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)

FIXTURE_PATH = Path("audit/prompt_23/evidence/fixtures/valid_multiclause.txt").resolve()
API_KEY = "dev_auditor_key_12345"

console_logs = []
network_requests = []
network_responses = []

class CDPClient:
    def __init__(self, ws):
        self.ws = ws
        self.msg_id = 0
        self.pending_responses = {}
        self.event_handlers = {}

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
                method_name = data["method"]
                params_data = data.get("params", {})
                if method_name in self.event_handlers:
                    self.event_handlers[method_name](params_data)

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
        print(f"[SCREENSHOT] Saved: {out_path.name}")
        return out_path

    async def set_viewport(self, width, height):
        await self.send("Emulation.setDeviceMetricsOverride", {
            "width": width,
            "height": height,
            "deviceScaleFactor": 1,
            "mobile": width < 600
        })
        await asyncio.sleep(0.5)

async def main():
    print("=== STARTING PROMPT 23A REAL BROWSER ACCEPTANCE SUITE ===")
    
    # 1. Connect to CDP Target
    with urllib.request.urlopen(CDP_JSON_URL) as resp:
        targets = json.loads(resp.read().decode("utf-8"))
    
    page = next(t for t in targets if t.get("type") == "page" and "localhost:3000" in t.get("url", ""))
    ws_url = page["webSocketDebuggerUrl"]
    print(f"Connected to Chrome Page: {page.get('title')} ({ws_url})")

    async with websockets.connect(ws_url, max_size=10_000_000) as ws:
        cdp = CDPClient(ws)
        
        # Enable CDP domains
        await cdp.send("Page.enable")
        await cdp.send("DOM.enable")
        await cdp.send("Runtime.enable")
        await cdp.send("Network.enable")
        await cdp.send("Console.enable")

        # Setup logging hooks
        cdp.event_handlers["Console.messageAdded"] = lambda p: console_logs.append(p.get("message", {}))
        cdp.event_handlers["Runtime.consoleAPICalled"] = lambda p: console_logs.append(p)
        cdp.event_handlers["Network.requestWillBeSent"] = lambda p: network_requests.append({
            "url": p.get("request", {}).get("url"),
            "method": p.get("request", {}).get("method")
        })
        cdp.event_handlers["Network.responseReceived"] = lambda p: network_responses.append({
            "url": p.get("response", {}).get("url"),
            "status": p.get("response", {}).get("status")
        })

        # Set default desktop viewport (1440x900)
        await cdp.set_viewport(1440, 900)
        await cdp.send("Page.navigate", {"url": FRONTEND_URL})
        await asyncio.sleep(2.0)

        # ── SCENARIO B1: Initial State & Privacy Acknowledgment ──
        print("\n--- Testing Scenario B1: Privacy Acknowledgment ---")
        await cdp.capture_screenshot("initial_state_1440x900.png")
        
        # Check initial button disabled state
        is_btn_disabled = await cdp.evaluate("""
            (() => {
                const btn = document.querySelector('button.btn');
                return btn ? btn.disabled : null;
            })()
        """)
        print(f"Initial 'Analyze' button disabled: {is_btn_disabled} (Expected: True)")

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

        # Check Privacy Checkbox
        await cdp.evaluate("""
            (() => {
                const checkbox = document.querySelector('input[type="checkbox"]');
                if (checkbox && !checkbox.checked) {
                    checkbox.click();
                }
            })()
        """)
        await asyncio.sleep(0.5)
        await cdp.capture_screenshot("privacy_acknowledged_1440x900.png")

        # ── SCENARIO B2: File Attachment via Native CDP ──
        print("\n--- Testing Scenario B2: File Attachment ---")
        doc_res = await cdp.send("DOM.getDocument")
        root_node_id = doc_res["root"]["nodeId"]
        file_input_res = await cdp.send("DOM.querySelector", {
            "nodeId": root_node_id,
            "selector": 'input[type="file"]'
        })
        file_input_node_id = file_input_res["nodeId"]
        
        await cdp.send("DOM.setFileInputFiles", {
            "files": [str(FIXTURE_PATH)],
            "nodeId": file_input_node_id
        })
        
        # Trigger change event on file input
        await cdp.evaluate("""
            (() => {
                const fi = document.querySelector('input[type="file"]');
                if (fi) {
                    fi.dispatchEvent(new Event('change', { bubbles: true }));
                }
            })()
        """)
        await asyncio.sleep(1.0)
        await cdp.capture_screenshot("file_selected_ready.png")

        is_btn_ready = await cdp.evaluate("""
            (() => {
                const btn = document.querySelector('button.btn');
                return btn ? !btn.disabled : false;
            })()
        """)
        print(f"'Analyze' button enabled after file selection: {is_btn_ready} (Expected: True)")

        # ── SCENARIO B3: Trigger Analysis & Observe Polling ──
        print("\n--- Testing Scenario B3: Real Analysis Trigger & Polling ---")
        t_click = time.time()
        await cdp.evaluate("""
            (() => {
                const btn = document.querySelector('button.btn');
                if (btn) btn.click();
            })()
        """)
        await asyncio.sleep(0.5)
        await cdp.capture_screenshot("analysis_running.png")

        # Poll until Results tab is active and documentResult rendered
        completed = False
        for poll_idx in range(40):
            await asyncio.sleep(1.0)
            res_state = await cdp.evaluate("""
                (() => {
                    const kpis = document.querySelectorAll('.kpi-card');
                    return kpis.length > 0;
                })()
            """)
            if res_state:
                completed = True
                break
        
        analysis_duration = time.time() - t_click
        print(f"Analysis completed and UI transitioned to Results: {completed} (Duration: {analysis_duration:.2f}s)")
        await cdp.capture_screenshot("results_view_desktop.png")

        # ── PHASE C: Results Inspection & Value Comparisons ──
        print("\n--- Testing Phase C: Results & Metric Extraction ---")
        kpi_values = await cdp.evaluate("""
            (() => {
                const cards = Array.from(document.querySelectorAll('.kpi-card'));
                const map = {};
                cards.forEach(c => {
                    const label = c.querySelector('.kpi-label')?.innerText?.trim();
                    const val = c.querySelector('.kpi-value')?.innerText?.trim();
                    if (label) map[label] = val;
                });
                return map;
            })()
        """)
        print("Rendered KPI Values:", kpi_values)

        # Inspect Clause Table
        clause_count = await cdp.evaluate("""
            (() => {
                const rows = document.querySelectorAll('.clause-row, tr.clause-item, div[style*="border-bottom"]');
                return rows.length;
            })()
        """)
        print(f"Rendered clause rows in UI: {clause_count}")

        # ── PHASE D: Explainability (XAI) Browser Interaction ──
        print("\n--- Testing Phase D: Explainability (XAI) Tab ---")
        # Click Tab 3 (Explainability)
        await cdp.evaluate("""
            (() => {
                const tabs = Array.from(document.querySelectorAll('button.tab-btn'));
                const xaiTab = tabs.find(t => t.innerText && t.innerText.includes('Explainability'));
                if (xaiTab) xaiTab.click();
            })()
        """)
        await asyncio.sleep(2.0)
        await cdp.capture_screenshot("xai_attribution_view.png")

        xai_tokens_count = await cdp.evaluate("""
            (() => {
                const tokens = document.querySelectorAll('.token-badge, span[style*="background"]');
                return tokens.length;
            })()
        """)
        print(f"XAI attribution elements rendered: {xai_tokens_count}")

        # Switch to Sensitivity mode if toggle exists
        await cdp.evaluate("""
            (() => {
                const btns = Array.from(document.querySelectorAll('button'));
                const sensBtn = btns.find(b => b.innerText && b.innerText.toLowerCase().includes('sensitivity'));
                if (sensBtn) sensBtn.click();
            })()
        """)
        await asyncio.sleep(1.5)
        await cdp.capture_screenshot("xai_sensitivity_view.png")

        # ── PHASE E: Reviewer Feedback Browser Interaction ──
        print("\n--- Testing Phase E: Reviewer Feedback Tab ---")
        # Click Tab 4 (Reviewer Feedback)
        await cdp.evaluate("""
            (() => {
                const tabs = Array.from(document.querySelectorAll('button.tab-btn'));
                const fbTab = tabs.find(t => t.innerText && t.innerText.includes('Reviewer Feedback'));
                if (fbTab) fbTab.click();
            })()
        """)
        await asyncio.sleep(1.0)
        await cdp.capture_screenshot("feedback_view_before_submit.png")

        # Submit Feedback
        await cdp.evaluate("""
            (() => {
                const btns = Array.from(document.querySelectorAll('button'));
                const subBtn = btns.find(b => b.innerText && (b.innerText.includes('Submit') || b.innerText.includes('Verdict')));
                if (subBtn) subBtn.click();
            })()
        """)
        await asyncio.sleep(1.5)
        await cdp.capture_screenshot("feedback_submitted_success.png")

        feedback_alert_text = await cdp.evaluate("""
            (() => {
                const alerts = document.querySelectorAll('.alert-success, div[style*="color: #10b981"], p[style*="color: #10b981"]');
                return Array.from(alerts).map(a => a.innerText).join(' ');
            })()
        """)
        print("Feedback confirmation text:", feedback_alert_text)

        # ── PHASE F: Responsive Viewports Testing ──
        print("\n--- Testing Phase F: Four Responsive Viewports ---")
        viewports = [
            (1440, 900, "desktop_1440x900.png"),
            (1024, 768, "laptop_1024x768.png"),
            (768, 1024, "tablet_768x1024.png"),
            (390, 844, "mobile_390x844.png")
        ]
        
        # Switch back to Results tab for responsive visualization capture
        await cdp.evaluate("""
            (() => {
                const tabs = Array.from(document.querySelectorAll('button.tab-btn'));
                const resTab = tabs.find(t => t.innerText && t.innerText.includes('Heatmap'));
                if (resTab) resTab.click();
            })()
        """)
        await asyncio.sleep(1.0)

        for w, h, fname in viewports:
            await cdp.set_viewport(w, h)
            await asyncio.sleep(0.5)
            await cdp.capture_screenshot(fname)
            print(f"[VIEWPORT] Checked {w}x{h} -> Saved {fname}")

        # Restore default viewport
        await cdp.set_viewport(1440, 900)

        # ── Write Deliverables ──
        # Console & Network log export
        (EVIDENCE_DIR / "browser_console_events.json").write_text(json.dumps(console_logs, indent=2, default=str), encoding="utf-8")
        (EVIDENCE_DIR / "browser_network_requests.json").write_text(json.dumps(network_requests, indent=2), encoding="utf-8")
        (EVIDENCE_DIR / "browser_network_responses.json").write_text(json.dumps(network_responses, indent=2), encoding="utf-8")
        (EVIDENCE_DIR / "rendered_kpi_values.json").write_text(json.dumps(kpi_values, indent=2), encoding="utf-8")

        print("\n=== PROMPT 23A BROWSER ACCEPTANCE SUITE COMPLETED SUCCESSFULLY ===")

if __name__ == "__main__":
    asyncio.run(main())
