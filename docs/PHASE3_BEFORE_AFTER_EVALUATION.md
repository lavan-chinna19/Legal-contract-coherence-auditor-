# Phase 3 paired evaluation — 2026-10-28

Authoritative run: `evaluations/phase3_temporal_reasoning_2026_10_26/results/paired_v3/`.
The directory date records work started on October 26, not a claim that the final run happened then.
The runner, frozen inputs, exact legacy checker, source manifests, predictions, changes, source
spans and verification JSON are retained. Earlier runs are not overwritten.

## Provenance and tasks

Original Phase 1 labels remain unchanged: 17 temporal documents, 14 with a mechanical chronology
screen label and three interpretive/uncertain cases. Their authored/TXT inputs plus selected
PDF/DOCX probes produce 38 observations. Format repetitions are not independent examples.

New inputs: 50 mechanically constructed examples and eight provisional interpretation examples.
Twelve additional mechanical challenges were authored after the first engine implementation.
These strata remain separate, explicitly exposed development data. No independent legal labels,
unseen-family holdout or external adjudication was created. The generator and construction rules
are retained; challenge errors were used to improve the grammar, so their final scores are
development regression evidence, not blind generalization estimates.

Original-case metrics compare any temporal candidate flag with the original chronology labels.
Payment-before-effectiveness and notice-after-expiry stay arithmetic candidates; they are not
silently re-labelled as definite legal contradictions. New controlled labels describe exact
constructed calendar/offset/event incompatibility. The old checker only has an any-flag screen;
its score against these new labels is an alert proxy, not an equivalent confirmed-conflict model.

Metric unit: one TXT document. P = TP/(TP+FP), R = TP/(TP+FN), F1 = 2TP/(2TP+FP+FN),
FPR = FP/(FP+TN). Undefined ratios are null in machine-readable results. A lack of confirmation
is a negative *screen*, including abstentions; it does not certify legal or parsed consistency.
A positive example that abstains counts as a miss. Selective supported-relation metrics are
reported alongside the full denominator to avoid hiding abstention.

## Measured results

| Task / stratum | Detector | TP / FP / FN / TN | Precision | Recall | F1 | FPR |
| --- | --- | --- | --- | --- | --- | --- |
| Original chronology screen, n=14 | Old any flag | 6 / 2 / 2 / 4 | 75% | 75% | 75% | 33.33% |
| Original chronology screen, n=14 | New any flag | 8 / 0 / 0 / 6 | 100% | 100% | 100% | 0% |
| New mechanical, n=50 | Old alert proxy | 4 / 5 / 9 / 32 | 44.44% | 30.77% | 36.36% | 13.51% |
| New mechanical, n=50 | New confirmation screen | 13 / 0 / 0 / 37 | 100% | 100% | 100% | 0% |
| Post-implementation challenges, n=12 | Old alert proxy | 0 / 1 / 2 / 9 | 0% | 0% | 0% | 10% |
| Post-implementation challenges, n=12 | New confirmation screen | 2 / 0 / 0 / 10 | 100% | 100% | 100% | 0% |

Eight provisional cases have null gold labels: no confusion matrix or accuracy claim is made.
There is no aggregate legal-error accuracy. Perfect constructed-screen scores are explicitly
limited by development exposure, narrow grammar, very small positive counts and partial coverage.

## Coverage, abstention and alert burden

| Stratum | Explicit supported relation documents | Documents with review/unsupported decisions | Supported / recognized statements | Candidate-alert documents |
| --- | --- | --- | --- | --- |
| New mechanical, n=50 | 22/50 (44%) | 21/50 (42%) | 94/118 (79.66%) | 17/50 |
| Challenges, n=12 | 3/12 (25%) | 6/12 (50%) | 20/28 (71.43%) | 3/12 |
| Provisional, n=8 | 0/8 | 6/8 (75%) | 4/11 (36.36%) | 2/8 |

Review and unsupported counts can overlap within a document. In the new mechanical stratum,
16 documents have reviews and five have unsupported decisions; challenges have five reviews
and one unsupported; provisional cases have one review and six unsupported decisions.
Some otherwise confirmed documents also retain an unrelated review; one document-wide status
cannot express all evidence. Read the statement/decision inventory.

An explicit supported relation is a multi-statement CONSISTENT or CONFIRMED relation; parsing
a lone fact is not relational validation. Selective new mechanical results on 22 supported
documents are 13 TP / 0 FP / 0 FN / 9 TN. Selective challenge results on three supported documents
are 2 TP / 0 FP / 0 FN / 1 TN. Their P/R/F1 are 100%, FPR 0%, with the small denominators shown.
Unrecognized temporal language may be absent entirely: supported/recognized share is not a
claim of complete temporal-language extraction coverage.

New mechanical candidate-alert frequency is **17**, versus nine old alert documents. Thirteen
are confirmations and four are potential compatible-deadline differences. Reducing confirmed
false positives does not mean the number of things surfaced for human review always decreases.
Challenges surface two confirmations and one potential; six retain abstention evidence.

## Corrected and introduced errors

On the original labelled TXT task, corrected false alarms are T08 (incidental `relates to`)
and T12 (different agreements). Corrected misses are T13 (date-only line/role separation) and
T16 (role farther than the old 60-character window). No original labelled TXT regressions remain.

Against the new mechanical confirmation target, corrected old-proxy false alarms are
N03/N22/N25/N30/N41; corrected misses are N05/N10/N11/N14/N15/N31/N36/N38/N43.
The separate challenges correct C05/C07 misses and the old proxy's C12 approximate-range alarm.
No labelled final new errors remain on these exposed subsets. `changes.json` retains every
labelled before/after outcome, not only successes; full prediction JSONL retains provisional cases.

Initial new-engine challenges exposed five false confirmations (C01/C02/C03/C10/C11) and two
misses (C05/C07). Their original outputs remain in `challenge_initial_predictions.json`. A full
regression subsequently caught an additional MSA false confirmation from modal endpoint/actor
binding; its diagnostic and failing full-suite output are retained. Both kinds of development
failure are discussed in the false-positive report rather than omitted from the final score.

## Reproduction and preserved-channel checks

* All 38 pre-change legacy temporal observations reproduce. The legacy implementation creates
  involved-clause IDs from a set; reproduction sorts only that unordered list. Dates, values,
  spans, categories, descriptions, scores and thresholds are not rounded or discarded.
* All 148 Phase 2 case/mode records were analyzed with the actual offline frozen neural models.
  Neural clause results, structure, reference results and experimental graphs each match **148/148**.
* 108 temporal paired observations (38 original modes + 70 new/provisional/challenge documents)
  have exact source/date spans verified; zero parser exceptions occurred. These are not 108
  independent legally labelled documents.
* The final evaluated production source manifest is unchanged after predictions. Phase 1/2
  evidence is preserved separately. Native, format and frontend test evidence is documented in
  `PHASE3_IMPLEMENTATION_REPORT.md`; Docker runtime was unavailable.

The evidence supports a narrower, safer deterministic interpreter on the tested development
tasks. It is insufficient for a meaningful real-world legal accuracy percentage.
