# LexAudit Phase 1 — errors and improvement priorities

2026-10-26. **Analysis only: no detection algorithm, threshold or model change in this phase.**
All case files, per-clause predictions and full evidence are under
`evaluations/phase1_detection_baseline_2026_10_26/`. Counts below use unique TXT documents unless
authored/transport mode is explicitly named. See `results/frozen_primary/decisions.csv` for every
mechanical confusion outcome; all provisional cases remain outside legal classification metrics.

## False-positive evidence

| Case | Gold and observed prediction | Diagnosis |
| --- | --- | --- |
| R17 | Existing `Section 1.1(a)` cited correctly above; two dangling flags, including the heading itself | Implementation bug: declarations index `1.1`, while citation processing produces malformed `1.1(a` without closing parenthesis. Graph correctly resolves this case and emits no finding |
| T08 | December 31 record relates to an independent January 1 historical entry; `INVERTED_DATE_RANGE`, delta=-364 | Implementation bug: substring `to` in `relates to` is sufficient to infer an ordered range. No service interval was stated |
| T12 | Agreement A June→December and B January→March are individually ordered; cross-agreement `INVERTED_CONTRACT_TERM`, delta=-92 | Implementation/scope limitation: global all-effective × all-end comparisons pair A's June start with B's March end |
| O09, order proxy only | Original unperturbed generic six-clause document; all six clauses MEDIUM, max B=.7053, max E=.3527, A=0 | Model/task/aggregation limitation. This is a false order-change alarm; there is no independent legal label permitting a legal-FP claim |

R16 receives a coarse document TP for its missing `(b)` reference but also flags its valid `(a)`
heading. Document-level precision masks this localization/spurious-flag problem. It should not
be treated as evidence that the subclause parser is working correctly.

## False-negative evidence

| Case | Missed fact and actual behavior | Diagnosis |
| --- | --- | --- |
| R11/R12 | Missing Section 9 in sentence-start citations; no reference flags | Declaration regex mistakes a citation at line start for a target. Segmentation also treats it as a new numbered clause. Graph correctly requests review |
| R15 | Only `1.1` declared, exact-identity citation `1.01` missing; legacy rule resolves it | Normalization-policy limitation: decimal aliases collapse distinct author-specified identities. Graph requests review. Need explicit identity policy rather than assume all contracts use this namespace |
| R25 | Missing `Sections 8 and 9`; neither legacy reference rule nor graph recognizes it | Unsupported plural citation grammar; graph silently returns NO_FINDINGS rather than review |
| R28 | Missing Exhibit Z appears as `Exhibit Z supplies...` at line start; no reference flag | Citation incorrectly self-declares exhibit attachment |
| R23/R24 | Target actually below, cited `Section 1, above` or `above Section 1`; graph NO_FINDINGS | Supported direction grammar is too narrow. Punctuation/preposed relationship is discarded; these are misses of clear author-defined positional predicates |
| T13 | Effective June 1 after May 1 termination; authored mode flags -31 days, TXT/PDF/DOCX do not | Segmentation bug: date-leading lines become numbered clauses. June date is assigned TERMINATION_DATE from following text; May becomes GENERAL_DATE |
| T16 | Effective date appears over 60 characters after its role; end is earlier; no date flag | Fixed local role window misses association; parsed start is GENERAL_DATE |
| S04 | Plain comparison text contains missing Section 9 between `<` and `>`; authored mode flags, TXT/PDF/DOCX silently lose citation | Source-loss bug: HTML stripping deletes `< 100, payment follows Section 9; if volume >`. Remaining normalized text is `If price   20, delivery is expedited.` |
| O02–O04/O06–O08, order proxy only | Changed MSA/SLA orders receive no B/ensemble alert | Model/task limitation: adjacency head does not distinguish these orders enough to cross frozen alert trigger. A is order-independent and detects none of nine changed-order documents |

There are six TXT reference FNs, two graph positional FNs and two date FNs in the labelled subsets.
These task denominators overlap and must not be added into one legal-error miss rate.
No legal false negatives are assigned to the provisional distant-contradiction examples.

## Segmentation and extraction errors

Thirteen TXT cases differ from authored units/text: R11, R12, R14, T13, T17, S01, S02, S03,
S04, S05, O01, O02, O04. The complete observed/expected spans are in `summary.json` and raw
predictions. R14 contains two true headings inside one authored unit, so its split can be useful;
S05's HTML cleanup is intentional normalization. These are not all erroneous legal boundaries.

S01's two unnumbered paragraphs merge; S02's line-wrapped `100 units` splits; S03's internal
all-caps line splits. T17's date-leading lines create four units instead of two but the mechanical
chronology flag survives; a segmentation mismatch does not necessarily cause a detector error.
MSA Exhibit A merges into a preceding clause for three orders, while reversal changes its placement
enough to change segmentation. This can confound neural comparisons across order operations.
Authored-mode order metrics were therefore reported separately and happened to have identical
document confusion counts to TXT; this does not mean all scores or boundaries were identical.

All normalized-source offset checks passed, which does not establish preservation of the raw input.
The S04 source-loss failure passes those checks. PDF and DOCX transport checks reproduced rather
than repaired this problem. No scanned-PDF/OCR or table accuracy claims follow from these probes.

