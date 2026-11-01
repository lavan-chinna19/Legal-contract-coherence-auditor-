# Phase 4A.1 — binding reliability and real-world feasibility

Completed native verification on 2026-10-28. This phase repairs only supported passive voice,
joint/compound responsible parties, and event type versus event instance. It introduces no model,
training framework, frontend redesign, temporal change or contradiction detector. **Phase 4B was
not started. Final decision: NO-GO for moving to a narrow contradiction-detection demonstration.**

Evidence directory: `evaluations/phase4a1_reliability_2026_10_28/`.

## 1. Original evaluation counts reconcile

The Phase 4A reports, raw predictions, summary, frozen manifest and error audit were inspected.
The original reserved set has **30 documents**, each containing one preselected annotated pair:

| Original group | Documents / selected pairs | Outcome |
| --- | --- | --- |
| Mechanically labelled comparable pairs | 8 | 7 MATCHED, 1 UNSUPPORTED abstention |
| Mechanically labelled different pairs | 8 | 8 DIFFERENT |
| Mechanically labelled uncertainty policy | 12 | 12 UNCERTAIN |
| Unsupported-action diagnostic | 1 | UNSUPPORTED |
| Provisional interpretation, no accuracy label | 1 | UNSUPPORTED |
| Total | **30** | 15 decided, 15 abstained |

The binary confusion matrix denominator is **16 trustworthy binary labels**, including the
abstained positive: TP7 / FP0 / FN1 / TN8. The 15/30 supported-coverage figure is the number of
MATCHED or DIFFERENT predictions divided by **all 30** documents. These denominators answer
different questions. Excluding the passive abstention yields selective binary n15, which must
not replace full recall 7/8. Null binary labels are not invented negatives. Negative abstentions
would count only as screen TN, not validated difference. One provisional case per original split
has neither a four-state nor a binary accuracy label.

The original development set similarly has 28 documents, 14 binary labels and 14 decided pairs.
All-emitted pair workload is separate from the selected-pair metric: original development emits
34 pairs and reserved emits 36 because some diagnostic sections contain additional obligations.
`original_count_audit.json` records these units. No original count needs silent relabelling.

### Recurrence annotation correction, kept separate

The two left/right recurrence fields in each split copy `invoice alpha` / `invoice cedar` into
event-instance gold even though `each month` identifies no unique occurrence. A separate explicit
overlay corrects **four field cells total to null**. Original labels, predictions and pair gold
remain unchanged. The same overlay is applied to both baseline and repaired outputs:

| Exposed original field task | Frozen baseline | Repaired |
| --- | --- | --- |
| Development event-instance exact, original raw gold | 53/55 | 53/55 |
| Development event-instance exact, corrected overlay | 55/55 | 55/55 |
| Former reserved event-instance exact, original raw gold | 55/59 | 57/59 |
| Former reserved event-instance exact, corrected overlay | 57/59 | 59/59 |
| Former reserved actor exact | 56/59 | 59/59 |

Improvement due solely to annotation correction is not credited to the algorithm. The passive
and joint-actor changes are genuine extraction repairs on exposed examples. These field rates
are descriptive development evidence, not independent validation. See `annotation_overlay.json`
and the original Phase 4A `post_evaluation_error_audit.json` for each cell and reason.

## 2. Three targeted implementation repairs

**Passive voice.** Supported paid/remitted, delivered/provided and notified/informed forms now
recover the responsible party only from an explicit `by` phrase. Grammatical patients become
the explicit object or notification recipient; source offsets remain in unchanged extraction.
Missing agents abstain. This does not add unrestricted passive parsing or a general action map.

**Joint/compound subjects.** Records now preserve `actors`, `actor_mode` and the readable `actor`.
Conjunctive parties, comma lists and `&` remain a group; order does not change group identity.
Alternative subjects remain unresolved. A coordination split occurs only after an earlier modal,
preventing “Purchaser and Vendor must …” from silently becoming Vendor alone. Independent explicit
modal obligations still split. No aliases, pronouns or joint/several legal responsibility are inferred.

