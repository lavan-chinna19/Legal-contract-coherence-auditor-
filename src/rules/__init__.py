"""
src/rules — Rule-Based Information Extraction and Logic Validation Layer.
Provides spaCy cross-reference validation, dateparser date-logic checking,
and integration into the unified auditor pipeline.
"""
from src.rules.schema import (
    RuleFlag,
    UnifiedAuditReport,
    ReferenceTarget,
    CrossReferenceCitation,
    DateEntity,
    ClaimScope
)
from src.rules.reference_checker import CrossReferenceChecker
from src.rules.date_checker import DateLogicChecker
from src.rules.unified_pipeline import UnifiedAuditor, format_unified_audit_report

__all__ = [
    "RuleFlag",
    "UnifiedAuditReport",
    "ReferenceTarget",
    "CrossReferenceCitation",
    "DateEntity",
    "ClaimScope",
    "CrossReferenceChecker",
    "DateLogicChecker",
    "UnifiedAuditor",
    "format_unified_audit_report"
]
