"use client";

import React, { useMemo, useState } from "react";
import { ClauseTypeItem, SelectedCell } from "./types";

interface CompatibilityHeatmapProps {
  clauseTypes: ClauseTypeItem[];
  matrix: number[][];
  selectedIndices: number[];
  selectedCell: SelectedCell | null;
  onSelectCell: (cell: SelectedCell) => void;
  minScore: number;
  maxScore: number;
}

/**
 * Interpolates color along a 4-stop scientific heatmap gradient:
 * 0.0: #991b1b (red) -> 0.33: #d97706 (amber) -> 0.67: #15803d (green) -> 1.0: #2563eb (blue)
 */
function interpolateColor(val: number, min: number, max: number): string {
  const t = Math.max(0, Math.min(1, (val - min) / (max - min || 1)));

  let r: number, g: number, b: number;
  if (t < 0.33) {
    const s = t / 0.33;
    r = Math.round(153 + (217 - 153) * s);
    g = Math.round(27 + (119 - 27) * s);
    b = Math.round(27 + (6 - 27) * s);
  } else if (t < 0.67) {
    const s = (t - 0.33) / 0.34;
    r = Math.round(217 + (21 - 217) * s);
    g = Math.round(119 + (128 - 119) * s);
    b = Math.round(6 + (61 - 6) * s);
  } else {
    const s = (t - 0.67) / 0.33;
    r = Math.round(21 + (37 - 21) * s);
    g = Math.round(128 + (99 - 128) * s);
    b = Math.round(61 + (235 - 61) * s);
  }

  return `rgb(${r}, ${g}, ${b})`;
}

