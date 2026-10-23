"use client";

import React from "react";
import { SensitivityPayload } from "./types";
import { ArrowRightLeft } from "lucide-react";

interface SensitivityComparisonProps {
  sensitivityData: SensitivityPayload | null;
  loading: boolean;
}

export function SensitivityComparison({ sensitivityData, loading }: SensitivityComparisonProps) {
  if (loading) {
    return (
      <div
        style={{
          background: "var(--color-surface)",
          border: "1px solid var(--color-border)",
          borderRadius: "var(--radius-md)",
          padding: "1.25rem",
          marginBottom: "1rem",
        }}
      >
        <p style={{ color: "var(--color-text-secondary)", margin: 0, fontSize: "0.9rem" }}>
          Evaluating neighbor perturbation sensitivity...
        </p>
      </div>
    );
  }

  if (!sensitivityData) {
    return (
      <div
        style={{
          background: "var(--color-surface)",
          border: "1px solid var(--color-border)",
          borderRadius: "var(--radius-md)",
          padding: "1.25rem",
          marginBottom: "1rem",
        }}
      >
        <p style={{ color: "var(--color-text-secondary)", margin: 0, fontSize: "0.9rem" }}>
          No sensitivity data available for this clause.
        </p>
      </div>
    );
  }

  const { baseline_anomaly, perturbed_anomaly, delta, neighbor_id, neighbor_pos, method } = {
    baseline_anomaly: sensitivityData.original_score ?? 0,
    perturbed_anomaly: sensitivityData.perturbed_score ?? 0,
    delta: sensitivityData.score_delta ?? 0,
    neighbor_id: sensitivityData.neighbor_clause_id || "N/A",
    neighbor_pos: (sensitivityData.neighbor_position || "none").toUpperCase(),
    method: sensitivityData.perturbation_method || "mask_neighbor_text",
  };

  const isImpactful = delta >= 0.05;

  return (
    <div
      id="xai-sensitivity-card"
      style={{
        background: "var(--color-surface)",
        border: "1px solid var(--color-border)",
        borderRadius: "var(--radius-md)",
        padding: "1.25rem",
        marginBottom: "1rem",
      }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.5rem" }}>
        <ArrowRightLeft size={18} style={{ color: "var(--color-accent)" }} aria-hidden="true" />
        <h3 style={{ fontSize: "1rem", fontWeight: 600, margin: 0, color: "var(--color-text-primary)" }}>
          Channel B Perturbation Sensitivity Analysis
        </h3>
      </div>
      <p style={{ fontSize: "0.85rem", color: "var(--color-text-secondary)", margin: "0 0 1rem 0" }}>
        Measures the change in Channel B Discourse Anomaly score when immediately adjacent context is masked via intervention (Method: <code style={{ fontSize: "0.8rem" }}>{method}</code>).
      </p>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
          gap: "1rem",
          marginBottom: "1rem",
        }}
      >
        <div style={{ background: "var(--color-bg)", padding: "0.75rem 1rem", borderRadius: "var(--radius-sm)", border: "1px solid var(--color-border)" }}>
          <div style={{ fontSize: "0.75rem", color: "var(--color-text-secondary)", marginBottom: "0.25rem" }}>
            Baseline Anomaly Score (S_B)
          </div>
          <div style={{ fontSize: "1.25rem", fontWeight: 700, fontFamily: "monospace", color: "var(--color-text-primary)" }}>
            {baseline_anomaly.toFixed(4)}
          </div>
          <div style={{ fontSize: "0.7rem", color: "var(--color-text-secondary)" }}>Unperturbed Clause Order</div>
        </div>

        <div style={{ background: "var(--color-bg)", padding: "0.75rem 1rem", borderRadius: "var(--radius-sm)", border: "1px solid var(--color-border)" }}>
          <div style={{ fontSize: "0.75rem", color: "var(--color-text-secondary)", marginBottom: "0.25rem" }}>
            Perturbed Anomaly Score (S&apos;_B)
          </div>
          <div style={{ fontSize: "1.25rem", fontWeight: 700, fontFamily: "monospace", color: "var(--color-text-primary)" }}>
            {perturbed_anomaly.toFixed(4)}
          </div>
          <div style={{ fontSize: "0.7rem", color: "var(--color-text-secondary)" }}>With Neighbor Masked</div>
        </div>

        <div style={{ background: "var(--color-bg)", padding: "0.75rem 1rem", borderRadius: "var(--radius-sm)", border: "1px solid var(--color-border)" }}>
          <div style={{ fontSize: "0.75rem", color: "var(--color-text-secondary)", marginBottom: "0.25rem" }}>
            Sensitivity Delta (|ΔS_B|)
          </div>
          <div
            style={{
              fontSize: "1.25rem",
              fontWeight: 700,
              fontFamily: "monospace",
              color: isImpactful ? "var(--sev-high-text, #dc2626)" : "var(--color-text-primary)",
            }}
          >
            {delta.toFixed(4)}
          </div>
          <div style={{ fontSize: "0.7rem", color: isImpactful ? "#dc2626" : "var(--color-text-secondary)" }}>
            {isImpactful ? "Significant Context Dependency" : "Stable Under Perturbation"}
          </div>
        </div>

        <div style={{ background: "var(--color-bg)", padding: "0.75rem 1rem", borderRadius: "var(--radius-sm)", border: "1px solid var(--color-border)" }}>
          <div style={{ fontSize: "0.75rem", color: "var(--color-text-secondary)", marginBottom: "0.25rem" }}>
            Key Neighbor Influence
          </div>
          <div style={{ fontSize: "0.95rem", fontWeight: 600, color: "var(--color-text-primary)", fontFamily: "monospace" }}>
            {neighbor_id}
          </div>
          <div style={{ fontSize: "0.7rem", color: "var(--color-text-secondary)" }}>
            Position: <strong>{neighbor_pos}</strong>
          </div>
        </div>
      </div>
    </div>
  );
}
