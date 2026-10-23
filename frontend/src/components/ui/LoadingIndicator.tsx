"use client";

import React from "react";
import { Loader2 } from "lucide-react";

export interface LoadingIndicatorProps {
  message?: string;
  size?: "sm" | "md" | "lg";
}

export function LoadingIndicator({
  message = "Processing request...",
  size = "md",
}: LoadingIndicatorProps) {
  const pixelSize = size === "sm" ? 16 : size === "lg" ? 32 : 24;

  return (
    <div
      role="status"
      aria-live="polite"
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        gap: "0.75rem",
        padding: "1.5rem",
        color: "var(--color-text-secondary)",
        fontSize: "0.875rem",
      }}
    >
      <Loader2
        size={pixelSize}
        style={{
          animation: "spin 1s linear infinite",
          color: "var(--color-accent)",
        }}
        aria-hidden="true"
      />
      <span>{message}</span>
      <style jsx>{`
        @keyframes spin {
          from {
            transform: rotate(0deg);
          }
          to {
            transform: rotate(360deg);
          }
        }
      `}</style>
    </div>
  );
}
