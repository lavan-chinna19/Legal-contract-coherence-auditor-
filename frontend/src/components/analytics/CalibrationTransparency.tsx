"use client";

import React from "react";
import { DocumentResult, ClauseResult } from "./types";
import { ShieldAlert, BookOpen, Layers, Info } from "lucide-react";

interface CalibrationTransparencyProps {
  scoringResult: DocumentResult["scoring_result"];
  selectedClause?: ClauseResult;
}

export function CalibrationTransparency({
  scoringResult,
  selectedClause,
}: CalibrationTransparencyProps) {
  const calibrationSource = scoringResult?.calibration_source || "synthetic_shuffle_ledgar";
  const interval = selectedClause?.confidence_interval;
  const intervalWidth = selectedClause?.interval_width ?? (interval ? (interval[1] - interval[0]) : undefined);

  return (
    <section
      className="card analytics-calibration-section"
      role="region"
      aria-label="Calibration Transparency & Scientific Methodology Limitations"
      style={{ marginBottom: "1.75rem" }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "1rem", flexWrap: "wrap", gap: "0.5rem" }}>
        <div>
          <h3 style={{ fontSize: "1.05rem", fontWeight: 600, color: "var(--color-text-primary)", margin: 0, display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <Layers size={18} style={{ color: "var(--color-accent)" }} aria-hidden="true" />
            <span>Calibration Transparency &amp; Uncertainty Disclosures</span>
          </h3>
          <p style={{ fontSize: "0.8rem", color: "var(--color-text-secondary)", margin: "0.25rem 0 0 0" }}>
            Rigorous statistical attribution of confidence intervals, conformal thresholds, and empirical boundaries.
          </p>
        </div>
        <span
          style={{
            fontSize: "0.75rem",
            fontWeight: 600,
            padding: "0.2rem 0.55rem",
            borderRadius: "4px",
            background: "var(--color-surface-raised)",
            border: "1px solid var(--color-border)",
            color: "var(--color-accent)",
          }}
        >
          Source: {calibrationSource}
        </span>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "1rem", marginBottom: "1.25rem" }}>
        {/* Card 1: Selected Clause Conformal Uncertainty */}
        <div
          style={{
            background: "var(--color-surface-raised)",
            border: "1px solid var(--color-border)",
            borderRadius: "6px",
            padding: "1rem",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "0.4rem", marginBottom: "0.5rem" }}>
            <BookOpen size={16} style={{ color: "var(--color-accent)" }} aria-hidden="true" />
            <h4 style={{ fontSize: "0.9rem", fontWeight: 600, color: "var(--color-text-primary)", margin: 0 }}>
              Clause Uncertainty Bounds (§ {selectedClause?.sequence_idx ?? 0})
            </h4>
          </div>

          <p style={{ fontSize: "0.8rem", color: "var(--color-text-secondary)", marginBottom: "0.75rem" }}>
            Non-parametric conformal prediction interval for the current clause combined score.
          </p>

          <div style={{ display: "flex", flexDirection: "column", gap: "0.4rem", fontSize: "0.8rem" }}>
            <div style={{ display: "flex", justifyContent: "space-between", borderBottom: "1px solid var(--color-border)", paddingBottom: "0.3rem" }}>
              <span style={{ color: "var(--color-text-muted)" }}>Point Estimate Score:</span>
              <strong style={{ color: "var(--color-text-primary)" }}>
                {selectedClause ? selectedClause.combined_score.toFixed(3) : "N/A"}
              </strong>
            </div>

            <div style={{ display: "flex", justifyContent: "space-between", borderBottom: "1px solid var(--color-border)", paddingBottom: "0.3rem" }}>
              <span style={{ color: "var(--color-text-muted)" }}>90% Conformal Interval:</span>
              <span style={{ fontWeight: 600, color: "var(--color-accent)" }}>
                {interval ? `[${interval[0].toFixed(3)}, ${interval[1].toFixed(3)}]` : "N/A"}
              </span>
            </div>

            <div style={{ display: "flex", justifyContent: "space-between", borderBottom: "1px solid var(--color-border)", paddingBottom: "0.3rem" }}>
              <span style={{ color: "var(--color-text-muted)" }}>Interval Uncertainty Width:</span>
              <span style={{ color: "var(--color-text-primary)" }}>
                {typeof intervalWidth === "number" ? intervalWidth.toFixed(3) : "N/A"}
              </span>
            </div>

            <div style={{ display: "flex", justifyContent: "space-between" }}>
              <span style={{ color: "var(--color-text-muted)" }}>Calibration Provenance:</span>
              <span style={{ color: "var(--color-text-secondary)" }}>{selectedClause?.calibration_source || calibrationSource}</span>
            </div>
          </div>
        </div>

        {/* Card 2: Empirical Calibration Methodology */}
        <div
          style={{
            background: "var(--color-surface-raised)",
            border: "1px solid var(--color-border)",
            borderRadius: "6px",
            padding: "1rem",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "0.4rem", marginBottom: "0.5rem" }}>
            <ShieldAlert size={16} style={{ color: "var(--color-warning)" }} aria-hidden="true" />
            <h4 style={{ fontSize: "0.9rem", fontWeight: 600, color: "var(--color-text-primary)", margin: 0 }}>
              Calibration Methodology &amp; Reference Corpus
            </h4>
          </div>

          <p style={{ fontSize: "0.8rem", color: "var(--color-text-secondary)", marginBottom: "0.75rem" }}>
            Trained on LEDGAR SEC filings with split-conformal calibration on held-out permutation sets.
          </p>

          <ul style={{ paddingLeft: "1.2rem", margin: 0, fontSize: "0.8rem", color: "var(--color-text-secondary)", lineHeight: 1.6 }}>
            <li>
              <strong>Nominal coverage target:</strong> 90% under the calibration assumptions for synthetic shuffles. This is not an independently verified guarantee for real contracts or legal defects.
            </li>
            <li>
              <strong>Non-Exchangeability Notice:</strong> Real-world legal drafting variations do not satisfy identically distributed exchangeability with synthetic permutations.
            </li>
            <li>
              <strong>Zero LLM Generation:</strong> All diagnostics are deterministic mathematical operations over Legal-BERT representations.
            </li>
          </ul>
        </div>
      </div>

      {/* Mandatory Scientific Caveat Box */}
      <div
        className="caveat-box"
        style={{
          padding: "1rem",
          background: "var(--color-surface-raised)",
          borderLeft: "4px solid var(--color-warning)",
          borderRadius: "4px",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.4rem" }}>
          <Info size={16} style={{ color: "var(--color-warning)" }} aria-hidden="true" />
          <h4 style={{ fontSize: "0.9rem", fontWeight: 700, color: "var(--color-text-primary)", margin: 0 }}>
            Mandatory Academic Research &amp; Legal Defect Limitation Notice
          </h4>
        </div>
        <p style={{ fontSize: "0.85rem", color: "var(--color-text-secondary)", margin: 0, lineHeight: 1.55 }}>
          <strong>Synthetic shuffle-based calibration does not establish real-world legal defect correctness.</strong>{" "}
          LexAudit evaluates statistical divergence from common corpus sequence patterns. A low anomaly score does not certify
          enforceability, compliance, or legal soundness. Conversely, a high anomaly score indicates structural sequence divergence
          under the model, which may represent bespoke drafting, transaction-specific negotiated covenants, or customary deviations
          rather than errors. Human legal counsel review is always required.
        </p>
      </div>
    </section>
  );
}