**Event type and instance.** `event_type` and `event_instance_basis` distinguish type-level facts
from source-backed named/explicit occurrence identity. Recurrence leaves instance unknown. An
explicit occurrence identifier is retained; one-sided occurrence detail requires UNCERTAIN rather
than inventing equivalence. Trigger occurrence details cannot become the action's occurrence.

For the user's active/passive notification examples, both records now identify provider / NOTIFY /
customer. Their `actor_action_relationship` is MATCHED. Without an established notification
occurrence, the **full obligation pair remains UNCERTAIN**. Adding an explicit shared Notice Alpha
permits MATCHED when other supported fields agree. This distinction prevents a grammar repair from
manufacturing an event. Different instances remain DIFFERENT; conditions/exceptions still abstain.

The four top-level decision meanings remain MATCHED, DIFFERENT, UNCERTAIN and UNSUPPORTED.
Version is `experimental-obligation-binding-v1.1`; existing opt-in API/history behavior is retained.
The experimental PDF/DOCX section now displays actor group, voice, event type and instance basis.

## 3. Focused frozen-baseline comparison

The original binding module was copied **before repairs** and matches its original frozen hash:
`18195475a72060c5df63c9cfed585fb793ac164d76104bcdd7e607205e030836`.
It was actually executed and reproduced **58/58 archived Phase 4A document outputs** exactly.
This is the actual old implementation, not the earlier guard ablation.

Twenty additional mechanical examples were authored and hashed before implementation/final
testing. Both the original examples and these additions are exposed/authored development evidence,
not unseen or independently adjudicated evaluation. Every run is retained under a new run ID.

| Selected-pair task | Baseline TP/FP/FN/TN | Repaired TP/FP/FN/TN | Baseline -> repaired decided documents |
| --- | --- | --- | --- |
| Original development, binary n14, all docs28 | 7/0/0/7 | 7/0/0/7 | 14/28 -> 14/28 |
| Former reserved, now exposed, binary n16, all docs30 | 7/0/1/8 | **8/0/0/8** | 15/30 -> **16/30 (53.33%)** |
| Focused authored additions, binary n10, all docs20 | 0/0/7/3 | **7/0/0/3** | 1/20 -> **10/20 (50%)** |

On trustworthy constructed binary labels only, former-reserved precision/recall/F1 change from
100% / 87.5% / 93.33% to 100% / 100% / 100%, with FPR 0% both times. Focused baseline precision
is undefined (no positive predictions), recall/F1 0%; repaired precision/recall/F1 are 100%, FPR0%.
These small exposed synthetic scores do not measure legal correctness or real-world accuracy.

Repaired selected-pair abstention: development14/28, former reserved14/30, focused10/20. Full
denominators retain abstention; positive abstentions are misses. Both original provisional examples
remain unscored. No parser exception was suppressed in the 78-document comparison.

All emitted pairs, including unlabelled additional workload, have separate denominators:

| Workload | Baseline decided / emitted | Repaired decided / emitted | Repaired docs with any decided pair |
| --- | --- | --- | --- |
| Original development | 17/34 | 17/34 | 15/28 |
| Former reserved | 18/36 | 19/36 | 17/30 |
| Focused additions | 1/20 | 10/20 | 10/20 |

These extra emitted pairs have no independent gold labels and are not extra confusion-matrix
examples. Document-level “any supported pair” is not interchangeable with selected-pair coverage.

Corrected errors include the original passive pair FN and the joint actor field. Seventeen focused
four-state policy outcomes also become correct. No newly introduced final labelled pair errors
were observed. All 20 focused actor-group and actor/action relationship checks pass. Comparison_v1
exposed an unwanted actor-group candidate on a public definitional sentence; it was corrected by
a narrow nonparty-subject guard and retained in the evidence. **comparison_v2 is final**; earlier
predictions were not overwritten. This is not a claim that arbitrary natural-contract binding is solved.

