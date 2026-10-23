"use client";

import React from "react";

export interface SectionHeadingProps {
  title: string;
  description?: string;
  action?: React.ReactNode;
  tag?: React.ReactNode;
}

export function SectionHeading({
  title,
  description,
  action,
  tag,
}: SectionHeadingProps) {
  return (
    <div
      style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "flex-start",
        marginBottom: "1.25rem",
        gap: "1rem",
        flexWrap: "wrap",
      }}
    >
      <div>
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
          <h2 style={{ fontSize: "1.25rem", fontWeight: 700, color: "var(--color-text-primary)" }}>
            {title}
          </h2>
          {tag}
        </div>
        {description && (
          <p style={{ fontSize: "0.85rem", color: "var(--color-text-secondary)", marginTop: "0.25rem" }}>
            {description}
          </p>
        )}
      </div>
      {action && <div>{action}</div>}
    </div>
  );
}
