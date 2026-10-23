"use client";

import React from "react";
import { RepositionCandidate } from "./types";
import { ArrowDown, AlignLeft } from "lucide-react";

interface ClauseSnippet {
  clause_id: string;
  sequence_idx: number;
  text_preview: string;
}

interface RepairClausePreviewProps {
  targetClause: ClauseSnippet;
  allClauses: ClauseSnippet[];
  candidate: RepositionCandidate;
}

export function RepairClausePreview({
  targetClause,
  allClauses,
  candidate,
}: RepairClausePreviewProps) {
  const precedingClause = candidate.preceding_clause_id
    ? allClauses.find((c) => c.clause_id === candidate.preceding_clause_id)
    : null;

  const succeedingClause = candidate.succeeding_clause_id
    ? allClauses.find((c) => c.clause_id === candidate.succeeding_clause_id)
    : null;

  return (
    <div
      className="repair-clause-preview"
      style={{
        display: "flex",
        flexDirection: "column",
        gap: "0.6rem",
        padding: "1rem",
        borderRadius: "6px",
        background: "var(--color-surface-raised, #f8fafc)",
        border: "1px solid var(--color-border, #e2e8f0)",
        marginBottom: "1rem",
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: "0.35rem",
          fontSize: "0.75rem",
          fontWeight: 700,
          color: "var(--color-text-secondary, #64748b)",
          textTransform: "uppercase",
          letterSpacing: "0.03em",
        }}
      >
        <AlignLeft size={13} aria-hidden="true" />
        <span>Simulated Context at Position {candidate.position_idx}</span>
      </div>

      {/* Preceding Neighbor */}
      {precedingClause ? (
        <div
          style={{
            padding: "0.6rem 0.85rem",
            borderRadius: "5px",
            background: "var(--color-surface, #ffffff)",
            border: "1px solid var(--color-border, #e2e8f0)",
            fontSize: "0.8rem",
            color: "var(--color-text-secondary, #64748b)",
          }}
        >
          <div style={{ fontSize: "0.7rem", fontWeight: 600, color: "var(--color-text-muted, #94a3b8)", marginBottom: "0.2rem" }}>
            PRECEDING CLAUSE §{precedingClause.sequence_idx} ({precedingClause.clause_id})
          </div>
          <p style={{ margin: 0, fontStyle: "italic", whiteSpace: "pre-wrap" }}>
            {precedingClause.text_preview}
          </p>
        </div>
      ) : (
        <div
          style={{
            padding: "0.4rem 0.75rem",
            fontSize: "0.72rem",
            color: "var(--color-text-muted, #94a3b8)",
            fontStyle: "italic",
            background: "var(--color-surface, #ffffff)",
            borderRadius: "4px",
            border: "1px dashed var(--color-border, #e2e8f0)",
          }}
        >
          [Document Start — No preceding clause]
        </div>
      )}

      {/* Down Arrow Indicator */}
      <div style={{ display: "flex", justifyContent: "center", color: "var(--color-accent, #2563eb)" }}>
        <ArrowDown size={14} aria-hidden="true" />
      </div>

      {/* Repositioned Target Clause (Highlighted) */}
      <div
        style={{
          padding: "0.75rem 0.95rem",
          borderRadius: "6px",
          background: "rgba(37, 99, 235, 0.05)",
          border: "2px solid var(--color-accent, #2563eb)",
          fontSize: "0.82rem",
          color: "var(--color-text-primary, #0f172a)",
        }}
      >
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            fontSize: "0.7rem",
            fontWeight: 700,
            color: "var(--color-accent, #2563eb)",
            marginBottom: "0.3rem",
          }}
        >
          <span>TARGET CLAUSE (CURRENTLY §{targetClause.sequence_idx})</span>
          <span style={{ fontSize: "0.68rem", fontWeight: 600, color: "var(--color-text-muted, #94a3b8)" }}>
            ID: {targetClause.clause_id}
          </span>
        </div>
        <p style={{ margin: 0, fontWeight: 500, whiteSpace: "pre-wrap" }}>
          {targetClause.text_preview}
        </p>
      </div>

      {/* Down Arrow Indicator */}
      <div style={{ display: "flex", justifyContent: "center", color: "var(--color-accent, #2563eb)" }}>
        <ArrowDown size={14} aria-hidden="true" />
      </div>

      {/* Succeeding Neighbor */}
      {succeedingClause ? (
        <div
          style={{
            padding: "0.6rem 0.85rem",
            borderRadius: "5px",
            background: "var(--color-surface, #ffffff)",
            border: "1px solid var(--color-border, #e2e8f0)",
            fontSize: "0.8rem",
            color: "var(--color-text-secondary, #64748b)",
          }}
        >
          <div style={{ fontSize: "0.7rem", fontWeight: 600, color: "var(--color-text-muted, #94a3b8)", marginBottom: "0.2rem" }}>
            SUCCEEDING CLAUSE §{succeedingClause.sequence_idx} ({succeedingClause.clause_id})
          </div>
          <p style={{ margin: 0, fontStyle: "italic", whiteSpace: "pre-wrap" }}>
            {succeedingClause.text_preview}
          </p>
        </div>
      ) : (
        <div
          style={{
            padding: "0.4rem 0.75rem",
            fontSize: "0.72rem",
            color: "var(--color-text-muted, #94a3b8)",
            fontStyle: "italic",
            background: "var(--color-surface, #ffffff)",
            borderRadius: "4px",
            border: "1px dashed var(--color-border, #e2e8f0)",
          }}
        >
          [Document End — No succeeding clause]
        </div>
      )}
    </div>
  );
}
