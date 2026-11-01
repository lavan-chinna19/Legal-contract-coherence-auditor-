# LexAudit Phase 1 — frozen detection accuracy baseline

Date: 2026-10-26. Classification: **exposed development diagnostic; independent legal accuracy unestablished**.
The bounded evaluation phase is complete. Detection code, model weights, thresholds, calibration,
frontend changes and historical research artifacts were preserved. Application feature completion
in `FINAL_COMPLETION_TRACKER.md` is a different question from detection validity.

## Evidence and frozen configuration

Evaluation directory: [`evaluations/phase1_detection_baseline_2026_10_26`](../evaluations/phase1_detection_baseline_2026_10_26/).
Read its `PROTOCOL.md`, `corpus.json`, `frozen_manifest.json`, `results/frozen_primary/metadata.json`,
`predictions.jsonl`, `decisions.csv`, `clause_predictions.csv` and `summary.json` for the complete evidence.
Each prediction retains the source case, authored facts, label provenance, extracted text, actual
clause IDs/spans, component scores, rule evidence, graph evidence, failures and abstentions.

* Git HEAD: `0106f32f0d2cf99a210adf5550b6abe2f66aafc9`, branch `codex/lexaudit-personal-release`.
  The checkout already had uncommitted UI/documentation changes and untracked historical research.
  They were included in inspection and preserved; HEAD alone is not the full evaluated state.
* Frozen manifest SHA-256: `384ca26762c95e72c413485a544d0a87b33e8817c88a284c06db473a56e4e0f6`.
  It hashes all `src/**/*.py`, corpus/case files, builder/evaluator/protocol, checkpoint, centroids
  and calibration state before predictions. No local threshold override file existed.
* Checkpoint SHA-256: `9c0a5a096cdf03a63615134500a64f4bc559314be64366812d6a6f1762d4017f`.
  Centroids SHA-256: `2ea33ac1cb8430e720be85cd501f11539c143901b2173b63b942b34b9d31ce07`.
* Actual local model: `nlpaueb/legal-bert-base-uncased`, mean pooled normalized 768-dimensional
  embeddings, 512-token maximum, CPU, eval mode, BERT parameters frozen. The adjacent-clause
  head was in eval mode. Downloads were disabled. The supplementary post-run cache fingerprint
  records cached revision `15b570cbf88259610b082a167dacc190124f60f6` and file hashes.
* Actual environment: Python 3.11.9, torch 2.13.0+cpu, numpy 1.26.4,
  sentence-transformers 6.0.0, transformers 5.15.1, spaCy 3.8.15 with
  `en_core_web_sm` 3.8.0 (NER disabled), dateparser 1.4.2, crepes 0.9.1.
  Full parser versions and runtime settings are in each run's metadata.
* Channel A uses 66 centroid categories, raw-distance OOD threshold .50, and normalized score
  `clip((nearest_cosine_distance - .20) / .60, 0, 1)`. Raw-distance threshold and normalized
  score thresholds have different meanings.
* Channel B scores adjacent pairs with the existing trained MLP. Transition anomaly = `1-P`;
  middle clauses take the maximum incoming/outgoing anomaly, endpoints their single transition.
  One-clause documents get B=0. The stored coherence_threshold .50 is not used in scoring.
* Ensemble = `.5*A + .5*B`. Effective ranker parameters: high=.75, medium=.50,
  extreme single=.85, medium single=.70, low=.35, channel agreement=.50,
  conformal lower bound=.40. The ranker class's default high=.65 is overridden by the API.
  HIGH can also arise from combined>=.75, extreme single>=.85 with combined>=.60, or
  CI lower>=.40 with combined>=.60; MEDIUM also arises from either channel>=.70.
  Only HIGH/MEDIUM set ML `is_anomaly`; LOW does not.
* Existing calibration was restored, never refitted on this evaluation: synthetic shuffle only,
  target coverage .90, n=108, quantile .7265. It is not legal-error probability calibration.

See [`DETECTION_CAPABILITY_MATRIX.md`](DETECTION_CAPABILITY_MATRIX.md) for exact detector scope
and [`ERROR_ANALYSIS_AND_IMPROVEMENT_PLAN.md`](ERROR_ANALYSIS_AND_IMPROVEMENT_PLAN.md) for error evidence.

## Dataset and measurement boundaries

There are **70 unique documents: 59 mechanically labelled synthetic and 11 provisional human-review**.
Independent expert adjudication: **0**. The agent authored cases after inspecting the detectors;
they are deliberately detector-aware, exposed development diagnostics. Existing MSA/SLA fixtures
remain development evidence. There is no newly independent or unseen holdout.

