"use client";

import React from "react";
import { BrainCircuit, ArrowRight } from "lucide-react";

interface ExplainabilityEmptyStateProps {
  onNavigateToUpload?: () => void;
}

export function ExplainabilityEmptyState({ onNavigateToUpload }: ExplainabilityEmptyStateProps) {
  return (
    <div
      style={{
        background: "var(--color-surface)",
        border: "1px dashed var(--color-border)",
        borderRadius: "var(--radius-lg)",
        padding: "3rem 2rem",
        textAlign: "center",
        maxWidth: "600px",
        margin: "2rem auto",
      }}
    >
      <div
        style={{
          width: "56px",
          height: "56px",
          borderRadius: "50%",
          background: "var(--color-bg)",
          display: "inline-flex",
          alignItems: "center",
          justifyContent: "center",
          marginBottom: "1rem",
          color: "var(--color-accent)",
        }}
      >
        <BrainCircuit size={28} aria-hidden="true" />
      </div>

      <h2 style={{ fontSize: "1.25rem", fontWeight: 600, color: "var(--color-text-primary)", marginBottom: "0.5rem" }}>
        No Contract Available for Explainability Analysis
      </h2>
      <p style={{ fontSize: "0.9rem", color: "var(--color-text-secondary)", marginBottom: "1.5rem", lineHeight: 1.6 }}>
        Please upload and analyze a contract document in Overview. Once processed, you can inspect token-level Integrated Gradients attributions and adjacent clause perturbation sensitivity.
      </p>

      {onNavigateToUpload && (
        <button
          id="xai-empty-upload-btn"
          className="btn"
          onClick={onNavigateToUpload}
          style={{ display: "inline-flex", alignItems: "center", gap: "0.5rem" }}
        >
          <span>Go to Ingestion &amp; Upload</span>
          <ArrowRight size={16} aria-hidden="true" />
        </button>
      )}
    </div>
  );
}
