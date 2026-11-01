"""
src/rules/unified_pipeline.py — Unified Audit Pipeline combining ML Anomaly Scoring and Rule-Based Validation.
Coordinates DualChannelScorer (ML Channel A + Channel B + Conformal Calibration + Severity Ranking)
with CrossReferenceChecker (spaCy) and DateLogicChecker (dateparser) to yield an integrated audit report.
"""
import time
import json
from typing import List, Optional, Dict, Any

from src.config import ClauseRecord
from src.scoring.pipeline import DualChannelScorer
from src.scoring.schema import DocumentScoringResult
from src.rules.schema import (
    RuleFlag,
    UnifiedAuditReport,
    ReferenceTarget,
    DateEntity
)
from src.rules.reference_checker import CrossReferenceChecker
from src.rules.date_checker import DateLogicChecker


class UnifiedAuditor:
    """
    Unified Legal Contract Coherence and Integrity Auditor.
    Integrates multi-paradigm checks:
    1. Statistical / ML Semantic OOD Anomaly Detection (Channel A)
    2. Statistical / ML Discourse Transition Incoherence (Channel B)
    3. Rule-Based Cross-Reference Resolution (spaCy)
    4. Rule-Based Date-Logic & Chronology Validation (dateparser)
    """

    def __init__(
        self,
        scorer: Optional[DualChannelScorer] = None,
        reference_checker: Optional[CrossReferenceChecker] = None,
        date_checker: Optional[DateLogicChecker] = None
    ):
        self.scorer = scorer or DualChannelScorer()
        self.reference_checker = reference_checker or CrossReferenceChecker()
        self.date_checker = date_checker or DateLogicChecker()

    def audit_document(
        self,
        clauses: List[ClauseRecord],
        doc_id: Optional[str] = None
    ) -> UnifiedAuditReport:
        """
        Executes end-to-end audit across both ML and rule-based pipelines.
        """
        effective_doc_id = doc_id or (clauses[0].doc_id if clauses else "empty_doc")

        if not clauses:
            empty_ml = self.scorer.score_document([], doc_id=effective_doc_id)
            return UnifiedAuditReport(
                doc_id=effective_doc_id,
                total_clauses=0,
                ml_anomaly_count=0,
                rule_violation_count=0,
                total_flags=0,
                high_severity_count=0,
                medium_severity_count=0,
                low_severity_count=0,
                scoring_result=empty_ml,
                rule_flags=[],
                declared_targets=[],
                extracted_dates=[],
                metadata={"timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())}
            )

        # 1. Run ML Dual-Channel Anomaly Scoring Pipeline
        ml_result: DocumentScoringResult = self.scorer.score_document(clauses, doc_id=effective_doc_id)

        # 2. Run spaCy Cross-Reference Validation
        ref_flags, declared_targets = self.reference_checker.check_document(clauses, doc_id=effective_doc_id)

        # 3. Run dateparser Date-Logic Validation
        date_flags, extracted_dates = self.date_checker.check_document(clauses, doc_id=effective_doc_id)

        all_rule_flags: List[RuleFlag] = ref_flags + date_flags

        # Attach rule flags to ml_result metadata for backward compatibility
        ml_result.metadata["rule_flags"] = [f.to_dict() for f in all_rule_flags]
        ml_result.metadata["rule_violation_count"] = len(all_rule_flags)

        # Calculate unified severity counts
        # ML anomalies
        ml_high = ml_result.high_severity_count
        ml_med = ml_result.medium_severity_count
        ml_anomalies = ml_result.anomaly_count

        # Rule violations
        rule_high = sum(1 for f in all_rule_flags if f.severity == "HIGH")
        rule_med = sum(1 for f in all_rule_flags if f.severity == "MEDIUM")
        rule_low = sum(1 for f in all_rule_flags if f.severity == "LOW")

        total_flags = ml_anomalies + len(all_rule_flags)
        total_high = ml_high + rule_high
        total_med = ml_med + rule_med
        total_low = rule_low

        return UnifiedAuditReport(
            doc_id=effective_doc_id,
            total_clauses=len(clauses),
            ml_anomaly_count=ml_anomalies,
            rule_violation_count=len(all_rule_flags),
            total_flags=total_flags,
            high_severity_count=total_high,
            medium_severity_count=total_med,
            low_severity_count=total_low,
            scoring_result=ml_result,
            rule_flags=all_rule_flags,
            declared_targets=declared_targets,
            extracted_dates=extracted_dates,
            metadata={
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
                "ref_flags_count": len(ref_flags),
                "date_flags_count": len(date_flags),
                "declared_targets_count": len(declared_targets),
                "extracted_dates_count": len(extracted_dates)
            }
        )


def format_unified_audit_markdown(report: UnifiedAuditReport) -> str:
    """
    Renders a comprehensive, human-readable markdown unified audit report.
    """
    lines = []
    lines.append(f"# Unified Contract Integrity & Coherence Audit: `{report.doc_id}`\n")
    lines.append("## 1. Executive Summary")
    lines.append(f"- **Total Clauses Audited:** {report.total_clauses}")
    lines.append(f"- **Total Flags Raised:** {report.total_flags} ({report.high_severity_count} High, {report.medium_severity_count} Medium, {report.low_severity_count} Low)")
    lines.append(f"  - **ML Coherence Anomalies:** {report.ml_anomaly_count}")
    lines.append(f"  - **Rule-Based Violations:** {report.rule_violation_count} (References: {report.metadata.get('ref_flags_count', 0)}, Dates: {report.metadata.get('date_flags_count', 0)})")
    lines.append(f"- **Mean ML Anomaly Score:** {report.scoring_result.mean_combined_score:.4f}")
    lines.append(f"- **Declared Structural Elements:** {len(report.declared_targets)}")
    lines.append(f"- **Extracted Contract Dates:** {len(report.extracted_dates)}\n")

    # Rule-Based Integrity Flags
    lines.append("## 2. Rule-Based Integrity Violations")
    if not report.rule_flags:
        lines.append("✓ No cross-reference or date-logic violations detected.\n")
    else:
        lines.append("| Flag ID | Type | Severity | Clause(s) | Summary |")
        lines.append("|:---|:---|:---:|:---:|:---|")
        for f in report.rule_flags:
            sev_str = f"**{f.severity}** [!]" if f.severity == "HIGH" else f"{f.severity} [*]"
            clauses_str = ", ".join(f.involved_clause_ids) if f.involved_clause_ids else (f.clause_id or "Doc")
            lines.append(f"| `{f.flag_id}` | `{f.flag_type}` | {sev_str} | `{clauses_str}` | {f.title} |")
        lines.append("")

        lines.append("### Rule Violation Details")
        for f in report.rule_flags:
            lines.append(f"#### [{f.severity}] {f.title} (`{f.flag_id}`)")
            lines.append(f"- **Type:** `{f.flag_type}` (Category: `{f.category}`)")
            lines.append(f"- **Description:** {f.description}")
            if f.claim_scope:
                lines.append(f"- **Scope:** *{f.claim_scope.what_this_shows}*")
            lines.append("")

    # ML Dual-Channel Diagnostics Table
    lines.append("## 3. ML Dual-Channel Coherence Table")
    lines.append(
        "| Seq | Clause ID | Score A (OOD) | Score B (Trans) | Combined | Conformal 90% CI | ML Severity | Rationale |"
    )
    lines.append(
        "|:---:|:---|:---:|:---:|:---:|:---:|:---:|:---|"
    )

    for c in report.scoring_result.clauses:
        sev_badge = c.severity
        if c.severity == "HIGH":
            sev_badge = "**HIGH** [!]"
        elif c.severity == "MEDIUM":
            sev_badge = "**MED** [*]"
        elif c.severity == "LOW":
            sev_badge = "LOW [-]"
        else:
            sev_badge = "CLEAN [OK]"

        ci_str = f"[{c.confidence_interval[0]:.2f}, {c.confidence_interval[1]:.2f}]" if c.confidence_interval else "N/A"
        just = c.severity_justification or "N/A"

        lines.append(
            f"| {c.sequence_idx} | `{c.clause_id}` | {c.channel_a_score:.3f} | {c.channel_b_score:.3f} | "
            f"**{c.combined_score:.3f}** | {ci_str} | {sev_badge} | {just} |"
        )

    return "\n".join(lines)


def format_unified_audit_report(report: UnifiedAuditReport, format_type: str = "markdown") -> str:
    """
    Formats the unified audit report in markdown or JSON format.
    """
    if format_type == "json":
        return json.dumps(report.to_dict(), indent=2)
    return format_unified_audit_markdown(report)
