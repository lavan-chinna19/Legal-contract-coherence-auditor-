# Frozen detection baseline protocol — 2026-10-26

This is a detector-aware, exposed DEVELOPMENT diagnostic, authored after source inspection.
It is neither an unseen holdout nor independent legal annotation. There are 70 documents:
59 mechanically labelled synthetic cases and 11 provisional human-review cases. Independently
adjudicated examples: ZERO. Existing MSA/SLA development fixtures retain their exposed provenance.
The corpus, this protocol, evaluator and production detector files are hashed before predictions.
No weights, scoring rules, thresholds, calibration observations or production files may change.

## Predefined tasks and units

One document-case is one observation. Report each detector, task, input mode and stratum separately.
Never pool input-format replications as independent documents. Canonical/challenge strata are
predefined in the corpus, not selected based on outcomes. Do not aggregate legal-error accuracy.

* Reference presence: a declared exact target identity exists or is missing, from literal author
  facts. Positive = at least one missing citation target. The reference checker's reference flag
  is the prediction. R15 explicitly tests an exact-identity namespace; numbering equivalence is
  policy-sensitive. This is not a label for every legal use of decimal numbering.
* Directional position: unique numeric target exists and an explicit above/below/immediately
  preceding relation is textually false. Positive = positional conflict. Graph findings are the
  prediction. Non-directional references with unique targets are negative controls. Missing,
  ambiguous and unsupported Roman targets have no directional binary label. If a labelled
  positive receives only REVIEW_REQUIRED it remains a miss, with abstention recorded separately.
* Date chronology: author-specified date arithmetic within the stated agreement scope/range.
  Positive = the specified comparison is inverted. Any date-rule flag is the prediction.
  Prepayments and notice predicates are arithmetic labels, not judgments of legal validity.
  Ambiguous locale, invalid calendar date and intentional prepayment examples are reported
  separately; they do not enter chronology metrics without a defined label.
* Neural order proxy: only O01–O12. Positive = an author-applied order perturbation occurred.
  This is NOT a legal-defect label. A predicts any existing `is_ood` flag (raw distance >= .5).
  B diagnostic predicts any score >= the existing severity single-channel trigger (.70).
  This is explicitly a component diagnostic; B has no standalone API binary verdict and its
  stored coherence_threshold .5 is unused in scoring. Ensemble predicts any actual ML anomaly.
  Do not optimize these thresholds or use this corpus to calibrate. Raw clause scores and
  paired order changes are retained, including benign changes and misses.
* Provisional wording and distant-contradiction candidates: raw scores, flags and evidence only.
  No TP/FP/FN/TN or legal precision, recall, F1, FPR. An unrelated anomaly is not credited as
  contradiction detection. No dedicated distant logical-entailment head is present.

## Input modes and failure accounting

Run all 70 cases as authored clause records (detector isolation) and actual UTF-8 TXT ingestion
plus the API's v1 segmenter (application detection path). Four predefined transport probes
(R02, T02, T13, S04) also run through generated text PDF and DOCX. These are parser integration
probes, not full browser/authentication tests or representative PDF/OCR benchmarks.
Preserve raw extracted text, normalized text, authored units, actual segments and offsets.
Segmentation count/text mismatch is diagnostic against authored boundaries, not expert legal
segmentation gold. Verify offsets against NORMALIZED text and identify source-text loss.
Malformed PDF/DOCX/UTF-8 and blank PDF are safe-rejection probes, not classification negatives.

Prediction/parse exceptions are retained, never counted as TN; report coverage and failed case IDs.
Graph reviews on predefined missing/duplicate/Roman/vague cases are recorded as abstention-policy
checks. Unsupported plural references may produce silence; that is not a correct abstention.
Graph NO_FINDINGS is not affirmative legal correctness. Date parse omissions without an explicit
review signal are not credited as abstentions. Metric denominators and undefined values are visible.

TP, FP, FN, TN are counted only for boolean mechanical labels and the clearly named order proxy.
Precision=TP/(TP+FP), recall=TP/(TP+FN), F1=2TP/(2TP+FP+FN), FPR=FP/(FP+TN).
An undefined denominator yields null, not 100%. Confidence/generalization claims are inappropriate
for small, correlated, adversarially authored development cases. Source IDs permit exact review.

## Reproduction and preservation

Use the existing clean CPU Python environment. Offline Legal-BERT must load real local weights;
fail if centroids/checkpoint/calibrator are unavailable. Runtime embedding/feedback caches live
under this evaluation's ignored runtime directory. No model or centroid fitting occurs.
Each run gets a new directory and refuses overwrite. Manifest verifies the corpus, cases, evaluator,
protocol and detector sources before execution; a changed manifest requires a new named baseline.
Run affected production regression tests, test metric/provenance invariants and compare existing
file hashes before/after. Historical results are evidence to audit, never rewritten by this phase.
