# Phase 4A pre-implementation protocol — 2026-10-28

This protocol and labelled inputs are written and hashed before binding production code exists.
No expert adjudication is claimed. Synthetic labels are author-defined explicit slot/grammar
identities, not legal truth. Ambiguous/legal interpretations receive null gold, not invented truth.

## Task and representation

Extract explicit actor, action, object, recipient if stated, trigger, event instance, deadline,
conditions/exceptions, agreement/phase, source section/offsets and uncertainty. Evidence is exact
source text. Compare two records as MATCHED (potentially comparable), DIFFERENT (explicit relevant
field difference), UNCERTAIN (insufficient bindings or unknown condition/trigger relation), or
UNSUPPORTED (grammar/limits outside the bounded implementation). Matching never asserts conflict.

Action normalization is a small published lexical mapping (pay/remit, deliver/provide, notify/inform).
It supports only controlled direct obligations, not general semantic paraphrases. Explicit named
objects (Invoice Alpha, Report Bravo, Shipment Cedar, Notice Delta) also identify an event instance
for the constructed task; recurring/each-month language cannot establish the same occurrence.
Party names remain exact normalized strings, no coreference or guessed corporate aliases.
Recipients are optional, but one-sided recipient detail is uncertainty; explicit different recipients
are different. Explicit different actors/actions/objects/instances/scopes can establish DIFFERENT.
Different or missing-one-side triggers and different condition strings require UNCERTAIN.
Identical simple explicit conditions are potentially comparable, without evaluating their truth.
Exceptions, amendments, negation, ambiguous pronouns and complex conditions abstain.
Unstated timing is retained as missing; matching structural obligations can still be possible when
both lack deadlines, but no timeline comparison or contradiction follows.

Section references use the unchanged Phase 2 resolver. A unique explicit target with one supported
obligation may supply a referenced object/instance only if the local actor/action are explicit and
the reference is resolved. Missing/duplicate/recursive/multiple targets require uncertainty.
Evidence must identify both source record and target. No reference imports conditions or responsibility.

## Labels and split policy

Development and evaluation use disjoint document/template-family IDs, full input hashes and exact
template descriptions. No document or exact text appears in both. They share the declared controlled
ontology/slot rules; this is not independent natural-contract generalization. Evaluation examples
are authored by the same agent with transparent mechanical rules, never expert/model-independent
legal labels. Even a pre-frozen split is not an independent real-world holdout.

Freeze all input files before implementation; develop only on the development file. Freeze source,
tests, input hashes and protocol before first evaluation split prediction. Do not change production
binding rules after observing evaluation labels/predictions; record failures and recommend future
work instead. Additional bug fixes before source freeze are allowed using development/unit cases.
Evaluation exposure is recorded once in an append-only run directory; no case-ID production logic.

## Metrics and denominators

Unit: one labelled obligation pair. MATCHED is the positive comparable-identity task. DIFFERENT is
negative. UNCERTAIN/UNSUPPORTED are abstentions; mechanically unknown pairs have null binary gold.
For binary full-denominator screening, a MATCHED prediction is positive and everything else negative:
positive abstentions are FN; negative abstentions are screen TN, never proof of different obligations.
Report TP/FP/FN/TN, precision, recall, F1, FPR=FP/(FP+TN), FNR=FN/(FN+TP), null on zero denominator.
Also report four-state accuracy/confusion on explicitly labelled states, prediction coverage
(MATCHED+DIFFERENT)/all pairs and abstention (UNCERTAIN+UNSUPPORTED)/all pairs; selective metrics
must include their actual denominator. Unsupported-vs-uncertain choice is an implementation policy,
not expert legal truth. Do not give provisional interpretation cases four-state accuracy labels.

Field extraction metrics: exact normalized actor/action/event-instance/trigger values per expected
record; missing and wrong values both count as full-denominator failures. Also report non-null
field precision/recall and parsed-record coverage. Count multiple-obligation records, omissions,
extras and null cases explicitly; record source evidence, expected and observed values per case.
No overall legal-accuracy percentage or calibrated probability is defined.

## Preservation and integration

New module is separately experimental and opt-in through an authenticated existing-job route;
save its output separately and show it in existing PDF/DOCX exports only after opt-in. Do not alter
neural, structural, reference or Phase 3 date outputs/state. No frontend edits. Source preservation
hashes include preexisting dirty work and all earlier evaluation files. Actual frozen model parity,
full native regression, TXT/PDF/DOCX workflows, public-contract smoke without labels, missing/ambiguous
data and bounded long-input tests are required. Docker only if engine exists; no recovery/reset.
