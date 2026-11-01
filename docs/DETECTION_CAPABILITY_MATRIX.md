# LexAudit detection capability matrix — frozen Phase 1

2026-10-26. This describes the actual local pipeline, including existing uncommitted UI work,
not an aspirational feature list. Measured numbers are exposed synthetic development evidence.
Full task definitions and denominators: [`ACCURACY_BASELINE_AUDIT.md`](ACCURACY_BASELINE_AUDIT.md).

| Component and source | Actual operation / integration | Supported evidence | What it cannot establish / observed limit |
| --- | --- | --- | --- |
| Text ingestion — `src/api/ingestion.py` | Strict UTF-8 TXT; pdfplumber text PDFs; bounded DOCX ZIP/defused XML paragraphs; used by upload | Four safe rejection probes passed; text-PDF/DOCX R02/T02 detection survived | No OCR, scan understanding, table/layout reconstruction or legal interpretation; format probes are not representative extraction accuracy |
| Clause boundaries — `src/segmentation/rule_based.py` | Active v1 regex splits line-start section/article/numeric/parenthesized markers and all-caps headings; first unmatched region is preamble | 222 TXT segments; all offsets valid in normalized source | Dates/amounts and sentence-start citations over-split; unnumbered paragraphs merge; MSA Exhibit A merges; 13/70 authored-unit mismatches including normalization |
| Text normalization — same file | HTML-like block tags become newlines, all `<...>` is removed, entities decoded | HTML-style development input becomes segmentable | Also applied to plain TXT/PDF/DOCX: S04 comparison operators remove a whole reference. Offsets refer to normalized, not original raw, text |
| A semantic deviation — `src/scoring/channel_a.py`, `src/embeddings/frozen.py` | Frozen Legal-BERT mean embeddings vs 66 LEDGAR centroids; minimum cosine distance, affine clipped anomaly score; API scorer uses it | Per-clause category distances and nearest-category evidence; actual 512-token truncation recorded | No reference resolution, chronology, contradiction semantics or order awareness. Zero OOD alerts in 222 TXT clauses; zero of nine order proxies detected. A low distance does not prove legal validity |
| B adjacent coherence — `src/coherence/fine_tuned.py`, `src/coherence/model.py`, `src/scoring/channel_b.py` | Existing trained MLP over `[u,v,abs(u-v),u*v]`; sigmoid pair probability, `1-P` anomaly, per-clause maximum incident transition | Local transition sensitivity; at existing .70 component trigger, 3/9 changed order documents and 1/3 unchanged controls flagged | No distant-clause logical/obligation comparison; training adjacency/shuffle labels are not legal defect labels; single clause B=0; stored .50 threshold unused |
| Ensemble / severity — `src/scoring/pipeline.py`, `severity.py` | `.5A+.5B`; configured rule-based severity, MEDIUM/HIGH alert; integrated into unified report | Reproducible diagnostic alert ranking; order proxy 3 TP/1 FP/6 FN/2 TN | Not calibrated legal defect probability; single B>=.70 can make MEDIUM despite combined<.50; alerts on wording/unchanged documents do not certify defects |
| Conformal intervals — `src/calibration/conformal.py`, calibration fixture | Frozen 108-observation synthetic-shuffle calibration restored; .90 target | Preserved calibration provenance and actual intervals | Does not certify legal correctness or new-domain coverage. 210/222 TXT intervals [0,1]; mean width .98513; no calibration on current cases |
| Cross-reference existence — `src/rules/reference_checker.py` | Regex declarations/citations plus spaCy processing; Roman/decimal aliases; missing section/article/exhibit/schedule targets; always runs in unified audit | Typical missing Section 9 and Exhibit Z detected; document presence 3 TP/1 FP/6 FN/18 TN on TXT | No directional/order verification or duplicate ambiguity review; citations can self-declare targets; plural refs missed; subclause declaration/reference identities disagree; decimal normalization policy can merge distinct identities |
| Defined terms — same file | Quoted terms are indexed as declarations | Metadata includes definitions | No matching general undefined-term validation head; declaration indexing is not comprehensive definition-consistency detection |
| Date consistency — `src/rules/date_checker.py` | Absolute dates, nearest preceding 60/following 40 character role; within-clause ranges; effective/end, execution/end, payment/start, notice/end comparisons; always runs | Five canonical positives and four canonical negatives correct; whole TXT subset 6 TP/2 FP/2 FN/4 TN | No agreement/scope graph, exception reasoning, relative-date arithmetic, business-day/calendar obligations, or explicit locale/invalid-date abstention. Cross-scope and substring-range false alarms; role-distance and segmentation misses |
| Experimental dependency graph — `src/rules/dependency_graph.py` | Separate opt-in `/v1/experimental/dependencies`; uses stored authoritative clause inventory; unique explicit numeric section references and textual source/target positions | Four canonical positional conflicts detected; nine canonical negatives clean; two punctuation/preposed misses; emits evidence edges | Not arbitrary legal dependency extraction, causal ordering, NLI or general reorder defect detection. No Roman/exhibit/plural support. Trailing whitespace above/below and narrow immediately-preceding syntax only |
| Graph abstention — same file | REVIEW_REQUIRED for recognized unresolved/duplicate targets, Roman references and boundary vague antecedents; not merged into A/B/ensemble | Correct reviews for 10/12 predefined TXT review-policy cases, including both duplicate examples | Unrecognized/deleted references can produce NO_FINDINGS rather than review. NO_FINDINGS is not proof of no defect; reviews are not positive legal findings |
| Unified audit — `src/rules/unified_pipeline.py`, `src/api/jobs.py` | Runs A/B/ensemble then reference/date rules, combines counts; graph explicitly requested separately | Authored and extracted detection path tested with real offline weights | Count addition is not unique-defect counting or calibrated document risk; unrelated ML alerts do not count as detecting a specific mechanical or legal defect |
| Distant contradiction candidates | C01–C04 retain scope/exception questions and provisional provenance; raw evidence saved | All four received some local ML alerts | No adjudicated labels, no global pairwise contradiction detector or relation evidence. Precision/recall for contradiction detection cannot be calculated |
| Attribution / counterfactual / robustness tools | Existing explanation, reorder sensitivity and controlled perturbation workflows consume current scores | Regression suite covers integration; baseline retains perturbation operations/provenance | Explanation is not validation of the underlying verdict. Better neural score after moving a clause does not establish better legal coherence |

