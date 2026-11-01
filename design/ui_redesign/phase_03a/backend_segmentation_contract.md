# LexAudit Authoritative Backend Segmentation & Preview Contract

## 1. Executive Summary
This specification documents the authentic data contract, segmentation semantics, and serialization behavior of the FastAPI backend (`src/segmentation/rule_based.py`, `src/scoring/pipeline.py`, and `src/api/v1/router.py`).

A rigorous audit was conducted on the actual Python source code and live HTTP responses to ensure that frontend alignment makes zero unvalidated assumptions about how clauses, previews, IDs, and boundaries are generated.

---

## 2. Ingestion & Preprocessing Semantics

### Text Decoding & Validation
- **Endpoint:** `POST /v1/upload` (in `src/api/v1/router.py`).
- **Encoding:** Ingested via `content.decode("utf-8")`. Corrupt binary bytes raise `HTTP 400 UnicodeDecodeError`.
- **Empty file rejection:** Whitespace-only files raise `HTTP 400 Uploaded file is empty.`
- **Line ending normalization:** In Python runtime ingestion, standard text handlers convert Windows CRLF (`\r\n`) to Unix LF (`\n`). However, the raw document in browser memory retains the client's native line endings (`\r\n` or `\n`).

### HTML Cleaning & Whitespace Transformation
In `RuleBasedSegmenter._clean_html`:
- Block HTML tags (`<div>`, `<p>`, `<br>`, `<tr>`, `<td>`, `<table>`, `<h1-h6>`) are replaced with `\n`.
- All other HTML tags are replaced with a single space ` `.
- HTML entities are unescaped via `html.unescape()` (`&nbsp;` $\to$ space).
- Excessive newlines are collapsed: `re.sub(r'\n\s*\n', '\n\n', text)`.

---

## 3. Segmentation Algorithm & Clause Record Construction

### Boundary Detection Patterns
In `RuleBasedSegmenter`:
1. **Numbered clause pattern:**
   ```regex
   ^\s*(?:(?:(?:Article|Section)\s+[IVXLCDM\d]+[.:]*\s*)|(?:\d+(?:\.\d+)*[.:]*\s*)|(?:\([a-z\divxlcdm]+\)\s*))
   ```
   Matches patterns like `1.`, `1.1`, `1.1(a)`, `(a)`, `(i)`, `Section 1.`, `Article I.`, `1)` at start of line (`MULTILINE`).
2. **Heading pattern:**
   ```regex
   ^\s*([A-Z][A-Z\s,.-]{2,100})$
   ```
   Matches uppercase heading lines.
3. **Preamble:** If the first split offset is $> 0$, the text from offset 0 to split 0 is emitted as a `Preamble` clause.

### Clause Record Identity & Offsets
For each split $i$:
- `sequence_idx = len(clauses)` (zero-indexed, monotonically increasing: `0, 1, 2, ...`).
- `clause_id = f"{doc_id}_{sequence_idx}"`.
- `clause_text = raw.strip()` (leading and trailing whitespace stripped).
- `char_start`: computed relative to the internal cleaned text buffer.
- `char_end`: computed as `actual_start + len(clause_text)`.

---

## 4. Text Preview Construction & Serialization

### Truncation Formula
In `src/scoring/pipeline.py`:
```python
preview = c.text[:100] + "..." if len(c.text) > 100 else c.text
```

### Critical API Boundary Limitation
- The HTTP response schema `ClauseScoringResultModel` (in `src/api/schema.py`) exposes:
  `clause_id`, `doc_id`, `sequence_idx`, `text_preview`, scores, and diagnostic evidence.
- **`char_start` and `char_end` are NOT serialized over HTTP.**
- **Consequence:** The frontend client does NOT receive authoritative source character offsets over the network. Therefore, reconstructing full clause boundaries from raw document text in browser memory requires rigorous sequential evidence verification or safe fallback to `text_preview`.

### Punctuation & Ellipsis Gotchas
- If an original clause contains a literal ellipsis `...` (e.g. `15 U.S.C. § 78a et seq...`) and its total length is $\le 100$ characters, the backend does **not** append an ellipsis, but the preview ends in `...`.
- If an original clause exceeds 100 characters, the backend strips at 100 and appends `...`.
- The frontend `extractSearchToken` utility correctly differentiates these cases by checking both trailing `...` and length $\ge 100$.

---

## 5. Duplicate Clauses & Identity Guarantees
- **Duplicate complete text:** If two clauses in a document share identical text (e.g. standard boilerplate provisions), `RuleBasedSegmenter` generates **distinct, unique clause IDs**:
  e.g., `doc_1234_1` and `doc_1234_3`.
- **Identity stability:** Backend clause IDs are never derived from text content. They are strictly sequential indices within the ingested document.
- **Rule associations:** Deterministic rule findings flag specific clause IDs (`clause_id` or `involved_clause_ids`).
- **XAI and Feedback:** XAI token attribution and reviewer feedback persistence are keyed strictly by `doc_id` and `clause_id`.

---

## 6. Authoritative Alignment Specification

| Mapping Transition | Evidence Requirement | Alignment Status | Displayed Content |
|---|---|---|---|
| Exact & Unique Match | Unique monotonic occurrence with verified non-overlapping adjacent boundary | `VERIFIED_FULL_TEXT` | Authoritative full-text slice from browser contract memory |
| Repeated Prefix | Consecutive duplicate group matched sequentially with monotonic ordering | `VERIFIED_FULL_TEXT` | Authoritative full-text slice from browser contract memory |
| Ambiguous Offset | Multiple candidate occurrences with unprovable boundary | `PREVIEW_ONLY_AMBIGUOUS` | Authoritative backend `text_preview` with warning badge |
| Missing Preview | Search token not found in source text at expected sequence | `PREVIEW_ONLY_UNMATCHED` | Authoritative backend `text_preview` with warning badge |
| Missing Raw Text | Raw contract text not present in browser memory | `PREVIEW_ONLY_INSUFFICIENT_EVIDENCE` | Authoritative backend `text_preview` |
| Document ID Mismatch | Active upload document ID does not match clause `doc_id` | `PREVIEW_ONLY_AMBIGUOUS` | Authoritative backend `text_preview` (Async race guard) |

---

## 7. Compliance Statement
The interface strictly enforces:
> *A visually incomplete but truthful preview is preferable to presenting incorrect legal-document content.*

Under zero circumstances will the frontend guess or invent boundaries when evidence is inconclusive.
