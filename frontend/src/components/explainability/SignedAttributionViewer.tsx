"use client";

import React, { useState, useMemo } from "react";
import { groupWordPieceTokens, WordGroup } from "./wordpieceGrouping";
import { Layers, AlignLeft } from "lucide-react";

interface SignedAttributionViewerProps {
  tokens: string[];
  attributions: number[];
  targetScore: number;
  baselineScore: number;
  selectedTokenGroup: WordGroup | null;
  onSelectTokenGroup: (group: WordGroup | null) => void;
}

export function SignedAttributionViewer({
  tokens,
  attributions,
  targetScore,
  baselineScore,
  selectedTokenGroup,
  onSelectTokenGroup,
}: SignedAttributionViewerProps) {
  const [viewMode, setViewMode] = useState<"grouped" | "raw">("grouped");

  // Compute grouped words memoized
  const wordGroups = useMemo(() => {
    return groupWordPieceTokens(tokens, attributions);
  }, [tokens, attributions]);

  // Compute maximum absolute magnitude across tokens for normalized color intensity
  const maxAbsScore = useMemo(() => {
    if (!attributions || attributions.length === 0) return 1.0;
    const maxVal = Math.max(...attributions.map((a) => Math.abs(a)));
    return maxVal > 0 ? maxVal : 1.0;
  }, [attributions]);

  const getTokenStyle = (score: number) => {
    const intensity = Math.min(1.0, Math.abs(score) / maxAbsScore);
    const alpha = (0.12 + intensity * 0.45).toFixed(2);

    if (score > 0.0005) {
      // Positive: drives OOD anomaly distance
      return {
        background: `rgba(220, 38, 38, ${alpha})`,
        border: "1px solid rgba(220, 38, 38, 0.45)",
        color: "var(--color-text-primary)",
      };
    } else if (score < -0.0005) {
      // Negative: pulls toward canonical cluster (anchor)
      return {
        background: `rgba(22, 163, 74, ${alpha})`,
        border: "1px solid rgba(22, 163, 74, 0.45)",
        color: "var(--color-text-primary)",
      };
    } else {
      return {
        background: "var(--color-bg)",
        border: "1px solid var(--color-border)",
        color: "var(--color-text-secondary)",
      };
    }
  };

  return (
    <div
      style={{
        background: "var(--color-surface)",
        border: "1px solid var(--color-border)",
        borderRadius: "var(--radius-md)",
        padding: "1.25rem",
        marginBottom: "1rem",
      }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexWrap: "wrap",
          gap: "1rem",
          marginBottom: "1rem",
          borderBottom: "1px solid var(--color-border)",
          paddingBottom: "0.75rem",
        }}
      >
        <div>
          <h3 style={{ fontSize: "1rem", fontWeight: 600, margin: "0 0 0.25rem 0", color: "var(--color-text-primary)" }}>
            Token-Level Integrated Gradients Feature Attribution
          </h3>
          <p style={{ fontSize: "0.8rem", color: "var(--color-text-secondary)", margin: 0 }}>
            Baseline Distance: <strong>{baselineScore.toFixed(4)}</strong> → Target Distance:{" "}
            <strong>{targetScore.toFixed(4)}</strong> (Δ = {(targetScore - baselineScore).toFixed(4)})
          </p>
        </div>

        {/* View mode toggle */}
        <div style={{ display: "flex", gap: "0.25rem", background: "var(--color-bg)", padding: "0.2rem", borderRadius: "var(--radius-sm)" }}>
          <button
            id="xai-toggle-grouped-btn"
            className={`btn ${viewMode === "grouped" ? "btn-primary" : "btn-secondary"}`}
            style={{ padding: "0.25rem 0.6rem", fontSize: "0.8rem", display: "inline-flex", alignItems: "center", gap: "0.3rem" }}
            onClick={() => setViewMode("grouped")}
          >
            <Layers size={13} aria-hidden="true" />
            <span>Grouped Words ({wordGroups.length})</span>
          </button>
          <button
            id="xai-toggle-raw-btn"
            className={`btn ${viewMode === "raw" ? "btn-primary" : "btn-secondary"}`}
            style={{ padding: "0.25rem 0.6rem", fontSize: "0.8rem", display: "inline-flex", alignItems: "center", gap: "0.3rem" }}
            onClick={() => setViewMode("raw")}
          >
            <AlignLeft size={13} aria-hidden="true" />
            <span>Subtokens ({tokens.length})</span>
          </button>
        </div>
      </div>

      {/* Attribution Tokens Container */}
      <div
        id="xai-attribution-tokens-container"
        style={{
          lineHeight: "2.2",
          display: "flex",
          flexWrap: "wrap",
          gap: "0.35rem",
          padding: "1rem",
          background: "var(--color-bg)",
          borderRadius: "var(--radius-sm)",
          minHeight: "120px",
          maxHeight: "350px",
          overflowY: "auto",
        }}
      >
        {viewMode === "grouped"
          ? wordGroups.map((group) => {
              const style = getTokenStyle(group.totalAttribution);
              const isSelected = selectedTokenGroup?.id === group.id;

              return (
                <button
                  key={group.id}
                  className="xai-token-btn"
                  style={{
                    ...style,
                    cursor: "pointer",
                    borderRadius: "4px",
                    padding: "0.15rem 0.45rem",
                    fontSize: "0.85rem",
                    fontFamily: group.isSpecialToken ? "monospace" : "inherit",
                    fontWeight: isSelected ? 700 : 400,
                    outline: isSelected ? "2px solid var(--color-accent)" : "none",
                    boxShadow: isSelected ? "0 0 8px rgba(37, 99, 235, 0.4)" : "none",
                    display: "inline-flex",
                    alignItems: "center",
                    gap: "0.25rem",
                  }}
                  onClick={() => onSelectTokenGroup(isSelected ? null : group)}
                  title={`${group.word}: Attribution = ${group.totalAttribution > 0 ? "+" : ""}${group.totalAttribution} (${group.subtokens.length} subtoken${group.subtokens.length > 1 ? "s" : ""})`}
                >
                  <span>{group.word}</span>
                  {group.subtokens.length > 1 && (
                    <span
                      style={{
                        fontSize: "0.65rem",
                        padding: "0.05rem 0.25rem",
                        borderRadius: "3px",
                        background: "rgba(0,0,0,0.15)",
                        opacity: 0.8,
                      }}
                    >
                      {group.subtokens.length}
                    </span>
                  )}
                </button>
              );
            })
          : tokens.map((token, idx) => {
              const score = attributions[idx] ?? 0;
              const style = getTokenStyle(score);
              const isContinuation = token.startsWith("##");

              return (
                <button
                  key={`raw_token_${idx}_${token}`}
                  className="xai-raw-token-btn"
                  style={{
                    ...style,
                    cursor: "pointer",
                    borderRadius: "4px",
                    padding: "0.15rem 0.4rem",
                    fontSize: "0.8rem",
                    fontFamily: "monospace",
                    opacity: isContinuation ? 0.9 : 1,
                  }}
                  onClick={() => {
                    // Find group containing this token
                    const parent = wordGroups.find((g) => g.subtokens.some((s) => s.originalIndex === idx));
                    if (parent) onSelectTokenGroup(parent);
                  }}
                  title={`[${idx}] ${token}: ${score > 0 ? "+" : ""}${score.toFixed(4)}`}
                >
                  {token}
                </button>
              );
            })}
      </div>
    </div>
  );
}
