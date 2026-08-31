"""
src/scoring/diagnostics.py — Human-readable and JSON diagnostics reporting for Dual-Channel scoring.
Surfaces per-clause Channel A (semantic OOD), Channel B (transition), Cross-Channel Agreement,
Conformal Uncertainty Intervals, and Severity Rationale.
"""
import json
from typing import Dict, Any
from src.scoring.schema import DocumentScoringResult


def format_diagnostics_markdown(result: DocumentScoringResult) -> str:
    """
    Renders a detailed, human-readable markdown diagnostics report.
    """
    lines = []
    lines.append(f"# Contract Anomaly Audit Report: `{result.doc_id}`\n")
    lines.append("## Executive Summary")
    lines.append(f"- **Total Clauses Audited:** {result.total_clauses}")
    lines.append(f"- **Total Anomalies Detected:** {result.anomaly_count}")
    lines.append(f"- **High Severity Anomalies:** {result.high_severity_count}")
    lines.append(f"- **Medium Severity Anomalies:** {result.medium_severity_count}")
    lines.append(f"- **Mean Combined Anomaly Score:** {result.mean_combined_score:.4f}")
    lines.append(f"- **Max Anomaly Score:** {result.max_combined_score:.4f}")
    lines.append(f"- **Calibration Provenance:** `{result.calibration_source}`\n")

    lines.append("## Per-Clause Diagnostics Table")
    lines.append(
        "| Seq | Clause ID | Score A (OOD) | Score B (Trans) | Combined | Agreement | Conformal 90% CI | Severity | Rationale |"
    )
    lines.append(
        "|:---:|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---|"
    )

    for c in result.clauses:
        sev_badge = c.severity
        if c.severity == "HIGH":
            sev_badge = "**HIGH** [!]"
        elif c.severity == "MEDIUM":
            sev_badge = "**MED** [*]"
        elif c.severity == "LOW":
            sev_badge = "LOW [-]"
        else:
            sev_badge = "CLEAN [OK]"

        # Agreement string
        agree_str = f"{c.cross_channel_agreement:.2f} ({c.agreement_type})"

        # CI string
        if c.confidence_interval is not None:
            ci_str = f"[{c.confidence_interval[0]:.2f}, {c.confidence_interval[1]:.2f}]"
        else:
            ci_str = "N/A"

        just = c.severity_justification or "N/A"

        lines.append(
            f"| {c.sequence_idx} | `{c.clause_id}` | {c.channel_a_score:.3f} | {c.channel_b_score:.3f} | "
            f"**{c.combined_score:.3f}** | {agree_str} | {ci_str} | {sev_badge} | {just} |"
        )

    lines.append("\n## Anomaly Detail Breakdown")
    anomalies = [c for c in result.clauses if c.is_anomaly]
    if not anomalies:
        lines.append("No high or medium severity anomalies detected in this document.")
    else:
        for a in anomalies:
            lines.append(f"### Clause `{a.clause_id}` (Index {a.sequence_idx}) — Severity: {a.severity}")
            lines.append(f"- **Preview:** *\"{a.text_preview}\"*")
            lines.append(
                f"- **Channel A (Semantic OOD):** Score = `{a.channel_a_score:.4f}` | "
                f"Nearest Reference Centroid: `{a.channel_a_evidence.nearest_centroid_label}` "
                f"(Distance = `{a.channel_a_evidence.centroid_distance:.4f}`)"
            )
            lines.append(
                f"- **Channel B (Discourse Transition):** Score = `{a.channel_b_score:.4f}` | "
                f"Incoming Continuity: `{a.channel_b_evidence.incoming_prob}` | "
                f"Outgoing Continuity: `{a.channel_b_evidence.outgoing_prob}`"
            )
            lines.append(
                f"- **Cross-Channel Agreement:** `{a.cross_channel_agreement:.4f}` ({a.agreement_type})"
            )
            if a.confidence_interval is not None:
                lines.append(
                    f"- **Conformal Interval (90%):** `[{a.confidence_interval[0]:.4f}, {a.confidence_interval[1]:.4f}]` "
                    f"(Width = `{a.interval_width:.4f}` | Source: `{a.calibration_source}`)"
                )
            lines.append(f"- **Decision Rationale:** {a.severity_justification}\n")

    return "\n".join(lines)


def format_diagnostics_report(result: DocumentScoringResult, format_type: str = "markdown") -> str:
    """
    Formats the document scoring result in the specified format ('markdown', 'text', or 'json').
    """
    if format_type == "json":
        return json.dumps(result.to_dict(), indent=2)
    else:
        return format_diagnostics_markdown(result)
