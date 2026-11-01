# Phase 3 error and false-positive analysis

See `PHASE3_BEFORE_AFTER_EVALUATION.md` and the retained per-case JSONL for the actual metrics,
coverage and label provenance. Mechanical labels assert explicit constructed constraints, not
expert legal truth. No synthetic clause reorder is presumed to be a legal error.

## Corrected legacy failures

| Evidence | Cause | Correction and limitation |
| --- | --- | --- |
| T08: reversed incidental dates with `relates to` | Substring range detection confused `to` with a range | Require explicit from/to or between/and grammar; roleless incidental dates remain review |
| T12 / N03: individually valid Agreement A and B | Global effective/end cross product | Compare only matching explicit agreement scope and phase |
| T13: dates split onto source lines | Neural segmentation lost role association for date-only fragments | Read unchanged Phase 2 source units while preserving neural inputs |
| T16: effective role beyond 60 characters | Fixed local window missed a valid source relation | Use supported full-statement context and unique unit-role fallback |
| T11 / N20: ambiguous numeric date | Old parser silently selected numeric locale | Retain raw date, abstain and report ambiguous locale |
| T14 / N21: February 30 | Invalid input disappeared | Retain invalid-date uncertainty rather than invent ISO or silently drop it |
| T15 / N08 / N24: advance or retroactivity | Arithmetic precedence was treated too strongly | Explicitly permitted advance is consistent; interpretive cases remain potential, with null legal gold |
| N13 / N16 / N48 | Different deadline magnitudes looked contradictory | Intersect offset intervals; overlapping bounds are potential differences, not confirmed conflicts |

## New-engine failures found and fixed during development

These are actual failed predictions, not hypothetical risks. The original challenge outputs and
the failed native run remain saved; challenge inputs are explicitly post-implementation exposed
development examples. No case-ID conditions exist in production code.

| Case | Initial error | General fix |
| --- | --- | --- |
| C01 | Negated effective date treated as positive singleton | Preserve negation as uncertain, exclude from firm fact comparisons |
| C02 | Two named events in one sentence both assigned to first event | Bind to nearest preceding explicit event |
| C03 | Same event label across Buyer/Seller contexts falsely merged | Preserve separate explicit party context; do not invent responsible actor |
| C10 | Two modal actors assigned to first actor | Abstain on unresolved multiple action binding |
| C11 | Phase 1 and Phase 2 event dates falsely merged | Retain explicit named phase and partition relations |
| C05 | Thirty-one-day deadline missed | Support bounded compound-number grammar; never partially parse unsupported hundreds |
| C07 | Between/and inverted interval missed | Add narrow explicit range grammar with unchanged source spans |
| Native MSA negative control | `termination date shall be` became actor/action and aliased two term dates | Exclude date/term/event subjects as parties; preserve endpoint role over modal obligation alias |

The MSA failure occurred in `full_native_v1.xml`: 391 passed, one failed, two skipped. Its
zero-alert expectation remains covered. Its generic receipt deadline lacks a calendar basis,
unique named trigger and operational actor; the upgraded API now correctly reports REVIEW_REQUIRED.
The original NO_FINDINGS test keeps every zero-alert/export assertion but uses explicit ordered
term endpoints. A separate actual-model MSA workflow requires zero alerts **and** retained review
state; additional unit tests exercise the false-conflict fix. This is a deliberate behavioral
contract correction, not a suppressed failure or a model/threshold change.

Additional regression guards cover negated ranges, alternative dates, inequality term endpoints
and conditional milestone anchors. These are targeted grammar tests, not independent accuracy data.

## Correct abstention and remaining misses

Business-day cases N17/N49 and C09 retain unsupported calendar evidence. N18 has no unique trigger;
N19 no explicit actor; N20 ambiguous numeric dates; N21 invalid dates; N44 written/numeric mismatch;
N51 timezone semantics; N35/N50 month/year rollover policy. Missing relationships are never guessed.
Some exact date facts in different scopes are parsed without a comparison; this is not abstention
and also not evidence that the whole contract is consistent.

No final labelled false confirmations/misses remain on the narrow exposed subsets. That does
not imply zero remaining algorithmic errors. Complex syntax, implicit obligations, pronouns,
repeated event instances with the same name, unrecognized legal conditions, attachment-defined
timing, jurisdictional calendars and amendment precedence can still be missed or misbound.
Multiple actors in one sentence currently lose coverage by design. There is no independently
labelled corpus on which to count these generalization errors. Provisional examples stay unscored.

The existing neural channels retain exactly their earlier capabilities and limitations. A semantic
or transition anomaly is a statistical candidate, not a legal defect. No phase claims additional
neural contradiction accuracy from these deterministic-rule improvements.

## Highest-impact next work

1. **Improve source-backed actor/action/event-instance binding with an annotated error set.**
   Distinguish recurring events, aliases, embedded subclauses, conditions and override scope before
   broadening comparisons. Include hard negatives and independent adjudication of intended meaning.
2. **Add explicit calendar/trigger policies through user-supplied metadata.** Calendar basis,
   jurisdiction, holidays, receipt event, rollover and inclusion conventions must be supplied and
   visible, with abstention whenever absent. Do not silently assume business-day policy.
3. **Research distant-clause contradiction candidates only after establishing a held-out protocol.**
   Link explicit entities/obligations with evidence and abstention; benchmark retrieval and reasoning
   separately on expert-labelled pairs, across unseen document families, before calling it detection.

For Phase 4, start with the first item and independent annotation/protocol design. A limited
experimental evidence graph can then connect explicit obligations; unrestricted legal contradiction
classification is not justified by the current exposed synthetic results. Do not retrain a large
model or recalibrate the frozen channels merely to raise development scores.
