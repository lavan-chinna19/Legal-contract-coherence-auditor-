"use client";

import React from "react";
import { RepositionCandidate } from "./types";
import { ArrowDownRight, ArrowUpRight, Minus, Scale, Activity } from "lucide-react";

interface RepairScoreComparisonProps {
  originalMeanScore: number;
  originalTargetSb: number;
  candidate: RepositionCandidate;
}

export function RepairScoreComparison({
  originalMeanScore,
  originalTargetSb,
  candidate,
}: RepairScoreComparisonProps) {
  const isOriginal = candidate.is_current_position;
  const delta = candidate.objective_delta;
  const isImprovement = delta > 0;

  const sbDelta = originalTargetSb - candidate.clause_channel_b_score;
  const isSbImprovement = sbDelta > 0;

  return (
    <div
      className="repair-score-comparison"
      style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
        gap: "0.75rem",
        marginBottom: "1rem",
      }}
    >
      {/* Metric 1: Whole-Document Objective J(D^(p)) */}
      <div
        style={{
          padding: "0.85rem",
          borderRadius: "6px",
          border: "1px solid var(--color-border, #e2e8f0)",
          background: "var(--color-surface, #ffffff)",
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            fontSize: "0.75rem",
            color: "var(--color-text-muted, #94a3b8)",
            marginBottom: "0.35rem",
          }}
        >
          <span style={{ fontWeight: 600 }}>DOC MEAN ANOMALY J(D)</span>
          <Scale size={14} aria-hidden="true" />
        </div>
        <div style={{ display: "flex", alignItems: "baseline", gap: "0.5rem" }}>
          <span
            style={{
              fontSize: "1.2rem",
              fontWeight: 700,
              fontFamily: "ui-monospace, monospace",
              color: "var(--color-text-primary, #0f172a)",
            }}
          >
            {candidate.mean_combined_score.toFixed(4)}
          </span>
          <span
            style={{
              fontSize: "0.78rem",
              fontWeight: 600,
              display: "inline-flex",
              alignItems: "center",
              gap: "0.15rem",
              color: isOriginal
                ? "var(--color-text-muted, #94a3b8)"
                : isImprovement
                ? "var(--color-success, #10b981)"
                : "var(--sev-high-text, #ef4444)",
            }}
          >
            {isOriginal ? (
              <>
                <Minus size={12} /> Baseline
              </>
            ) : isImprovement ? (
              <>
                <ArrowDownRight size={13} /> -{Math.abs(delta).toFixed(4)}
              </>
            ) : (
              <>
                <ArrowUpRight size={13} /> +{Math.abs(delta).toFixed(4)}
              </>
            )}
          </span>
        </div>
        <div style={{ fontSize: "0.7rem", color: "var(--color-text-muted, #94a3b8)", marginTop: "0.25rem" }}>
          Original: {originalMeanScore.toFixed(4)} (Lower is more coherent)
        </div>
      </div>

      {/* Metric 2: Target Clause Channel B Anomaly S_B(c_k) */}
      <div
        style={{
          padding: "0.85rem",
          borderRadius: "6px",
          border: "1px solid var(--color-border, #e2e8f0)",
          background: "var(--color-surface, #ffffff)",
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            fontSize: "0.75rem",
            color: "var(--color-text-muted, #94a3b8)",
            marginBottom: "0.35rem",
          }}
        >
          <span style={{ fontWeight: 600 }}>CLAUSE TRANSITION S_B</span>
          <Activity size={14} aria-hidden="true" />
        </div>
        <div style={{ display: "flex", alignItems: "baseline", gap: "0.5rem" }}>
          <span
            style={{
              fontSize: "1.2rem",
              fontWeight: 700,
              fontFamily: "ui-monospace, monospace",
              color: "var(--color-text-primary, #0f172a)",
            }}
          >
            {candidate.clause_channel_b_score.toFixed(4)}
          </span>
          <span
            style={{
              fontSize: "0.78rem",
              fontWeight: 600,
              display: "inline-flex",
              alignItems: "center",
              gap: "0.15rem",
              color: isOriginal
                ? "var(--color-text-muted, #94a3b8)"
                : isSbImprovement
                ? "var(--color-success, #10b981)"
                : "var(--sev-high-text, #ef4444)",
            }}
          >
            {isOriginal ? (
              <>
                <Minus size={12} /> Baseline
              </>
            ) : isSbImprovement ? (
              <>
                <ArrowDownRight size={13} /> -{Math.abs(sbDelta).toFixed(4)}
              </>
            ) : (
              <>
                <ArrowUpRight size={13} /> +{Math.abs(sbDelta).toFixed(4)}
              </>
            )}
          </span>
        </div>
        <div style={{ fontSize: "0.7rem", color: "var(--color-text-muted, #94a3b8)", marginTop: "0.25rem" }}>
          Original S_B: {originalTargetSb.toFixed(4)}
        </div>
      </div>
    </div>
  );
}
