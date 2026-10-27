# Phase 2 — paired before/after development results

2026-10-26. **Final verified run: `paired_v4`, exit 0.** This reuses exposed Phase 1 development
examples and is not independent legal validation, a new holdout or a real-world accuracy estimate.

## Design and evidence

The original 70 documents and labels remain frozen: 59 mechanically labelled synthetic and 11
provisional human-review; independently adjudicated examples: zero. Five original modules were
copied before changes and rerun with the same actual local frozen models. Both implementations
received identical legacy neural/date clauses. The new structural checks additionally received
the unchanged extracted source, including text the legacy cleaner could remove.

The final run executed **148 analyses per implementation**: 70 authored, 70 TXT and the same eight
PDF/DOCX transport probes used in Phase 1. These are 70 documents, not 296 independent examples.
All old component/rule/graph predictions reproduced their Phase 1 artifacts. Every new per-clause
neural score, evidence, severity and interval matched its old counterpart. Date-rule outputs were
also identical. All 148 structural unit concatenations and source spans passed preservation checks.

Machine-readable evidence is under `evaluations/phase2_structural_parser_2026_10_26/results/paired_v4/`:

* `paired_predictions.jsonl`: complete old/new audit, source, segments, graph and parity record for
  every case/mode, with original label provenance and author facts.
* `case_comparison.json` / `.csv`: all 148 rows, including unlabelled/provisional cases; original/new
  predictions, changes/reasons, corrected/regressed tasks, reviews and supporting source evidence.
  No legal correctness outcome is assigned without adjudicated legal truth.
* `comparison.json`, `old_decisions.csv`, `new_decisions.csv`: defined labelled task outcomes.
* `old_summary.json`, `new_summary.json`: all metrics with denominators, predefined strata and errors.
* `coverage.json`, `parity.json`, `verification.json`: resolver status coverage, frozen-model/date/source
  checks and success conditions. `source_manifest_before_predictions.json` identifies the evaluated code.

## Main TXT detection path — document-level metrics

| Task / implementation | n | TP | FP | FN | TN | Precision | Recall | F1 | FPR |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Missing targets, old | 28 | 3 | 1 | 6 | 18 | 75.00% | 33.33% | 46.15% | 5.26% |
| Missing targets, new | 28 | 9 | 0 | 0 | 19 | 100% | 100% | 100% | 0% |
| Directional graph, old | 15 | 4 | 0 | 2 | 9 | 100% | 66.67% | 80% | 0% |
| Directional graph, new | 15 | 6 | 0 | 0 | 9 | 100% | 100% | 100% | 0% |

The 100% values describe these small authored development subsets only. They do not demonstrate
100% contract accuracy or generalization. Cases are correlated, detector-aware and previously exposed.
Document-level precision does not establish per-citation localization precision or detect every
possible issue. Review-only outputs are not counted as positive missing/directional findings.

All **13 canonical directional cases** retained their original correct outcome (four conflicts,
nine controls); both previously missed challenge directions were recovered. Missing-reference
predefined strata now have canonical 2 TP/15 TN, challenge 7 TP/2 TN, Roman controls 2 TN.
All original task labels and strata were retained, not reassigned to improve metrics.

## Corrected errors and unchanged coarse outcomes

| Case | Old → new | Source-backed reason |
| --- | --- | --- |
| R11 | Reference FN → TP | Sentence-start `Section 9 above applies` is a citation, not a declaration |
| R12 | Reference FN → TP | Sentence-start `Section 9 shall apply` cannot declare its missing target |
| R15 | Reference FN → TP | Exact namespace keeps `1.01` distinct from declared `1.1`; this is the corpus's explicit policy, not a universal legal numbering rule |
| R17 | Reference FP → TN | Declared/cited `1.1(a)` retains its complete suffix; no malformed `1.1(a` key or self-heading flag |
| R23 | Graph FN → TP | Comma before `above` no longer discards the direction |
| R24 | Graph FN → TP | Preposed `above Section 1` is checked against actual below-position target |
| R25 | Reference FN → TP | `Sections 8 and 9` yields two supported missing lookups; graph reviews both unresolved targets |
| R28 | Reference FN → TP | `Exhibit Z supplies` is a citation sentence, not an attachment heading |
| S04 | Reference FN → TP | Source comparison operators and intervening Section 9 survive structural parsing; legacy neural clauses stay unchanged |

These are nine corrected unique TXT case/task decisions: six reference false negatives, one
reference false positive and two directional false negatives. Across authored/transport repetitions,
the final comparison records 19 corrected decisions and zero newly introduced labelled regressions;
do not report those repetitions as 19 independent defects. R16 was already a coarse document TP;
the new rule additionally removes its spurious existing-heading flag and keeps only the genuinely
missing child reference. That quality improvement is not relabelled as an extra document TP.

## Other input modes, coverage and abstention

Authored references improved from 4 TP/1 FP/5 FN/18 TN (P=80%, R=44.44%, F1=57.14%) to
9/0/0/19. Authored graph improved from 4/0/2/9 to 6/0/0/9. In each PDF and DOCX subset, the
reference task now has 1 TP/1 TN; the graph has 1 TP and no negative control (FPR undefined).
These tiny transport subsets remain separate from TXT metrics.

TXT reference resolution records **41 RESOLVED, 10 MISSING, 2 AMBIGUOUS_TARGET, 3 UNSUPPORTED**
lookups. Thus 51/56 recognized lookups have an existence decision, with five explicitly reviewed.
Plural citations can create multiple lookups from one span; this is coverage of recognized syntax,
not recall over every possible reference. Unrecognized natural language is not in that denominator.

The two ambiguous lookups are R13/R14 duplicate targets. The three unsupported lookups are the
literal-markup S05 case, where no missing-target claim is made. The graph retains Roman/vague
antecedent abstentions and now emits review for all **12/12 predefined review-needed TXT cases**
(previously 10/12). This policy count includes provisional R20 and is not legal-error accuracy.
New grammar tests separately cover uncertain heading identity, unsupported/malformed/range/external
syntax and bounded-parser abstention; those are regression tests, not an independent dataset.

No new missing-target flags appeared outside the main labelled reference subset in TXT. A spurious
review for the heading title `Schedule of Fees` was found during development and corrected using a
general title-noun rule, with a regression test. The earlier outputs remain in paired_v3; final metrics
come from paired_v4. Unsupported HTML review remains an explicit limitation, not a hidden success.

## Frozen channels and outstanding accuracy limits

Date chronology remains 6 TP/2 FP/2 FN/4 TN on TXT (P/R/F1=.75), including T08/T12 false alarms
and T13/T16 misses. No temporal code or date input boundaries changed. Neural B/ensemble order-proxy
results remain 3 TP/1 FP/6 FN/2 TN; A detects none of nine perturbations. Those are order proxies,
not legal error labels. Distant contradictions and unusual wording remain provisional and unscored
for legal correctness. Independent legal annotation, unseen-family evaluation and external security
validation remain outstanding.
