# Phase 2 paired DEVELOPMENT comparison

Reuse the frozen 70-case Phase 1 corpus and its label provenance without modification. This is
exposed development evidence, not independent legal annotation or an unseen holdout. No case ID
or expected prediction is used by production parsing/resolution. Additional grammar tests define
supported syntax; they are regression tests, not an independent accuracy estimate.

Execute old modules copied byte-for-byte BEFORE implementation and the new parser-integrated
pipeline on identical inputs. Repeat Phase 1 authored/TXT modes and its four PDF/DOCX transport
probes (148 analyses per implementation). Legacy modules import unchanged actual local scorer,
checkpoint, centroid and calibration assets; no mocks, fitting or new thresholds. Reproduce old
Phase 1 component/rule/graph predictions, and separately require every new ML clause score,
evidence, severity, interval and old date-rule flag to match. Rule flags inside scoring metadata
are expected to change; they are not neural model predictions.

Both implementations receive IDENTICAL frozen legacy neural/date clauses. New structural checks
also receive unchanged actual extracted text, so citation loss in the legacy cleaner can be
recovered without silently changing ML inputs. Preview and saved metadata expose both inventories
with explicit coordinate spaces. Structure unit concatenation must equal extraction byte-for-byte
as Unicode text; heading/reference spans must match exact source slices. These are code-point
offsets in extracted text, not PDF page coordinates or byte offsets. Legacy clause association
is marked partial if only its first line survives normalization.

Primary paired metrics: missing-target reference rule and explicit-position graph, one document
per task/mode. Keep Phase 1 boolean labels, TP/FP/FN/TN definitions and predefined strata.
Graph reviews on unresolved/ambiguous cases are not positive findings. Reference ambiguity/unsupported
syntax goes to metadata review, not a missing-target defect flag. In a mechanically labelled
positive, abstention without a missing flag remains a miss; report coverage alongside all metrics.
No provisional legal examples enter classification metrics. Null undefined metrics remain null.
Do not pool PDF/DOCX or repeated runs as independent documents. Record corrected errors AND any
new FP/FN; document-level precision does not establish localization/per-reference precision.

Publish source/parser versions and per-run pre-prediction hashes. If a later bug fix changes source,
retain prior run outputs and use a new run ID; never overwrite a failed scientific run. Keep Phase 1
files/historical evidence fixed. Run full native tests, frontend compatibility/build and real ingestion/
ownership/preview/export/history tests. Docker is NOT VERIFIED when engine connectivity is absent;
do not reset the user's runtime. Algorithmic or legal generalization is not inferred from green tests.