## Effective API severity logic

Let A/B be normalized component scores, E=.5(A+B). The active ranker is configured by
`src/api/dependencies.py` → `DualChannelScorer` with high=.75 and medium=.50. A class docstring
listing high=.65 is not the effective API value. Agreement magnitude is `1-abs(A-B)`; channel
agreement categories compare normalized A/B against .50, unlike A's raw-distance OOD flag.

HIGH: `(E>=.75 and A>=.5 and B>=.5)` OR `E>=.75` OR `(max(A,B)>=.85 and E>=.60)`
OR `(CI lower>=.40 and E>=.60)`. MEDIUM: E>=.50 OR max(A,B)>=.70.
LOW: E>=.35, otherwise CLEAN. Only HIGH/MEDIUM are ML anomalies. Thresholds and rules were
not changed. With A=0/B=.7019, E=.3509 and MEDIUM are entirely possible (W02).

## Limits of the measured coverage

No independently adjudicated examples, real-world prevalence sample, unseen contract-family split,
OCR benchmark, multi-column/table extraction benchmark, calibrated legal confidence study or
external legal/security assessment was produced. A mechanically correct date comparison may be
an intentional prepayment or an authorized exception; human interpretation remains necessary.
Roman negative presence controls do not demonstrate graph Roman support: the graph abstained.
Treat each capability and limitation above independently instead of reporting one overall accuracy.
