"use client";

import React from "react";
import { WordGroup } from "./wordpieceGrouping";
import { X, Search } from "lucide-react";

interface TokenDetailPanelProps {
  selectedGroup: WordGroup | null;
  onClose: () => void;
}

export function TokenDetailPanel({ selectedGroup, onClose }: TokenDetailPanelProps) {
  if (!selectedGroup) return null;

  return (
    <div
      id="xai-token-inspector-panel"
      style={{
        background: "var(--color-surface)",
        border: "1px solid var(--color-border)",
        borderRadius: "var(--radius-md)",
        padding: "1rem 1.25rem",
        marginBottom: "1rem",
        borderLeft: "4px solid var(--color-accent)",
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "0.75rem" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
          <Search size={16} style={{ color: "var(--color-accent)" }} aria-hidden="true" />
          <h4 style={{ margin: 0, fontSize: "0.95rem", fontWeight: 600, color: "var(--color-text-primary)" }}>
            Token Inspector: <span style={{ fontFamily: selectedGroup.isSpecialToken ? "monospace" : "inherit" }}>&quot;{selectedGroup.word}&quot;</span>
          </h4>
          <span
            className="badge"
            style={{
              fontSize: "0.7rem",
              background:
                selectedGroup.sign === "POSITIVE"
                  ? "rgba(220, 38, 38, 0.15)"
                  : selectedGroup.sign === "NEGATIVE"
                  ? "rgba(22, 163, 74, 0.15)"
                  : "var(--color-bg)",
              color:
                selectedGroup.sign === "POSITIVE"
                  ? "#dc2626"
                  : selectedGroup.sign === "NEGATIVE"
                  ? "#16a34a"
                  : "var(--color-text-secondary)",
            }}
          >
            {selectedGroup.sign === "POSITIVE" ? "Anomaly Driver (+)" : selectedGroup.sign === "NEGATIVE" ? "Coherence Anchor (−)" : "Neutral"}
          </span>
        </div>
        <button
          className="btn btn-secondary"
          style={{ padding: "0.2rem 0.4rem", fontSize: "0.75rem" }}
          onClick={onClose}
          aria-label="Close Token Inspector"
        >
          <X size={14} aria-hidden="true" />
        </button>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "0.75rem", marginBottom: "0.75rem" }}>
        <div style={{ background: "var(--color-bg)", padding: "0.5rem 0.75rem", borderRadius: "var(--radius-sm)" }}>
          <div style={{ fontSize: "0.75rem", color: "var(--color-text-secondary)" }}>Total Sum Attribution</div>
          <div style={{ fontSize: "1.1rem", fontWeight: 700, fontFamily: "monospace", color: "var(--color-text-primary)" }}>
            {selectedGroup.totalAttribution > 0 ? "+" : ""}{selectedGroup.totalAttribution.toFixed(4)}
          </div>
        </div>
        <div style={{ background: "var(--color-bg)", padding: "0.5rem 0.75rem", borderRadius: "var(--radius-sm)" }}>
          <div style={{ fontSize: "0.75rem", color: "var(--color-text-secondary)" }}>Peak Subtoken Magnitude</div>
          <div style={{ fontSize: "1.1rem", fontWeight: 700, fontFamily: "monospace", color: "var(--color-text-primary)" }}>
            {selectedGroup.maxAttribution > 0 ? "+" : ""}{selectedGroup.maxAttribution.toFixed(4)}
          </div>
        </div>
        <div style={{ background: "var(--color-bg)", padding: "0.5rem 0.75rem", borderRadius: "var(--radius-sm)" }}>
          <div style={{ fontSize: "0.75rem", color: "var(--color-text-secondary)" }}>Underlying Subtokens</div>
          <div style={{ fontSize: "1.1rem", fontWeight: 700, color: "var(--color-text-primary)" }}>
            {selectedGroup.subtokens.length}
          </div>
        </div>
      </div>

      {/* Subtoken breakdown */}
      {selectedGroup.subtokens.length > 1 && (
        <div>
          <div style={{ fontSize: "0.75rem", fontWeight: 600, color: "var(--color-text-secondary)", marginBottom: "0.35rem" }}>
            WordPiece Subtoken Breakdown:
          </div>
          <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
            {selectedGroup.subtokens.map((sub) => (
              <div
                key={`sub_${sub.originalIndex}_${sub.token}`}
                style={{
                  background: "var(--color-bg)",
                  border: "1px solid var(--color-border)",
                  borderRadius: "4px",
                  padding: "0.25rem 0.5rem",
                  fontSize: "0.8rem",
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "0.35rem",
                }}
              >
                <span style={{ fontFamily: "monospace", color: "var(--color-text-primary)" }}>{sub.token}</span>
                <span
                  style={{
                    fontFamily: "monospace",
                    fontSize: "0.75rem",
                    color: sub.attribution > 0 ? "#dc2626" : sub.attribution < 0 ? "#16a34a" : "var(--color-text-secondary)",
                    fontWeight: 600,
                  }}
                >
                  {sub.attribution > 0 ? "+" : ""}{sub.attribution.toFixed(4)}
                </span>
                <span style={{ fontSize: "0.65rem", color: "var(--color-text-secondary)" }}>#{sub.originalIndex}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
