# Phase 2 — source-preserving structural parser design

2026-10-26. Implementation and development evaluation; no independent legal validation.

## Design boundary

The structural inventory is a new rule input, separate from the frozen neural/date input inventory.
`RuleBasedSegmenter` and its legacy HTML normalization are unchanged. Changing their output would
change Legal-BERT embeddings and adjacent-clause pairs, conflating a parser improvement with a model
change. Phase 2 therefore preserves that input path and exposes its limitations explicitly rather
than silently replacing it. The UI was not redesigned or edited.

```text
TXT/PDF/DOCX bytes -> existing bounded ingestion -> unchanged extracted Unicode text
  |-> existing v1 normalization/segmentation -> frozen A/B/ensemble + unchanged date rules
  |-> new source-preserving structural parser -> reference resolver -> missing flags / reviews
                                                            |-> opt-in positional graph
```

The pre-change interface/consumer inventory and five exact legacy modules were recorded before
implementation in `evaluations/phase2_structural_parser_2026_10_26/INTERFACES_BEFORE.md` and
`legacy_snapshot/`. Phase 1 corpus, predictions, scripts and documentation remain untouched.

## Representation and invariants

`src/structure/parser.py` provides `parse_contract(clauses=None, doc_id=None, *, source_text=None,
coordinate_space=None) -> StructuralDocument`. Its reusable dataclass serializes via `to_dict()`:

* `source_text`: exact input string, including CRLF, whitespace, comparison operators and Unicode.
  No HTML cleaner, entity decoding, identifier rewriting or text deletion occurs here.
* `coordinate_space`: `original_extracted_text` when the original extraction is supplied;
  `assembled_clause_text` when only existing clause records are available. Assembly inserts two
  newline characters between provided clauses and does not claim to recover missing source text.
* `source_sha256`, version, and an explicit half-open Unicode code-point offset convention.
  These are not UTF-8 byte positions, PDF page coordinates, bounding boxes or OCR alignments.
* `sections`: exact identity/raw identifier, namespace, title/title span, heading span/text,
  physical order, stable document-local UID, immediate body-unit span/text, parent identity/UID,
  parent candidates, children and associated source clause IDs. Duplicate identities are retained.
* `references`: source span/text, group and reference UIDs, target identity/type, direction,
  source-section UID, associated clause ID, coordinate space and any unsupported syntax reason.
* `reviews`: uncertain headings or resource-limit evidence. Uncertainty is not converted into
  a declaration. A possible target heading prevents an unsupported absence finding for that identity.
* `units`: exact, contiguous source slices. Concatenating all unit texts equals source_text;
  all heading/title/identifier/reference slices equal their literal source evidence.
* `clause_links`: associations with existing scoring clause IDs, marked exact text/assembly or
  `PARTIAL_FIRST_LINE_ANCHOR`. Partial association never asserts the legacy clause retained the
  whole source. If no link is justified, a separate source-unit identity is used.

Section `char_end` terminates at the next structural heading; this is an immediate content unit,
not a recursively expanded parent extent. Children are linked explicitly. Missing parents are not
invented, and duplicate parent identities leave parent_uid unset with candidates retained.

## Heading evidence

Supported numeric headings include `Section 4. Payment`, `4. Payment`, `4.2 Payment`,
`4.2.1 Timetable` and explicit nested identifiers such as `Section 4.2(a). Fees`.
A parenthesized `(a)` enumerator under an established numeric section can declare `4.2(a)`;
its body may be an ordinary sentence. A standalone enumerator without a numeric parent is uncertain.
Heading titles are retained exactly as source substrings, not generated labels.

Recognition is anchored to physical line starts, requires defined delimiter/title evidence, and
rejects clear citation/verb continuations such as `Section 4 shall apply`, `Section 4 above applies`
and `Exhibit Z supplies`. Date-like lines, years and amount continuations are not headings.
An untitled `Section 4.` or uncertain title is a review candidate, not an invented declaration.
The conservative grammar remains heuristic: unfamiliar heading styles and titleless numbered body
clauses can require review or fall outside support; it is not a universal legal-document parser.

Actual section/article/exhibit/schedule declarations use separate namespaces. Exact numeric strings
are preserved, including leading zeroes and parenthesized suffixes; matching is case-insensitive,
but `4.01` is not automatically `4.1`, and a parent does not imply all children exist.

Known HTML markup is preserved literally. This phase does not reconstruct its structure; unresolved
targets in markup receive unsupported/review status rather than a claim of absence. Plain comparison
operators do not trigger that markup fallback. OCR, tables and layout reconstruction remain unchanged.

## Integration and compatibility

* `CrossReferenceChecker.check_document` still returns `(flags, declared_targets)`. New
  `analyze_document` returns the shared structure, resolutions and separate reviews as well.
  The legacy `normalize_section_num` import remains available but does not control resolution.
  Only supported genuinely missing targets produce existing `DANGLING_*_REFERENCE` flags.
* `UnifiedAuditor.audit_document` adds optional keyword `source_text`; ML/date calls still use the
  original clause arguments. Metadata adds structural_document, reference_resolutions,
  reference_reviews and reference_review_count. Reviews are not counted as confirmed missing targets.
* API jobs pass the original extraction and save it, the structural inventory and references in the
  existing encrypted analysis snapshot. Review-only analyses have REVIEW_REQUIRED state.
* Preview retains old `source_text`/`clauses` meanings for existing UI/model alignment. It adds
  `original_source_text`, `structural_document`, `reference_resolutions` and
  `neural_input_coordinate_space=legacy_normalized_extracted_text`.
* The graph keeps edges/findings/reviews/status and legacy clause association fields; it adds exact
  absolute extraction spans, resolution status, parser version and association quality. Original
  extraction is reused for new jobs. Old saved jobs disclose assembled-only evidence and request
  reanalysis to recover original extraction; they do not claim to reconstruct lost text.
* PDF and DOCX reports share the added structure/review/source-coordinate evidence. Neural and
  legacy clause sections remain identified separately. Ownership/authentication are unchanged.

Because full source is now an explicit input, API/direct parity tests must pass identical extraction.
The original EDGAR test used normalized clauses only and universal-newline file reads; it was updated
to use the same upload decoder and assert original-source/inventory preservation, retaining all its
existing numerical and rule parity assertions. This is documented input alignment, not relaxed tests.

## Bounds and validation

Source maximum is 250,000 characters, matching ingestion. The structural inventory allows 1,000
heading/candidate records and 5,000 references; supported ranges expand to at most 100 targets.
An incomplete bounded parse forces resolver abstention, including apparent unique matches.
Parent and span lookups use indices; fallback citation scanning avoids quadratic scans through
all already recognized references. Resource limits preserve the full source and cannot prove absence.

Tests cover grammar, hierarchy, duplicate/ambiguous/malformed syntax, source slices/CRLF/Unicode,
resource bounds, all 13 existing canonical directional cases, real format ingestion and authenticated
release workflows. Actual paired results and final test evidence are recorded separately in
`PHASE2_BEFORE_AFTER_RESULTS.md` and `PHASE2_IMPLEMENTATION_REPORT.md`.
