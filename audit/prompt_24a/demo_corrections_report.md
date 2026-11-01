# Demonstration Corrections Report — Prompt 24A

**Author:** Academic Demonstration Coordinator & FastAPI Integration Engineer  
**Audit Phase:** Prompt 24A (Final Release Corrections & Verification)  
**Date:** October 10, 2026  

---

## 1. Executive Summary

During the Prompt 24 acceptance review, an inconsistency was identified between the demonstration scripts and the actual FastAPI backend implementation regarding reviewer feedback verdicts. Specifically, the Prompt 24 draft scripts referred to verdicts named `ACCEPT`, `REJECT`, and `UNSURE`.

This report documents the verification and correction of all demonstration guidance to strictly align with the actual, tested API endpoint `POST /v1/feedback` and the Pydantic schema `FeedbackRequest`.

---

## 2. API Schema and Route Verification

### 2.1 Backend Route Specification (`src/api/v1/router.py`)
Lines 312–323 of `src/api/v1/router.py` enforce strict validation on incoming feedback submissions:
```python
valid_verdicts = {"CONFIRM_ANOMALY", "REJECT_ANOMALY"}
if request.reviewer_verdict not in valid_verdicts:
    log_audit_event(
        event_type="FEEDBACK_SUBMIT",
        action="POST /v1/feedback",
        client_id=client_id,
        status="FAILED",
        http_status=422,
        resource_id=request.doc_id,
        details={"error": "invalid_verdict"}
    )
    raise HTTPException(
        status_code=422,
        detail=f"Invalid reviewer_verdict. Must be one of: {valid_verdicts}"
    )
```

Any request with verdicts such as `ACCEPT` or `UNSURE` is rejected with HTTP `422 Unprocessable Entity`.

### 2.2 Frontend UI Selector (`frontend/src/app/page.tsx`)
In `frontend/src/app/page.tsx`, lines 666–668, the Reviewer Feedback tab exposes the exact supported options:
```tsx
<select
  id="feedback-verdict-select"
  aria-label="Reviewer Verdict"
  value={feedbackVerdict}
  onChange={(e) => setFeedbackVerdict(e.target.value)}
  className="input-field"
>
  <option value="CONFIRM_ANOMALY">CONFIRM_ANOMALY (True Anomaly)</option>
  <option value="REJECT_ANOMALY">REJECT_ANOMALY (False Alarm)</option>
</select>
```

---

## 3. Corrected Demonstration Documents

The following documents have been updated to eliminate references to `ACCEPT`, `REJECT`, and `UNSURE` and replace them with the canonical verdicts:
1. **[`audit/prompt_24/five_minute_demo_script.md`](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/audit/prompt_24/five_minute_demo_script.md):**
   - Corrected Minute 4:15–5:00 to instruct the presenter to choose `CONFIRM_ANOMALY` or `REJECT_ANOMALY`.
2. **[`audit/prompt_24/ten_minute_technical_demo.md`](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/audit/prompt_24/ten_minute_technical_demo.md):**
   - Corrected Minute 8:30–10:00 to specify `CONFIRM_ANOMALY` / `REJECT_ANOMALY`.
3. **[`audit/prompt_24/faculty_viva_questions.md`](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/audit/prompt_24/faculty_viva_questions.md):**
   - Updated Question 7 answer to reference `CONFIRM_ANOMALY` and `REJECT_ANOMALY`.
4. **[`audit/prompt_24/final_api_contract_matrix.md`](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/audit/prompt_24/final_api_contract_matrix.md):**
   - Aligned Pydantic model description with `FeedbackRequest` and `CONFIRM_ANOMALY` / `REJECT_ANOMALY`.
5. **[`audit/prompt_24/demo_environment_setup.md`](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/audit/prompt_24/demo_environment_setup.md):**
   - Documented the exact dropdown options for manual testing.

---

## 4. Retraining vs. Persistence Clarification

In accordance with scientific integrity guidelines:
- Submitting feedback via `POST /v1/feedback` writes a new `FeedbackRecord` row into `data/processed/feedback.sqlite` (table `feedback`).
- Submitting feedback **DOES NOT** trigger live online retraining of the underlying Legal-BERT transformer or discourse classifier weights.
- The recorded feedback is preserved as an auditable dataset for offline threshold recalibration and active learning.