## 4. Authentic public-contract applicability

Selection is fixed to the **same three substantive cached SEC exhibits** from Phase 4A, avoiding
new selection based on successful predictions. They share an issuer/filing and amendment-heavy
language; this is a small, non-representative feasibility sample. Manifest retrieval was 2026-08-29;
these are cached documents, not a fresh download or independent label set.

Issuer: TORO CO, CIK 0000737758. Filing date: 2023-12-20. Accession: 0000737758-23-000034.

| Authentic exhibit / source | Normalized modal records, old -> new | Decided / emitted pairs, old -> new | Modal cues skipped on inline heading lines |
| --- | --- | --- | --- |
| [EX-10.27](https://www.sec.gov/Archives/edgar/data/737758/000073775823000034/ttc-10312023xex1027.htm) | 2 -> 2 | 0/1 -> 0/1 | 24/26 |
| [EX-10.29](https://www.sec.gov/Archives/edgar/data/737758/000073775823000034/ttc-10312023xex1029.htm) | 1 -> 1 | 0/0 -> 0/0 | 25/26 |
| [EX-10.34](https://www.sec.gov/Archives/edgar/data/737758/000073775823000034/ttc-10312023xex1034.htm) | 5 -> 5 | 0/10 -> 0/10 | 5/10 |

Totals: **0/11 emitted normalized-view pairs supported, 11/11 abstained (100%)**, and **0/3
documents** have any supported pair. The one-record document's zero pairs are not treated as
a successful negative analysis. Eight records are partial modal candidates, not eight verified
legal obligations. There are no expert contradiction or matching labels, so no public precision,
recall, F1 or legal accuracy is calculated.

Raw HTML is separately unsupported: 542 emitted raw-source pairs all abstain. Raw and normalized
views are **six observations of three documents**, not six independent contracts. The normalized
view is identified by its own hash and Unicode offsets; those are not original HTML byte offsets
or PDF coordinates. Original cached text, manifest identity/URL and raw hash remain intact. Full
view text, exact record spans, at most three candidate pairs per view and omitted-cue evidence are
retained in `paired_public.jsonl` and `public_applicability_audit.json`.

### Why applicability fails: distinct categories

* **Parsing implementation bug:** 54/62 recognizable modal cues in normalized text fall on heading
  lines containing inline body text. The binding consumer starts after `heading_end`, skipping
  that whole line. For example EX-10.27 has omitted source context at normalized offsets
  `[2181,2371)`; EX-10.29 at `[1526,1716)`; EX-10.34 at `[3836,4028)`. These are exact retained
  text evidence, not 54 labelled obligations or legal defects. Fixing inline body consumption is
  outside the three authorized repairs, so it is documented and **not silently implemented**.
  Phase 2 parser and outputs remain unchanged.
* **Unsupported grammar/action:** all eleven emitted normalized pairs include a record with an
  unsupported action, including definitional `shall have` / `shall mean` and other legal wording.
  A lexical modal match is not proof of an operational obligation. The action ontology was not expanded.
* **Unestablished meaning/evidence:** conditional/exception language, amendment scope, unknown
  subjects and absent named occurrences can require human interpretation or better evidence.
  These reasons are recorded but are not the primary top-level cause of these eleven UNSUPPORTED
  decisions. They are not labelled contradictions.
* **Genuine targeted bug fixed:** the initial joint-party repair split a definitional subject into
  apparent actors. That candidate never yielded a supported pair; the guard removes the false
  responsibility assertion in final comparison_v2. Unsupported definitions are not repaired by
  pretending their words are parties.

No qualified reviewer annotated this sample. The evidence establishes inadequate applicability,
not validated correctness or proof that the contracts contain no conflicts.

## 5. Integration, regression and preservation

* **Full native: 468 passed, 0 failed, 2 optional skips**, exit0, 152.63 seconds, nine retained warnings.
  `full_native_v1.xml/.log` are authoritative. Skips are the optional CUAD order-report existence/
  verdict tests; historical reports were not regenerated. Warnings remain visible, not suppressed.
* Affected integration: **73 passed**, exit0, 34.77 seconds. This overlaps the full suite and is
  not added to its count. Initial targeted suite had 63 passes before the final safety guards/tests.
* Actual TXT/PDF/DOCX workflows verify supported active/passive joint notification, exact source
  and field spans, authentication/other-owner rejection, saved-history restoration, and parsed-back
  PDF/DOCX actor/voice/type/instance evidence. All existing core result fields compare exactly
  before versus after experimental opt-in. This is real local TestClient/model integration,
  not browser usability, external security or a complete OS-process restart test.
* Core verification: **148/148** neural, structure, reference and graph outputs match; **148/148**
  date results match the direct unchanged Phase 3 checker; **38/38** saved historical Phase 3 date
  outputs/flags match exactly. Frozen core hashes pass. No model, threshold or temporal edits.
* Docker version exits1, Server=null, missing `dockerDesktopLinuxEngine` pipe. Runtime validation
  is **BLOCKED**. No reset, prune, WSL deletion, volume change or container deployment was attempted.
* Frontend source and existing research/evaluation files are preserved by the pre-change snapshot;
  no frontend design or behavior code was changed. No new frontend test results are claimed here.

## 6. Reproduction and use

From `F:\projects\nlp\Legal-contract-coherence-auditor-` in PowerShell:

```powershell
$env:HF_HUB_OFFLINE='1'
$env:TRANSFORMERS_OFFLINE='1'
$env:LEXAUDIT_ALLOW_MODEL_DOWNLOAD='0'
$env:OMP_NUM_THREADS='2'
$env:MKL_NUM_THREADS='2'
tmp/final-release/clean-env/Scripts/python.exe -m pytest tests -q
tmp/final-release/clean-env/Scripts/python.exe evaluations/phase4a1_reliability_2026_10_28/run_comparison.py --run-id your_new_comparison_id
# Optional independent rerun of the exact old module, using a NEW artifact directory:
tmp/final-release/clean-env/Scripts/python.exe evaluations/phase4a1_reliability_2026_10_28/run_comparison.py --baseline --run-id your_new_baseline_id
```

The saved baseline_v1 exists for paired reproduction. Every run ID must be new; scripts refuse
to overwrite evidence. Do not regenerate the frozen focused inputs or edit historical labels.
Original Phase 4A scripts expecting the old production source hash are historical; use the
preserved baseline snapshot to rerun that original implementation after this intentional repair.

Use the existing authenticated `POST /v1/experimental/obligation-bindings` with a completed owned
job ID and `experimental: true`; the result persists separately as before. Native launcher remains
`tmp/final-release/clean-env/Scripts/python.exe scripts/run_server.py --port 8012`, with existing
private authentication/encryption configuration. No running user service was restarted.

## 7. Final decision and strict stop

**Counts reconcile. Supported passive/joint examples are fixed. Event identity is safer within
the tested grammar, with explicit type/instance separation and documented annotation corrections.**

**NO-GO for a narrow contradiction-detection demonstration on authentic contracts.** The fixed
sample has zero supported pairs, a concrete inline-body parsing bug and unsupported legal wording;
independent matching/contradiction ground truth is absent. Synthetic success does not overcome
those failures. Any controlled example demonstration must remain a grammar/binding demonstration,
not a claim of real-contract contradiction detection.

The bounded phase stops here. No Phase 4B, additional model, training framework, unrestricted
relation extraction or extra benchmark expansion was introduced. The unrelated parsing blocker
and independent legal/security validation remain explicit limitations. No commit, push, deployment
or historical research deletion occurred.
