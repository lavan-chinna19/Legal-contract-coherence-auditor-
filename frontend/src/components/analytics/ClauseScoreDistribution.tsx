"use client";

import React, { useState, useRef, useEffect } from "react";
import { ClauseResult } from "./types";
import { ArrowUpRight, ChevronRight, BarChart2, CheckCircle2, AlertTriangle, AlertOctagon } from "lucide-react";

interface ClauseScoreDistributionProps {
  clauses: ClauseResult[];
  selectedClauseId: string;
  onSelectClauseId: (clauseId: string) => void;
  onNavigateToReview?: () => void;
}

export function ClauseScoreDistribution({
  clauses,
  selectedClauseId,
  onSelectClauseId,
  onNavigateToReview,
}: ClauseScoreDistributionProps) {
  const [hoveredClauseId, setHoveredClauseId] = useState<string | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // Authoritative sort by sequence_idx
  const sortedClauses = [...clauses].sort((a, b) => a.sequence_idx - b.sequence_idx);

  const selectedClause = sortedClauses.find((c) => c.clause_id === selectedClauseId) || sortedClauses[0];
  const activeHoverClause = hoveredClauseId ? sortedClauses.find((c) => c.clause_id === hoveredClauseId) : selectedClause;

  // Ensure selected bar is scrolled into view smoothly
  useEffect(() => {
    if (!selectedClauseId || !containerRef.current) return;
    const activeEl = containerRef.current.querySelector(`[data-clause-id="${selectedClauseId}"]`);
    if (activeEl) {
      activeEl.scrollIntoView({ behavior: "smooth", block: "nearest", inline: "center" });
    }
  }, [selectedClauseId]);

  const handleKeyDown = (e: React.KeyboardEvent, index: number) => {
    if (e.key === "ArrowRight") {
      e.preventDefault();
      const nextIdx = Math.min(sortedClauses.length - 1, index + 1);
      onSelectClauseId(sortedClauses[nextIdx].clause_id);
    } else if (e.key === "ArrowLeft") {
      e.preventDefault();
      const prevIdx = Math.max(0, index - 1);
      onSelectClauseId(sortedClauses[prevIdx].clause_id);
    } else if (e.key === "Home") {
      e.preventDefault();
      if (sortedClauses.length > 0) onSelectClauseId(sortedClauses[0].clause_id);
    } else if (e.key === "End") {
      e.preventDefault();
      if (sortedClauses.length > 0) onSelectClauseId(sortedClauses[sortedClauses.length - 1].clause_id);
    } else if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      onSelectClauseId(sortedClauses[index].clause_id);
      if (onNavigateToReview) onNavigateToReview();
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "HIGH":
        return "var(--sev-high-text)";
      case "MEDIUM":
        return "var(--sev-med-text)";
      case "LOW":
        return "var(--color-warning)";
      default:
        return "var(--color-success)";
    }
  };

  const getSeverityBg = (severity: string) => {
    switch (severity) {
      case "HIGH":
        return "var(--sev-high-bg)";
      case "MEDIUM":
        return "var(--sev-med-bg)";
      case "LOW":
        return "rgba(234, 179, 8, 0.15)";
      default:
        return "var(--sev-clean-bg)";
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case "HIGH":
        return <AlertOctagon size={14} style={{ color: "var(--sev-high-text)" }} aria-hidden="true" />;
      case "MEDIUM":
        return <AlertTriangle size={14} style={{ color: "var(--sev-med-text)" }} aria-hidden="true" />;
      default:
        return <CheckCircle2 size={14} style={{ color: "var(--color-success)" }} aria-hidden="true" />;
    }
  };

  return (
    <section
      className="card analytics-distribution-card"
      role="region"
      aria-label="Clause Anomaly Score Sequence Distribution"
      style={{ marginBottom: "1.75rem" }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "1rem", flexWrap: "wrap", gap: "0.5rem" }}>
        <div>
          <h3 style={{ fontSize: "1.05rem", fontWeight: 600, color: "var(--color-text-primary)", margin: 0, display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <BarChart2 size={18} style={{ color: "var(--color-accent)" }} aria-hidden="true" />
            <span>Sequential Clause Anomaly Trajectory</span>
          </h3>
          <p style={{ fontSize: "0.8rem", color: "var(--color-text-secondary)", margin: "0.25rem 0 0 0" }}>
            Real dual-channel combined anomaly score $S_i \in [0.00, 1.00]$ plotted across {sortedClauses.length} consecutive clauses. Select any bar to navigate.
          </p>
        </div>

        {onNavigateToReview && (
          <button
            type="button"
            className="btn btn-secondary"
            id="analytics-inspect-review-btn"
            onClick={onNavigateToReview}
            style={{ fontSize: "0.8rem", padding: "0.4rem 0.75rem", display: "inline-flex", alignItems: "center", gap: "0.35rem" }}
          >
            <span>Open § {selectedClause?.sequence_idx ?? 0} in Contract Review</span>
            <ArrowUpRight size={14} aria-hidden="true" />
          </button>
        )}
      </div>

      {/* Interactive Sequence Chart Container */}
      <div
        ref={containerRef}
        role="group"
        aria-label="Sequential clause score timeline"
        style={{
          position: "relative",
          background: "var(--color-surface-raised)",
          border: "1px solid var(--color-border)",
          borderRadius: "6px",
          padding: "1.5rem 1rem 1rem",
          overflowX: "auto",
          minHeight: "220px",
        }}
      >
        {/* Domain Axis Reference Lines */}
        <div
          aria-hidden="true"
          style={{
            position: "absolute",
            top: "1.5rem",
            bottom: "2.5rem",
            left: "1rem",
            right: "1rem",
            pointerEvents: "none",
            display: "flex",
            flexDirection: "column",
            justifyContent: "space-between",
          }}
        >
          <div style={{ borderTop: "1px dashed var(--color-border)", width: "100%", display: "flex", justifyContent: "flex-end" }}>
            <span style={{ fontSize: "0.65rem", color: "var(--color-text-muted)", marginTop: "-0.5rem", background: "var(--color-surface-raised)", padding: "0 0.25rem" }}>
              1.00 (Max)
            </span>
          </div>
          <div style={{ borderTop: "1px dashed rgba(239, 68, 68, 0.35)", width: "100%", display: "flex", justifyContent: "flex-end" }}>
            <span style={{ fontSize: "0.65rem", color: "var(--sev-high-text)", marginTop: "-0.5rem", background: "var(--color-surface-raised)", padding: "0 0.25rem" }}>
              0.67 (Score scale)
            </span>
          </div>
          <div style={{ borderTop: "1px dashed rgba(245, 158, 11, 0.35)", width: "100%", display: "flex", justifyContent: "flex-end" }}>
            <span style={{ fontSize: "0.65rem", color: "var(--sev-med-text)", marginTop: "-0.5rem", background: "var(--color-surface-raised)", padding: "0 0.25rem" }}>
              0.33 (Score scale)
            </span>
          </div>
          <div style={{ borderTop: "1px solid var(--color-border)", width: "100%", display: "flex", justifyContent: "flex-end" }}>
            <span style={{ fontSize: "0.65rem", color: "var(--color-text-muted)", marginTop: "-0.5rem", background: "var(--color-surface-raised)", padding: "0 0.25rem" }}>
              0.00 (Baseline)
            </span>
          </div>
        </div>

        {/* Sequential Bars */}
        <div
          style={{
            display: "flex",
            alignItems: "flex-end",
            height: "150px",
            gap: sortedClauses.length > 30 ? "4px" : "8px",
            minWidth: `${Math.max(sortedClauses.length * 28, 400)}px`,
            paddingBottom: "1.75rem",
          }}
        >
          {sortedClauses.map((clause, idx) => {
            const isSelected = clause.clause_id === selectedClauseId;
            const isHovered = clause.clause_id === hoveredClauseId;
            const score = typeof clause.combined_score === "number" ? clause.combined_score : 0;
            // Clamped bar height between 4% and 100%
            const heightPercent = Math.max(Math.min(score * 100, 100), 4);
            const sevColor = getSeverityColor(clause.severity);

            return (
              <div
                key={clause.clause_id}
                data-clause-id={clause.clause_id}
                role="button"
                tabIndex={0}
                aria-label={`Clause § ${clause.sequence_idx}: score ${score.toFixed(3)}, severity ${clause.severity}`}
                aria-pressed={isSelected}
                onKeyDown={(e) => handleKeyDown(e, idx)}
                onClick={() => onSelectClauseId(clause.clause_id)}
                onMouseEnter={() => setHoveredClauseId(clause.clause_id)}
                onMouseLeave={() => setHoveredClauseId(null)}
                style={{
                  flex: 1,
                  minWidth: "18px",
                  maxWidth: "40px",
                  height: "100%",
                  display: "flex",
                  flexDirection: "column",
                  justifyContent: "flex-end",
                  alignItems: "center",
                  cursor: "pointer",
                  position: "relative",
                  outline: "none",
                }}
              >
                {/* Bar Element */}
                <div
                  style={{
                    width: "100%",
                    height: `${heightPercent}%`,
                    background: isSelected
                      ? sevColor
                      : isHovered
                      ? `rgba(59, 130, 246, 0.7)`
                      : `color-mix(in srgb, ${sevColor} 70%, transparent)`,
                    borderRadius: "3px 3px 0 0",
                    transition: "all 0.15s ease-in-out",
                    border: isSelected ? `2px solid var(--color-text-primary)` : "1px solid transparent",
                    boxShadow: isSelected ? `0 0 8px ${sevColor}` : "none",
                  }}
                />

                {/* Clause Index Label below bar */}
                <span
                  style={{
                    position: "absolute",
                    bottom: 0,
                    fontSize: "0.68rem",
                    fontWeight: isSelected ? 700 : 400,
                    color: isSelected ? "var(--color-text-primary)" : "var(--color-text-muted)",
                    transform: "translateY(100%)",
                    whiteSpace: "nowrap",
                  }}
                >
                  §{clause.sequence_idx}
                </span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Selected / Hovered Clause Context Strip */}
      {activeHoverClause && (
        <div
          style={{
            marginTop: "1.75rem",
            padding: "0.75rem 1rem",
            background: "var(--color-surface-raised)",
            border: "1px solid var(--color-border)",
            borderRadius: "6px",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            flexWrap: "wrap",
            gap: "0.75rem",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", flexWrap: "wrap" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "0.35rem" }}>
              {getSeverityIcon(activeHoverClause.severity)}
              <span style={{ fontWeight: 700, fontSize: "0.85rem", color: "var(--color-text-primary)" }}>
                § {activeHoverClause.sequence_idx}
              </span>
              <span
                style={{
                  fontSize: "0.75rem",
                  padding: "0.15rem 0.45rem",
                  borderRadius: "4px",
                  background: getSeverityBg(activeHoverClause.severity),
                  color: getSeverityColor(activeHoverClause.severity),
                  fontWeight: 600,
                }}
              >
                {activeHoverClause.severity}
              </span>
            </div>

            <div style={{ fontSize: "0.8rem", color: "var(--color-text-secondary)" }}>
              Combined Score: <strong style={{ color: "var(--color-text-primary)" }}>{activeHoverClause.combined_score.toFixed(3)}</strong>
              <span style={{ color: "var(--color-text-muted)", marginLeft: "0.5rem" }}>
                (Channel A: {activeHoverClause.channel_a_score.toFixed(3)} &bull; Channel B: {activeHoverClause.channel_b_score.toFixed(3)})
              </span>
            </div>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
            <span
              style={{
                fontSize: "0.75rem",
                color: "var(--color-text-muted)",
                maxWidth: "280px",
                whiteSpace: "nowrap",
                overflow: "hidden",
                textOverflow: "ellipsis",
              }}
              title={activeHoverClause.text_preview}
            >
              &ldquo;{activeHoverClause.text_preview}&rdquo;
            </span>

            {onNavigateToReview && (
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => {
                  onSelectClauseId(activeHoverClause.clause_id);
                  onNavigateToReview();
                }}
                style={{ fontSize: "0.75rem", padding: "0.25rem 0.6rem", display: "inline-flex", alignItems: "center", gap: "0.25rem" }}
              >
                <span>Inspect</span>
                <ChevronRight size={12} aria-hidden="true" />
              </button>
            )}
          </div>
        </div>
      )}
    </section>
  );
}
