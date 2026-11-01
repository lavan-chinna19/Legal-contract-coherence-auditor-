# Phase 4A evaluation results — 2026-10-28

This is author-controlled synthetic evidence for explicit-field obligation comparability, not
legal-error accuracy. No qualified reviewer supplied labels; no large model generated or validated
them. Original datasets, Phase 1/2/3 evidence and the frozen reserved-split predictions are intact.

## Phase 3 audit

All original reported confusion matrices and their precision/recall/F1/FPR reproduce from final
raw observations. Supported relational coverage is correctly **22/50 (44%)**. The final raw
review/unsupported union is **20/50 (40%)**, not the stale 21/50 (42%) in the Phase 3 prose and
previous conversation. Review count is 15, not 16; supported statements are 96/118 (81.36%), not
94/118 (79.66%). See the additive erratum in the design report and `phase3_audit_verified.json`.
No historical report was overwritten to hide the discrepancy.

## Frozen benchmark and scope

* Development: **28** pair documents, 27 mechanically labelled four-state cases, one provisional.
* Reserved evaluation: **30** pair documents, 29 mechanically labelled four-state cases, one provisional.
* Binary comparability subset: development **14** (7 same / 7 different), evaluation **16**
  (8 same / 8 different). Cases whose relationship is uncertain have null binary gold, not a
  manufactured negative label. Provisional interpretation cases also have null state gold.
* Inputs, expected fields, protocol and construction script were frozen before production code.
  Source/tests were frozen after development/native verification and before reserved evaluation.
  The reserved split was predicted once; no binding code changed after exposure.

Document/template-family IDs and exact texts are disjoint. Development uses shall/shall renderers;
evaluation uses is-required-to/must renderers plus passive/joint-subject diagnostics. These are
separate whole-document surface templates, but the ontology, lexical map, slot-based construction
rules and some diagnostic clause forms are shared. This does not establish phrase-level novelty
or independent natural-contract family generalization. Do not describe it as a blind legal holdout.

Early benchmark draft literal-field annotations were corrected before implementation; originals
are retained in `benchmark_draft/`. A later occurrence/type label problem found after exposure
is explicitly discussed below; first-pass labels and metrics were not rewritten.

## Pair matching: full and selective denominators

MATCHED is a positive comparability screen, not a contradiction. For binary-labelled cases,
DIFFERENT/UNCERTAIN/UNSUPPORTED are negative screens: a positive abstention is FN, while a
negative abstention is only screen TN. Unknown binary gold does not enter TP/FP/FN/TN.
All cases still enter state counts, coverage and abstention; unsafe confirmations on labelled
UNCERTAIN/UNSUPPORTED cases are counted separately rather than hidden outside binary gold.

| Split / task | TP / FP / FN / TN | P | R | F1 | FPR | FNR |
| --- | --- | --- | --- | --- | --- | --- |
| Development full binary, n=14 | 7 / 0 / 0 / 7 | 100% | 100% | 100% | 0% | 0% |
| Reserved full binary, n=16 | 7 / 0 / 1 / 8 | 100% | 87.5% | 93.33% | 0% | 12.5% |
| Development selective binary, n=14 | 7 / 0 / 0 / 7 | 100% | 100% | 100% | 0% | 0% |
| Reserved selective binary, n=15 | 7 / 0 / 0 / 8 | 100% | 100% | 100% | 0% | 0% |

Selective scores exclude the unsupported passive positive. They must never replace the full
reserved recall of 87.5%. P=TP/(TP+FP), R=TP/(TP+FN), F1=2TP/(2TP+FP+FN), FPR=FP/(FP+TN),
FNR=FN/(FN+TP); undefined denominators are null in machine-readable summaries.

| Split | MATCHED | DIFFERENT | UNCERTAIN | UNSUPPORTED | Decided / all | Abstained / all |
| --- | --- | --- | --- | --- | --- | --- |
| Development | 7 | 7 | 12 | 2 | **14/28 (50%)** | **14/28 (50%)** |
| Reserved evaluation | 7 | 8 | 12 | 3 | **15/30 (50%)** | **15/30 (50%)** |

Each split's UNSUPPORTED count includes the unscored provisional example. On state-labelled
examples, development has 27/27 expected states; reserved has **28/29 (96.55%)**, with one
MATCHED -> UNSUPPORTED error. This four-state development-policy score is not legal accuracy.
Unsafe MATCHED predictions on expected UNCERTAIN/UNSUPPORTED cases: **0/13** in each split
(12 uncertainty cases plus one unsupported-action case). Provisional cases remain unscored.

