# Final source-parsing correction and research freeze

Freeze date: **2026-10-28**. Classification: **reproducible native research prototype with explicit
limits**, not scientifically validated legal production readiness. Implementation stops after this
freeze. No Phase 4B, new model, scoring adjustment or new benchmark cycle was started.

## Original failure and exact cause

Reproduced input:

```text
Section 1. Payment. Buyer shall pay Invoice Alpha.
Section 1.1. Notice
Provider shall deliver Report Bravo.
```

The original structural document retained both sections and every source character, but binding
returned only the delivery record. `original_reproduction.json` preserves the exact input,
structural metadata and omitted-payment evidence. Pre-fix regression: **10 failures / 3 passes**,
exit1, retained as `reproduction_before.xml/.log` rather than discarded.

The responsible function is `src/obligations/binding.py::_extract`, not document extraction,
neural clause segmentation or the Phase 2 parser. A structural node's `heading_end` is the end
of the **whole physical heading line**, which can include inline body sentences. Starting the
consumer after that offset silently excluded same-line text.

## Smallest correction and preservation

One executable line now starts consumption at the known **`identifier_end`** instead of
`heading_end`, with two explanatory comments. This retains the title and all following text;
it does not guess where an ambiguous title ends or modify structural boundaries. Existing sentence
splitting ignores non-modal title text, retains inline obligations, and preserves uncertainty
where the structural parser cannot establish a boundary. Relative child enumerators whose whole
line contains body text are also retained. Existing record/pair bounds still advertise truncation.

`source_fix.patch` shows the complete runtime delta. No structural-parser, clause-segmentation,
neural, reference, temporal, model-weight or rule-threshold code changed. No frontend code changed.
Source substrings, Unicode half-open offsets, section identity/parent-child hierarchy and citation
resolution remain intact. This fixes a specific consumption omission; it does not guarantee that
every linguistic obligation can be recognized or correctly interpreted.

Final binding source SHA-256:

```text
e82426fd6d4fea02ce4a2f1b1b34075361f928569a5eb30d088e83ca30200772
```

The existing experimental schema version remains v1.1; the freeze manifest and source hash
identify this corrected implementation rather than pretending older v1.1 measurements used it.

## Tests and audit-output compatibility

| Verification | Actual result | Evidence under `audit/final_source_freeze_2026_10_28/` |
| --- | --- | --- |
| Original omission regression | 10 failed, 3 passed, exit1 | `reproduction_before.xml/.log` |
| Corrected affected suite | 127 passed, exit0; 24.17 s | `affected_after.xml/.log` |
| **Final full native suite** | **484 passed, 0 failed, 2 skipped**, exit0; 144.89 s; nine warnings | `full_native_v1.xml/.log` |
| Frozen neural clause results | 148/148 identical | `preserved_output_verification.json` |
| Structure / references / graph | 148/148 identical for each | same core evidence |
| Temporal integration | 148/148 match direct unchanged checker; 38/38 saved Phase 3 outputs match | same core evidence |
| Frontend lint / production build | exit0 for both | frontend logs and results JSON |
| Frontend workflow / alignment | 20 passed / 17 passed | corresponding frontend logs |
| Docker runtime | **UNVERIFIED / BLOCKED**, version exit1, Server=null, missing engine pipe | `docker_engine.log` |

Overlapping test runs are not added together. Optional skips remain the live CUAD order-report
existence/verdict checks. Starlette/httpx and tokenizer deprecations and small conformal-fixture
warnings are retained. No tests, labels, warnings or historical experiment results were suppressed.

New regression cases cover numbered/Article headings, nested and relative headings, same-line
and multiline bodies, inline citations, indented headings, malformed/ambiguous inputs, Unicode,
CRLF and the existing explicit source/record/pair limits. Actual TXT/PDF/DOCX integration verifies
same-line nested/relative bodies with real offline model analysis, authentication and other-owner
rejection, saved history, exact source evidence and both rendered reports parsed back for content.
These are local TestClient workflows, not a new browser audit, full OS-process restart test or
external security validation. Existing user services were not interrupted.

Existing core API/scoring/reference/date output is compatible and unchanged in these checks.
The opt-in experimental obligation inventory is intentionally more complete on affected inputs;
it is not promised byte-identical to the buggy inventory. New inline workflow tests also compare
the complete core result before versus after experimental opt-in. The report formats and owner
access controls remain working.

## Same three authentic public contracts: before/after