export function CompatibilityHeatmap({
  clauseTypes,
  matrix,
  selectedIndices,
  selectedCell,
  onSelectCell,
  minScore,
  maxScore,
}: CompatibilityHeatmapProps) {
  const [hoveredCell, setHoveredCell] = useState<{ rowIdx: number; colIdx: number; score: number } | null>(null);
  const [showTableView, setShowTableView] = useState(false);

  // Filtered clause items in order
  const displayItems = useMemo(() => {
    return selectedIndices.map((idx) => clauseTypes[idx]).filter(Boolean);
  }, [selectedIndices, clauseTypes]);

  const numItems = displayItems.length;
  // If fewer items, cells can be larger and display numbers; if 66 items, compact cells
  const cellSize = numItems <= 15 ? 44 : numItems <= 30 ? 28 : 18;
  const showTextInside = numItems <= 15;

  const handleCellClick = (antecedentIdx: number, successorIdx: number) => {
    const score = matrix[antecedentIdx]?.[successorIdx] ?? 0;
    const reverseScore = matrix[successorIdx]?.[antecedentIdx] ?? 0;
    const antecedentName = clauseTypes[antecedentIdx]?.name || `Type ${antecedentIdx}`;
    const successorName = clauseTypes[successorIdx]?.name || `Type ${successorIdx}`;

    onSelectCell({
      antecedentIndex: antecedentIdx,
      successorIndex: successorIdx,
      antecedentName,
      successorName,
      score,
      reverseScore,
    });
  };

  return (
    <div
      style={{
        background: "var(--color-surface)",
        border: "1px solid var(--color-border)",
        borderRadius: "var(--radius-md)",
        padding: "1rem",
        marginBottom: "1rem",
      }}
    >
      {/* Controls row */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.75rem", flexWrap: "wrap", gap: "0.5rem" }}>
        <div style={{ fontSize: "0.85rem", color: "var(--color-text-secondary)" }}>
          <span style={{ fontWeight: 600, color: "var(--color-text-primary)" }}>Axes:</span> Vertical = Antecedent Clause (c_i) | Horizontal = Successor Clause (c_j)
        </div>
        <button
          className="btn btn-secondary"
          style={{ padding: "0.25rem 0.6rem", fontSize: "0.75rem" }}
          onClick={() => setShowTableView(!showTableView)}
        >
          {showTableView ? "Switch to Interactive Heatmap" : "Switch to Accessible Table View"}
        </button>
      </div>

      {hoveredCell && (
        <div
          style={{
            background: "var(--color-bg)",
            border: "1px solid var(--color-border)",
            borderRadius: "4px",
            padding: "0.3rem 0.6rem",
            marginBottom: "0.5rem",
            fontSize: "0.75rem",
            display: "flex",
            gap: "0.75rem",
            alignItems: "center",
          }}
        >
          <span>
            <strong>Antecedent:</strong> {clauseTypes[hoveredCell.rowIdx]?.name} [{hoveredCell.rowIdx}]
          </span>
          <span>→</span>
          <span>
            <strong>Successor:</strong> {clauseTypes[hoveredCell.colIdx]?.name} [{hoveredCell.colIdx}]
          </span>
          <span>
            <strong>Score:</strong> {hoveredCell.score.toFixed(6)}
          </span>
        </div>
      )}

      {showTableView ? (
        /* Accessible Table View */
        <div style={{ maxHeight: "500px", overflow: "auto", border: "1px solid var(--color-border)", borderRadius: "var(--radius-sm)" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.75rem" }}>
            <thead style={{ position: "sticky", top: 0, background: "var(--color-surface)", zIndex: 2 }}>
              <tr>
                <th style={{ padding: "0.5rem", borderBottom: "1px solid var(--color-border)", textAlign: "left" }}>Antecedent (c_i)</th>
                <th style={{ padding: "0.5rem", borderBottom: "1px solid var(--color-border)", textAlign: "left" }}>Successor (c_j)</th>
                <th style={{ padding: "0.5rem", borderBottom: "1px solid var(--color-border)", textAlign: "right" }}>Compatibility P(c_i → c_j)</th>
                <th style={{ padding: "0.5rem", borderBottom: "1px solid var(--color-border)", textAlign: "right" }}>Reverse P(c_j → c_i)</th>
                <th style={{ padding: "0.5rem", borderBottom: "1px solid var(--color-border)", textAlign: "right" }}>Asymmetry Δ</th>
              </tr>
            </thead>
            <tbody>
              {displayItems.flatMap((rowItem) =>
                displayItems.map((colItem) => {
                  const rIdx = rowItem.matrix_index;
                  const cIdx = colItem.matrix_index;
                  const fwd = matrix[rIdx]?.[cIdx] ?? 0;
                  const rev = matrix[cIdx]?.[rIdx] ?? 0;
                  const asym = fwd - rev;
                  const isSelected = selectedCell?.antecedentIndex === rIdx && selectedCell?.successorIndex === cIdx;
                  return (
                    <tr
                      key={`${rIdx}-${cIdx}`}
                      onClick={() => handleCellClick(rIdx, cIdx)}
                      style={{
                        background: isSelected ? "var(--color-surface-selected, rgba(37, 99, 235, 0.12))" : "transparent",
                        cursor: "pointer",
                      }}
                    >
                      <td style={{ padding: "0.4rem 0.5rem", borderBottom: "1px solid var(--color-border)" }}>{rowItem.name}</td>
                      <td style={{ padding: "0.4rem 0.5rem", borderBottom: "1px solid var(--color-border)" }}>{colItem.name}</td>
                      <td style={{ padding: "0.4rem 0.5rem", borderBottom: "1px solid var(--color-border)", textAlign: "right", fontWeight: 600 }}>{fwd.toFixed(4)}</td>
                      <td style={{ padding: "0.4rem 0.5rem", borderBottom: "1px solid var(--color-border)", textAlign: "right" }}>{rev.toFixed(4)}</td>
                      <td style={{ padding: "0.4rem 0.5rem", borderBottom: "1px solid var(--color-border)", textAlign: "right", color: asym > 0 ? "var(--color-accent)" : "inherit" }}>
                        {asym >= 0 ? `+${asym.toFixed(4)}` : asym.toFixed(4)}
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      ) : (
        /* Heatmap Grid View */
        <div
          id="flow-heatmap-container"
          style={{
            overflow: "auto",
            maxHeight: "650px",
            border: "1px solid var(--color-border)",
            borderRadius: "var(--radius-sm)",
            padding: "0.5rem",
          }}
        >
          <div
            style={{
              display: "inline-block",
              minWidth: "fit-content",
            }}
            role="grid"
            aria-label="Learned Clause-Pair Compatibility Heatmap"
          >
            {/* Top Column Labels */}
            <div style={{ display: "flex", marginLeft: "140px", marginBottom: "4px" }}>
              {displayItems.map((colItem) => (
                <div
                  key={`col-hdr-${colItem.matrix_index}`}
                  style={{
                    width: `${cellSize}px`,
                    minWidth: `${cellSize}px`,
                    height: "100px",
                    display: "flex",
                    alignItems: "flex-end",
                    justifyContent: "center",
                    paddingBottom: "4px",
                  }}
                  title={colItem.name}
                >
                  <span
                    style={{
                      writingMode: "vertical-rl",
                      transform: "rotate(180deg)",
                      fontSize: "0.65rem",
                      color: "var(--color-text-secondary)",
                      whiteSpace: "nowrap",
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                      maxHeight: "95px",
                      textAlign: "left",
                    }}
                  >
                    {colItem.name}
                  </span>
                </div>
              ))}
            </div>

            {/* Rows */}
            {displayItems.map((rowItem) => {
              const rIdx = rowItem.matrix_index;
              return (
                <div key={`row-${rIdx}`} style={{ display: "flex", alignItems: "center", marginBottom: "1px" }}>
                  {/* Row Header Label */}
                  <div
                    style={{
                      width: "140px",
                      minWidth: "140px",
                      paddingRight: "8px",
                      textAlign: "right",
                      fontSize: "0.7rem",
                      color: "var(--color-text-secondary)",
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                      whiteSpace: "nowrap",
                    }}
                    title={rowItem.name}
                  >
                    {rowItem.name}
                  </div>

                  {/* Grid Cells */}
                  <div style={{ display: "flex", gap: "1px" }}>
                    {displayItems.map((colItem) => {
                      const cIdx = colItem.matrix_index;
                      const score = matrix[rIdx]?.[cIdx] ?? 0;
                      const bgColor = interpolateColor(score, minScore, maxScore);
                      const isSelected = selectedCell?.antecedentIndex === rIdx && selectedCell?.successorIndex === cIdx;
                      const isDiagonal = rIdx === cIdx;

                      return (
                        <div
                          key={`cell-${rIdx}-${cIdx}`}
                          role="gridcell"
                          tabIndex={0}
                          aria-label={`Antecedent: ${rowItem.name}, Successor: ${colItem.name}, Score: ${score.toFixed(4)}`}
                          onClick={() => handleCellClick(rIdx, cIdx)}
                          onKeyDown={(e) => {
                            if (e.key === "Enter" || e.key === " ") {
                              e.preventDefault();
                              handleCellClick(rIdx, cIdx);
                            }
                          }}
                          onMouseEnter={() => setHoveredCell({ rowIdx: rIdx, colIdx: cIdx, score })}
                          onMouseLeave={() => setHoveredCell(null)}
                          style={{
                            width: `${cellSize}px`,
                            height: `${cellSize}px`,
                            backgroundColor: bgColor,
                            borderRadius: "2px",
                            cursor: "pointer",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            color: "#ffffff",
                            fontSize: "0.65rem",
                            fontWeight: 600,
                            border: isSelected
                              ? "2px solid #ffffff"
                              : isDiagonal
                              ? "1px dashed rgba(255,255,255,0.4)"
                              : "none",
                            boxShadow: isSelected ? "0 0 0 2px var(--color-accent, #2563eb)" : "none",
                            transition: "transform 0.1s ease",
                            userSelect: "none",
                          }}
                          title={`Antecedent: ${rowItem.name}\nSuccessor: ${colItem.name}\nP(A → B): ${score.toFixed(6)}`}
                        >
                          {showTextInside && score.toFixed(2)}
                        </div>
                      );
                    })}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
