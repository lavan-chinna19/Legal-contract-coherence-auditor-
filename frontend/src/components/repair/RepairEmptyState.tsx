"use client";

import React from "react";
import { ArrowRightLeft } from "lucide-react";

interface RepairEmptyStateProps {
  message?: string;
}

export function RepairEmptyState({
  message = "Select a clause in the Contract Review workspace and click 'Suggested positions (Experimental)' to inspect counterfactual candidate insertion slots.",
}: RepairEmptyStateProps) {
  return (
    <div
      className="repair-empty-state"
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        padding: "3rem 1.5rem",
        textAlign: "center",
        background: "var(--color-surface, #ffffff)",
        borderRadius: "8px",
        border: "1px dashed var(--color-border, #e2e8f0)",
      }}
    >
      <div
        style={{
          width: "48px",
          height: "48px",
          borderRadius: "50%",
          background: "rgba(37, 99, 235, 0.1)",
          color: "var(--color-accent, #2563eb)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          marginBottom: "1rem",
        }}
      >
        <ArrowRightLeft size={24} aria-hidden="true" />
      </div>
      <h3
        style={{
          fontSize: "1rem",
          fontWeight: 600,
          color: "var(--color-text-primary, #0f172a)",
          marginBottom: "0.5rem",
        }}
      >
        Suggested Clause Positions
      </h3>
      <p
        style={{
          fontSize: "0.82rem",
          color: "var(--color-text-secondary, #64748b)",
          maxWidth: "420px",
          lineHeight: 1.5,
          margin: 0,
        }}
      >
        {message}
      </p>
    </div>
  );
}
