# LexAudit Clause Alignment Algorithm Audit & Defect Forensics

## 1. Audit Overview
This report documents the forensic security and integrity audit of the pre-Phase 3A clause alignment algorithm previously embedded inline within `frontend/src/components/review/ContractReviewWorkspace.tsx`.

The objective of the audit was to determine whether the existing algorithm could silently misattribute legal document text, present misleading boundaries, or produce cross-clause collisions under adversarial contract conditions.

---

## 2. Pre-Phase 3A Implementation Analysis

The historical implementation was located in `ContractReviewWorkspace.tsx` lines 48–69:

```typescript
// HISTORICAL NAIVE IMPLEMENTATION (Pre-Phase 3A)
if (raw.length > 0) {
  const searchPrefix = c.text_preview.replace(/\.{2,}$/, "").trim();
  const pos = raw.indexOf(searchPrefix);
  if (pos !== -1) {
    const nextClause = clauses[idx + 1];
    let endPos = raw.length;
    if (nextClause) {
      const nextPrefix = nextClause.text_preview.replace(/\.{2,}$/, "").trim();
      const nextPos = raw.indexOf(nextPrefix, pos + searchPrefix.length);
      if (nextPos !== -1) {
        endPos = nextPos;
      }
    }
    const slice = raw.substring(pos, endPos).trim();
    if (slice.length >= searchPrefix.length) {
      resolvedFullText = slice;
      isFull = true;
    }
  }
}
```

---

## 3. Confirmed Failure Modes & Minimal Reproducible Examples

### Defect 1: First-Occurrence Collisions on Duplicate Clauses
- **Mechanism:** `pos = raw.indexOf(searchPrefix)` searched from offset `0` for every clause without maintaining a monotonic search cursor.
- **Consequence:** If two separate clauses (e.g. § 1 and § 3) share identical boilerplate text, Clause § 3 was matched to the position of Clause § 1!
- **Minimal Reproducible Example:**
  Contract with two boilerplate provisions at lines 2 and 4:
  `Neither party may assign its rights without prior written consent.`
  Under naive algorithm: Clause § 3 displayed text belonging to Clause § 1.

### Defect 2: Entire Document Swallowing on Next-Clause Miss
- **Mechanism:** `let endPos = raw.length;`
  If `nextPos === -1` (e.g. if the next clause prefix had formatting variations, indentation, or character differences), `endPos` remained `raw.length`.
- **Consequence:** Clause $i$ swallowed all remaining text of the contract (Clauses $i+1, \dots, N$) into its single card body!

### Defect 3: Indiscriminate Ellipsis Stripping
- **Mechanism:** `replace(/\.{2,}$/, "")` unconditionally stripped trailing dots.
- **Consequence:** A short clause containing a literal ellipsis in its substantive legal text (e.g. `15 U.S.C. § 78a et seq...`) had its legal terminology mutilated.

### Defect 4: Windows CRLF vs Unix LF Line Ending Desynchronization
- **Mechanism:** Python backend normalizes newlines to `\n` during ingestion. If a client uploaded a document with Windows CRLF (`\r\n`), search tokens spanning across a newline contained `\n` while the raw text contained `\r\n`.
- **Consequence:** Verbatim `indexOf` returned `-1`, falsely claiming the clause was unmatched.

### Defect 5: Unverified Boundaries Marked as Authoritative
- **Mechanism:** If `slice.length >= searchPrefix.length`, `isFull` was unconditionally set to `true`, presenting unverified and potentially overlapping slices as authoritative legal text.

### Defect 6: Async Document Race Condition
- **Mechanism:** The component did not verify that `documentResult.doc_id` matched the active contract upload before aligning. If the user selected Contract B while Contract A was analyzing, A's delayed response aligned with B's raw text.

---

## 4. Architectural Corrections in `alignment.ts`

To permanently resolve these failure modes, a dedicated, pure TypeScript alignment engine was implemented in `frontend/src/components/review/alignment.ts`:

1. **Strict Monotonicity:** `currentSearchOffset` advances monotonically after each candidate match, guaranteeing that Clause $i+1$ can never search prior to the start of Clause $i$.
2. **Line-Ending Invariant Matching:** `findOccurrencesForToken` detects if tokens contain newlines and adapts between CRLF and LF dynamically without altering character offset calculations.
3. **Smart Truncation Tokenization:** `extractSearchToken` only strips trailing `...` when preview length $\ge 100$, preserving literal ellipses in short clauses.
4. **Boundary Verification Gate:** Full text is declared `VERIFIED_FULL_TEXT` only when:
   - Candidate match is unique or resolved via sequential group disambiguation.
   - Subsequent boundary $i+1$ is proven non-overlapping and monotonic.
   - Sliced text contains the expected search token.
5. **Safe Ambiguity Fallback:** Any inconclusive boundary, duplicate conflict, or desynchronized token automatically falls back to `PREVIEW_ONLY_AMBIGUOUS` or `PREVIEW_ONLY_UNMATCHED`, displaying the authoritative API preview.
6. **Async Race Guard:** `options.documentId` verifies that the active upload matches `clause.doc_id`, dropping to preview if an in-flight race condition occurs.

---

## 5. Audit Verdict
The previous inline algorithm is fully decommissioned and replaced by `alignment.ts`. All 6 identified vulnerabilities are closed and proven resolved by the 17-case automated test suite.
