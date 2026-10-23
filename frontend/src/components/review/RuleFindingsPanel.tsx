"use client";

import React from "react";
import { RuleFlag } from "./types";
import { AlertTriangle, CheckCircle2, ShieldAlert } from "lucide-react";
import { Badge } from "../ui/Badge";

interface RuleFindingsPanelProps {
  clauseRules: RuleFlag[];
  documentRules: RuleFlag[];
  selectedClauseId: string;
}

export function RuleFindingsPanel({
  clauseRules,
  documentRules,
  selectedClauseId,
}: RuleFindingsPanelProps) {
  const totalRelevantRules = clauseRules.length;

  return (
    <div className="rule-findings-panel" style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
      {/* Clause-Specific Rule Violations */}
      <div>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "0.5rem" }}>
          <h4 style={{ fontSize: "0.88rem", fontWeight: 700, color: "var(--color-text-primary)" }}>
            Clause-Specific Rule Violations ({clauseRules.length})
          </h4>
          <span style={{ fontSize: "0.72rem", color: "var(--color-text-muted)" }}>
            Bound to {selectedClauseId}
          </span>
        </div>

        {clauseRules.length === 0 ? (
          <div
            style={{
              padding: "0.85rem 1rem",
              background: "var(--color-surface-raised)",
              borderRadius: "6px",
              border: "1px dashed var(--color-border)",
              display: "flex",
              alignItems: "center",
              gap: "0.6rem",
              fontSize: "0.82rem",
              color: "var(--color-text-secondary)",
            }}
          >
            <CheckCircle2 size={16} style={{ color: "var(--color-success)", flexShrink: 0 }} aria-hidden="true" />
            <span>No deterministic rule violations were flagged on this specific clause.</span>
          </div>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: "0.6rem" }}>
            {clauseRules.map((rule) => {
              const severityVariant =
                rule.severity === "HIGH" ? "high" : rule.severity === "MEDIUM" ? "medium" : "low";

              return (
                <div
                  key={rule.flag_id}
                  style={{
                    padding: "0.85rem",
                    borderRadius: "6px",
                    background: "var(--color-surface)",
                    border: "1px solid var(--color-border)",
                    borderLeft: `4px solid ${
                      rule.severity === "HIGH"
                        ? "var(--color-danger)"
                        : rule.severity === "MEDIUM"
                        ? "var(--color-warning)"
                        : "var(--color-accent)"
                    }`,
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.35rem" }}>
                    <div style={{ display: "flex", alignItems: "center", gap: "0.4rem" }}>
                      <AlertTriangle size={14} style={{ color: "var(--color-danger)" }} aria-hidden="true" />
                      <strong style={{ fontSize: "0.85rem", color: "var(--color-text-primary)" }}>
                        {rule.title}
                      </strong>
                    </div>
                    <Badge variant={severityVariant} />
                  </div>

                  <p style={{ fontSize: "0.8rem", color: "var(--color-text-secondary)", lineHeight: 1.45, marginBottom: "0.4rem" }}>
                    {rule.description}
                  </p>

                  <div style={{ display: "flex", gap: "0.75rem", fontSize: "0.72rem", color: "var(--color-text-muted)" }}>
                    <span>Type: <strong>{rule.flag_type}</strong></span>
                    {rule.category && <span>Category: <strong>{rule.category}</strong></span>}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Document-Level Rules Section */}
      {documentRules.length > 0 && (
        <div style={{ paddingTop: "0.5rem", borderTop: "1px solid var(--color-border-subtle)" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "0.4rem", marginBottom: "0.5rem" }}>
            <ShieldAlert size={15} style={{ color: "var(--color-warning)" }} aria-hidden="true" />
            <h4 style={{ fontSize: "0.88rem", fontWeight: 700, color: "var(--color-text-primary)" }}>
              Document-Level Rule Findings ({documentRules.length})
            </h4>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "0.6rem" }}>
            {documentRules.map((rule) => (
              <div
                key={rule.flag_id}
                style={{
                  padding: "0.75rem",
                  borderRadius: "6px",
                  background: "var(--color-surface-raised)",
                  border: "1px solid var(--color-border)",
                  borderLeft: "4px solid var(--color-warning)",
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.25rem" }}>
                  <strong style={{ fontSize: "0.82rem", color: "var(--color-text-primary)" }}>
                    {rule.title}
                  </strong>
                  <span style={{ fontSize: "0.7rem", color: "var(--color-warning)", fontWeight: 700 }}>
                    [{rule.severity}]
                  </span>
                </div>
                <p style={{ fontSize: "0.78rem", color: "var(--color-text-secondary)", lineHeight: 1.4 }}>
                  {rule.description}
                </p>
                {rule.involved_clause_ids && rule.involved_clause_ids.length > 0 && (
                  <div style={{ marginTop: "0.3rem", fontSize: "0.7rem", color: "var(--color-text-muted)" }}>
                    Involved clauses: {rule.involved_clause_ids.join(", ")}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Empty State when zero total document rules */}
      {totalRelevantRules === 0 && documentRules.length === 0 && (
        <div className="caveat-box" style={{ margin: 0 }}>
          <span>
            No deterministic rule violations were reported for this analysis. <em>Note: The absence of automated rule flags does not certify complete legal enforceability or contractual validity.</em>
          </span>
        </div>
      )}
    </div>
  );
}
