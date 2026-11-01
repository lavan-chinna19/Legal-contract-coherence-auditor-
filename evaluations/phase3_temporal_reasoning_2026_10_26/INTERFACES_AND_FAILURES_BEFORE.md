# Phase 3 pre-change audit

Date checker: `extract_dates_from_clause(ClauseRecord)->list[DateEntity]` and
`check_document(clauses,doc_id=None)->(flags,dates)`. DateEntity's parsed_iso is a string; uncertain
parses need separate temporal metadata rather than fake dates. RuleFlag severity and existing types
are consumed by APIs, reports and redteam. Preserve the two-value facade; add richer analyze_document.

UnifiedAuditor currently runs dates on legacy neural clauses. Phase 2 already supplies unchanged
extraction plus a source-preserving StructuralDocument for references. Reuse that object for temporal
source/section evidence without altering the structural parser or neural clauses. API jobs save metadata
and infer review state from flags/reference reviews; extend review state to temporal uncertainty.
PDF/DOCX report_blocks must show temporal categories and exact spans, not only generic rule severity.

Observed frozen failures: T08 substring `to` in `relates to` invents a range; T12 global effective×end
cross-products compare different agreements; T13 legacy date-line segmentation loses role association;
T16 60-character context window misses the effective role. T11 silently chooses numeric locale, T14
silently drops invalid February 30. T15 permitted prepayment still gets an operational warning. Old
payment-before-effective and notice-after-expiry rules express arithmetic candidates, not proof of
incompatible obligations. Effective/execution dates, renewal phases, actors, trigger events, conditions,
business calendars and compatible stricter deadlines are not represented.

The exact old checker was copied before implementation. Old Phase 1 temporal cases are run before
new code. Phase 1/2 results, parser, neural assets and historical datasets are hashed and immutable.
Existing tests expect legacy flag types and priority severity; decision category will independently
state mathematical certainty. Existing expectations will not be disabled to hide changed behavior.
