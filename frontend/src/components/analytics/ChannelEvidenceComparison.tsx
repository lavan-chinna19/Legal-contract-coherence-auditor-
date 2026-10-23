"use client";

import React from "react";
import { ClauseResult } from "./types";
import { Compass, GitCommit, Split } from "lucide-react";

interface ChannelEvidenceComparisonProps {
  selectedClause?: ClauseResult;
}

export function ChannelEvidenceComparison({ selectedClause }: ChannelEvidenceComparisonProps) {
  if (!selectedClause) {
    return (
      <div className="card" style={{ height: "100%", display: "flex", alignItems: "center", justifyContent: "center", padding: "2rem" }}>
        <p style={{ color: "var(--color-text-muted)", fontSize: "0.9rem" }}>
          Select a clause to inspect multi-channel diagnostic evidence.
        </p>
      </div>
    );
  }

  const { channel_a_evidence, channel_b_evidence, channel_a_score, channel_b_score, combined_score, sequence_idx, clause_id } =
    selectedClause;

  const centroidDist = channel_a_evidence?.centroid_distance ?? channel_a_score;
  const nearestLabel = channel_a_evidence?.nearest_centroid_label ?? "Unknown Reference Cluster";
  const isOod = channel_a_evidence?.is_ood ?? false;

  const incomingProb = channel_b_evidence?.incoming_prob;
  const outgoingProb = channel_b_evidence?.outgoing_prob;
  const incomingAnomaly = channel_b_evidence?.incoming_anomaly;
  const outgoingAnomaly = channel_b_evidence?.outgoing_anomaly;

  return (
    <div
      className="card analytics-channel-comparison-card"
      role="region"
      aria-label="Multi-Channel Evidence Comparison"
      style={{ height: "100%", display: "flex", flexDirection: "column" }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "1rem" }}>
        <div>
          <h3 style={{ fontSize: "1.05rem", fontWeight: 600, color: "var(--color-text-primary)", margin: 0, display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <Split size={18} style={{ color: "var(--color-accent)" }} aria-hidden="true" />
            <span>Dual-Channel Evidence Decomposition</span>
          </h3>
          <p style={{ fontSize: "0.8rem", color: "var(--color-text-secondary)", margin: "0.25rem 0 0 0" }}>
            Detailed breakdown for § {sequence_idx} (<code style={{ fontSize: "0.75rem" }}>{clause_id}</code>).
          </p>
        </div>
        <div style={{ fontSize: "0.75rem", padding: "0.2rem 0.5rem", borderRadius: "4px", background: "var(--color-surface-raised)", border: "1px solid var(--color-border)" }}>
          Combined Score: <strong>{combined_score.toFixed(3)}</strong>
        </div>
      </div>

      {/* Scientific Incompatibility Disclosure */}
      <div
        className="caveat-box"
        style={{
          marginBottom: "1.25rem",
          padding: "0.75rem 1rem",
          fontSize: "0.8rem",
          background: "var(--color-surface-raised)",
          borderLeft: "3px solid var(--color-accent)",
          borderRadius: "4px",
          color: "var(--color-text-secondary)",
          lineHeight: 1.5,
        }}
      >
        <strong style={{ color: "var(--color-text-primary)" }}>⚠️ Scale &amp; Metric Distinction Notice:</strong>{" "}
        Channel A and Channel B operate in distinct mathematical domains. Channel A is a{" "}
        <strong>geometric cosine distance</strong> in R&sup7;&sup6;&sup8; Legal-BERT space (domain [0, 2]), whereas
        Channel B evaluates <strong>sequential discourse transition likelihoods</strong> (domain [0, 1]). They are
        analyzed independently below to prevent invalid direct-axis conflation.
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: "1rem", flex: 1 }}>
        {/* Panel 1: Channel A Semantic Out-of-Distribution Diagnostics */}
        <div
          style={{
            background: "var(--color-surface-raised)",
            border: "1px solid var(--color-border)",
            borderRadius: "6px",
            padding: "1rem",
            display: "flex",
            flexDirection: "column",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "0.75rem" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "0.4rem" }}>
              <Compass size={16} style={{ color: "var(--color-accent)" }} aria-hidden="true" />
              <h4 style={{ fontSize: "0.9rem", fontWeight: 600, color: "var(--color-text-primary)", margin: 0 }}>
                Channel A: Semantic Topic Fit
              </h4>
            </div>
            <span
              style={{
                fontSize: "0.7rem",
                fontWeight: 600,
                padding: "0.15rem 0.4rem",
                borderRadius: "3px",
                background: isOod ? "var(--sev-high-bg)" : "var(--sev-clean-bg)",
                color: isOod ? "var(--sev-high-text)" : "var(--color-success)",
              }}
            >
              {isOod ? "OOD Outlier" : "In-Distribution"}
            </span>
          </div>

          <div style={{ fontSize: "0.8rem", color: "var(--color-text-secondary)", marginBottom: "0.75rem" }}>
            Evaluates semantic isolation from canonical LEDGAR legal clause clusters.
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem", flex: 1, fontSize: "0.8rem" }}>
            <div style={{ display: "flex", justifyContent: "space-between", borderBottom: "1px solid var(--color-border)", paddingBottom: "0.35rem" }}>
              <span style={{ color: "var(--color-text-muted)" }}>Nearest Cluster:</span>
              <strong style={{ color: "var(--color-text-primary)", maxWidth: "160px", textOverflow: "ellipsis", overflow: "hidden", whiteSpace: "nowrap" }} title={nearestLabel}>
                {nearestLabel}
              </strong>
            </div>

            <div style={{ display: "flex", justifyContent: "space-between", borderBottom: "1px solid var(--color-border)", paddingBottom: "0.35rem" }}>
              <span style={{ color: "var(--color-text-muted)" }}>Centroid Distance (d):</span>
              <span style={{ fontWeight: 600, color: "var(--color-text-primary)" }}>
                {typeof centroidDist === "number" ? centroidDist.toFixed(4) : "N/A"}
              </span>
            </div>

            <div style={{ display: "flex", justifyContent: "space-between", borderBottom: "1px solid var(--color-border)", paddingBottom: "0.35rem" }}>
              <span style={{ color: "var(--color-text-muted)" }}>Channel Score (S_A):</span>
              <span style={{ fontWeight: 600, color: "var(--color-accent)" }}>
                {channel_a_score.toFixed(4)}
              </span>
            </div>

            <div style={{ display: "flex", justifyContent: "space-between" }}>
              <span style={{ color: "var(--color-text-muted)" }}>Metric Family:</span>
              <span style={{ color: "var(--color-text-secondary)" }}>Cosine Distance in R&sup7;&sup6;&sup8;</span>
            </div>
          </div>

          <div style={{ marginTop: "0.75rem", fontSize: "0.72rem", color: "var(--color-text-muted)", fontStyle: "italic" }}>
            Distance does not measure legal clarity or drafted quality.
          </div>
        </div>

        {/* Panel 2: Channel B Discourse Transition Diagnostics */}
        <div
          style={{
            background: "var(--color-surface-raised)",
            border: "1px solid var(--color-border)",
            borderRadius: "6px",
            padding: "1rem",
            display: "flex",
            flexDirection: "column",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "0.75rem" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "0.4rem" }}>
              <GitCommit size={16} style={{ color: "var(--sev-med-text)" }} aria-hidden="true" />
              <h4 style={{ fontSize: "0.9rem", fontWeight: 600, color: "var(--color-text-primary)", margin: 0 }}>
                Channel B: Discourse Flow
              </h4>
            </div>
            <span
              style={{
                fontSize: "0.7rem",
                fontWeight: 600,
                padding: "0.15rem 0.4rem",
                borderRadius: "3px",
                background: channel_b_score >= 0.5 ? "var(--sev-med-bg)" : "var(--sev-clean-bg)",
                color: channel_b_score >= 0.5 ? "var(--sev-med-text)" : "var(--color-success)",
              }}
            >
              Score: {channel_b_score.toFixed(3)}
            </span>
          </div>

          <div style={{ fontSize: "0.8rem", color: "var(--color-text-secondary)", marginBottom: "0.75rem" }}>
            Evaluates structural transitions across adjacent predecessor and successor clauses.
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem", flex: 1, fontSize: "0.8rem" }}>
            <div style={{ display: "flex", justifyContent: "space-between", borderBottom: "1px solid var(--color-border)", paddingBottom: "0.35rem" }}>
              <span style={{ color: "var(--color-text-muted)" }}>Incoming Flow (P_in):</span>
              <span style={{ fontWeight: 600, color: "var(--color-text-primary)" }}>
                {typeof incomingProb === "number" ? incomingProb.toFixed(3) : "First Clause (Bound)"}
              </span>
            </div>

            <div style={{ display: "flex", justifyContent: "space-between", borderBottom: "1px solid var(--color-border)", paddingBottom: "0.35rem" }}>
              <span style={{ color: "var(--color-text-muted)" }}>Outgoing Flow (P_out):</span>
              <span style={{ fontWeight: 600, color: "var(--color-text-primary)" }}>
                {typeof outgoingProb === "number" ? outgoingProb.toFixed(3) : "Terminal Clause (Bound)"}
              </span>
            </div>


            <div style={{ display: "flex", justifyContent: "space-between", borderBottom: "1px solid var(--color-border)", paddingBottom: "0.35rem" }}>
              <span style={{ color: "var(--color-text-muted)" }}>Incoming Discontinuity:</span>
              <span style={{ fontWeight: 600, color: incomingAnomaly && incomingAnomaly > 0.5 ? "var(--sev-high-text)" : "var(--color-text-primary)" }}>
                {typeof incomingAnomaly === "number" ? incomingAnomaly.toFixed(3) : "0.000"}
              </span>
            </div>

            <div style={{ display: "flex", justifyContent: "space-between" }}>
              <span style={{ color: "var(--color-text-muted)" }}>Outgoing Discontinuity:</span>
              <span style={{ fontWeight: 600, color: outgoingAnomaly && outgoingAnomaly > 0.5 ? "var(--sev-high-text)" : "var(--color-text-primary)" }}>
                {typeof outgoingAnomaly === "number" ? outgoingAnomaly.toFixed(3) : "0.000"}
              </span>
            </div>
          </div>

          <div style={{ marginTop: "0.75rem", fontSize: "0.72rem", color: "var(--color-text-muted)", fontStyle: "italic" }}>
            Transition anomalies reflect learned sequence discontinuity, not ungrammatical text.
          </div>
        </div>
      </div>
    </div>
  );
}
