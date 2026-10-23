"use client";

import React from "react";
import { EnrichedClause } from "./types";
import { HelpCircle } from "lucide-react";

interface ScoreEvidencePanelProps {
  clause: EnrichedClause;
}

export function ScoreEvidencePanel({ clause }: ScoreEvidencePanelProps) {
  const chA = clause.channel_a_evidence;
  const chB = clause.channel_b_evidence;

  return (
    <div className="score-evidence-panel" style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
      {/* Primary KPI Score Grid */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(130px, 1fr))",
          gap: "0.75rem",
        }}
      >
        <div className="kpi-card" style={{ padding: "0.75rem" }}>
          <div className="kpi-label">Combined Score</div>
          <div
            className="kpi-value inspector-combined-score"
            style={{
              fontSize: "1.4rem",
              color:
                clause.severity === "HIGH"
                  ? "var(--color-danger)"
                  : clause.severity === "MEDIUM"
                  ? "var(--color-warning)"
                  : "var(--color-text-primary)",
            }}
          >
            {clause.combined_score.toFixed(3)}
          </div>
        </div>

        <div className="kpi-card" style={{ padding: "0.75rem" }}>
          <div className="kpi-label">Channel A (Semantic)</div>
          <div className="kpi-value inspector-cha-score" style={{ fontSize: "1.4rem" }}>
            {clause.channel_a_score.toFixed(3)}
          </div>
        </div>

        <div className="kpi-card" style={{ padding: "0.75rem" }}>
          <div className="kpi-label">Channel B (Transition)</div>
          <div className="kpi-value inspector-chb-score" style={{ fontSize: "1.4rem" }}>
            {clause.channel_b_score.toFixed(3)}
          </div>
        </div>

        <div className="kpi-card" style={{ padding: "0.75rem" }}>
          <div className="kpi-label">Agreement</div>
          <div className="kpi-value inspector-agreement-score" style={{ fontSize: "1.4rem" }}>
            {(clause.cross_channel_agreement * 100).toFixed(0)}%
          </div>
        </div>
      </div>

      {/* Channel A Details Card */}
      <div
        className="card"
        style={{
          margin: 0,
          padding: "1rem",
          background: "var(--color-surface-raised)",
          border: "1px solid var(--color-border)",
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.5rem" }}>
          <h4 style={{ fontSize: "0.88rem", fontWeight: 700, color: "var(--color-text-primary)" }}>
            Channel A — Legal-BERT Semantic Representation
          </h4>
          <span style={{ fontSize: "0.72rem", color: "var(--color-text-muted)", fontStyle: "italic" }}>
            Cosine / Centroid Distance
          </span>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.5rem", fontSize: "0.8rem" }}>
          <div>
            <span style={{ color: "var(--color-text-secondary)" }}>Nearest Cluster: </span>
            <strong style={{ color: "var(--color-text-primary)" }}>{chA.nearest_centroid_label || "Not available"}</strong>
          </div>
          <div>
            <span style={{ color: "var(--color-text-secondary)" }}>Centroid Distance: </span>
            <strong className="metric-cha-dist" style={{ color: "var(--color-text-primary)", fontFamily: "ui-monospace, monospace" }}>
              {chA.centroid_distance != null ? chA.centroid_distance.toFixed(3) : "Not available"}
            </strong>
          </div>
          <div>
            <span style={{ color: "var(--color-text-secondary)" }}>Distribution Status: </span>
            <strong style={{ color: chA.is_ood ? "var(--color-danger)" : "var(--color-success)" }}>
              {chA.is_ood ? "Out-of-Distribution (OOD)" : "In-Distribution"}
            </strong>
          </div>
          <div>
            <span style={{ color: "var(--color-text-secondary)" }}>Raw Score: </span>
            <strong style={{ color: "var(--color-text-primary)", fontFamily: "ui-monospace, monospace" }}>
              {clause.channel_a_score != null ? clause.channel_a_score.toFixed(3) : "Not available"}
            </strong>
          </div>
        </div>
      </div>

      {/* Channel B Details Card */}
      <div
        className="card"
        style={{
          margin: 0,
          padding: "1rem",
          background: "var(--color-surface-raised)",
          border: "1px solid var(--color-border)",
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.5rem" }}>
          <h4 style={{ fontSize: "0.88rem", fontWeight: 700, color: "var(--color-text-primary)" }}>
            Channel B — Adjacent Clause Coherence
          </h4>
          <span style={{ fontSize: "0.72rem", color: "var(--color-text-muted)", fontStyle: "italic" }}>
            Frozen neural classifier over Legal-BERT embeddings
          </span>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.5rem", fontSize: "0.8rem" }}>
          <div>
            <span style={{ color: "var(--color-text-secondary)" }}>Incoming Anomaly: </span>
            <strong className="metric-chb-incoming" style={{ color: "var(--color-text-primary)", fontFamily: "ui-monospace, monospace" }}>
              {chB?.incoming_anomaly != null ? chB.incoming_anomaly.toFixed(3) : "Boundary (None)"}
            </strong>
          </div>
          <div>
            <span style={{ color: "var(--color-text-secondary)" }}>Outgoing Anomaly: </span>
            <strong style={{ color: "var(--color-text-primary)", fontFamily: "ui-monospace, monospace" }}>
              {chB?.outgoing_anomaly != null ? chB.outgoing_anomaly.toFixed(3) : "Boundary (None)"}
            </strong>
          </div>
          <div>
            <span style={{ color: "var(--color-text-secondary)" }}>Prev Clause ID: </span>
            <strong style={{ color: "var(--color-text-primary)", fontFamily: "ui-monospace, monospace" }}>
              {chB?.prev_clause_id || "Document Start"}
            </strong>
          </div>
          <div>
            <span style={{ color: "var(--color-text-secondary)" }}>Next Clause ID: </span>
            <strong style={{ color: "var(--color-text-primary)", fontFamily: "ui-monospace, monospace" }}>
              {chB?.next_clause_id || "Document End"}
            </strong>
          </div>
        </div>
      </div>

      {/* Calibration & Conformal Metadata */}
      <div
        className="card"
        style={{
          margin: 0,
          padding: "1rem",
          background: "var(--color-surface)",
          border: "1px solid var(--color-border)",
        }}
      >
        <h4 style={{ fontSize: "0.88rem", fontWeight: 700, marginBottom: "0.5rem", color: "var(--color-text-primary)" }}>
          Calibration &amp; Conformal Uncertainty
        </h4>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.5rem", fontSize: "0.8rem" }}>
          <div>
            <span style={{ color: "var(--color-text-secondary)" }}>Confidence Interval: </span>
            <strong style={{ color: "var(--color-text-primary)", fontFamily: "ui-monospace, monospace" }}>
              {clause.confidence_interval != null && clause.confidence_interval.length === 2 && clause.confidence_interval[0] != null && clause.confidence_interval[1] != null
                ? `[${clause.confidence_interval[0].toFixed(2)}, ${clause.confidence_interval[1].toFixed(2)}]`
                : "Not available"}
            </strong>
          </div>
          <div>
            <span style={{ color: "var(--color-text-secondary)" }}>Calibration Source: </span>
            <strong style={{ color: "var(--color-text-primary)" }}>
              {clause.calibration_source || "Uncalibrated Baseline"}
            </strong>
          </div>
          <div>
            <span style={{ color: "var(--color-text-secondary)" }}>Agreement Type: </span>
            <strong style={{ color: "var(--color-text-primary)" }}>
              {clause.agreement_type || "Concordant"}
            </strong>
          </div>
          {clause.interval_width != null && (
            <div>
              <span style={{ color: "var(--color-text-secondary)" }}>Interval Width: </span>
              <strong style={{ color: "var(--color-text-primary)", fontFamily: "ui-monospace, monospace" }}>
                {clause.interval_width.toFixed(3)}
              </strong>
            </div>
          )}
        </div>

        {clause.severity_justification && (
          <div style={{ marginTop: "0.6rem", paddingTop: "0.6rem", borderTop: "1px solid var(--color-border-subtle)" }}>
            <span style={{ fontSize: "0.75rem", color: "var(--color-text-secondary)", fontWeight: 600 }}>
              Severity Justification:
            </span>
            <p style={{ fontSize: "0.8rem", color: "var(--color-text-primary)", marginTop: "0.2rem" }}>
              {clause.severity_justification}
            </p>
          </div>
        )}
      </div>

      {/* Scientific Limitation Footnote */}
      <div className="caveat-box" style={{ margin: 0 }}>
        <div style={{ display: "flex", gap: "0.5rem", alignItems: "flex-start" }}>
          <HelpCircle size={15} style={{ color: "var(--color-text-muted)", marginTop: "2px", flexShrink: 0 }} aria-hidden="true" />
          <span>
            <strong>Diagnostic Metric Scope:</strong> Combined anomaly scores reflect relative divergence from baseline SEC Exhibit 10 corpora. Higher scores indicate mathematical discourse atypicality, not statutory invalidity or unenforceable contract terms.
          </span>
        </div>
      </div>
    </div>
  );
}
