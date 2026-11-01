# LexAudit Fallback Behavior & Preview-Only Validation

## 1. Executive Summary
This document validates the safe fallback mechanisms implemented across LexAudit when clause boundaries cannot be conclusively verified against raw contract text.

In accordance with Phase 3A principles:
> **The highest priority is correct evidence attribution, not maximizing the amount of displayed text.**
> **A visually incomplete but truthful preview is preferable to presenting incorrect legal-document content.**

---

## 2. Fallback Scenarios & Trigger Conditions

| Fallback Scenario | Cause / Trigger | Assigned Status | UI Label / Warning Displayed |
|---|---|---|---|
| **Ambiguous Candidate Match** | Multiple identical tokens in remaining text without structural disambiguation | `PREVIEW_ONLY_AMBIGUOUS` | `Preview only — full clause boundary could not be verified.` |
| **Unverified Subsequent Boundary** | Subsequent clause $i+1$ is unmatched or ambiguous | `PREVIEW_ONLY_AMBIGUOUS` | `Preview only — full clause boundary could not be verified.` |
| **Desynchronized Preview** | Token not found in uploaded text | `PREVIEW_ONLY_UNMATCHED` | `Clause text preview unavailable or could not be aligned safely.` |
| **Missing Raw Text in Memory** | Direct tab navigation or page refresh | `PREVIEW_ONLY_INSUFFICIENT_EVIDENCE` | `Authoritative API Preview` |
| **Async Document Race Condition** | Active `doc_id` differs from analysis response | `PREVIEW_ONLY_AMBIGUOUS` | `Preview only — full clause boundary could not be verified.` |

---

## 3. UI Component Behavior Under Fallback

### `ClauseCard.tsx`
When `clause.alignment_status !== "VERIFIED_FULL_TEXT"`:
1. Renders the backend-provided `clause.text_preview` directly.
2. Inserts an accessible status badge above the footer:
   - Warning styling: subtle amber background (`rgba(245, 158, 11, 0.12)`) and border.
   - Text: `Preview only — full clause boundary could not be verified.`
   - Native `title` tooltip displaying `clause.alignment_explanation`.
3. Updates footer label to `Authoritative API Preview (Ambiguous Boundary)` or `Authoritative API Preview`.

### `FindingsInspector.tsx`
In the inspector header and evidence excerpt panel:
1. Excerpt badge dynamically updates to:
   `Preview Only (Ambiguous Boundary)` or `Preview Only (Unverified)`.
2. Text displayed is the authentic API preview, italicized for clear visual distinction from verified full text.
3. Scoring, Legal-BERT centroid distances, Markov probabilities, and rule associations remain 100% active and bound to the authoritative backend `clause_id`.

---

## 4. Search and Filter Resilience Under Fallback
A key requirement is that search and severity filtering continue to operate seamlessly when clauses are in preview-only mode:
- In `ContractReviewWorkspace.tsx`:
  `const textToSearch = (c.full_text || c.text_preview).toLowerCase();`
- When in preview-only mode, `c.full_text` holds the preview text, allowing full-text searches, keyword queries, section searches (`§ 1`), and severity filter buttons (`HIGH`, `MEDIUM`, `LOW`, `FLAGGED`, `CLEAN`) to function normally.

---

## 5. Verification Verdict
Safe fallback behavior is verified across unit tests (`TC-11`, `TC-14`, `TC-15`, `TC-16`, `TC-17`) and real browser CDP execution (`screenshot_04_preview_fallback_badge.png`). Zero guessed or misattributed legal text is ever presented to the reviewer.
