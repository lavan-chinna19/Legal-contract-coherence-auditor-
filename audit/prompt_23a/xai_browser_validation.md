# Explainability (XAI) Real Browser Validation (Prompt 23A)

**Phase:** Prompt 23A — Phase D  
**Execution Date:** 2026-10-10  
**Browser Engine:** Chrome via Chrome DevTools Protocol  
**Active Document:** `doc_97a800a4` (5-clause NDA)  
**Target Clause:** `doc_97a800a4_0` ("1. Term and Duration...")  

---

## 1. Browser Navigation & Tab Unlocking
- Prior to analysis completion, Tab 3 (`3. Explainability (XAI)`) was disabled via `disabled={!documentResult}`.
- Upon asynchronous job completion, Tab 3 automatically unlocked.
- Clicking Tab 3 successfully opened the Explainability dashboard view.
- Screenshot captured: [`audit/prompt_23a/evidence/xai_attribution_view.png`](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/audit/prompt_23a/evidence/xai_attribution_view.png).

---

## 2. Integrated Gradients Token Attribution in Browser
- **API Call:** Browser issued real `GET http://localhost:8000/v1/xai/attribution?doc_id=doc_97a800a4&clause_id=doc_97a800a4_0` with `X-API-Key: dev_auditor_key_12345`.
- **Response Received:** HTTP `200 OK`.
- **Rendered Elements:** 26 individual token badges rendered in a horizontal inline flow.
  - Sample tokens: `[CLS]`, `1`, `.`, `term`, `and`, `duration`, `.`, `this`, `agreement`, `commence`, `##s`
  - Tokens styled with subtle color weights corresponding to real Integrated Gradients attribution scores.
- **Claim Scope Rendered:**
  - Notice rendered: *"Integrated Gradients indicates which input tokens contributed most to the Channel A semantic distance anomaly score. It does not prove that those tokens are legally significant or that the model prediction is correct."*

---

## 3. Channel B Neighborhood Sensitivity in Browser
- **API Call:** Browser issued real `GET http://localhost:8000/v1/xai/sensitivity?doc_id=doc_97a800a4&clause_id=doc_97a800a4_0`.
- **Response Received:** HTTP `200 OK`.
- **Rendered Elements:**
  - Displayed neighboring clause identifier (`doc_97a800a4_1`).
  - Rendered delta score (`+0.0752`) with intervention type `mask_neighbor_text`.
- **Screenshot Captured:** [`audit/prompt_23a/evidence/xai_sensitivity_view.png`](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/audit/prompt_23a/evidence/xai_sensitivity_view.png).

---

## 4. XAI Browser Acceptance Verdict
**STATUS: PASS (BROWSER_VERIFIED)**
- Both XAI modes render genuine computed data in the real browser DOM.
- Zero placeholder or hardcoded token strings.
- Academic claim scopes clearly communicated to user.
