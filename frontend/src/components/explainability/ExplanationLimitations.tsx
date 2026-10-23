"use client";

import React from "react";
import { ClaimScopeData } from "./types";
import { AlertTriangle, CheckCircle, ShieldAlert } from "lucide-react";

interface ExplanationLimitationsProps {
  claimScope?: ClaimScopeData;
}

export function ExplanationLimitations({ claimScope }: ExplanationLimitationsProps) {
  const whatShows =
    claimScope?.what_this_shows ||
    "Integrated Gradients indicates which input tokens/features contributed most to the Channel A semantic distance anomaly score.";
  const whatDoesNotShow =
    claimScope?.what_this_does_not_show ||
    "It does not prove that those tokens are legally significant, causally responsible for a contract defect, or that the model's prediction is correct.";

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
      <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.75rem" }}>
        <ShieldAlert size={18} style={{ color: "var(--color-accent)" }} aria-hidden="true" />
        <h3 style={{ fontSize: "1rem", fontWeight: 600, margin: 0, color: "var(--color-text-primary)" }}>
          Explainability Claim Boundaries & Scientific Scope
        </h3>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "1rem" }}>
        <div
          style={{
            background: "var(--color-bg)",
            border: "1px solid var(--color-border)",
            borderRadius: "var(--radius-sm)",
            padding: "0.75rem 1rem",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "0.4rem", marginBottom: "0.35rem", color: "var(--color-success)" }}>
            <CheckCircle size={15} aria-hidden="true" />
            <strong style={{ fontSize: "0.85rem" }}>What This Explains:</strong>
          </div>
          <p style={{ fontSize: "0.8rem", color: "var(--color-text-secondary)", margin: 0, lineHeight: 1.5 }}>
            {whatShows}
          </p>
        </div>

        <div
          style={{
            background: "var(--color-bg)",
            border: "1px solid var(--color-border)",
            borderRadius: "var(--radius-sm)",
            padding: "0.75rem 1rem",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "0.4rem", marginBottom: "0.35rem", color: "var(--sev-high-text, #dc2626)" }}>
            <AlertTriangle size={15} aria-hidden="true" />
            <strong style={{ fontSize: "0.85rem" }}>What This Does NOT Explain:</strong>
          </div>
          <p style={{ fontSize: "0.8rem", color: "var(--color-text-secondary)", margin: 0, lineHeight: 1.5 }}>
            {whatDoesNotShow}
          </p>
        </div>
      </div>
    </div>
  );
}