## Correct abstentions and silent omissions

Graph correctly requests review in R10/R11/R12/R15/R16 (unresolved numeric target), R13/R14
(duplicate target), R18/R19 (unsupported Roman identity), and provisional R20 (vague boundary
antecedent). It does not fabricate a directional conflict for these uncertain targets. That is the
intended conservative behavior. R25 and extracted S04 evade even review; NO_FINDINGS is not
successful abstention. The graph lacks exhibit support, so R27/R28 silence is a scope limit,
not evidence of a present exhibit.

T14's February 30 is calendar-invalid but dateparser returns no date; no review is emitted. T11's
03/04 and 04/03 are assigned month/day values without locale review. Neither is a correct explicit
abstention. T14 is excluded from chronology F1 because calendar validity is a distinct unsupported
task, and T11 has no unique chronology gold without locale. These exclusions were predefined.

## Statistical signals mistaken for defects

W02 and W04, intended benign but unadjudicated unusual wording, receive two MEDIUM ML alerts each;
W01/W03 receive none. W02 has A=0, B=.7019, E=.3509. This is an existing single-channel trigger,
not evidence that wording is legally defective. Without expert negative labels, do not call the
2/4 alert frequency a legal false-positive rate.

C01/C02/C03/C04 receive 3/3/4/2 ML alerts. Alerts often attach to the common intervening notices
and definitions. There is no scored relation connecting the distant obligation pair. A potential
same-invoice 30/60-day conflict, a compatible disputed-invoice exception, a potential disclosure
exception and compatible monthly/annual fees cannot be distinguished as legal conflicts by these
alerts. No TP/FN or contradiction accuracy can be credited without adjudication and relation evidence.
T15's expressly allowed advance deposit still gets PAYMENT_BEFORE_EFFECTIVE_DATE; the arithmetic
is true but legal invalidity does not follow. Calibration intervals are nearly uninformative here
(210/222 full [0,1]); they do not repair missing semantics or labels.

## Reproducibility findings and validation limitations

All model scores, outcomes and graph decisions repeated across all 148 analyses. Python set
iteration changed the ordering of declared targets, available-target samples and involved clause
IDs across processes. Comparison canonicalizes only those unordered fields and ignores UUIDs/
timestamps; no numerical differences are hidden. Raw records retain the ordering differences.
This is a minor presentation/reproducibility limitation, separate from scientific prediction drift.

Known source/parser failures are implementation issues; poor sensitivity to permutations and absence
of nonlocal logical inference are model/task limits. The interpretation of unusual wording,
exceptions, legally meaningful reordering and real contradictions is primarily missing ground truth.
Historical random pair-level validation may share documents between train and validation; it is
not a replacement for family-separated evaluation. No new legal validity labels were invented.

## Three priorities for the next authorized phase

1. **Shared, source-preserving structural parsing and reference resolution — implement first.**
   Distinguish actual headings from citations, preserve plain-text operators, keep full hierarchical
   target identities, retain duplicate targets, recognize singular/plural/punctuation/preposed references,
   and abstain on unresolved syntax/identity policies. Use the same structural inventory for segmentation,
   reference checks and graph edges, with a raw-to-normalized offset map. Evidence: six reference misses,
   R17's false flags, two directional misses, S04 source loss and T13's boundary-induced miss. Begin
   with plain-text preservation and line-start declaration/citation discrimination, then hierarchical
   identity resolution. Acceptance: retain current canonical true findings, recover specified challenge
   evidence, preserve duplicate/unknown reviews and source spans. All current cases remain development
   regressions; add a genuinely new evaluation before claiming generalization.
2. **Scope-aware temporal relation extraction with explicit uncertainty.**
   Associate dates with the correct agreement/event and full role phrase, require actual range syntax,
   preserve roles across line wraps, and request review for ambiguous locale/invalid dates. Represent
   chronology predicates separately from judgments about permitted prepayment or survival. Evidence:
   T08/T12 false alarms and T13/T16 misses. Acceptance: avoid cross-scope comparisons and non-range
   `to` matches; retain canonical date detections; expose parser uncertainty rather than silently dropping it.
3. **Task-specific document relation scoring with an abstention gate, after credible labelled data.**
   Separate order anomaly, topic novelty and distant obligation conflicts. First measure existing B
   probabilities/aggregation on document/family-separated labels including valid reorderings; collect
   qualified annotation of entity/action/scope/exception/precedence relations. Then evaluate an explicit
   relation-based distant-clause verifier and conservative abstention rather than treating adjacent
   scores as contradiction proof. Evidence: 3/9 order sensitivity, unchanged O09 alerts and no pair
   evidence in C01–C04. No basis exists yet to choose new thresholds or promise improved legal accuracy.
   Reuse frozen embeddings/models where possible; large retraining is not justified by this baseline.

The first priority has deterministic, inspectable failures affecting multiple channels before neural
scoring and can be verified without fabricated legal labels. Fixing that layer makes later scientific
evaluation interpretable. It was deliberately **not implemented** in this frozen baseline phase.
