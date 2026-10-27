# Phase 2 — reference resolution specification

2026-10-26. Deterministic textual structure/position only. No claim about legal validity.

## Identity and structure

A declaration needs justified source-heading evidence from the shared parser. Each actual occurrence
is retained; no duplicate is deduplicated into apparent uniqueness. Namespace and full identity are
matched case-insensitively without decimal or parent-child aliasing. For example, `4.2(a)` requires
that explicit child or an established parent plus supported `(a)` heading; `4.2` alone is insufficient.
`4.01` and `4.1` remain distinct strings. Numeric policy equivalence requires explicit future design,
not floating-point normalization. Section and Article are distinct namespaces.

## Supported reference grammar

| Syntax | Defined operation |
| --- | --- |
| `Section 4`, `Section 4.2`, `Section 4.2(a)` | Exact identity lookup; no direction inferred |
| `pursuant to Section 4`, `subject to Section 4`, `as defined in Section 4` | Same lookup, preserving critical-citation severity if genuinely missing |
| `Section 4 above/below` | Compare actual target heading position to literal citation position |
| `the above/below Section 4` | Same positional predicate, preposed direction retained |
| `Section 4, above`, `Section 4 (above)` | Supported surrounding direction punctuation, same positional predicate |
| `Sections 4 and 5`, `Sections 4, 5 and 6`, `Sections 4, 5, and 6` | Separate exact lookups with shared source citation/group ID |
| `Sections 4.1 through 4.3` / `to` | Inclusive final-integer expansion 4.1/4.2/4.3; same prefix, ordered endpoints, no zero-padding ambiguity, <=100 targets |
| `immediately preceding Section 4` | Previous physical SECTION declaration before the citation's source section; no guessed document-level legal dependency |
| Supported article/exhibit/schedule references | Same namespace-aware existence resolution; graph positional checks remain numeric SECTION only |
| Sentence-start citation | Same reference lookup, never a declaration merely because it starts a sentence |

Nondirectional references remain valid regardless of whether the target appears before or after the
citation. Noncanonical section order alone creates no defect. A target earlier in the same clause
can satisfy above; absolute source positions, not just clause sequence numbers, decide.

Hyphen/en-dash ranges, disjunctive `or`, cross-prefix/reversed/oversized/zero-ambiguous ranges,
malformed parenthesized identifiers, conflicting pre/post directions, unsupported word identifiers
and explicitly external Master/Other/Separate Agreement scope request review. No partial identifier
is allowed to turn an unsupported continuation into a missing-target assertion. A recognized keyword
with unsupported identity is retained as review evidence. Ordinary heading-title nouns such as
`Schedule of Fees` do not create an identifier citation; explicit identifiers inside titles can.
Other unrecognized natural-language references remain outside coverage; silence is not correctness.

## Resolver states and consumer behavior

| `resolution_status` | Meaning | Missing-reference rule | Experimental graph |
| --- | --- | --- | --- |
| RESOLVED | Exactly one justified exact declaration | No missing flag | Numeric sections: evaluate only explicit direction, otherwise SATISFIED |
| MISSING | No matching declaration in supported structure | Existing DANGLING namespace flag, source-backed evidence | REVIEW_REQUIRED; do not invent a positional conflict without a target |
| AMBIGUOUS_TARGET | Multiple actual candidate declarations | Separate metadata REVIEW_REQUIRED | REVIEW_REQUIRED, no directional verdict |
| AMBIGUOUS_STRUCTURE | An uncertain heading could declare the requested identity | Separate metadata REVIEW_REQUIRED | REVIEW_REQUIRED |
| UNSUPPORTED | Identifier/range/scope syntax outside support, markup prevents proving absence, or bounded parse is incomplete | Separate metadata REVIEW_REQUIRED | REVIEW_REQUIRED for recognized SECTION references |

Resolved Roman section references can be represented by the existence resolver when their exact
headings are explicit. The graph still abstains on Roman directions; it does not silently translate
Roman and Arabic identities. Missing Roman section references are unsupported rather than confident
absence findings. Article Roman identities are handled in their distinct namespace.

Reference metadata reviews also include heading ambiguity. A genuinely missing numeric target has
a reference-rule flag while the positional graph appropriately abstains. These different decisions
are deliberate and must not be pooled as one classifier. Rule counts exclude uncertain reviews;
API analysis_state still reflects their need for human attention.

Graph statuses retain NO_FINDINGS/REVIEW_REQUIRED/FINDING. An edge can be SATISFIED,
REVIEW_REQUIRED or VERIFIED_TEXTUAL_CONFLICT. A finding is a narrow source-backed positional
contradiction, not an inference about enforceability. Vague boundary antecedents retain review
behavior; intact local antecedents are not broken merely by moving their containing clause.

## Evidence schema and coordinates

Every reference stores literal text, `[char_start,char_end)` in the declared source coordinate space,
reference/group UIDs, target identity/type, direction and source section/clause association. Resolution
adds candidate section UIDs, reason, status and exact target evidence if unique. Missing flags keep
legacy flag fields while adding coordinate_space, source_sha256, reference_uid and resolution_status.

Graph edges preserve legacy names and add authoritative `source_char_start/source_char_end` plus
coordinate_space. Target evidence has absolute heading span/excerpt and section UID. Legacy local
offsets/positions are associated with a scoring clause or source region and carry clause_offset_mapping;
partial associations are not exact positions in legacy-normalized text. Consumers requiring precise
highlighting must use the absolute span with the matching source text/coordinate space.

Source coordinates are Unicode character indices in extracted text. CRLF counts as two code points.
They are not original PDF page coordinates. Clause-only calls explicitly use assembled text and do
not claim to recover content deleted by the old cleaner. Source text is preserved in encrypted saved
snapshots and intended reports, not application logs.

## Evaluation interpretation

Metrics count document-level presence and directional predicates separately. An unresolved positive
remains a miss in labelled recall; review coverage is also reported. Unknown/provisional legal labels
are never converted into TNs. The reused 70 cases and all new grammar tests are development evidence.
No independent legal adjudication, unseen-family validation or real-world accuracy estimate exists.
