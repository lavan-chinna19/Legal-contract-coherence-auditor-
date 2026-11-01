# LexAudit Document Switching & Async Race Validation Report

## 1. Executive Summary
This report documents the testing and validation of asynchronous race condition protections during document upload, analysis polling, and document switching in LexAudit.

A core risk in single-page web applications is that an in-flight HTTP request from an earlier document (Contract A) completes after the user has begun viewing or analyzing a subsequent document (Contract B), resulting in stale clause mappings, identity misattribution, or text desynchronization.

---

## 2. Race Condition Safeguard Architecture

### Document ID Binding & Guard in `alignment.ts`
In `frontend/src/components/review/alignment.ts`:
```typescript
if (options.documentId && backendClauses.length > 0) {
  const firstDocId = backendClauses[0].doc_id;
  if (firstDocId && firstDocId !== options.documentId) {
    return backendClauses.map((c) => ({
      clauseId: c.clause_id,
      sequenceIdx: c.sequence_idx,
      status: "PREVIEW_ONLY_AMBIGUOUS" as ClauseAlignmentStatus,
      displayText: c.text_preview || "Clause text preview unavailable",
      explanation: "Document ID mismatch detected between active upload and analysis result.",
    }));
  }
}
```

### Ingestion State Lock in `page.tsx`
- When a document analysis is in-flight, the UI disables the `#analyze-btn` and sets `loading = true`.
- Concurrently, `docId` is generated uniquely per upload (`doc_{hex}`).
- When a new contract is uploaded, `rawContractText` is set to the new file's text, and previous results are reset or rebound.

---

## 3. Test Scenarios & Verified Outcomes

### Scenario 1: Automated Unit Test `TC-16` (Synthetic Race Injection)
- **Setup:** A delayed analysis result containing `doc_id = "contract_A_id"` is passed to `alignClausesWithRawText` while the active workspace is configured with `documentId = "contract_B_id"`.
- **Expected Outcome:** Alignment engine rejects full text extraction and returns `PREVIEW_ONLY_AMBIGUOUS` with explanation `"Document ID mismatch detected between active upload and analysis result."`
- **Observed Outcome:** `PASS`. Zero Contract A full text is sliced or associated with Contract B.

### Scenario 2: Rapid Sequential Document Analysis (End-to-End)
- **Procedure:**
  1. Upload `fixture_01_baseline.txt` $\to$ Analysis completes with `doc_5a1984c5`.
  2. Navigate to Overview $\to$ Upload `fixture_02_repeated_prefix.txt`.
  3. Start analysis for Contract B.
  4. Ensure previous Contract A clauses and selections are invalidated.
  5. Upon completion of Contract B, verify that all clause cards, inspector headers, and XAI targets reference Contract B's `doc_id`.
- **Observed Outcome:** `PASS`. Zero cross-contamination between Contract A and Contract B.

### Scenario 3: Stale Selection Invalidation
- When switching documents or receiving a new `documentResult`, if `selectedClauseId` belongs to the previous document, the workspace automatically falls back to selecting the first clause of the newly loaded document (`clauses[0].clause_id`).
- This prevents XAI and Feedback navigation from pointing to dead IDs from expired sessions.

---

## 4. Conclusion
Document switching and asynchronous response handling are fully guarded against race conditions, ensuring that displayed text and clause identity remain strictly bound to the active document.
