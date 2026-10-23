"use client";

import React from "react";
import { RuleFlag, ClauseResult } from "./types";
import { Scale, CheckCircle2, AlertOctagon, AlertTriangle, ArrowRight } from "lucide-react";

interface RuleFindingsSummaryProps {
  ruleFlags: RuleFlag[];
  clauses: ClauseResult[];
  onSelectClauseId: (clauseId: string) => void;
  onNavigateToReview?: () => void;
}

export function RuleFindingsSummary({
  ruleFlags,
  clauses,
  onSelectClauseId,
  onNavigateToReview,
}: RuleFindingsSummaryProps) {
  const count = ruleFlags.length;

  const handleInspectClause = (clauseId: string) => {
    onSelectClauseId(clauseId);
    if (onNavigateToReview) {
      onNavigateToReview();
    }
  };

  return (
    <section
      className="card analytics-rules-section"
      role="region"
      aria-label="Deterministic Rule Violations Summary"
      style={{ marginBottom: "1.75rem" }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "1rem", flexWrap: "wrap", gap: "0.5rem" }}>
        <div>
          <h3 style={{ fontSize: "1.05rem", fontWeight: 600, color: "var(--color-text-primary)", margin: 0, display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <Scale size={18} style={{ color: count > 0 ? "var(--color-warning)" : "var(--color-success)" }} aria-hidden="true" />
            <span>Deterministic Rule Violations ({count})</span>
          </h3>
          <p style={{ fontSize: "0.8rem", color: "var(--color-text-secondary)", margin: "0.25rem 0 0 0" }}>
            Automated textual checks of internal cross-references, exhibit citations, and chronological consistency.
          </p>
        </div>
        <span
          style={{
            fontSize: "0.75rem",
            fontWeight: 600,
            padding: "0.2rem 0.55rem",
            borderRadius: "4px",
            background: count > 0 ? "rgba(234, 179, 8, 0.15)" : "var(--sev-clean-bg)",
            color: count > 0 ? "var(--color-warning)" : "var(--color-success)",
          }}
        >
          {count > 0 ? `${count} Violations Detected` : "0 Detected Violations"}
        </span>
      </div>

      {count === 0 ? (
        <div
          style={{
            padding: "1.5rem",
            background: "var(--color-surface-raised)",
            borderRadius: "6px",
            border: "1px solid var(--color-border)",
            display: "flex",
            flexDirection: "column",
            gap: "0.5rem",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", color: "var(--color-success)" }}>
            <CheckCircle2 size={18} aria-hidden="true" />
            <strong style={{ fontSize: "0.9rem" }}>
              No deterministic rule violations were reported by the current rule checks.
            </strong>
          </div>
          <p style={{ fontSize: "0.8rem", color: "var(--color-text-muted)", margin: 0, lineHeight: 1.5 }}>
            No configured textual rule check raised a flag. Unsupported references, parsing omissions and legal interpretation still require human review.
          </p>
          <div
            style={{
              marginTop: "0.5rem",
              padding: "0.5rem 0.75rem",
              background: "var(--color-surface)",
              borderRadius: "4px",
              border: "1px dashed var(--color-border)",
              fontSize: "0.75rem",
              color: "var(--color-text-secondary)",
            }}
          >
            <strong>Preservation Safeguard:</strong> This finding does <em>not</em> establish that this contract has no legal defects, ambiguities, or omissions. Machine-audited rule verification tests only formal syntactic patterns.
          </div>
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
          {ruleFlags.map((flag) => {
            const isHigh = flag.severity === "HIGH";
            const targetClause = flag.clause_id ? clauses.find((c) => c.clause_id === flag.clause_id) : undefined;
            const seqIdx = targetClause ? `§ ${targetClause.sequence_idx}` : flag.clause_id ? flag.clause_id : "Global / Multi-Clause";

            return (
              <div
                key={flag.flag_id}
                className="rule-violation-card"
                style={{
                  padding: "1rem",
                  background: "var(--color-surface-raised)",
                  border: "1px solid var(--color-border)",
                  borderLeft: `4px solid ${isHigh ? "var(--sev-high-border)" : "var(--sev-med-border)"}`,
                  borderRadius: "6px",
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "flex-start",
                  flexWrap: "wrap",
                  gap: "0.75rem",
                }}
              >
                <div style={{ flex: 1, minWidth: "260px" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.35rem", flexWrap: "wrap" }}>
                    <span
                      style={{
                        display: "inline-flex",
                        alignItems: "center",
                        gap: "0.25rem",
                        fontSize: "0.72rem",
                        fontWeight: 700,
                        padding: "0.15rem 0.45rem",
                        borderRadius: "3px",
                        background: isHigh ? "var(--sev-high-bg)" : "var(--sev-med-bg)",
                        color: isHigh ? "var(--sev-high-text)" : "var(--sev-med-text)",
                      }}
                    >
                      {isHigh ? <AlertOctagon size={12} aria-hidden="true" /> : <AlertTriangle size={12} aria-hidden="true" />}
                      <span>{flag.severity}</span>
                    </span>

                    <span style={{ fontSize: "0.75rem", color: "var(--color-text-muted)", background: "var(--color-surface)", padding: "0.1rem 0.4rem", borderRadius: "3px" }}>
                      Category: {flag.category || flag.flag_type}
                    </span>

                    <span style={{ fontSize: "0.75rem", fontWeight: 600, color: "var(--color-accent)" }}>
                      Target: {seqIdx}
                    </span>
                  </div>

                  <h4 style={{ fontSize: "0.95rem", fontWeight: 600, color: "var(--color-text-primary)", margin: "0 0 0.35rem 0" }}>
                    {flag.title}
                  </h4>

                  <p style={{ fontSize: "0.85rem", color: "var(--color-text-secondary)", margin: 0, lineHeight: 1.5 }}>
                    {flag.description}
                  </p>

                  {flag.evidence && Object.keys(flag.evidence).length > 0 && (
                    <div style={{ marginTop: "0.5rem", fontSize: "0.75rem", color: "var(--color-text-muted)" }}>
                      Evidence: <code style={{ fontSize: "0.72rem", background: "var(--color-surface)", padding: "0.1rem 0.3rem", borderRadius: "3px" }}>{JSON.stringify(flag.evidence)}</code>
                    </div>
                  )}
                </div>

                {flag.clause_id && (
                  <button
                    type="button"
                    className="btn btn-secondary"
                    onClick={() => handleInspectClause(flag.clause_id!)}
                    style={{ fontSize: "0.78rem", padding: "0.35rem 0.65rem", display: "inline-flex", alignItems: "center", gap: "0.35rem" }}
                  >
                    <span>Inspect Clause</span>
                    <ArrowRight size={14} aria-hidden="true" />
                  </button>
                )}
              </div>
            );
          })}
        </div>
      )}
    </section>
  );
}
