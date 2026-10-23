"use client";

import React from "react";
import { Loader2 } from "lucide-react";

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "outline" | "danger" | "ghost";
  size?: "sm" | "md" | "lg";
  loading?: boolean;
  icon?: React.ReactNode;
}

export function Button({
  children,
  variant = "primary",
  size = "md",
  loading = false,
  disabled,
  icon,
  className = "",
  ...props
}: ButtonProps) {
  const variantClass =
    variant === "secondary"
      ? "btn-secondary"
      : variant === "outline"
      ? "btn-outline"
      : variant === "danger"
      ? "btn-danger"
      : variant === "ghost"
      ? "btn-ghost"
      : "btn";

  const sizeStyles: Record<string, React.CSSProperties> = {
    sm: { padding: "0.4rem 0.75rem", fontSize: "0.8rem" },
    md: { padding: "0.6rem 1.2rem", fontSize: "0.875rem" },
    lg: { padding: "0.75rem 1.5rem", fontSize: "1rem" },
  };

  return (
    <button
      className={`${variantClass} ${className}`.trim()}
      style={sizeStyles[size]}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? (
        <Loader2 size={16} className="animate-spin" aria-hidden="true" />
      ) : icon ? (
        <span aria-hidden="true">{icon}</span>
      ) : null}
      <span>{children}</span>
    </button>
  );
}