The corpus covers valid/incorrect directional references, missing/ambiguous/nondirectional targets,
date arithmetic, unusual wording, clause-order perturbations and distant potential contradictions.
Mechanical labels come from author-specified literal identities/positions or ISO-date arithmetic.
Legal validity of wording, prepayments, exception clauses and distant contradictions is provisional.
Order labels identify the applied permutation, **not legal defects**. Exact-identity case R15 is
explicitly a numbering-policy challenge, not a universal claim about 1.01 versus 1.1.

The primary run executed 70 authored-clause analyses, 70 TXT ingestion/segmentation analyses,
and PDF/DOCX transport probes for R02/T02/T13/S04: **148/148 successful, zero execution failures**.
The second run repeated all 148. These are 70 documents, not 296 independent observations.
Four additional malformed/blank parser probes per run returned the expected HTTP 400 rejection.
This evaluates the actual backend detection path directly, not browser/authentication usability.

Metrics use one document-case as the unit and only defined task labels. A positive prediction
means at least one relevant flag/finding. A coarse document TP can contain spurious flags:
R16 both flags the missing subclause and incorrectly flags the existing heading. Per-flag semantic
precision and localization accuracy are therefore not established by document-level precision.
No unrelated cases are added as easy TNs. Undefined precision/FPR is null in saved results.

## Current measured performance: actual TXT application detection path

| Task / prediction | n | TP | FP | FN | TN | Precision | Recall | F1 | FPR |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Missing-target reference rule | 28 | 3 | 1 | 6 | 18 | 75.00% | 33.33% | 46.15% | 5.26% |
| Explicit-position graph | 15 | 4 | 0 | 2 | 9 | 100.00% | 66.67% | 80.00% | 0.00% |
| Scoped date chronology predicate | 14 | 6 | 2 | 2 | 4 | 75.00% | 75.00% | 75.00% | 33.33% |
| A OOD flag vs order-change proxy | 12 | 0 | 0 | 9 | 3 | Undefined | 0.00% | 0.00% | 0.00% |
| B >= existing .70 trigger vs order proxy | 12 | 3 | 1 | 6 | 2 | 75.00% | 33.33% | 46.15% | 33.33% |
| Actual ensemble flag vs order proxy | 12 | 3 | 1 | 6 | 2 | 75.00% | 33.33% | 46.15% | 33.33% |

B's row is a component diagnostic at an existing severity trigger; B has no standalone binary
API verdict. All three neural rows concern transformation detection only. Their FP/FN labels
must not be presented as false legal-defect judgments or legal-error recall.

Predefined canonical/challenge strata further expose limitations:

| TXT task / stratum | n | TP/FP/FN/TN | Precision / recall / F1 |
| --- | ---: | --- | --- |
| Reference, canonical | 17 | 2/1/0/14 | 66.67% / 100% / 80% |
| Reference, challenge | 9 | 1/0/6/2 | 100% / 14.29% / 25% |
| Reference, Roman identity | 2 | 0/0/0/2 | Undefined / undefined / undefined |
| Graph, canonical | 13 | 4/0/0/9 | 100% / 100% / 100% |
| Graph, punctuation/preposed challenge | 2 | 0/0/2/0 | Undefined / 0% / 0% |
| Dates, canonical | 9 | 5/0/0/4 | 100% / 100% / 100% |
| Dates, challenge | 5 | 1/2/2/0 | 33.33% / 33.33% / 33.33% |

These tiny, correlated, authored strata do not establish population reliability. The graph correctly
handled the four canonical positive positional conflicts and nine negative controls, including
noncanonical nondirectional arrangements and a same-clause earlier target. Date rules handled
the five canonical inverted predicates and four canonical controls. Broader syntax/scope does fail.

## Authored boundaries, extraction and abstention

With authored boundaries, references were TP=4/FP=1/FN=5/TN=18 (precision 80%, recall 44.44%,
F1 57.14%, FPR 5.26%). Dates were 7/2/1/4 (precision 77.78%, recall 87.50%, F1 82.35%,
FPR 33.33%). Graph and order-proxy confusion counts were unchanged.
TXT segmentation/normalization therefore lost an additional reference hit (S04) and chronology
hit (T13). There were **13/70 TXT authored-unit mismatches**, including text normalization
differences, not 13 proven legal segmentation errors. No normalized-source offset assertion failed.

Both PDF and DOCX preserved the R02 graph finding and T02 date finding, but reproduced the T13
date-role miss and S04 citation deletion. Their tiny format-specific metrics are saved separately;
do not pool them into main precision/recall. Real scanned/OCR, table and multi-column accuracy
has not been measured.

