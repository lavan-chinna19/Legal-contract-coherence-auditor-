"use client";

import React from "react";
import { SelectedCell } from "./types";
import { ArrowRight, ArrowLeftRight, ShieldCheck, X } from "lucide-react";

interface CompatibilityDetailsProps {
  selectedCell: SelectedCell | null;
  onClearSelection?: () => void;
}

export function CompatibilityDetails({ selectedCell, onClearSelection }: CompatibilityDetailsProps) {
  if (!selectedCell) {
    return (
      <div
        style={{
          background: "var(--color-surface)",
          border: "1px dashed var(--color-border)",
          borderRadius: "var(--radius-md)",
          padding: "1.25rem",
          textAlign: "center",
          color: "var(--color-text-secondary)",
          fontSize: "0.85rem",
        }}
      >
        <ArrowLeftRight size={24} style={{ margin: "0 auto 0.5rem", opacity: 0.5 }} aria-hidden="true" />
        <p style={{ margin: 0, fontWeight: 500 }}>No clause-pair cell selected</p>
        <p style={{ margin: "0.25rem 0 0", fontSize: "0.75rem" }}>
          Click or focus any cell in the compatibility heatmap to inspect pairwise model score, directional asymmetry, and Channel B anomaly equivalence.
        </p>
      </div>
    );
  }

  const { antecedentName, successorName, antecedentIndex, successorIndex, score, reverseScore } = selectedCell;
  const asymmetry = score - reverseScore;
  const channelBAnomaly = 1.0 - score;
  const isSelfTransition = antecedentIndex === successorIndex;

  return (
    <div
      id="flow-cell-details"
      style={{
        background: "var(--color-surface)",
        border: "1px solid var(--color-border)",
        borderRadius: "var(--radius-md)",
        padding: "1rem 1.25rem",
        marginBottom: "1rem",
        position: "relative",
      }}
    >
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "0.75rem" }}>
        <div>
          <span style={{ fontSize: "0.7rem", textTransform: "uppercase", letterSpacing: "0.05em", color: "var(--color-accent)", fontWeight: 600 }}>
            Selected Clause Pair Inspection
          </span>
          <h4 style={{ margin: "0.2rem 0 0", fontSize: "1rem", display: "flex", alignItems: "center", gap: "0.5rem", flexWrap: "wrap" }}>
            <span style={{ color: "var(--color-text-primary)", fontWeight: 600 }}>
              [{antecedentIndex}] {antecedentName}
            </span>
            <ArrowRight size={16} style={{ color: "var(--color-text-secondary)" }} aria-hidden="true" />
            <span style={{ color: "var(--color-text-primary)", fontWeight: 600 }}>
              [{successorIndex}] {successorName}
            </span>
            {isSelfTransition && (
              <span
                style={{
                  fontSize: "0.7rem",
                  background: "var(--color-bg)",
                  border: "1px solid var(--color-border)",
                  borderRadius: "4px",
                  padding: "0.1rem 0.4rem",
                  color: "var(--color-text-secondary)",
                }}
              >
                Self-transition (diagonal)
              </span>
            )}
          </h4>
        </div>
        {onClearSelection && (
          <button
            onClick={onClearSelection}
            className="btn btn-secondary"
            style={{ padding: "0.25rem 0.5rem", fontSize: "0.75rem", display: "flex", alignItems: "center", gap: "0.25rem" }}
            aria-label="Clear selected cell"
          >
            <X size={14} /> Clear
          </button>
        )}
      </div>

      {/* Numerical Metrics Grid */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
          gap: "0.75rem",
          marginBottom: "1rem",
        }}
      >
        {/* Forward Score */}
        <div
          style={{
            background: "var(--color-bg)",
            border: "1px solid var(--color-border)",
            borderRadius: "var(--radius-sm)",
            padding: "0.75rem",
          }}
        >
          <div style={{ fontSize: "0.75rem", color: "var(--color-text-secondary)" }}>
            Forward Compatibility [P(A → B)]
          </div>
          <div style={{ fontSize: "1.25rem", fontWeight: 700, color: "var(--color-accent)", margin: "0.25rem 0" }}>
            {score.toFixed(6)}
          </div>
          <div style={{ fontSize: "0.7rem", color: "var(--color-text-secondary)" }}>
            f_θ(c_{antecedentIndex}, c_{successorIndex})
          </div>
        </div>

        {/* Reverse Score */}
        <div
          style={{
            background: "var(--color-bg)",
            border: "1px solid var(--color-border)",
            borderRadius: "var(--radius-sm)",
            padding: "0.75rem",
          }}
        >
          <div style={{ fontSize: "0.75rem", color: "var(--color-text-secondary)" }}>
            Reverse Compatibility [P(B → A)]
          </div>
          <div style={{ fontSize: "1.25rem", fontWeight: 700, color: "var(--color-text-primary)", margin: "0.25rem 0" }}>
            {reverseScore.toFixed(6)}
          </div>
          <div style={{ fontSize: "0.7rem", color: "var(--color-text-secondary)" }}>
            f_θ(c_{successorIndex}, c_{antecedentIndex})
          </div>
        </div>

        {/* Directional Asymmetry */}
        <div
          style={{
            background: "var(--color-bg)",
            border: "1px solid var(--color-border)",
            borderRadius: "var(--radius-sm)",
            padding: "0.75rem",
          }}
        >
          <div style={{ fontSize: "0.75rem", color: "var(--color-text-secondary)" }}>
            Directional Asymmetry [Δ]
          </div>
          <div
            style={{
              fontSize: "1.25rem",
              fontWeight: 700,
              color: Math.abs(asymmetry) > 0.01 ? "var(--sev-medium-text, #d97706)" : "var(--color-text-primary)",
              margin: "0.25rem 0",
            }}
          >
            {asymmetry >= 0 ? `+${asymmetry.toFixed(6)}` : asymmetry.toFixed(6)}
          </div>
          <div style={{ fontSize: "0.7rem", color: "var(--color-text-secondary)" }}>
            {isSelfTransition
              ? "Symmetric (identical centroids)"
              : asymmetry > 0
              ? `Forward ordering favored (+${(asymmetry * 100).toFixed(2)}%)`
              : asymmetry < 0
              ? `Reverse ordering favored (${(asymmetry * 100).toFixed(2)}%)`
              : "Strictly balanced"}
          </div>
        </div>

        {/* Channel B Anomaly Equivalence */}
        <div
          style={{
            background: "var(--color-bg)",
            border: "1px solid var(--color-border)",
            borderRadius: "var(--radius-sm)",
            padding: "0.75rem",
          }}
        >
          <div style={{ fontSize: "0.75rem", color: "var(--color-text-secondary)" }}>
            Channel B Anomaly Score [1.0 - P]
          </div>
          <div
            style={{
              fontSize: "1.25rem",
              fontWeight: 700,
              color: channelBAnomaly > 0.65 ? "var(--sev-high-text, #dc2626)" : "var(--color-text-primary)",
              margin: "0.25rem 0",
            }}
          >
            {channelBAnomaly.toFixed(6)}
          </div>
          <div style={{ fontSize: "0.7rem", color: "var(--color-text-secondary)" }}>
            {channelBAnomaly < 0.58 ? "Coherent transition expected" : "Discontinuity / boundary flag candidate"}
          </div>
        </div>
      </div>

      {/* Scientific Disclosure */}
      <div
        style={{
          background: "var(--color-surface-sunken, rgba(0,0,0,0.03))",
          borderRadius: "var(--radius-sm)",
          padding: "0.5rem 0.75rem",
          fontSize: "0.75rem",
          color: "var(--color-text-secondary)",
          display: "flex",
          alignItems: "flex-start",
          gap: "0.5rem",
          lineHeight: "1.4",
        }}
      >
        <ShieldCheck size={16} style={{ color: "var(--color-accent)", flexShrink: 0, marginTop: "0.1rem" }} aria-hidden="true" />
        <div>
          <strong>Scientific Methodology Disclosure:</strong> This score is generated by evaluation-mode inference of the frozen neural pairwise head{" "}
          <code>CoherenceScorerHead</code> on LEDGAR centroid vectors. It is an independent binary classification likelihood, not an empirical transition frequency or Markov probability.
        </div>
      </div>
    </div>
  );
}
