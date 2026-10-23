"use client";

import React from "react";
import { AlertCircle, AlertTriangle, Info, CheckCircle2 } from "lucide-react";

export type BadgeVariant = "default" | "high" | "medium" | "low" | "clean" | "research";

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: BadgeVariant;
  children?: React.ReactNode;
}

export function Badge({ variant = "default", children, className = "", style, ...props }: BadgeProps) {
  if (variant === "high") {
    return (
      <span className={`severity-tag HIGH ${className}`.trim()} style={style} {...props}>
        <AlertCircle size={12} aria-hidden="true" />
        <span>{children || "HIGH"}</span>
      </span>
    );
  }

  if (variant === "medium") {
    return (
      <span className={`severity-tag MEDIUM ${className}`.trim()} style={style} {...props}>
        <AlertTriangle size={12} aria-hidden="true" />
        <span>{children || "MEDIUM"}</span>
      </span>
    );
  }

  if (variant === "low") {
    return (
      <span className={`severity-tag LOW ${className}`.trim()} style={style} {...props}>
        <Info size={12} aria-hidden="true" />
        <span>{children || "LOW"}</span>
      </span>
    );
  }

  if (variant === "clean") {
    return (
      <span
        className={`severity-tag ${className}`.trim()}
        style={{
          background: "var(--color-success-bg)",
          border: "1px solid var(--color-success-border)",
          color: "var(--color-success)",
          ...style,
        }}
        {...props}
      >
        <CheckCircle2 size={12} aria-hidden="true" />
        <span>{children || "CLEAN"}</span>
      </span>
    );
  }

  if (variant === "research") {
    return (
      <span className={`badge-research ${className}`.trim()} style={style} {...props}>
        {children || "Research Prototype"}
      </span>
    );
  }

  return (
    <span
      className={`badge ${className}`.trim()}
      style={{
        background: "var(--color-surface-raised)",
        border: "1px solid var(--color-border)",
        color: "var(--color-text-secondary)",
        ...style,
      }}
      {...props}
    >
      {children}
    </span>
  );
}
