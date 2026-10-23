"use client";

import React, { useState } from "react";
import { ChevronDown, ChevronUp, BookOpen, AlertCircle } from "lucide-react";

export function RepairMethodology() {
  const [expanded, setExpanded] = useState(false);

  return (
    <div
      className="repair-methodology"
      style={{
        borderRadius: "6px",
        border: "1px solid var(--color-border, #e2e8f0)",
        background: "var(--color-surface, #ffffff)",
        overflow: "hidden",
        marginTop: "1rem",
      }}
    >
      <button
        type="button"
        onClick={() => setExpanded(!expanded)}
        style={{
          width: "100%",
          padding: "0.75rem 1rem",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          background: "transparent",
          border: "none",
          cursor: "pointer",
          textAlign: "left",
        }}
      >
        <span
          style={{
            fontSize: "0.8rem",
            fontWeight: 600,
            color: "var(--color-text-secondary, #64748b)",
            display: "flex",
            alignItems: "center",
            gap: "0.4rem",
          }}
        >
          <BookOpen size={14} aria-hidden="true" />
          Experimental Methodology &amp; Scientific Disclosures
        </span>
        {expanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
      </button>

      {expanded && (
        <div
          style={{
            padding: "0.75rem 1rem 1rem",
            borderTop: "1px solid var(--color-border, #e2e8f0)",
            fontSize: "0.78rem",
            color: "var(--color-text-secondary, #64748b)",
            lineHeight: 1.6,
          }}
        >
          <div style={{ marginBottom: "0.5rem" }}>
            <strong>Primary Objective Function:</strong> Evaluates whole-document mean combined anomaly:
            <div
              style={{
                fontFamily: "ui-monospace, monospace",
                background: "var(--color-surface-raised, #f8fafc)",
                padding: "0.4rem 0.6rem",
                borderRadius: "4px",
                margin: "0.35rem 0",
                fontSize: "0.75rem",
              }}
            >
              J(D^(p)) = (1/N) * Σ [ α * S_A(c_i) + (1 - α) * S_B(c_i) ]
            </div>
            Where <em>α = 0.5</em>. Channel A measures semantic out-of-distribution distance to LEDGAR centroids and is 100% position-invariant. Channel B evaluates discourse continuity across adjacent transitions via the frozen neural scorer head.
          </div>

          <div style={{ marginBottom: "0.5rem" }}>
            <strong>Zero Contract Mutation:</strong> This feature is strictly read-only decision support. LexAudit never modifies, reorders, rewrites, or auto-applies clause movements to the underlying document text.
          </div>

          <div
            style={{
              display: "flex",
              alignItems: "flex-start",
              gap: "0.4rem",
              padding: "0.5rem 0.65rem",
              borderRadius: "4px",
              background: "rgba(245, 158, 11, 0.08)",
              border: "1px solid rgba(245, 158, 11, 0.2)",
              color: "var(--sev-med-text, #d97706)",
              fontSize: "0.74rem",
            }}
          >
            <AlertCircle size={14} style={{ flexShrink: 0, marginTop: "0.15rem" }} aria-hidden="true" />
            <span>
              <strong>Drafting Warning:</strong> Structural movement constraints could not be fully verified automatically. Proposed positions must be evaluated by qualified legal counsel for cross-reference consistency, defined term order, and statutory enforceability.
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
