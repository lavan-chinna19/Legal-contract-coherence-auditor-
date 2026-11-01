# Demonstration Fixture & Output Metric Validation — Prompt 24A

**Author:** Academic Demonstration Coordinator & QA Lead  
**Audit Phase:** Prompt 24A (Final Release Corrections & Verification)  
**Date:** October 10, 2026  

---

## 1. Fixture Provenance & Authenticity

The verified demonstration fixture used throughout the Prompt 23B independent browser reproduction suite and demonstration materials is located at:
```text
audit/prompt_23/evidence/fixtures/valid_multiclause.txt
```

### 1.1 Integrity Fingerprint
- **File Path:** `audit/prompt_23/evidence/fixtures/valid_multiclause.txt`
- **File Size:** 597 bytes
- **SHA-256 Digest:** `55558d95947bb2050782035de4f7a9f938d29c5b3d0b8e53014cf22c8c085825`
- **Line Count:** 5 numbered clauses
- **Confidentiality Review:** Contains only generic, synthetic boilerplate clauses (Term, Confidentiality, IP, Termination, Dispute Resolution). Confirmed zero confidential, proprietary, or personal data.

### 1.2 Verbatim Content
```text
1. Term and Duration. This Agreement commences on January 15, 2026 and terminates on January 14, 2027.
2. Confidentiality Obligations. The Receiving Party agrees to protect Confidential Information as defined in Section 1.
3. Intellectual Property Rights. All patent, copyright, and trade secret rights shall remain the sole property of the Discloser.
4. Termination for Convenience. Either party may terminate this Agreement pursuant to Section 1 upon thirty (30) days notice.
5. Dispute Resolution. All disputes arising under this Agreement shall be resolved via arbitration in New York, NY.
```

---

## 2. Empirical Execution Metrics

When processed through the unified analysis pipeline (`POST /v1/upload` followed by `POST /v1/analyze`), the pipeline produces the following verified results:

| Metric Axis | Observed Value | Pipeline Source | Notes |
|---|:---:|---|---|
| **Total Clauses** | 5 | Segmentation Regex & spaCy | 5 numbered sections detected |
| **Total Anomalies** | 2 | Dual-Channel Anomaly Scorer | Clause 1 and Clause 5 flagged |
| **High Severity Count** | 2 | Severity Decision Logic | Elevated discourse shift at boundaries |
| **Medium Severity Count** | 0 | Severity Decision Logic | No mid-tier anomalies flagged |
| **Rule Violations** | 0 | Reference & Date Checkers | Dates sequential; internal references valid |
| **Mean Anomaly Score** | 0.341 | Channel A & B Composite | Composite score across all clauses |
| **Integrated Gradients Tokens** | 26 badges | WordPiece / Legal-BERT Explainer | Clause 1 tokenized into 26 subword tokens |

---

## 3. Scientific Integrity Disclosure & Demo Script Guidance

In previous Prompt 24 materials, these numerical values were cited as examples. Prompt 24A mandates that they must not be presented as universal or guaranteed outputs for arbitrary contracts:

1. **Qualification in Scripts:** All demonstration materials have been updated with explicit language:
   > *"These metrics (5 clauses, 2 anomalies, 2 high-severity, 0.341 score) are observed with the verified demonstration fixture (`valid_multiclause.txt`) under the frozen model checkpoint. They are sample-specific empirical results, not hardcoded constants or universal outputs for arbitrary contracts."*
2. **Dynamic Presenter Guidance:** If a faculty evaluator requests uploading a different contract during the live presentation, the presenter is instructed to read and explain the actual dynamically computed values displayed on the screen.
3. **No Metric Hardcoding:** The frontend derives all KPI values directly from the backend API response (`resData.scoring_result`), with zero hardcoded metrics in `frontend/src/app/page.tsx`.
