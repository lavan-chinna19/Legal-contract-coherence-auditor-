# Phase 2 — error analysis and remaining limits

2026-10-26. Analysis uses preserved Phase 1 development labels; no expert annotation was invented.
Final comparison: `evaluations/phase2_structural_parser_2026_10_26/results/paired_v4/`.

## Resolved implementation errors

Sentence-start citations no longer self-declare section/exhibit targets. Full nested identities no
longer lose parentheses or collide with parent identities. Plural citations are represented separately.
Preposed/punctuated directions retain their actual relationship. Source comparison operators and text
between them survive structural parsing. Duplicate declarations remain multiple candidates instead
of being deduplicated into a false unique target. Existing model/date inputs are untouched.

On the labelled TXT subsets this corrects R11/R12/R15/R25/R28/S04 reference misses, R17's false
missing flags, and R23/R24 directional misses. R16's extra self-heading flag is removed while its
existing document TP remains a TP. No newly introduced FP/FN occurred in the 28-case existence or
15-case directional task, nor in their authored/transport counterparts. This is a finite development
observation, not evidence that the parser has no unseen bugs.

## Errors and failures found during implementation

All failed runs remain recorded; no failing assertions were disabled.

* Initial grammar run: 56 passed, two failed, 14 deselected. One failure exposed parenthesized
  direction text being treated as an uncertain heading; fixed with a supported punctuation rule.
  The other test placed a bare `Section 4.` line where the source itself could mean a heading or
  citation. Its supported-reference specimen was clarified to an ordinary sentence, retaining
  the RESOLVED expectation, and an additional test requires abstention for the genuinely ambiguous
  bare marker. Ambiguity was not turned into fabricated heading evidence.
* Paired_v1 stopped before predictions: legacy segmenter relative import needed its original
  package context. The saved module was not changed; the loader was corrected.
* Paired_v2 completed all predictions but verification exited 1: Python confidence-interval tuples
  were directly compared with JSON arrays. Artifact inspection showed equality of all numerical
  values. The comparison now normalizes JSON representation only; no scores, evidence or thresholds
  are ignored/rounded. A fresh paired_v3 reproduced all 148 Phase 1 predictions, and paired_v4 did so again.
* First full regression: 294 passed, one failed, two skipped. The direct API parity invocation omitted
  original source while API jobs now supply it; raw EDGAR markup and legacy-cleaned clauses were
  different structural inputs. Updated the direct call to supply the same extraction and added three
  preservation assertions without removing any original numerical/rule assertions.
* Second full regression: 296 passed, one failed, two skipped. The stricter preservation assertion
  caught Python universal-newline reads converting CRLF. The test now uses the actual upload decoder;
  final regression passed 298 tests, with two optional CUAD report skips. Production ingestion was
  already preserving these characters and was not changed.
* Coverage inspection found four unnecessary review notices for `Schedule of Fees` in exposed SLA
  orders. A general rule distinguishes an ordinary function-word phrase in a heading title from an
  identifier citation; a new test preserves genuine references inside titles. Final paired_v4 has
  no such notices. This was an extra review burden, not a missing-target classification FP.

Initial and intermediate XML/log artifacts are retained alongside final outputs, so corrected
harness mistakes and implementation bugs are distinguishable from scientific detector outcomes.

## Abstention is part of the interface

Reference existence is undecided for duplicate targets, possible but unjustified headings, unsupported
identifier/range/external scope syntax, unresolved markup structure and incomplete bounded parses.
Only genuinely absent supported targets produce a missing flag. The graph separately reviews unresolved
targets, Roman directions and vague boundary antecedents. NO_FINDINGS is not proof of legal correctness.

The final TXT corpus contains two ambiguous-target and three unsupported reference lookups. All
12 predefined graph review-policy cases now emit review. Explicit resource tests prove truncation
cannot create a confident missing/unique resolution. Cases with unknown legal truth have no TP/FP/FN/TN.

## Remaining parser and integration limits

1. The supported heading grammar is conservative and heuristic. Unfamiliar titles, titleless body
   clauses, unusual typography, alternative numbering schemes, complex relative enumeration and
   ambiguous attachment scopes are not universally handled. An uncertain possible heading is retained
   for review where recognized; unsupported natural-language references can still escape recognition.
2. Literal HTML is retained but not structurally reconstructed. The S05 markup example requests
   review rather than deciding target absence. A future HTML parser needs a tested raw-to-derived
   offset map; stripping tags blindly would repeat the Phase 1 source-loss problem.
3. Identity matching is exact within namespace. Decimal/zero-padding equivalence, Roman/Arabic
   aliases, reused numbering under separate exhibits and external-document scope require explicit
   policies. Duplicate numbering abstains rather than guessing the nearest target. Nested parent-child
   existence does not prove semantic legal dependency or correct contractual scope.
4. Structural offsets describe extracted Unicode text. They cannot locate words on original PDF
   pages or repair OCR/layout extraction. PDF/DOCX probes cover text transport, not scans, tables,
   multi-column reading order or representative extraction accuracy.
5. Legacy scoring/preview inventory remains normalized and can still split date/amount lines or
   lose source text. That defect is now visible alongside exact structural evidence, not silently
   repaired in the model input path. Existing UI consumers still use their old inventory; no UI
   redesign or source-pane migration occurred. Precise structural highlighting must use the new
   absolute source span and matching coordinate space, not a partially associated scoring-clause offset.
6. Clause-only callers cannot recover source removed before their invocation. They receive explicitly
   assembled coordinates. New API jobs save original extraction; older saved jobs disclose their
   evidence limit and require reanalysis for original-source structure.
7. A document-level TP can still hide localization errors or extra flags. Per-reference precision,
   structure coverage and expert legal correctness need a larger independently annotated evaluation.

## Unchanged model/temporal limits and Phase 3

Date rules still infer a range from `relates to` (T08), cross agreement scopes (T12), lose a role
across legacy boundaries (T13), and miss distant role keywords (T16). Ambiguous locale and invalid
dates still lack explicit temporal review. These are deliberately not repaired by changing Phase 2
date logic or neural segmentation. Neural order sensitivity and distant contradiction reasoning
remain as measured in Phase 1; source parsing is not a new legal-reasoning model.

**Phase 3 temporal reasoning can proceed on the native verified application**, using this structural
inventory for scope/evidence and a separately frozen paired evaluation. First address scope-aware
date/event association and real interval syntax, then ambiguity/invalid-date review. Preserve the
current date baseline and neural inputs unless an explicitly measured input-version migration is
authorized. Docker revalidation remains NOT VERIFIED while the host Linux engine is unavailable.
Independent qualified legal annotation, unseen-family testing and external security assessment
remain external validation work, not prerequisites that can be fabricated in this session.
