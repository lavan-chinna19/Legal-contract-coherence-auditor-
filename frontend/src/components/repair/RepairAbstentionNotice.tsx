"use client";

import React from "react";
import { ShieldCheck } from "lucide-react";

interface RepairAbstentionNoticeProps {
  reason: string | null;
}

export function RepairAbstentionNotice({ reason }: RepairAbstentionNoticeProps) {
  const getExplanation = (code: string | null) => {
    if (!code) return "The model did not find sufficient empirical justification to propose relocating this clause.";
    if (code.includes("ORIGINAL_POSITION_ALREADY_OPTIMAL")) {
      return "The current original position is already ranked #1. Relocating this clause to any alternative position would degrade or equal document coherence.";
    }
    if (code.includes("NO_IMPROVEMENT_OVER_ORIGINAL")) {
      return "No alternative insertion slot produces a lower anomaly score than the original sequence.";
    }
    if (code.includes("IMPROVEMENT_BELOW_THRESHOLD")) {
      return `The highest candidate improvement is below the empirical threshold (0.005). The predicted gain is within statistical noise and does not warrant restructuring.`;
    }
    if (code.includes("MULTI_CANDIDATE_OBJECTIVE_TIE")) {
      return "Multiple candidate positions produced identical objective values (within 0.0001). The model abstains from arbitrarily preferring one slot over another.";
    }
    if (code.includes("DOCUMENT_TOO_SHORT")) {
      return "The document contains too few clauses for meaningful alternative sequence evaluation.";
    }
    return code;
  };

  return (
    <div
      className="repair-abstention-notice"
      style={{
        padding: "0.85rem 1rem",
        borderRadius: "6px",
        background: "rgba(100, 116, 139, 0.08)",
        border: "1px solid var(--color-border, #e2e8f0)",
        marginBottom: "1rem",
        display: "flex",
        alignItems: "flex-start",
        gap: "0.65rem",
      }}
    >
      <ShieldCheck
        size={18}
        style={{ color: "var(--color-accent, #2563eb)", flexShrink: 0, marginTop: "0.1rem" }}
        aria-hidden="true"
      />
      <div>
        <div
          style={{
            fontSize: "0.82rem",
            fontWeight: 700,
            color: "var(--color-text-primary, #0f172a)",
            marginBottom: "0.2rem",
          }}
        >
          Model Abstention — No Repositioning Recommended
        </div>
        <p
          style={{
            margin: 0,
            fontSize: "0.78rem",
            color: "var(--color-text-secondary, #64748b)",
            lineHeight: 1.5,
          }}
        >
          {getExplanation(reason)}
        </p>
      </div>
    </div>
  );
}