## Actor, action, event, trigger and other fields

Expected records in scored source sections: **55 development / 59 evaluation**. All were represented;
no missing or extra records in those labelled sections. This is modal-record coverage, not complete
obligation recognition. Unsupported/partial records can exist without correct required fields.
Additional duplicate-target sections in reference diagnostics are not independently field-labelled.

| Field | Development exact / cells | Reserved exact / cells | Reserved non-null precision | Reserved non-null recall |
| --- | --- | --- | --- | --- |
| Actor | 55/55 | **56/59 (94.92%)** | 54/55 (98.18%) | 54/57 (94.74%) |
| Action | 54/55 | **56/59 (94.92%)** | 56/56 (100%) | 56/59 (94.92%) |
| Object | 50/55 | **52/59 (88.14%)** | 52/52 (100%) | 52/59 (88.14%) |
| Recipient | 55/55 | **59/59** | 5/5 | 5/5 |
| Trigger | 55/55 | **59/59** | 50/50 | 50/50 |
| Event instance, raw frozen labels* | 53/55 | **55/59 (93.22%)** | 50/50 | 50/54 (92.59%) |

Exact-cell rates include correctly absent fields. Non-null precision/recall expose extraction
coverage: a missing expected value is a miss; a wrong non-null value is both a precision and a
recall error. Five stated recipients are a small denominator. No model confidence scores apply.

**Event-instance annotation caveat:** two cells in each split's recurring-month case wrongly copy
the named invoice type as occurrence gold, despite no unique occurrence being established. Pair
gold UNCERTAIN remains correct. Raw labels/results remain unchanged and the raw event-instance
metric above is not a clean occurrence-accuracy estimate. Post-exposure audit identifies the cells;
excluding only these two cells gives an explicitly **posthoc sensitivity** of 53/53 development
and 55/57 reserved exact cells. That is not a replacement untouched result or an independent
annotation. The other passive, actor and generic-object failures remain counted.

## Guard ablation and errors

There was no historical Phase 3 obligation-pair classifier. A separately labelled ablation uses
the **same new extractions** but compares only actor/action/object, ignoring binding guards. It
is not represented as old production behavior or an independent baseline model.

Development ablation binary: 7/3/0/4, P70%, R100%, F1 82.35%, FPR42.86% (n=14).
Reserved ablation binary: 7/3/1/5, P70%, R87.5%, F1 77.78%, FPR37.5% (n=16).
Binding guards remove three binary false matches per split (recipient, scope and phase) and
seven unjustified confirmations on uncertainty-labelled pairs (trigger, condition, exception,
one-sided recipient and recurrence). One further state change distinguishes unsupported grammar.
There are 11 corrected four-state ablation outcomes per split, zero newly wrong state outcomes
relative to that ablation; the passive positive remains a miss under both.

Reserved exact failure: `evaluation_passive_identity`, “Invoice Cedar must be paid by Purchaser …”
is MATCHED by construction but UNSUPPORTED by this active grammar. The positive abstention is FN.
`evaluation_coordinated_subject` reaches the correct DIFFERENT pair state but wrongly extracts
Vendor from Purchaser-and-Vendor: the explicit compound subject was split. This actor field error
is retained, not excused by the correct pair outcome. Generic object/raw reference fields and an
unsupported reconcile action also lose extraction coverage. Full per-field evidence/errors remain
in `results/evaluation_first_pass/errors.json` and `post_evaluation_error_audit.json`.

## Public-source and preserved-output checks

Six existing public SEC exhibits were probed: three smallest reference-style exhibits and three
substantive exhibits selected by a fixed 20–200 KB size stratum/path order. Each ran as raw source
and an explicitly labelled existing HTML-normalization view: 12 observations, zero legal labels.
Raw markup abstains. The three substantive normalized views produce 2, 1 and 5 modal records;
their 11 candidate pairs are all unsupported. The reference-style probes produce no supported
obligations. Exact source spans pass. There is **no measured public-contract matching accuracy**,
and these results demonstrate inadequate practical coverage for broad contradiction detection.

Existing output preservation: 148/148 actual frozen neural, structure, reference and graph outputs
match. All 148 unified temporal results agree with the directly called unchanged Phase 3 checker;
38/38 original temporal modes also match saved Phase 3 metadata and flags exactly. All frozen core
hashes match. Full native: **440 passed, 0 failed, 2 optional skips**. Details in the implementation report.
