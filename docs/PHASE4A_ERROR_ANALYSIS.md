# Phase 4A error analysis and decision

This document reports actual observed failures and limits, not a general legal assessment.
All frozen predictions, failing test attempts, expected fields and source evidence remain available
under `evaluations/phase4a_obligation_binding_2026_10_28/`. No source or labels were tuned after
the first reserved split evaluation.

## Observed failures

1. **Passive same-obligation pair missed.** Reserved `evaluation_passive_identity` says
   “Invoice Cedar must be paid by Purchaser within 10 calendar days after receipt of Invoice Cedar”
   on each side. Explicit same actor/action/object/trigger supports mechanical comparability, but
   the active grammar reads the modal verb `be` as unsupported. It does not recover a by-agent.
   Result: one FN; full binary recall 7/8, not the selective 7/7. Both source records retain raw
   evidence and unsupported reasons. Expansion to passive syntax remains future work.
2. **Joint subject represented incorrectly.** `evaluation_coordinated_subject` has “Purchaser and
   Vendor must remit Invoice Cedar …”. The coordination splitter treats Vendor as a fresh subject
   and drops Purchaser. The DIFFERENT pair state happens to agree with the sole-vs-joint gold,
   but the extracted actor is wrong. This is an implementation limitation, not legal ambiguity,
   and it could misbind other cases. It remains reported in the experimental layer; no change is
   made after evaluation exposure to manufacture a better untouched result.
3. **Generic/raw-reference object coverage is low.** “the invoice” lacks a unique named occurrence;
   missing/duplicate target references cannot resolve an object. Pair abstention is correct, while
   the object's literal phrase may still be an extraction miss against the benchmark. The system
   does not confuse a parsed object string with established event identity.
4. **Unsupported action lexicon.** `reconcile the accounts` is outside the declared small map.
   Its state abstains correctly, but action/object field recalls lose a cell. This is not silently
   removed from the field denominator.
5. **Recurring event gold contains a type/instance defect.** Two event-instance cells per split
   identify Invoice Alpha/Cedar rather than a unique monthly occurrence. The source does not
   justify that occurrence label; the matcher correctly leaves it unknown. The defect was found
   in post-exposure error review. Raw frozen labels/results are retained and explicitly qualified;
   the separate sensitivity calculation excludes those cells transparently. No pair label or
   full binary score changes. This is an annotation-design defect, not a validated algorithm miss.

## Useful abstention and guard corrections

Different or one-sided triggers, differing conditions, exceptions, ambiguous pronouns, missing
actors, recurring occurrences and missing/ambiguous section targets preserve review reasons.
Only identical supported simple conditions can be compared without evaluating truth. Known
different actors, actions, objects, recipients, scopes or phases can establish DIFFERENT; none
of these are automatically legal conflicts.

The actor/action/object-only ablation wrongly confirms ten cases per split: three mechanical
DIFFERENT cases and seven mechanically UNCERTAIN cases. Guards correct all ten and classify one
unsupported case more precisely. Eleven four-state ablation errors are corrected per split, with
zero newly wrong state outcomes relative to that ablation. This is an internal guard ablation,
not a claim of fixing eleven historical legal defects. No historical binding classifier existed.

On the reserved binary subset there are no FP, one FN, seven TP and eight TN. The null-binary
cases are not quietly counted as negatives: their four-state labels, coverage and unsafe-match
counts remain visible. One provisional case per split has no state or binary accuracy label.
Coverage is only 15/30 (50%) for the reserved split; even perfect selective precision does not
support a general detection claim.

## Public contracts and missing evidence

Reference-only public exhibits contain no supported modal obligations. Substantive normalized
public exhibits produce eight partial modal records and eleven unsupported pairs; raw HTML is
unsupported. These unlabelled probes establish runtime/span behavior, not extraction recall,
comparability accuracy or legal validity. Long-document pair/record limits deliberately abstain
and advertise incomplete coverage. No independent human review, unseen natural document-family
test or external security validation was performed.

## Phase 3 audit erratum

Confusion matrices and 44% supported relational coverage reproduce. The final saved Phase 3
review/unsupported union is **40% (20/50)**, not the stale 42% in the prose; supported statements
are 96/118. This was reported before binding implementation and preserved as an additive erratum.
It is a reporting error, not a reason to alter historical measurements or frozen date logic.

## Phase 4B: NO-GO for automatic distant-clause contradiction detection

Current evidence supports a narrow opt-in explicit-field binding prototype. It does not support
reliable general actor/action/event identity in natural contracts, nor the additional reasoning
needed to infer contradiction. Joint-subject failure, passive coverage, event-instance ontology,
50% synthetic abstention, unsupported public pairs and absent independent labels are material.

The next bounded work should repair joint/passive binding and the type/occurrence annotation
schema on exposed development evidence, then freeze fresh family-separated evaluation inputs.
Obtain qualified annotations for difficult/public pairs before measuring legal contradiction.
A human-review retrieval experiment may be researched separately with evidence and abstention;
it must not be released or described as validated automatic contradiction detection. No additional
large model, indefinite benchmark expansion or neural retraining is justified by this phase.
