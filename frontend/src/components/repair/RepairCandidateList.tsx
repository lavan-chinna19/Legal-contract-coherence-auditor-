"use client";

import React from "react";
import { RepositionCandidate } from "./types";
import { Sparkles, Bookmark } from "lucide-react";

interface RepairCandidateListProps {
  candidates: RepositionCandidate[];
  selectedCandidateIdx: number | null;
  onSelectCandidate: (idx: number) => void;
}

export function RepairCandidateList({
  candidates,
  selectedCandidateIdx,
  onSelectCandidate,
}: RepairCandidateListProps) {
  return (
    <div
      className="repair-candidate-list"
      role="listbox"
      aria-label="Eligible Insertion Positions"
      style={{
        display: "flex",
        flexDirection: "column",
        gap: "0.5rem",
        maxHeight: "360px",
        overflowY: "auto",
        paddingRight: "0.25rem",
      }}
    >
      {candidates.map((c) => {
        const isSelected = selectedCandidateIdx === c.position_idx;
        const isOriginal = c.is_current_position;
        const isRecommended = c.is_recommended;
        const isImprovement = c.objective_delta > 0;

        return (
          <button
            key={c.position_idx}
            type="button"
            role="option"
            aria-selected={isSelected}
            onClick={() => onSelectCandidate(c.position_idx)}
            className={`candidate-card ${isSelected ? "selected" : ""}`}
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              padding: "0.75rem 1rem",
              borderRadius: "6px",
              border: isSelected
                ? "2px solid var(--color-accent, #2563eb)"
                : "1px solid var(--color-border, #e2e8f0)",
              background: isSelected
                ? "var(--color-surface-raised, #f8fafc)"
                : "var(--color-surface, #ffffff)",
              cursor: "pointer",
              textAlign: "left",
              transition: "all 0.15s ease",
              width: "100%",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", minWidth: 0 }}>
              {/* Rank Badge */}
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  width: "28px",
                  height: "28px",
                  borderRadius: "50%",
                  fontSize: "0.75rem",
                  fontWeight: 700,
                  flexShrink: 0,
                  background: isRecommended
                    ? "rgba(16, 185, 129, 0.15)"
                    : isOriginal
                    ? "rgba(100, 116, 139, 0.15)"
                    : "rgba(37, 99, 235, 0.1)",
                  color: isRecommended
                    ? "var(--color-success, #10b981)"
                    : isOriginal
                    ? "var(--color-text-secondary, #64748b)"
                    : "var(--color-accent, #2563eb)",
                }}
              >
                #{c.rank}
              </div>

              {/* Placement Text & Subtitle */}
              <div style={{ minWidth: 0 }}>
                <div
                  style={{
                    fontSize: "0.85rem",
                    fontWeight: 600,
                    color: "var(--color-text-primary, #0f172a)",
                    display: "flex",
                    alignItems: "center",
                    gap: "0.4rem",
                    flexWrap: "wrap",
                  }}
                >
                  <span>{c.relative_placement}</span>
                  {isRecommended && (
                    <span
                      style={{
                        display: "inline-flex",
                        alignItems: "center",
                        gap: "0.2rem",
                        fontSize: "0.68rem",
                        padding: "0.1rem 0.35rem",
                        borderRadius: "4px",
                        background: "rgba(16, 185, 129, 0.12)",
                        color: "var(--color-success, #10b981)",
                        fontWeight: 700,
                      }}
                    >
                      <Sparkles size={11} aria-hidden="true" />
                      Suggested
                    </span>
                  )}
                  {isOriginal && (
                    <span
                      style={{
                        display: "inline-flex",
                        alignItems: "center",
                        gap: "0.2rem",
                        fontSize: "0.68rem",
                        padding: "0.1rem 0.35rem",
                        borderRadius: "4px",
                        background: "rgba(100, 116, 139, 0.12)",
                        color: "var(--color-text-secondary, #64748b)",
                        fontWeight: 600,
                      }}
                    >
                      <Bookmark size={11} aria-hidden="true" />
                      Current
                    </span>
                  )}
                </div>
                <div
                  style={{
                    fontSize: "0.72rem",
                    color: "var(--color-text-muted, #94a3b8)",
                    marginTop: "0.15rem",
                  }}
                >
                  Position Index: {c.position_idx}
                </div>
              </div>
            </div>

            {/* Delta & Score Badges */}
            <div style={{ textAlign: "right", flexShrink: 0, marginLeft: "0.5rem" }}>
              <div
                style={{
                  fontSize: "0.85rem",
                  fontWeight: 700,
                  fontFamily: "ui-monospace, monospace",
                  color: isOriginal
                    ? "var(--color-text-muted, #94a3b8)"
                    : isImprovement
                    ? "var(--color-success, #10b981)"
                    : "var(--sev-high-text, #ef4444)",
                }}
              >
                {isOriginal ? "Baseline" : `${c.objective_delta > 0 ? "+" : ""}${c.objective_delta.toFixed(4)}`}
              </div>
              <div
                style={{
                  fontSize: "0.7rem",
                  color: "var(--color-text-muted, #94a3b8)",
                }}
              >
                J: {c.mean_combined_score.toFixed(4)}
              </div>
            </div>
          </button>
        );
      })}
    </div>
  );
}
