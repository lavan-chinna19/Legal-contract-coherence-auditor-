"use client";

import React from "react";
import { EnrichedClause } from "./types";
import { Badge } from "../ui/Badge";
import { AlertTriangle } from "lucide-react";

interface ClauseCardProps {
  clause: EnrichedClause;
  isSelected: boolean;
  onSelect: (clauseId: string) => void;
}

export function ClauseCard({
  clause,
  isSelected,
  onSelect,
}: ClauseCardProps) {
  const severityVariant =
    clause.severity === "HIGH"
      ? "high"
      : clause.severity === "MEDIUM"
      ? "medium"
      : clause.severity === "LOW"
      ? "low"
      : "clean";

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      onSelect(clause.clause_id);
    }
  };

  return (
    <div
      id={`clause-card-${clause.clause_id}`}
      data-clause-id={clause.clause_id}
      data-clause-idx={clause.sequence_idx}
      role="button"
      tabIndex={0}
      aria-pressed={isSelected}
      aria-label={`Clause § ${clause.sequence_idx}, severity ${clause.severity}, anomaly score ${clause.combined_score.toFixed(3)}`}
      onClick={() => onSelect(clause.clause_id)}
      onKeyDown={handleKeyDown}
      className={`clause-card ${isSelected ? "selected" : ""}`}
      style={{
        padding: "1rem 1.25rem",
        borderRadius: "8px",
        background: isSelected ? "var(--color-accent-subtle)" : "var(--color-surface)",
        border: `1px solid ${isSelected ? "var(--color-accent)" : "var(--color-border)"}`,
        borderLeft: isSelected
          ? "5px solid var(--color-accent)"
          : clause.severity === "HIGH"
          ? "4px solid var(--color-danger)"
          : clause.severity === "MEDIUM"
          ? "4px solid var(--color-warning)"
          : "1px solid var(--color-border)",
        cursor: "pointer",
        transition: "all 0.15s ease",
        marginBottom: "0.75rem",
        position: "relative",
      }}
    >
      {/* Header bar of clause item */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "0.5rem",
          gap: "0.5rem",
          flexWrap: "wrap",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
          <span
            style={{
              fontWeight: 700,
              fontSize: "0.95rem",
              color: "var(--color-text-primary)",
              fontFamily: "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace",
            }}
          >
            § {clause.sequence_idx}
          </span>
          <Badge variant={severityVariant} />
          {clause.associated_rules && clause.associated_rules.length > 0 && (
            <span
              style={{
                fontSize: "0.7rem",
                padding: "0.15rem 0.45rem",
                borderRadius: "4px",
                background: "rgba(220, 38, 38, 0.12)",
                color: "var(--color-danger)",
                fontWeight: 600,
                display: "inline-flex",
                alignItems: "center",
                gap: "0.25rem",
              }}
              title={`${clause.associated_rules.length} rule violation(s) flagged on this clause`}
            >
              <AlertTriangle size={11} aria-hidden="true" />
              <span>{clause.associated_rules.length} Rule Flag{clause.associated_rules.length > 1 ? "s" : ""}</span>
            </span>
          )}
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", fontSize: "0.8rem" }}>
          <span
            style={{
              fontFamily: "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace",
              fontWeight: 600,
              color: "var(--color-text-secondary)",
            }}
          >
            Score: <strong style={{ color: "var(--color-text-primary)" }}>{clause.combined_score.toFixed(3)}</strong>
          </span>
        </div>
      </div>

      {/* Clause Text Body */}
      <div
        className="clause-body"
        style={{
          fontSize: "0.875rem",
          lineHeight: 1.6,
          color: "var(--color-text-primary)",
          whiteSpace: "pre-wrap",
          wordBreak: "break-word",
        }}
      >
        {clause.full_text || clause.text_preview}
      </div>

      {/* Alignment Status Notice (if not verified full text) */}
      {clause.alignment_status && clause.alignment_status !== "VERIFIED_FULL_TEXT" && (
        <div
          className="alignment-status-badge"
          style={{
            marginTop: "0.5rem",
            padding: "0.3rem 0.55rem",
            borderRadius: "4px",
            background:
              clause.alignment_status === "PREVIEW_ONLY_AMBIGUOUS"
                ? "rgba(245, 158, 11, 0.12)"
                : "rgba(107, 114, 128, 0.12)",
            border: `1px solid ${
              clause.alignment_status === "PREVIEW_ONLY_AMBIGUOUS"
                ? "rgba(245, 158, 11, 0.35)"
                : "rgba(107, 114, 128, 0.25)"
            }`,
            color:
              clause.alignment_status === "PREVIEW_ONLY_AMBIGUOUS"
                ? "var(--color-warning, #d97706)"
                : "var(--color-text-secondary)",
            fontSize: "0.73rem",
            display: "inline-flex",
            alignItems: "center",
            gap: "0.35rem",
          }}
          title={clause.alignment_explanation}
        >
          {clause.alignment_status === "PREVIEW_ONLY_AMBIGUOUS" ? (
            <span>Preview only — full clause boundary could not be verified.</span>
          ) : (
            <span>Clause text preview unavailable or could not be aligned safely.</span>
          )}
        </div>
      )}

      {/* Footer metadata */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginTop: "0.6rem",
          paddingTop: "0.4rem",
          borderTop: "1px dashed var(--color-border-subtle)",
          fontSize: "0.72rem",
          color: "var(--color-text-muted)",
        }}
      >
        <span style={{ fontFamily: "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace" }}>
          ID: {clause.clause_id}
        </span>
        <span style={{ fontStyle: "italic" }}>
          {clause.is_full_text
            ? "Source Document Text (Verified)"
            : clause.alignment_status === "PREVIEW_ONLY_AMBIGUOUS"
            ? "Authoritative API Preview (Ambiguous Boundary)"
            : "Authoritative API Preview"}
        </span>
      </div>
    </div>
  );
}
