"use client";

import React from "react";
import { ClauseResult } from "../review/types";
import { BookOpen, MessageSquare, BrainCircuit } from "lucide-react";

interface ClauseExplanationHeaderProps {
  selectedClause?: ClauseResult;
  docId: string;
  onNavigateToReview?: () => void;
  onNavigateToFeedback?: () => void;
}

export function ClauseExplanationHeader({
  selectedClause,
  docId,
  onNavigateToReview,
  onNavigateToFeedback,
}: ClauseExplanationHeaderProps) {
  if (!selectedClause) return null;

  const nearestLabel = selectedClause.channel_a_evidence?.nearest_centroid_label || "Unknown";

  return (
    <div
      style={{
        background: "var(--color-surface)",
        border: "1px solid var(--color-border)",
        borderRadius: "var(--radius-md)",
        padding: "1rem 1.25rem",
        marginBottom: "1rem",
        display: "flex",
        flexWrap: "wrap",
        alignItems: "center",
        justifyContent: "space-between",
        gap: "1rem",
      }}
    >
      <div style={{ minWidth: 0, maxWidth: "100%", overflowWrap: "anywhere" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.25rem", flexWrap: "wrap" }}>
          <BrainCircuit size={18} style={{ color: "var(--color-accent)" }} aria-hidden="true" />
          <h2 style={{ fontSize: "1.1rem", fontWeight: 600, color: "var(--color-text-primary)", margin: 0 }}>
            Explanations · Clause {selectedClause.sequence_idx + 1}
          </h2>

          <span
            className={`badge badge-${selectedClause.severity.toLowerCase()}`}
            style={{ fontSize: "0.75rem" }}
          >
            {selectedClause.severity}
          </span>
        </div>
        <p style={{ fontSize: "0.85rem", color: "var(--color-text-secondary)", margin: 0 }}>
          Nearest reference topic: <strong>{nearestLabel}</strong>
        </p><details className="source-details"><summary>Source details</summary><p>Document: {docId} · Clause: {selectedClause.clause_id}</p></details>
      </div>

      <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
        {onNavigateToReview && (
          <button
            id="xai-nav-review-btn"
            className="btn btn-secondary"
            style={{ padding: "0.4rem 0.75rem", fontSize: "0.85rem", display: "inline-flex", alignItems: "center", gap: "0.35rem" }}
            onClick={onNavigateToReview}
          >
            <BookOpen size={14} aria-hidden="true" />
            <span>View in Review</span>
          </button>
        )}
        {onNavigateToFeedback && (
          <button
            id="xai-nav-feedback-btn"
            className="btn btn-secondary"
            style={{ padding: "0.4rem 0.75rem", fontSize: "0.85rem", display: "inline-flex", alignItems: "center", gap: "0.35rem" }}
            onClick={onNavigateToFeedback}
          >
            <MessageSquare size={14} aria-hidden="true" />
            <span>Provide Feedback</span>
          </button>
        )}
      </div>
    </div>
  );
}