The fixed selection is unchanged from Phase 4A/4A.1: TORO CO, CIK0000737758, accession
0000737758-23-000034, filing date2023-12-20. Cached source and provenance are retained; no new
contracts or labels were selected to improve results. Each ran as raw source and as the explicitly
identified existing HTML-extraction view: **six observations of three contracts**.

| Public source | Legacy clauses before/after | Binding records before -> after | Emitted pairs before -> after | Skipped lexical modal cues before -> after |
| --- | --- | --- | --- | --- |
| [EX-10.27](https://www.sec.gov/Archives/edgar/data/737758/000073775823000034/ttc-10312023xex1027.htm) | 26 / 26 | 2 -> 20 | 1 -> 190 | 24 -> 0 |
| [EX-10.29](https://www.sec.gov/Archives/edgar/data/737758/000073775823000034/ttc-10312023xex1029.htm) | 25 / 25 | 1 -> 20 | 0 -> 190 | 25 -> 0 |
| [EX-10.34](https://www.sec.gov/Archives/edgar/data/737758/000073775823000034/ttc-10312023xex1034.htm) | 19 / 19 | 5 -> 9 | 10 -> 36 | 5 -> 0 |

In the normalized views, previously skipped cues fall **54 -> 0**: all **62/62** recognized lexical
modal occurrences now fall within retained binding-record source spans. Multiple modal cues can
share one record; 62 cues are not 62 independently labelled obligations. Source, structure,
reference resolution and legacy clause inventories remain identical across before/after checks.

Binding records increase **8 -> 49** and emitted pairs **11 -> 416**. **All 416 remain UNSUPPORTED**:
supported pair coverage is0/416, pair abstention416/416, and documents with a supported pair0/3.
This correction improves text availability, not demonstrated natural-contract binding accuracy.
Raw markup remains unsupported. No public legal ground truth, contradiction labels, precision,
recall, F1 or legal-error accuracy is manufactured from these observations.

`public_source_evidence.jsonl` retains exact input views, raw/input hashes, source URLs/filing
identities, structures, clause inventories and complete baseline/corrected binding evidence.
`public_source_verification.json` provides the compact table and assertions. Offsets refer to
the identified Unicode extraction view, not original HTML bytes or PDF page coordinates.

## Exact repository state and freeze identity

* Workspace: `F:\projects\nlp\Legal-contract-coherence-auditor-`.
* Existing branch: **`codex/lexaudit-personal-release`**.
* Base HEAD: **`e5436ea4da3fcaeb7f000a0c06a95a3a125514b8`**. No new commit, tag, branch, push or deployment.
* The working tree remains intentionally **dirty**, including pre-existing UI/research work and
  untracked phase artifacts. HEAD alone does **not** identify the frozen prototype. Use the source
  file manifest and local archive receipt to identify the actual tested working tree.
* Initial preservation snapshot covers1,465 existing source/frontend/research/evidence files;
  root-file hashes are recorded separately. Existing private/runtime paths are not copied into
  the source package. Current status and included-file hashes are stored in the freeze manifest.
* Runtime source change in this task: only `src/obligations/binding.py`. Added two focused regression
  test files, this final report, release verification evidence, and additive README/tracker notices.
  Prior reports/results and pre-existing user changes remain intact.
* Existing CPU environment: Python3.11.9, Node24.13.1, npm11.8.0. Installed distribution versions
  are recorded in `environment.json`; existing dependency/lock files are included. No dependency
  installation, model download, retraining or recalibration was performed.

Freeze artifacts:

1. **`RESEARCH_FREEZE_MANIFEST.json`** — per-file SHA-256/size for included source/configuration,
   tests, docs and evaluation/final evidence; base Git/status identity; required local-asset hashes.
2. **`LexAudit-research-prototype-source.zip`** — local source/evidence snapshot; its manifest is
   included. It excludes Git objects, private environment files, user contracts/documents, databases,
   virtual environments, runtime/model caches and model weights. Historical datasets and broader
   research assets stay in the original workspace, covered by preservation hashes and inventory.
3. **`archive_receipt.json`** — archive SHA-256, size and checked member count. This hash identifies
   the archive without a circular self-hash inside its manifest.
4. **`final_verification.json`** — actual preservation, model/cache, baseline/patch, source-manifest,
   archive membership and native-test verification. Local assets are required separately; the ZIP
   is not represented as a model/data redistribution or a tested fresh-machine installation.

## Research-paper evidence inventory

| Evidence group | Repository location / artifact | What a paper may support—and its limit |
| --- | --- | --- |
| Frozen implementation and environment | Final freeze manifest, source ZIP/receipt, environment JSON; root dependency files | Exact tested native implementation; not a newly committed release or container proof |
| Frozen model/scoring assets | `models/coherence_classifier.pt`, centroid/calibration fixtures; local Legal-BERT fingerprint | Checkpoint/config identity; retain original calibration provenance and redistribution constraints |
| Data and source provenance | `data/raw/sec_edgar/edgar_manifest.json`; phase corpus/split manifests | Document identity and author-controlled labels; public documents are not expert legal ground truth |
| Initial detection baseline | `evaluations/phase1_detection_baseline_2026_10_26/` and its three reports | Exposed mechanical/provisional task results; no aggregate real-world legal accuracy |
| Structural parsing/reference work | Phase2 evaluation directory and five `PHASE2_*.md` reports | Exact-source/reference experiments with their original code manifests and development exposure |
| Temporal reasoning | Phase3 evaluation directory and four reports; Phase4A additive audit erratum | Original task results; final Phase3 review union40%, supported statements96/118 supersede stale prose |
| Obligation binding and repairs | Phase4A and Phase4A.1 directories/reports, baseline snapshots and annotation overlays | Controlled comparability results, abstentions and known label defects; formerly reserved examples are exposed |
| Final source correction | This report, exact patch, pre-fix failed tests, public before/after evidence | Text-consumption omission fixed; no claim that restored text is correctly bound |
| Application regression evidence | Final native XML/log, core parity, frontend checks and real-format workflows | Local application behavior/integration, not independent legal/scientific/security validation |
| Earlier exploratory research | Existing `research/`, `audit/`, `design/` files and original manifests | Preserved historical artifacts; do not imply this freeze independently validated every historical claim |

For paper collection, retain each result with its own source/input manifest and exposure/provenance
notes. Do not pool repeated formats or reused development examples as independent test samples.
The final source fix does not retroactively change historical predictions. Do not silently rename
synthetic/reused examples as unseen holdouts, qualified annotations or validated legal defects.

## Reproduce the frozen native prototype

From the repository root in PowerShell, with existing model/assets and private configuration:

```powershell
$env:HF_HUB_OFFLINE='1'
$env:TRANSFORMERS_OFFLINE='1'
$env:LEXAUDIT_ALLOW_MODEL_DOWNLOAD='0'
$env:OMP_NUM_THREADS='2'
$env:MKL_NUM_THREADS='2'
tmp/final-release/clean-env/Scripts/python.exe -m pytest tests -q
cd frontend
npm run lint
npm run build
npm run test:workflow
npm run test:alignment
```

The final public/core verification scripts refuse to overwrite their saved evidence. Inspect or
copy the archived audit output to a new output location when rerunning; do not replace originals.
The runtime remains the existing launcher/configuration:

```powershell
tmp/final-release/clean-env/Scripts/python.exe scripts/run_server.py --port 8012
# Another terminal:
cd frontend
$env:NEXT_PUBLIC_API_URL='http://127.0.0.1:8012'
npm run dev -- --port 3002
```

Use existing local authentication/encryption setup from `INSTALL_AND_RUN.md`; private keys are
not packaged. Keep stable storage encryption and original required model assets. Tests isolate
temporary storage and use actual local models. The configured frontend build fetches its fonts;
permitted-network build passed. No running user service was restarted for this task.

## Remaining limits and final decision

Raw HTML layout, OCR/scanned-document requirements, ambiguous boundaries, limited action grammar,
unestablished event occurrences, complex conditions/aliases and explicit source/record/pair bounds
remain. Absence of a finding is not a legal clean bill of health. Neural scores remain statistical
candidates; conformal intervals keep their original synthetic-shuffle limitations.

Independent legal annotation, genuinely unseen natural document-family evaluation, external
security validation and a fresh-machine portability test were not performed. Docker runtime for
this revision remains unverified because the engine pipe is absent. No reset/prune/WSL deletion
or deployment was attempted. Model/data rights and publication of private materials require their
own review; this local freeze does not authorize external redistribution.

**Source-text consumption bug: fixed in the tested scope. Previous core audit outputs: compatible.
Reproducible native research prototype: ready to freeze and collect paper evidence with these
limitations. Authentic-contract contradiction detection: NO-GO.** No further implementation or
experimental phase follows this task.
