"""
src/rules/schema.py — Schemas for Rule-Based Checkers and Unified Flag Pipeline.
Provides typed data structures for cross-reference targets, parsed dates,
rule violations, and unified multi-paradigm audit reports.
"""
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any, Tuple
import uuid


@dataclass
class ClaimScope:
    """
    Strict claim scoping to guarantee explainability and audit discipline (Contract §5).
    """
    what_this_shows: str
    what_this_does_not_show: str

    def to_dict(self) -> Dict[str, str]:
        return asdict(self)


@dataclass
class ReferenceTarget:
    """
    A structural element (Section, Article, Exhibit, Schedule, Defined Term) declared in the contract.
    """
    target_type: str  # "SECTION", "ARTICLE", "EXHIBIT", "SCHEDULE", "DEFINED_TERM"
    target_id: str    # Normalized identifier (e.g., "1.1", "1.01", "IV", "EXHIBIT_A")
    raw_label: str    # Exact text from header/definition
    clause_id: str    # Clause where this section is declared
    char_start: int = 0
    char_end: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CrossReferenceCitation:
    """
    A detected cross-reference citation within a clause pointing to an internal target.
    """
    target_type: str        # "SECTION", "ARTICLE", "EXHIBIT", "SCHEDULE", "DEFINED_TERM"
    target_id: str          # Normalized referenced key
    raw_text: str           # e.g., "Section 4.2", "as defined in Section 1.01"
    source_clause_id: str   # Clause containing the citation
    char_start: int = 0
    char_end: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class DateEntity:
    """
    A date extracted from a clause, associated with its legal role and parsed datetime value.
    """
    role: str               # "EFFECTIVE_DATE", "TERMINATION_DATE", "EXPIRATION_DATE", "EXECUTION_DATE", "PAYMENT_DUE_DATE", "MILESTONE_DATE", "NOTICE_DATE", "GENERAL_DATE"
    raw_text: str           # Verbatim date string (e.g., "October 15, 2024")
    parsed_iso: str         # ISO format date string (e.g., "2024-10-15")
    clause_id: str          # Clause where date occurs
    char_start: int = 0
    char_end: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RuleFlag:
    """
    First-class flag for rule-based violations (cross-references, date logic).
    Integrated alongside ML flags in the unified pipeline.
    """
    flag_id: str
    doc_id: str
    flag_type: str          # e.g., "DANGLING_SECTION_REFERENCE", "INVERTED_CONTRACT_TERM", "INVALID_PAYMENT_TIMELINE"
    category: str           # "RULE_BASED"
    severity: str           # "HIGH", "MEDIUM", "LOW"
    title: str              # Concise title
    description: str        # Detailed explanation of contradiction or dangling reference
    clause_id: Optional[str] = None
    involved_clause_ids: List[str] = field(default_factory=list)
    evidence: Dict[str, Any] = field(default_factory=dict)
    claim_scope: Optional[ClaimScope] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        if self.claim_scope:
            d["claim_scope"] = self.claim_scope.to_dict()
        return d


@dataclass
class UnifiedAuditReport:
    """
    Complete unified document audit output combining ML-based dual-channel anomaly scoring
    with rule-based cross-reference and date-logic validation.
    """
    doc_id: str
    total_clauses: int
    ml_anomaly_count: int
    rule_violation_count: int
    total_flags: int
    high_severity_count: int
    medium_severity_count: int
    low_severity_count: int
    scoring_result: Any       # DocumentScoringResult from ML dual-channel pipeline
    rule_flags: List[RuleFlag] = field(default_factory=list)
    declared_targets: List[ReferenceTarget] = field(default_factory=list)
    extracted_dates: List[DateEntity] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "doc_id": self.doc_id,
            "total_clauses": self.total_clauses,
            "ml_anomaly_count": self.ml_anomaly_count,
            "rule_violation_count": self.rule_violation_count,
            "total_flags": self.total_flags,
            "high_severity_count": self.high_severity_count,
            "medium_severity_count": self.medium_severity_count,
            "low_severity_count": self.low_severity_count,
            "scoring_result": self.scoring_result.to_dict() if hasattr(self.scoring_result, "to_dict") else self.scoring_result,
            "rule_flags": [f.to_dict() for f in self.rule_flags],
            "declared_targets": [t.to_dict() for t in self.declared_targets],
            "extracted_dates": [d.to_dict() for d in self.extracted_dates],
            "metadata": self.metadata
        }
