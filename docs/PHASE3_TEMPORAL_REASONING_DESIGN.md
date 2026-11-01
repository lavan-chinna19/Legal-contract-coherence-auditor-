# Phase 3: context-aware temporal reasoning

This is a bounded, deterministic English temporal interpreter. A confirmed conflict means that
explicit textual constraints are incompatible under the documented interpretation. It is not a
legal-invalidity judgment, model confidence probability, or expert opinion. Development examples
are exposed synthetic evidence. No independent adjudication exists in this phase.

## Data flow and preservation

`UnifiedAuditor` still scores the same legacy clauses with the frozen neural system. Its reference
analysis supplies the existing Phase 2 `StructuralDocument` to `DateLogicChecker.analyze_document`.
New `src/temporal/extraction.py` extracts statements from the unchanged structural units;
`analysis.py` compares supported constraints. The structural parser is reused without edits.

The old `check_document -> (flags, dates)` facade and `DateEntity`/`RuleFlag` schemas remain usable.
Richer statements and decisions are additive in `metadata.temporal_analysis`. Jobs retain that
metadata in saved analysis snapshots and include temporal uncertainty in `analysis_state`.
PDF and DOCX use the common report builder to display categories, exact source statements,
parties/actions/triggers, scope/phase/section, conditions, operators and source offsets.

The old checker is preserved byte-for-byte in
`evaluations/phase3_temporal_reasoning_2026_10_26/legacy_snapshot/date_checker.py`. Pre-change outputs
remain under `old_baseline/`; original Phase 1/2 evidence is read-only. Neural embeddings,
Channel A/B, checkpoints, calibration and severity/ensemble thresholds are not changed or fitted.

## Structured statements

Every statement retains its exact Unicode source substring and half-open `[char_start,char_end)`
span, coordinate space, source clause association, section UID/identity and date span where present.
Coordinates refer to extracted text, not PDF page geometry. Calls without original text explicitly
use assembled-clause coordinates. Source SHA-256 identifies the actual extraction.

Additional fields: kind, role, event, responsible actor when explicit, required action, triggering
event, absolute ISO date, original date, duration value/unit/basis, deadline operator, relative
direction, lower/upper day offsets, agreement scope, phase, party context, qualifiers, parsing
status and explicit uncertainty reasons. `For Buyer` is a party context, not invented responsibility.
No neural coreference, entity equivalence or obligation equivalence is inferred.

## Supported grammar and comparisons

* Explicit ISO/year-first, named-month and unambiguous numeric dates. Ambiguous numeric locales,
  invalid dates, approximation, negation, alternatives and time-of-day semantics require review
  or unsupported status. No current date, locale or missing year is guessed.
* Same-scope, same-phase exact effective/end endpoints; explicit from/to, through, until and
  between/and ranges. Physical section order supplies no temporal ordering assumption.
* Exact named Event/Milestone/Delivery dates and invoice receipt dates. Nearest explicit event
  text binds a date. Multiple modal actions in one sentence abstain pending reliable binding.
* Explicit actor/action deadlines: within, exactly, at least, no later than; after/before/from
  a named trigger. Calendar days and weeks support integer arithmetic, including zero and
  spelled numbers through ninety-nine. Written/numeric disagreement requires review.
* A unique, exact, unqualified trigger date must exist in the matching scope/phase/party context.
  Missing or conflicting anchors abstain. Equivalent named triggers are not guessed.
* Supported calendar constraints are inclusive offset intervals. An exact action date outside
  its interval confirms incompatibility. Disjoint intervals for the same actor/action/trigger
  confirm incompatibility. Different but overlapping bounds produce a potential discrepancy,
  not a contradiction: a stricter deadline can satisfy both.
* Explicit milestone-before relationships compare uniquely anchored exact dates. Same-day facts
  require review because dates cannot establish within-day order. Qualified anchors abstain.

Agreement names are explicit `Agreement A` style identifiers; named `Phase X`, initial and renewal
phases are retained. Unknown scope, multiple phases/contexts, unresolved actors/actions/triggers
and conditions are not filled in. Conditions/exceptions/amendment cues in statements or headings
prevent unconditional confirmation. This is a conservative lexical safeguard, not a general
conditional-logic or amendment-precedence solver. Business days lack jurisdiction/holiday calendars;
months/years lack rollover policy; all are unsupported. There is no external calendar service.

## Decision contract

| Category | Meaning |
| --- | --- |
| CONFIRMED_TEMPORAL_CONFLICT | Supported explicit deterministic constraints cannot both hold |
| POTENTIAL_INCONSISTENCY | Arithmetic candidate or different bounds needing interpretation |
| REVIEW_REQUIRED | Ambiguous syntax, missing binding/anchor, or meaning not established |
| CONSISTENT | Supported relationship agrees, or an explicit fact parsed without a comparison |
| UNSUPPORTED | Recognized temporal language exceeds supported grammar or policy |

`CONSISTENT / UNCOMPARED_STATEMENT` explicitly does **not** validate the fact or the document.
Only supported relation checks with multiple statement IDs count toward relational coverage.
Potential and confirmed decisions create compatible legacy rule flags with a `decision_category`
in evidence. Review/unsupported decisions live in metadata and force API review state even when
no flag exists. Legacy HIGH ordering priority remains compatible; severity is review priority,
separate from the decision category and from scientific confidence.

Relations retain statement IDs and exact evidence spans instead of copying whole paragraphs for
every pair. The inherited source limit is 250,000 characters; statements longer than 8,192 chars
are unsupported; extraction caps at 500 statements and decisions at 1,000. Truncation clears flags
and suppresses firm conclusions rather than treating a partial parse as complete.

## Remaining limits

The interpreter does not solve arbitrary legal English, pronouns/aliases, inherited implicit
obligations, legal precedence, jurisdiction-specific business calendars, timezones or general
distant-clause contradiction reasoning. Unrecognized language can be missed entirely. Unknown or
unsupported negatives are not validated consistent negatives. Independent expert labels and
unseen document-family testing remain prerequisites for real-world performance claims.
