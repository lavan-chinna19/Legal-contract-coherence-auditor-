"use client";

import React from "react";
import { AlertCircle, AlertTriangle, CheckCircle2, Info } from "lucide-react";

export interface AlertProps {
  type?: "info" | "warning" | "error" | "success";
  title?: string;
  children: React.ReactNode;
  className?: string;
}

export function Alert({
  type = "info",
  title,
  children,
  className = "",
}: AlertProps) {
  const styles: Record<
    string,
    { bg: string; border: string; text: string; icon: React.ReactNode }
  > = {
    info: {
      bg: "var(--color-surface-raised)",
      border: "var(--color-border-strong)",
      text: "var(--color-text-primary)",
      icon: <Info size={18} style={{ color: "var(--color-accent)" }} aria-hidden="true" />,
    },
    warning: {
      bg: "var(--disclaimer-bg)",
      border: "var(--disclaimer-border)",
      text: "var(--disclaimer-text)",
      icon: <AlertTriangle size={18} aria-hidden="true" />,
    },
    error: {
      bg: "var(--color-danger-bg)",
      border: "var(--color-danger-border)",
      text: "var(--color-danger)",
      icon: <AlertCircle size={18} aria-hidden="true" />,
    },
    success: {
      bg: "var(--color-success-bg)",
      border: "var(--color-success-border)",
      text: "var(--color-success)",
      icon: <CheckCircle2 size={18} aria-hidden="true" />,
    },
  };

  const current = styles[type];

  return (
    <div
      role={type === "error" ? "alert" : "region"}
      aria-live={type === "error" ? "assertive" : "polite"}
      className={className}
      style={{
        background: current.bg,
        border: `1px solid ${current.border}`,
        color: current.text,
        padding: "0.85rem 1.25rem",
        borderRadius: "8px",
        fontSize: "0.875rem",
        marginBottom: "1.25rem",
        display: "flex",
        alignItems: "flex-start",
        gap: "0.75rem",
        lineHeight: 1.45,
      }}
    >
      <div style={{ marginTop: "2px", flexShrink: 0 }}>{current.icon}</div>
      <div style={{ flexGrow: 1 }}>
        {title && (
          <div style={{ fontWeight: 700, marginBottom: "0.2rem" }}>
            {title}
          </div>
        )}
        <div>{children}</div>
      </div>
    </div>
  );
}
