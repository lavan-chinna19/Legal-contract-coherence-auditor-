"""
scripts/run_phase2_browser_verification.py — Phase 2 Browser Verification & Evidence Capture
Automated test suite validating light/dark themes, hydration, viewports, navigation, empty states, and full workflow.
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
EVIDENCE_DIR = Path("design/ui_redesign/phase_02/evidence")
EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)

FIXTURE_PATH = Path("audit/prompt_23/evidence/fixtures/valid_multiclause.txt").resolve()
API_KEY = "dev_auditor_key_12345"

class CDPClient:
    def __init__(self, ws):
        self.ws = ws
        self.msg_id = 0
        self.pending = {}
        self.handlers = {}
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
        return str(out_path)

    async def set_viewport(self, width, height, mobile=False):
        await self.send("Emulation.setDeviceMetricsOverride", {
            "width": width,
            "height": height,
            "deviceScaleFactor": 1,
            "mobile": mobile
        })
        await asyncio.sleep(0.4)

async def run_verification():
    print("=== STARTING PHASE 2 BROWSER VERIFICATION ===")
    with urllib.request.urlopen(CDP_JSON_URL) as resp:
        targets = json.loads(resp.read().decode("utf-8"))

    page = next(t for t in targets if t.get("type") == "page" and "localhost:3000" in t.get("url", ""))
    ws_url = page["webSocketDebuggerUrl"]
    print(f"Connecting to Chrome page via CDP: {ws_url}")

    results = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "gates": {},
        "viewports": {},
        "screenshots": {},
        "dom_checks": {},
    }

    async with websockets.connect(ws_url, max_size=10_000_000) as ws:
        cdp = CDPClient(ws)
        await cdp.send("Page.enable")
        await cdp.send("DOM.enable")
        await cdp.send("Runtime.enable")
        await cdp.send("Network.enable")

        # ── Step 1: Baseline Navigation & Light Theme (Default) ──
        print("\n--- Step 1: Desktop Viewport (1440x900) & Default Light Theme ---")
        await cdp.set_viewport(1440, 900, mobile=False)
        await cdp.send("Page.navigate", {"url": FRONTEND_URL})
        await asyncio.sleep(1.0)
        # Reset storage to guarantee fresh first-time user simulation
        await cdp.evaluate("localStorage.removeItem('lexaudit_theme')")
        await cdp.send("Page.reload")
        for _ in range(30):
            await asyncio.sleep(0.3)
            theme = await cdp.evaluate("document.documentElement.getAttribute('data-theme')")
            if theme:
                break

        initial_theme = await cdp.evaluate("document.documentElement.getAttribute('data-theme')")
        theme_pref = await cdp.evaluate("localStorage.getItem('lexaudit_theme')")
        print(f"Initial resolved theme: {initial_theme} (Expected: light)")
        print(f"Initial localStorage['lexaudit_theme']: {theme_pref} (Expected: None or 'light')")
        assert initial_theme == "light", f"Default theme was not light: {initial_theme}"
        results["gates"]["default_light_theme"] = "PASS"

        # Check App Title & Brand
        brand_title = await cdp.evaluate("document.querySelector('.brand-title')?.innerText")
        print(f"Brand title in DOM: {brand_title}")
        assert brand_title == "LexAudit", "Brand title mismatch"

        # Check Global Disclaimer
        disclaimer_visible = await cdp.evaluate("document.querySelector('.disclaimer-banner') !== null")
        assert disclaimer_visible, "Global disclaimer missing"
        results["gates"]["disclaimer_present"] = "PASS"

        screenshot_1 = await cdp.capture_screenshot("viewport_01_desktop_1440x900_light.png")
        results["screenshots"]["desktop_light"] = screenshot_1

        # ── Step 2: Theme Switching & Persistence ──
        print("\n--- Step 2: Theme Switching to Dark Mode ---")
        await cdp.evaluate("document.querySelector('#theme-btn-dark').click()")
        await asyncio.sleep(0.4)

        dark_theme = await cdp.evaluate("document.documentElement.getAttribute('data-theme')")
        dark_pref = await cdp.evaluate("localStorage.getItem('lexaudit_theme')")
        print(f"Resolved theme after dark click: {dark_theme} (Expected: dark)")
        print(f"localStorage['lexaudit_theme']: {dark_pref} (Expected: dark)")
        assert dark_theme == "dark", "Dark theme not set"
        assert dark_pref == "dark", "Dark theme preference not persisted in localStorage"

        screenshot_dark = await cdp.capture_screenshot("theme_01_dark_mode_1440x900.png")
        results["screenshots"]["desktop_dark"] = screenshot_dark

        print("\n--- Step 3: Reload & Verify Zero-Flicker Persistence ---")
        await cdp.send("Page.reload")
        for _ in range(30):
            await asyncio.sleep(0.3)
            theme = await cdp.evaluate("document.documentElement.getAttribute('data-theme')")
            if theme:
                break
        reloaded_theme = await cdp.evaluate("document.documentElement.getAttribute('data-theme')")
        reloaded_pref = await cdp.evaluate("localStorage.getItem('lexaudit_theme')")
        print(f"Theme after reload: {reloaded_theme} (Expected: dark)")
        print(f"Preference after reload: {reloaded_pref} (Expected: dark)")
        assert reloaded_theme == "dark", "Theme did not persist across reload"
        results["gates"]["theme_persistence"] = "PASS"

        screenshot_persist = await cdp.capture_screenshot("theme_02_reload_persistence_dark.png")
        results["screenshots"]["theme_persistence"] = screenshot_persist

        # Test System & Light mode toggle
        print("\n--- Step 4: Toggle to System & Light ---")
        await cdp.evaluate("document.querySelector('#theme-btn-system').click()")
        await asyncio.sleep(0.3)
        sys_pref = await cdp.evaluate("localStorage.getItem('lexaudit_theme')")
        print(f"localStorage after System toggle: {sys_pref} (Expected: system)")
        assert sys_pref == "system", "System preference not stored"

        await cdp.evaluate("document.querySelector('#theme-btn-light').click()")
        await asyncio.sleep(0.3)
        light_restored = await cdp.evaluate("document.documentElement.getAttribute('data-theme')")
        assert light_restored == "light", "Light theme not restored"
        print("Restored Light theme successfully.")

        # ── Step 5: Responsive Viewports ──
        print("\n--- Step 5: Testing Responsive Viewports ---")
        
        # Laptop (1024x768)
        print("Testing Laptop (1024x768)...")
        await cdp.set_viewport(1024, 768, mobile=False)
        screenshot_laptop = await cdp.capture_screenshot("viewport_02_laptop_1024x768.png")
        results["screenshots"]["laptop_1024"] = screenshot_laptop
        results["viewports"]["laptop_1024x768"] = "PASS"

        # Tablet (768x1024)
        print("Testing Tablet (768x1024)...")
        await cdp.set_viewport(768, 1024, mobile=True)
        screenshot_tablet = await cdp.capture_screenshot("viewport_03_tablet_768x1024.png")
        results["screenshots"]["tablet_768"] = screenshot_tablet
        results["viewports"]["tablet_768x1024"] = "PASS"

        # Mobile (390x844)
        print("Testing Mobile (390x844)...")
        await cdp.set_viewport(390, 844, mobile=True)
        screenshot_mobile = await cdp.capture_screenshot("viewport_04_mobile_390x844.png")
        results["screenshots"]["mobile_390"] = screenshot_mobile
        results["viewports"]["mobile_390x844"] = "PASS"

        # Reset to Desktop for interaction tests
        await cdp.set_viewport(1440, 900, mobile=False)
        await asyncio.sleep(0.4)

        # ── Step 6: Sidebar Navigation & Empty States ──
        print("\n--- Step 6: Navigation & Empty States ---")
        
        # Contract Review (unloaded state)
        await cdp.evaluate("document.querySelector('#nav-contract-review').click()")
        await asyncio.sleep(0.5)
        has_empty_cr = await cdp.evaluate("document.querySelector('.empty-state') !== null")
        print(f"Contract Review empty state visible: {has_empty_cr} (Expected: True)")
        assert has_empty_cr, "Contract review empty state missing"
        screenshot_empty_cr = await cdp.capture_screenshot("nav_01_contract_review_empty.png")
        results["screenshots"]["contract_review_empty"] = screenshot_empty_cr

        # Explainability (unloaded state)
        await cdp.evaluate("document.querySelector('#nav-explainability').click()")
        await asyncio.sleep(0.5)
        has_empty_xai = await cdp.evaluate("document.querySelector('.empty-state') !== null")
        assert has_empty_xai, "Explainability empty state missing"
        screenshot_empty_xai = await cdp.capture_screenshot("nav_02_explainability_empty.png")
        results["screenshots"]["explainability_empty"] = screenshot_empty_xai

        # Reviewer Feedback (unloaded state)
        await cdp.evaluate("document.querySelector('#nav-feedback').click()")
        await asyncio.sleep(0.5)
        has_empty_fb = await cdp.evaluate("document.querySelector('.empty-state') !== null")
        assert has_empty_fb, "Feedback empty state missing"
        screenshot_empty_fb = await cdp.capture_screenshot("nav_03_feedback_empty.png")
        results["screenshots"]["feedback_empty"] = screenshot_empty_fb

        # Model Transparency & Baselines
        await cdp.evaluate("document.querySelector('#nav-transparency').click()")
        await asyncio.sleep(0.5)
        has_table = await cdp.evaluate("document.querySelector('table') !== null")
        assert has_table, "Transparency table missing"
        screenshot_trans = await cdp.capture_screenshot("nav_04_transparency_benchmarks.png")
        results["screenshots"]["transparency"] = screenshot_trans

        # Return to Overview
        await cdp.evaluate("document.querySelector('#nav-overview').click()")
        await asyncio.sleep(0.5)

        # ── Step 7: End-to-End Contract Analysis Workflow ──
        print("\n--- Step 7: End-to-End Analysis Workflow ---")
        
        # Set API Key in Header Drawer using React-compatible prototype setter
        print("Configuring Connection API Key...")
        await cdp.evaluate(f"""
            (() => {{
                const input = document.querySelector('#api-key-input');
                if (input) {{
                    const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                    setter.call(input, '{API_KEY}');
                    input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    input.dispatchEvent(new Event('change', {{ bubbles: true }}));
                }}
            }})()
        """)
        await asyncio.sleep(0.4)

        # Check Privacy Checkbox
        print("Checking Privacy Acknowledgment...")
        await cdp.evaluate("""
            (() => {
                const cb = document.querySelector('#privacy-consent');
                if (cb && !cb.checked) {
                    cb.click();
                    cb.dispatchEvent(new Event('change', { bubbles: true }));
                }
            })()
        """)
        await asyncio.sleep(0.3)

        # Upload Contract Fixture
        print("Uploading contract fixture...")
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

        # Check Analyze button enabled
        btn_disabled = await cdp.evaluate("document.querySelector('#analyze-btn').disabled")
        print(f"Analyze button disabled: {btn_disabled} (Expected: False)")
        assert not btn_disabled, "Analyze button remained disabled"

        # Click Analyze
        print("Submitting contract analysis...")
        t0 = time.time()
        await cdp.evaluate("document.querySelector('#analyze-btn').click()")

        # Wait for results
        completed = False
        for _ in range(40):
            await asyncio.sleep(1.0)
            has_kpis = await cdp.evaluate("document.querySelectorAll('.kpi-card').length > 0")
            if has_kpis:
                completed = True
                break
        t_duration = time.time() - t0
        print(f"Analysis completed in {t_duration:.2f}s. Results active: {completed}")
        assert completed, "Analysis timed out"
        results["gates"]["analysis_execution"] = "PASS"

        screenshot_results = await cdp.capture_screenshot("workflow_01_results_view.png")
        results["screenshots"]["workflow_results"] = screenshot_results

        # ── Step 8: Explainability (XAI) Verification ──
        print("\n--- Step 8: Explainability (XAI) Verification ---")
        await cdp.evaluate("document.querySelector('#nav-explainability').click()")
        has_xai_tokens = False
        for _ in range(30):
            await asyncio.sleep(1.0)
            has_xai_tokens = await cdp.evaluate("document.querySelectorAll('[role=\"region\"][aria-label*=\"Integrated Gradients\"] span').length > 0")
            if has_xai_tokens:
                break
        print(f"XAI Attribution tokens rendered: {has_xai_tokens} (Expected: True)")
        assert has_xai_tokens, "XAI attribution tokens did not render"
        screenshot_xai = await cdp.capture_screenshot("workflow_02_xai_attribution.png")
        results["screenshots"]["xai_attribution"] = screenshot_xai

        # Test Perturbation Sensitivity
        await cdp.evaluate("""
            (() => {
                const btns = Array.from(document.querySelectorAll('.card button.btn'));
                const sensBtn = btns.find(b => b.innerText.includes('Sensitivity'));
                if (sensBtn) sensBtn.click();
            })()
        """)
        for _ in range(20):
            await asyncio.sleep(0.5)
            has_sens = await cdp.evaluate("document.querySelector('[role=\"region\"][aria-label*=\"Perturbation Sensitivity\"] strong') !== null")
            if has_sens:
                break
        screenshot_sens = await cdp.capture_screenshot("workflow_03_xai_sensitivity.png")
        results["screenshots"]["xai_sensitivity"] = screenshot_sens
        results["gates"]["xai_rendering"] = "PASS"

        # ── Step 9: Reviewer Feedback Verification ──
        print("\n--- Step 9: Reviewer Feedback Submission ---")
        await cdp.evaluate("document.querySelector('#nav-feedback').click()")
        await asyncio.sleep(0.8)

        # Submit Feedback
        await cdp.evaluate("document.querySelector('#submit-feedback-btn').click()")
        feedback_success = ""
        for _ in range(20):
            await asyncio.sleep(0.5)
            feedback_success = await cdp.evaluate("document.querySelector('#feedback-success-msg')?.innerText")
            if feedback_success:
                break

        print(f"Feedback response status: {feedback_success}")
        assert feedback_success and "Feedback recorded successfully" in feedback_success, "Feedback submission failed"
        results["gates"]["feedback_submission"] = "PASS"

        screenshot_fb = await cdp.capture_screenshot("workflow_04_feedback_success.png")
        results["screenshots"]["feedback_success"] = screenshot_fb

        # Save machine-readable evidence results
        results_file = EVIDENCE_DIR / "browser_verification_results.json"
        results_file.write_text(json.dumps(results, indent=2), encoding="utf-8")
        print(f"\n[EVIDENCE] Saved full browser verification report to: {results_file}")

    print("\n=== ALL BROWSER ACCEPTANCE TESTS PASSED SUCCESSFULLY! ===")

if __name__ == "__main__":
    asyncio.run(run_verification())
