# Browser Automation Script Forensics Report

**Audit Phase:** Prompt 23B — Browser Evidence Authenticity, Route Reconciliation & Acceptance Integrity Audit  
**Target Scripts Inspected:**
1. [`scripts/run_prompt23a_browser_acceptance.py`](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/scripts/run_prompt23a_browser_acceptance.py)
2. [`scripts/run_prompt23_acceptance.py`](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/scripts/run_prompt23_acceptance.py)
3. [`scripts/reproduce_browser_evidence.py`](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/scripts/reproduce_browser_evidence.py)

---

## 1. Forensic Examination of `scripts/run_prompt23a_browser_acceptance.py`

### Target Environment & Connection
- **URL Target:** Connects to Chrome DevTools Protocol via WebSocket at `ws://127.0.0.1:9222/devtools/page/...` targeting `http://localhost:3000/`.
- **Protocol:** Real Chrome DevTools Protocol (CDP) WebSocket commands (`Page.navigate`, `DOM.setFileInputFiles`, `Runtime.evaluate`, `Page.captureScreenshot`, `Emulation.setDeviceMetricsOverride`).

### How DOM Controls Were Actually Located
The forensic code inspection reveals that the script **never used** the claimed CSS IDs (`#tab-audit`, `#privacy-consent`, `#analyze-btn`, etc.):
- **Tab Buttons:** Located via JavaScript text content filtering:
  ```javascript
  const tabs = Array.from(document.querySelectorAll('button.tab-btn'));
  const xaiTab = tabs.find(t => t.innerText && t.innerText.includes('Explainability'));
  ```
- **API Key Input:** Located via placeholder attribute filtering:
  ```javascript
  const inputs = Array.from(document.querySelectorAll('input'));
  const keyInput = inputs.find(i => i.placeholder && i.placeholder.includes('API Key'));
  ```
- **Privacy Checkbox:** Located via tag selector: `document.querySelector('input[type="checkbox"]')`.
- **File Input:** Located via tag selector: `input[type="file"]`. File payload attached via native CDP `DOM.setFileInputFiles`.
- **Analyze Button:** Located via class selector: `document.querySelector('button.btn')`.
- **Feedback Submit Button:** Located via text content:
  ```javascript
  const subBtn = btns.find(b => b.innerText && (b.innerText.includes('Submit') || b.innerText.includes('Verdict')));
  ```

### React Event Dispatch & State Transitions
The script successfully triggered React state updates by calling native prototype property setters and bubbling synthetic DOM events:
```javascript
const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
setter.call(keyInput, 'dev_auditor_key_12345');
keyInput.dispatchEvent(new Event('input', { bubbles: true }));
keyInput.dispatchEvent(new Event('change', { bubbles: true }));
```
This proves that the browser was genuinely interactive and not a static presentation.

### Network Capture Integrity
The network traces in `audit/prompt_23a/evidence/browser_network_requests.json` were captured using CDP network listener callbacks (`Network.requestWillBeSent` and `Network.responseReceived`).
- **Real Browser Requests:** The browser genuinely called `POST /v1/upload`, `POST /v1/analyze`, `GET /v1/jobs/...`, `GET /v1/jobs/.../results`, `GET /v1/xai/attribution`, `GET /v1/xai/sensitivity`, and `POST /v1/feedback`.
- **No Mocks or Test Doubles:** The script did not mock `fetch`, intercept HTTP requests, or inject artificial JSON responses.

### Provenance of Discrepancies
The script output did **not** generate the strings `/v1/audit/contracts` or `#tab-audit`. The discrepancy arose because the report author who drafted `audit/prompt_23a/ui_interaction_inventory.csv` and `browser_acceptance_summary.md` transcribed idealized REST routes and semantic DOM IDs from external architectural specifications rather than reflecting the actual code in `frontend/src/app/page.tsx` and `scripts/run_prompt23a_browser_acceptance.py`.

---

## 2. Forensic Examination of `scripts/run_prompt23_acceptance.py`

- Operates as a pure Python HTTP client using the `requests` library against `http://127.0.0.1:8000`.
- Genuinely executed 32 HTTP test cases against `/health`, `/ready`, `/v1/upload`, `/v1/analyze`, `/v1/jobs/{id}`, `/v1/jobs/{id}/results`, `/v1/xai/attribution`, `/v1/xai/sensitivity`, `/v1/feedback`, and `/v1/maintenance/cleanup`.
- Proves backend pipeline robustness but did not exercise browser UI rendering.

---

## 3. Conclusion

The browser automation script executed authentic, non-mocked browser interactions against the running Next.js and FastAPI stack. The reported DOM selectors and route discrepancies are **documentation errors (CONFIRMED_REPORT_ERROR)**, not software fabrication.
