"use client";

import React from "react";

export interface StatusIndicatorProps {
  status: "online" | "offline" | "checking";
  label?: string;
  className?: string;
}

export function StatusIndicator({
  status,
  label,
  className = "",
}: StatusIndicatorProps) {
  const displayLabel = label || `Backend ${status}`;

  return (
    <div
      className={`status-pill ${className}`.trim()}
      role="status"
      aria-live="polite"
      title={`System status: ${status}`}
    >
      <span className={`status-dot ${status}`} aria-hidden="true" />
      <span>{displayLabel}</span>
    </div>
  );
}
