# Interfaces recorded before Phase 2 production changes

2026-10-26. Exact pre-change files are under `legacy_snapshot/`; hashes of all existing source,
dirty frontend work, models, historical research and Phase 1 evidence are in `preservation_before.json`.

* `parse_document(content: bytes, filename: str) -> str` (`src/api/ingestion.py`): extracted UTF-8
  text; FastAPI HTTPException on unsupported/invalid/oversized inputs. Upload router stores encrypted
  extraction. No PDF page coordinates. TXT/PDF/DOCX supported; no OCR.
* `RuleBasedSegmenter.segment(text, doc_id='unknown') -> list[ClauseRecord]`: `_clean_html` strips
  `<...>`, normalizes HTML entities/newlines; numbered/all-caps line splits. ClauseRecord fields:
  clause_id/doc_id/text/label/sequence_idx/char_start/char_end/source/split. Offsets in legacy
  normalized text. Consumers: API preview/jobs/XAI/reposition/redteam, direct scoring and research.
  Phase 2 will preserve this neural input path, including its known losses, and expose a separate
  exact-extraction structural inventory; it must not silently reinterpret old ML scores.
* `CrossReferenceChecker(nlp=None)`: `extract_declared_targets(clauses) -> list[ReferenceTarget]`,
  `extract_citations(clause) -> list[CrossReferenceCitation]`,
  `check_document(clauses, doc_id=None) -> (list[RuleFlag], list[ReferenceTarget])`.
  Consumers: UnifiedAuditor, existing tests. normalize_section_num helper imported by tests;
  it will retain compatibility but cease controlling exact resolver identity.
* ReferenceTarget: target_type/target_id/raw_label/clause_id/char_start/char_end.
  CrossReferenceCitation: target_type/target_id/raw_text/source_clause_id/char_start/char_end.
  RuleFlag: flag_id/doc_id/flag_type/category/severity/title/description/clause_id/
  involved_clause_ids/evidence/claim_scope. Existing dangling types and critical-citation severity
  must remain compatible. Ambiguous reviews must not become missing-target defect flags.
* `detect_dependencies(clauses: list[dict]) -> dict`: experimental/version/edges/findings/reviews/
  status/scope. Edge source_clause_id/target_section_id/reference/local char_start/char_end/
  direction/source_position/target/status/reason. Target clause_id/section_id/position/excerpt.
  Consumer: explicit opt-in authenticated release route, stored metadata, reports, frontend
  DependencyGraphResult and historical direction tests. Preserve these fields; add explicit
  extraction-coordinate evidence and resolver states without merging graph scores into ML.
* `UnifiedAuditor.audit_document(clauses, doc_id=None) -> UnifiedAuditReport`: ML then references
  and dates; counts and metadata. API job serializes result and adds clause_inventory/source_text.
  Dates receive the same legacy clauses. New exact source is an optional keyword; legacy callers
  with only clause records remain supported using documented clause-assembly coordinates.
* GET `/v1/documents/{doc_id}/clauses`: owner-protected `{doc_id,source_text,clauses}`;
  source_text normalized, clauses identical to job inventory. Extend, do not replace these meanings.
* POST `/v1/experimental/dependencies`: requires explicit opt-in and completed owner job;
  currently reads saved clause_inventory. New jobs can reuse shared structural metadata. Old saved
  jobs must disclose legacy-only evidence instead of claiming recovered raw extraction.
* `report_blocks` / `render_report`: PDF/DOCX share factual content, include rule evidence and graph
  JSON; source clause inventory currently legacy normalized text. Add source structural evidence
  and review states to both formats while retaining old report sections.

Existing tests: `test_rules`, `test_segmentation`, `test_final_release`, `test_ensemble`,
`test_severity`, API/XAI/redteam/security/ownership/report tests and historical research suites.
Phase 1 canonical directional subset: 13 documents, 4 conflicts/9 controls. Main paired baseline:
70 exposed development documents in authored/TXT modes plus 8 format probes. No unseen/legal labels.
