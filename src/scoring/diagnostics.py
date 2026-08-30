"""
src/scoring/diagnostics.py — Human-readable and JSON diagnostics reporting for Dual-Channel scoring.
Surfaces per-clause Channel A (semantic OOD) and Channel B (transition) evidence.
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
    lines.append(f"- **Max Anomaly Score:** {result.max_combined_score:.4f}\n")

    lines.append("## Per-Clause Diagnostics Table")
    lines.append("| Seq | Clause ID | Score A (OOD) | Nearest Centroid (Dist) | Score B (Trans) | Trans Probs (In / Out) | Combined | Severity |")
    lines.append("|:---:|:---|:---:|:---|:---:|:---|:---:|:---:|")

    for c in result.clauses:
        ev_a = c.channel_a_evidence
        ev_b = c.channel_b_evidence
        
        cent_str = f"{ev_a.nearest_centroid_label} ({ev_a.centroid_distance:.3f})"
        
        in_p = f"{ev_b.incoming_prob:.2f}" if ev_b.incoming_prob is not None else "N/A"
        out_p = f"{ev_b.outgoing_prob:.2f}" if ev_b.outgoing_prob is not None else "N/A"
        trans_str = f"{in_p} / {out_p}"

        sev_badge = c.severity
        if c.severity == "HIGH":
            sev_badge = "**HIGH** [!]"
        elif c.severity == "MEDIUM":
            sev_badge = "**MED** [*]"
        elif c.severity == "LOW":
            sev_badge = "LOW [-]"
        else:
            sev_badge = "CLEAN [OK]"

        lines.append(
            f"| {c.sequence_idx} | `{c.clause_id}` | {c.channel_a_score:.3f} | {cent_str} | {c.channel_b_score:.3f} | {trans_str} | **{c.combined_score:.3f}** | {sev_badge} |"
        )

    lines.append("\n## Anomaly Detail Breakdown")
    anomalies = [c for c in result.clauses if c.is_anomaly]
    if not anomalies:
        lines.append("No high or medium severity anomalies detected in this document.")
    else:
        for a in anomalies:
            lines.append(f"### Clause `{a.clause_id}` (Index {a.sequence_idx}) — Severity: {a.severity}")
            lines.append(f"- **Preview:** *\"{a.text_preview}\"*")
            lines.append(f"- **Channel A (Semantic OOD):** Score = `{a.channel_a_score:.4f}` | Nearest Reference Centroid: `{a.channel_a_evidence.nearest_centroid_label}` (Distance = `{a.channel_a_evidence.centroid_distance:.4f}`)")
            lines.append(f"- **Channel B (Discourse Transition):** Score = `{a.channel_b_score:.4f}` | Incoming Continuity: `{a.channel_b_evidence.incoming_prob}` | Outgoing Continuity: `{a.channel_b_evidence.outgoing_prob}`")
            lines.append(f"- **Attribution / Hypothesis:** {'Semantic domain shift (OOD)' if a.channel_a_score > 0.5 else 'Discourse transition breakdown (Structural Discontinuity)'}\n")

    return "\n".join(lines)


def format_diagnostics_report(result: DocumentScoringResult, format_type: str = "markdown") -> str:
    """
    Formats the document scoring result in the specified format ('markdown', 'text', or 'json').
    """
    if format_type == "json":
        return json.dumps(result.to_dict(), indent=2)
    else:
        return format_diagnostics_markdown(result)
