"use client";

import React from "react";

export interface CardProps extends Omit<React.HTMLAttributes<HTMLDivElement>, "title"> {
  title?: React.ReactNode;
  subtitle?: React.ReactNode;
  action?: React.ReactNode;
  children: React.ReactNode;
}

export function Card({
  title,
  subtitle,
  action,
  children,
  className = "",
  style,
  ...props
}: CardProps) {
  return (
    <div className={`card ${className}`.trim()} style={style} {...props}>
      {(title || action) && (
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "flex-start",
            marginBottom: subtitle ? "0.25rem" : "1rem",
            paddingBottom: "0.5rem",
            borderBottom: "1px solid var(--color-border-subtle)",
          }}
        >
          <div>
            {typeof title === "string" ? (
              <h2 style={{ fontSize: "1.1rem", fontWeight: 700, color: "var(--color-text-primary)" }}>
                {title}
              </h2>
            ) : (
              title
            )}
            {subtitle && (
              <p style={{ fontSize: "0.8rem", color: "var(--color-text-secondary)", marginTop: "0.2rem" }}>
                {subtitle}
              </p>
            )}
          </div>
          {action && <div>{action}</div>}
        </div>
      )}
      {children}
    </div>
  );
}