Graph review was correctly emitted for 10/12 predefined review-needed TXT cases: missing targets,
duplicates, unsupported Roman references and the provisional vague antecedent. R25 plural references
and S04's deleted reference produced silence. The authored mode reviewed 11/12 (only R25 silent).
This policy count includes provisional R20 and is not legal-error classification accuracy.
Ambiguous/missing targets have no directional binary label, so appropriate review is not counted
as a directional FN. No date-review abstention exists: T14's invalid date is silently omitted,
and T11's ambiguous numeric dates are accepted as March 4 and April 3 without locale review.

The TXT neural run flagged 31/70 documents and 86/222 segmented clauses. None of the 222 clauses
crossed A's raw OOD threshold. These are alert frequencies, not legal FP rates. Two of four unusual
wording candidates and all four distant-contradiction candidates received ML alerts, but there is
no nonlocal contradiction test or independently adjudicated truth to credit. 210/222 intervals
were [0,1]; mean interval width was .98513. Such intervals give little discrimination on these cases.

## Reproducibility, tests and preservation

* Primary run exit 0, 148/148 analyses, 4/4 safe rejections; scoring/probe elapsed 23.844 seconds
  excluding startup. Full independent process repetition also exit 0, 148/148 and 4/4.
* Repeatability: **148/148 equal prediction records** after excluding UUID flag IDs/timestamps
  and canonicalizing three semantically unordered evidence fields (`declared_targets`,
  `available_targets_sample`, `involved_clause_ids`). Raw evidence-list ordering differed:
  only 3/148 records were order-equal. No scores, clause order, positions or decisions were
  discarded. Both raw runs remain available in full.
* Corpus regeneration matched all 71 corpus/case files byte-for-byte.
* Relevant production regression: **43 passed, 0 failed, 0 skipped**, exit 0, 79.70 seconds.
  Files: `test_rules.py`, `test_final_release.py`, `test_ensemble.py`, `test_severity.py`,
  `test_segmentation.py`. This includes real model integration and HTTP/export acceptance.
  Four dependency deprecation warnings were retained. XML and console evidence are in the evaluation.
* The first restricted regression invocation stalled at its first HTTP test and was interrupted
  (exit 1, no completed suite result). The same suite passed with the local communication
  permissions needed by TestClient. That interrupted invocation is not counted as a passing run.
* Evaluation contract tests initially reported 9 passed/1 failed because the new harness test
  incorrectly required a trailing newline absent from the frozen case files. The assertion was
  corrected to the actual generator contract; no corpus, labels or predictions changed. Its
  first successful rerun passed 10/10. After adding evidence-set comparison and full saved-run
  coverage checks, the final evaluation suite passed **12/12**, exit 0, .45 seconds. Final relevant
  production plus evaluation suites: **55 passed / 0 failed / 0 skipped**; initial attempts are
  retained in the execution log rather than folded into that final-suite count.
* Preservation check: **1,040 existing files unchanged**, none missing, HEAD unchanged. This
  includes the existing uncommitted UI changes and historical research. No Git mutation or push.

Reproduce with the PowerShell commands in the evaluation README, using a NEW run ID. The
manifest refuses changed frozen inputs/source rather than silently evaluating a different system.

## Historical evidence interpretation and claim limits

Existing historical files were read, not regenerated. `coherence_training_curves.json` describes
894 sampled pairs and a 716/178 train/validation split; `trainer.py` shuffles pair indices, rather
than enforcing a document/family split. Shared-document leakage risk cannot be excluded from
those validation numbers; they are adjacency-label metrics, not adjudicated legal accuracy.
The old SEC benchmark computes alert rates assuming source contracts are clean, using only the
first 15 clauses per document. Without legal negative annotation those values are not validated
real-world legal false-positive rates. `claim_evidence_matrix.json` describes positive ordering
correlation while its stored result is tau=-.0285, p=.62252; that narrative is unsupported by its
own numbers. This audit records the discrepancy without rewriting the historical file.

Existing research validity documentation already classifies later structural experiments as
exploratory, with compromised preregistration and no independent adjudication. Optional research
models under `src/research` are not the active inference checkpoint evaluated here.

**The evidence supports reproducible descriptions of these controlled development cases only.**
It does not support 95% legal accuracy, overall real-world error accuracy, expert legal validation,
unseen-family generalization or production legal reliability. Independent qualified annotation,
document/family-separated unseen evaluation and external security/legal review remain external
validation work. No algorithmic improvement was implemented during this phase.
