"use client";

import React from "react";
import { BarChart3, ArrowRight, ShieldCheck, FileSpreadsheet } from "lucide-react";

interface AnalyticsEmptyStateProps {
  onNavigateToUpload?: () => void;
}

export function AnalyticsEmptyState({ onNavigateToUpload }: AnalyticsEmptyStateProps) {
  return (
    <div
      className="card analytics-empty-card"
      role="region"
      aria-label="Analytics Workspace Empty State"
      style={{
        padding: "3rem 2rem",
        textAlign: "center",
        maxWidth: "720px",
        margin: "2rem auto",
        background: "var(--color-surface)",
        border: "1px dashed var(--color-border)",
        borderRadius: "8px",
      }}
    >
      <div
        style={{
          width: "64px",
          height: "64px",
          borderRadius: "12px",
          background: "var(--color-surface-raised)",
          border: "1px solid var(--color-border)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          margin: "0 auto 1.5rem",
          color: "var(--color-accent)",
        }}
      >
        <BarChart3 size={32} aria-hidden="true" />
      </div>

      <h2
        style={{
          fontSize: "1.25rem",
          fontWeight: 600,
          color: "var(--color-text-primary)",
          marginBottom: "0.75rem",
        }}
      >
        No Active Audit Data in Analytics Workspace
      </h2>

      <p
        style={{
          fontSize: "0.9rem",
          color: "var(--color-text-secondary)",
          lineHeight: 1.6,
          maxWidth: "540px",
          margin: "0 auto 1.75rem",
        }}
      >
        To inspect document-level sequence coherence distributions, channel evidence breakdowns,
        and deterministic rule violation metrics, please ingest and analyze a contract document in the Overview workspace.
      </p>

      <div
        style={{
          display: "flex",
          justifyContent: "center",
          gap: "1rem",
          flexWrap: "wrap",
          marginBottom: "2rem",
        }}
      >
        {onNavigateToUpload && (
          <button
            type="button"
            className="btn"
            id="analytics-empty-upload-btn"
            onClick={onNavigateToUpload}
            style={{ display: "inline-flex", alignItems: "center", gap: "0.5rem" }}
          >
            <span>Go to Document Ingestion</span>
            <ArrowRight size={16} aria-hidden="true" />
          </button>
        )}
      </div>

      <div
        style={{
          borderTop: "1px solid var(--color-border)",
          paddingTop: "1.25rem",
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
          gap: "1rem",
          textAlign: "left",
          fontSize: "0.8rem",
          color: "var(--color-text-muted)",
        }}
      >
        <div style={{ display: "flex", gap: "0.5rem", alignItems: "flex-start" }}>
          <ShieldCheck size={16} style={{ color: "var(--color-accent)", flexShrink: 0, marginTop: "2px" }} />
          <span>Strict React memory persistence — zero client-side disk caching of legal text.</span>
        </div>
        <div style={{ display: "flex", gap: "0.5rem", alignItems: "flex-start" }}>
          <FileSpreadsheet size={16} style={{ color: "var(--color-accent)", flexShrink: 0, marginTop: "2px" }} />
          <span>Evaluation of LEDGAR centroid distance and neural scores for adjacent clause pairs.</span>
        </div>
      </div>
    </div>
  );
}
