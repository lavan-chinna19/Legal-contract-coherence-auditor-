# Phase 4A: experimental obligation and event binding

This separately identified, opt-in CPU component extracts limited explicit obligation fields and
decides whether records are potentially comparable. It does not classify legal contradictions,
resolve legal precedence, compare deadlines, fit probabilities or modify any existing detector.

## Phase 3 audit and reporting correction

The four Phase 3 reports were read alongside `results/paired_v3` raw predictions and summary.
`evaluations/phase4a_obligation_binding_2026_10_28/audit_phase3.py` recomputes all confusion counts,
precision, recall, F1 and FPR, including selective denominators. They match the saved raw summary.
Original chronology is 6/2/2/4 -> 8/0/0/6; new mechanical 4/5/9/32 -> 13/0/0/37; separate challenges
0/1/2/9 -> 2/0/0/10 (TP/FP/FN/TN). Old alerts against new conflict labels remain only a proxy.

**A reporting inconsistency was found and reported before implementing binding.** Final Phase 3
raw data contains **20/50 (40%)** documents with review/unsupported evidence, not the reports'
21/50 (42%); review-only count is 15, not 16; supported statements are **96/118 (81.36%)**, not
94/118 (79.66%). Those prose values were stale from the earlier paired_v2 run. Historical reports
and artifacts remain unchanged. This additive erratum supersedes those values in the previous
conversation and report narrative; `phase3_audit_verified.json` is the machine-readable audit.
The first Phase 4A audit checked raw summary agreement but repeated the stale 42% interpretation;
that intermediate file is retained and explicitly superseded by the verified audit.

The 44% supported relation value remains correct: 22/50 documents have at least one multi-statement
CONSISTENT or CONFIRMED relation. A parsed lone fact is not supported relational coverage. Review
union and relation support can overlap and are not complementary. In full-denominator screening,
abstention is no confirmation: a positive abstention counts FN; a negative abstention is only a
screen TN. Selective results never establish legal consistency of abstained cases.

## Representation and source evidence

New `src/obligations/binding.py` uses only the existing structural parser plus Python stdlib.
Each extracted modal record includes:

* Explicit responsible actor, normalized action, named object, recipient when stated, trigger,
  event-instance identity and deadline text.
* Simple explicit conditions, exception cues, agreement scope and phase.
* Original raw text, exact Unicode half-open source spans, section UID/identity, clause association,
  coordinate space, per-field evidence spans, missing fields, uncertainty and unsupported reasons.

For the controlled task, a named Invoice/Report/Shipment/Notice/Milestone plus an explicit identifier
denotes an object/occurrence. Recurrence words (each, every, monthly, etc.) invalidate a unique
instance. This is an explicit naming convention, not a generally sufficient legal event ontology.
No actor is invented from an object or deadline role. Optional recipient and missing deadline
remain absent; a missing deadline alone does not prevent structural identity matching, and no
timeline conclusion follows. Unknown pronouns or coordinated joint subjects are not resolved.

## Bounded grammar

Supported modalities: `shall`, `must`, `is required to`. A small published action map normalizes
pay/remit, deliver/provide and notify/inform. Synonym support is lexical and task-specific, not
general semantic paraphrase understanding. Named direct objects, `to Recipient`, explicit named
receipt/acceptance/delivery/execution triggers and textual calendar duration/date phrases are
retained. Timing is never recalculated; Phase 3 temporal code remains untouched.

Explicit full-modal subjects separated by sentence, semicolon or coordination can form separate
records in a clause. Shared implicit subjects/actions, compound objects, multiple triggers, complex
conditions, negation, exceptions, amendment cues and unresolved recipients require uncertainty.
Two identical simple `If approved` or `If requested` conditions can be compared syntactically;
their truth is never evaluated. Other conditional language remains outside the small grammar.

Cross-section object references use the unchanged Phase 2 resolver. Exactly one resolved section
with one direct supported target and the same action may supply the referenced object/instance.
The target and citation evidence are both retained. Responsibility is never inherited. Target
conditions, exceptions or uncertainty require review, and duplicate/missing/recursive/multiple
targets are unresolved. This narrow convention is not general incorporation-by-reference reasoning.

## Pair decision contract

| State | Meaning |
| --- | --- |
| MATCHED | Required explicit identity fields agree; no unresolved binding cue; potentially comparable only |
| DIFFERENT | A relevant explicit actor/action/object/instance/recipient/scope/phase differs |
| UNCERTAIN | Required field, coreference, event occurrence, trigger relationship, condition relationship or exception interpretation unresolved |
| UNSUPPORTED | Unsupported action/grammar, markup, or incomplete bounded parse |

An explicit known identity difference can establish DIFFERENT even when some other field remains
uncertain. That state never means conflicting duties. Different or one-sided triggers/conditions
are not guessed equivalent. One-sided recipient detail requires review. Reasons, compared values,
record IDs and evidence accompany every emitted decision.

Limits: inherited 250,000-character source bound; 8,192-character statement bound; 100 records and
1,000 pairs. If record, pair or structural inventory is truncated, all returned pairs abstain as
UNSUPPORTED and completion/limit metadata remains visible. Raw markup is unsupported; normalized
public HTML probes use an explicitly labelled derived text view. Offsets are never PDF geometry
or claims of mapping normalized text back to original HTML byte positions.

## Integration and preservation

`POST /v1/experimental/obligation-bindings` accepts `{job_id, experimental: true}` with strict
boolean opt-in and the existing owner authentication. It operates on a completed saved analysis
with original extracted source and clause inventory. Legacy records without that evidence require
reanalysis. The result is persisted as `metadata.obligation_binding`; existing neural/date/reference/
graph output and analysis state are unchanged. PDF and DOCX append a clearly identified experimental
section only after opt-in. There are no frontend changes or new models/dependencies.

The pre-change preservation snapshot covers dirty user files and all historical results. Full
native tests and actual-model parity verify separation; no Git mutation, deployment, source-data
deletion, model edit or detector threshold change is authorized or performed.

## Evaluation boundary

The pre-implementation protocol, mechanically labelled input slots, family split and hashes are
under the new Phase 4A evaluation directory. Development has 28 documents, evaluation has 30;
each split has one provisional interpretation case with null gold. Document/template-family IDs
and exact texts are disjoint; both share the declared small ontology and authoring rules. These
are author-controlled synthetic families, not independently annotated real legal holdouts.

The first benchmark draft contained an unsupported-literal field annotation error; the draft was
retained and corrected before production code or predictions existed, then final inputs frozen.
Only development inputs enter unit tests. Source/tests/protocol are frozen before first reserved
evaluation predictions. The reserved split is evaluated once; failures are retained without tuning
against it. Every metric includes its denominator, coverage and abstention; provisional legal
interpretations and public-source smoke never acquire manufactured accuracy labels.
