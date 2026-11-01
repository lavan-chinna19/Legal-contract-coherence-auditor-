# Document Text Alignment & Full-Clause Retention Report
**LexAudit Phase 3 UI Redesign Program**

## 1. Investigation of Backend Data Availability
Prior to implementing the `ClauseDocumentViewer`, the response payload of `/v1/analyze` was investigated:
- **FastAPI Model**: `ClauseScoringResultModel` (`src/api/schema.py`).
- **Response Truncation**: In strict accordance with Security Contract §4 (Confidentiality & Zero Plaintext Persistence), the backend stores ciphertext on disk and returns `text_preview` in the API payload truncated to 100 characters: `c.text[:100] + "..."`.
- **Finding**: The backend analysis API does *not* return the complete plaintext of every clause over the wire to prevent network exfiltration and audit log exposure.

---

## 2. Safe Frontend In-Memory Text Retention
To satisfy the requirement that the left panel display full clause text without truncating to 150 characters while strictly preserving backend segmentation and privacy:

### 2.1 Implementation Flow
1. During contract ingestion (`AuditorDashboard`), when the user selects a `.txt` file:
   ```typescript
   const rawText = await file.text();
   setRawContractText(rawText);
   ```
2. The complete raw string is retained exclusively in React state memory (`rawContractText`).
3. It is never persisted to `localStorage`, `sessionStorage`, or backend logs.

### 2.2 Alignment Algorithm (`alignClausesWithRawText`)
In `frontend/src/components/review/ContractReviewWorkspace.tsx`:
- The alignment algorithm iterates through the authoritative list of clauses returned by `documentResult.scoring_result.clauses`.
- For each clause, it extracts the initial prefix from `clause.text_preview` (stripping trailing `"..."`).
- It locates the exact starting character offset in `rawContractText` starting from the end of the previous clause.
- It determines the clause boundary based on the start of the next clause's prefix (or end of file).
- **Graceful Fallback**: If an exact prefix match cannot be established, the component falls back transparently to the authoritative `clause.text_preview`. It does not invent synthetic boundaries.

```typescript
function alignClausesWithRawText(
  backendClauses: ClauseResult[],
  rawText: string | null
): EnrichedClause[] {
  if (!rawText || !rawText.trim()) {
    return backendClauses.map((c) => ({
      ...c,
      full_text: c.text_preview,
    }));
  }

  let currentSearchOffset = 0;
  const enriched: EnrichedClause[] = [];

  for (let i = 0; i < backendClauses.length; i++) {
    const c = backendClauses[i];
    const prefix = c.text_preview.replace(/\.\.\.$/, "").trim().slice(0, 40);
    const startIdx = rawText.indexOf(prefix, currentSearchOffset);

    if (startIdx === -1) {
      enriched.push({ ...c, full_text: c.text_preview });
      continue;
    }

    let endIdx = rawText.length;
    if (i < backendClauses.length - 1) {
      const nextPrefix = backendClauses[i + 1].text_preview.replace(/\.\.\.$/, "").trim().slice(0, 40);
      const nextStart = rawText.indexOf(nextPrefix, startIdx + prefix.length);
      if (nextStart !== -1) {
        endIdx = nextStart;
      }
    }

    const fullClauseText = rawText.slice(startIdx, endIdx).trim();
    currentSearchOffset = endIdx;
    enriched.push({
      ...c,
      full_text: fullClauseText || c.text_preview,
    });
  }

  return enriched;
}
```

---

## 3. Alignment Integrity Verification
Browser testing with `audit/prompt_23/evidence/fixtures/valid_multiclause.txt` verified that:
- Clause 0 displays full text: `"1. Term and Duration. This Agreement commences on January 15, 2026 and terminates on January 14, 2027."`
- Clause 1 displays full text: `"2. Confidentiality Obligations. The Receiving Party agrees to protect Confidential Information as defined herein with reasonable care."`
- The findings displayed in the right panel (`FindingsInspector`) correspond 100% to the selected clause's backend ID (`doc_b6c220fb_0`, `doc_b6c220fb_1`), guaranteeing zero cross-clause displacement.
