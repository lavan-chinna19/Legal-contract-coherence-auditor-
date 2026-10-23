"use client";

import React from "react";
import { Info } from "lucide-react";

interface CompatibilityMatrixLegendProps {
  minScore: number;
  maxScore: number;
  meanScore: number;
}

export function CompatibilityMatrixLegend({ minScore, maxScore, meanScore }: CompatibilityMatrixLegendProps) {
  return (
    <div
      style={{
        background: "var(--color-surface)",
        border: "1px solid var(--color-border)",
        borderRadius: "var(--radius-md)",
        padding: "0.75rem 1rem",
        marginBottom: "1rem",
        fontSize: "0.85rem",
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "1rem" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
          <Info size={16} style={{ color: "var(--color-accent)" }} aria-hidden="true" />
          <strong style={{ color: "var(--color-text-primary)" }}>
            Learned Pairwise Compatibility Spectrum [P(Antecedent → Successor)]:
          </strong>
        </div>

        {/* Continuous gradient strip */}
        <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", flexWrap: "wrap" }}>
          <div style={{ textAlign: "right" }}>
            <span style={{ fontSize: "0.75rem", color: "var(--sev-high-text, #dc2626)", fontWeight: 600, display: "block" }}>
              Low Compatibility ({minScore.toFixed(3)})
            </span>
            <span style={{ fontSize: "0.7rem", color: "var(--color-text-secondary)" }}>
              High Discontinuity
            </span>
          </div>

          <div
            style={{
              width: "160px",
              height: "14px",
              borderRadius: "4px",
              background: "linear-gradient(to right, #991b1b, #d97706, #15803d, #2563eb)",
              border: "1px solid var(--color-border)",
            }}
          />

          <div>
            <span style={{ fontSize: "0.75rem", color: "var(--color-accent, #2563eb)", fontWeight: 600, display: "block" }}>
              High Compatibility ({maxScore.toFixed(3)})
            </span>
            <span style={{ fontSize: "0.7rem", color: "var(--color-text-secondary)" }}>
              Coherent Transition
            </span>
          </div>

          <div
            style={{
              background: "var(--color-bg)",
              padding: "0.2rem 0.5rem",
              borderRadius: "4px",
              border: "1px solid var(--color-border)",
              fontSize: "0.75rem",
              color: "var(--color-text-secondary)",
            }}
          >
            Matrix Mean: <strong>{meanScore.toFixed(3)}</strong>
          </div>
        </div>
      </div>
    </div>
  );
}
