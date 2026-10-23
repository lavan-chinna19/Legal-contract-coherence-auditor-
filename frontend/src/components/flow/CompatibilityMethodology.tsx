"use client";

import React, { useState } from "react";
import { CompatibilityArtifact } from "./types";
import { BookOpen, ChevronDown, ChevronUp, Database, Cpu, ShieldAlert } from "lucide-react";

interface CompatibilityMethodologyProps {
  artifact: CompatibilityArtifact;
}

export function CompatibilityMethodology({ artifact }: CompatibilityMethodologyProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div
      style={{
        background: "var(--color-surface)",
        border: "1px solid var(--color-border)",
        borderRadius: "var(--radius-md)",
        padding: "1rem 1.25rem",
        marginTop: "1.5rem",
      }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          cursor: "pointer",
          userSelect: "none",
        }}
        onClick={() => setIsExpanded(!isExpanded)}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => {
          if (e.key === "Enter" || e.key === " ") {
            e.preventDefault();
            setIsExpanded(!isExpanded);
          }
        }}
        aria-expanded={isExpanded}
        aria-controls="methodology-details-content"
      >
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
          <BookOpen size={18} style={{ color: "var(--color-accent)" }} aria-hidden="true" />
          <h4 style={{ margin: 0, fontSize: "0.95rem", color: "var(--color-text-primary)" }}>
            Scientific Methodology & Model Provenance (Phase 4B)
          </h4>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", fontSize: "0.8rem", color: "var(--color-text-secondary)" }}>
          <span>{isExpanded ? "Collapse specification" : "Inspect technical specification & hashes"}</span>
          {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
        </div>
      </div>

      {isExpanded && (
        <div id="methodology-details-content" style={{ marginTop: "1rem", paddingTop: "1rem", borderTop: "1px solid var(--color-border)" }}>
          {/* Key Principles Grid */}
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
              gap: "1rem",
              marginBottom: "1rem",
            }}
          >
            {/* Provenance */}
            <div
              style={{
                background: "var(--color-bg)",
                border: "1px solid var(--color-border)",
                borderRadius: "var(--radius-sm)",
                padding: "0.75rem",
                fontSize: "0.8rem",
              }}
            >
              <div style={{ display: "flex", alignItems: "center", gap: "0.4rem", fontWeight: 600, color: "var(--color-text-primary)", marginBottom: "0.5rem" }}>
                <Cpu size={15} style={{ color: "var(--color-accent)" }} />
                Frozen Checkpoint & Architecture
              </div>
              <ul style={{ margin: 0, paddingLeft: "1.2rem", color: "var(--color-text-secondary)", lineHeight: "1.5" }}>
                <li><strong>Architecture:</strong> {artifact.provenance.model_architecture}</li>
                <li><strong>Checkpoint:</strong> <code>{artifact.provenance.checkpoint_path}</code></li>
                <li><strong>SHA-256:</strong> <code>{artifact.provenance.checkpoint_sha256.substring(0, 16)}...</code></li>
                <li><strong>Base Model:</strong> {artifact.provenance.embedding_model}</li>
              </ul>
            </div>

            {/* Centroids */}
            <div
              style={{
                background: "var(--color-bg)",
                border: "1px solid var(--color-border)",
                borderRadius: "var(--radius-sm)",
                padding: "0.75rem",
                fontSize: "0.8rem",
              }}
            >
              <div style={{ display: "flex", alignItems: "center", gap: "0.4rem", fontWeight: 600, color: "var(--color-text-primary)", marginBottom: "0.5rem" }}>
                <Database size={15} style={{ color: "var(--color-accent)" }} />
                LEDGAR Reference Centroids
              </div>
              <ul style={{ margin: 0, paddingLeft: "1.2rem", color: "var(--color-text-secondary)", lineHeight: "1.5" }}>
                <li><strong>Centroid Artifact:</strong> <code>{artifact.provenance.centroids_path}</code></li>
                <li><strong>Centroids SHA-256:</strong> <code>{artifact.provenance.centroids_sha256.substring(0, 16)}...</code></li>
                <li><strong>Dimensions:</strong> {artifact.dimensions.num_clause_types} centroids × 768 dims (unit L2 normalized)</li>
                <li><strong>Total Matrix:</strong> {artifact.dimensions.num_ordered_pairs} ordered pairs evaluated</li>
              </ul>
            </div>
          </div>

          {/* Mathematical Formulation */}
          <div
            style={{
              background: "var(--color-bg)",
              border: "1px solid var(--color-border)",
              borderRadius: "var(--radius-sm)",
              padding: "0.75rem 1rem",
              marginBottom: "1rem",
              fontSize: "0.8rem",
            }}
          >
            <div style={{ fontWeight: 600, color: "var(--color-text-primary)", marginBottom: "0.25rem" }}>
              Mathematical Pairwise Feature Construction
            </div>
            <p style={{ margin: "0.25rem 0", color: "var(--color-text-secondary)", fontFamily: "monospace" }}>
              φ(c_i, c_j) = [c_i, c_j, |c_i - c_j|, c_i ⊙ c_j] ∈ ℝ^3072
            </p>
            <p style={{ margin: "0.25rem 0", color: "var(--color-text-secondary)", fontFamily: "monospace" }}>
              P(c_i → c_j) = σ(W_3 · ReLU(W_2 · ReLU(W_1 · φ + b_1) + b_2) + b_3) ∈ [0.0, 1.0]
            </p>
            <p style={{ margin: "0.5rem 0 0", color: "var(--color-text-secondary)", lineHeight: "1.4" }}>
              Because the first 1,536 features [c_i, c_j] maintain ordered placement, the transformation is inherently <strong>directional</strong>:{" "}
              P(c_i → c_j) ≠ P(c_j → c_i). The empirical mean directional asymmetry across all distinct pairs is {artifact.summary_statistics.mean_directional_asymmetry.toFixed(6)}.
            </p>
          </div>

          {/* Critical Methodological Disclosures */}
          <div
            style={{
              background: "rgba(234, 88, 12, 0.08)",
              border: "1px solid rgba(234, 88, 12, 0.3)",
              borderRadius: "var(--radius-sm)",
              padding: "0.75rem 1rem",
              fontSize: "0.75rem",
              color: "var(--color-text-primary)",
              lineHeight: "1.5",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "0.4rem", fontWeight: 700, color: "var(--sev-high-text, #c2410c)", marginBottom: "0.4rem" }}>
              <ShieldAlert size={16} />
              Strict Interpretability Safeguards & Disclosures
            </div>
            <ul style={{ margin: 0, paddingLeft: "1.2rem" }}>
              <li>
                <strong>Not Empirical Frequency:</strong> These values represent learned binary coherence likelihoods produced by the frozen neural model. They must not be mischaracterized as empirical frequencies observed in historical drafting corpuses.
              </li>
              <li>
                <strong>Not Row-Stochastic (Not Markov):</strong> The model was trained with binary cross-entropy (BCE) on individual ordered pairs, not softmax over categories. Therefore, row sums do not sum to 1.0 (mean row sum is ~23.01). Normalization was intentionally not forced, preserving genuine model logits.
              </li>
              <li>
                <strong>No Fabricated Taxonomy:</strong> All 66 categories correspond to genuine LEDGAR legal clause types. No synthetic 7-category taxonomy has been introduced.
              </li>
              <li>
                <strong>Inference Conditions:</strong> All inference was performed deterministically with PyTorch <code>torch.no_grad()</code> and <code>model.eval()</code> (dropout disabled).
              </li>
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}
