"use client";

import React from "react";
import { Info } from "lucide-react";

export function AttributionLegend() {
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
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: "0.75rem" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
          <Info size={16} style={{ color: "var(--color-accent)" }} aria-hidden="true" />
          <span style={{ fontWeight: 600, color: "var(--color-text-primary)" }}>
            Integrated Gradients Signed Attribution Scale:
          </span>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "1rem", flexWrap: "wrap" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "0.35rem" }}>
            <span
              style={{
                width: "14px",
                height: "14px",
                borderRadius: "3px",
                background: "rgba(220, 38, 38, 0.25)",
                border: "1px solid #dc2626",
                display: "inline-block",
              }}
            />
            <span style={{ color: "var(--color-text-primary)", fontSize: "0.8rem" }}>
              <strong>Positive (+)</strong>: Increases OOD Distance (Drives Anomaly)
            </span>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: "0.35rem" }}>
            <span
              style={{
                width: "14px",
                height: "14px",
                borderRadius: "3px",
                background: "rgba(22, 163, 74, 0.2)",
                border: "1px solid #16a34a",
                display: "inline-block",
              }}
            />
            <span style={{ color: "var(--color-text-primary)", fontSize: "0.8rem" }}>
              <strong>Negative (−)</strong>: Decreases OOD Distance (Coherence Anchor)
            </span>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: "0.35rem" }}>
            <span
              style={{
                width: "14px",
                height: "14px",
                borderRadius: "3px",
                background: "var(--color-bg)",
                border: "1px solid var(--color-border)",
                display: "inline-block",
              }}
            />
            <span style={{ color: "var(--color-text-secondary)", fontSize: "0.8rem" }}>
              Neutral (≈ 0)
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
