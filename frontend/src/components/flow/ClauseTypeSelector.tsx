"use client";

import React from "react";
import { ClauseTypeItem } from "./types";
import { Search, Filter } from "lucide-react";

interface ClauseTypeSelectorProps {
  clauseTypes: ClauseTypeItem[];
  searchQuery: string;
  onSearchChange: (q: string) => void;
  presetFilter: "all" | "core" | "boilerplate";
  onPresetChange: (preset: "all" | "core" | "boilerplate") => void;
  selectedIndicesCount: number;
}

export function ClauseTypeSelector({
  clauseTypes,
  searchQuery,
  onSearchChange,
  presetFilter,
  onPresetChange,
  selectedIndicesCount,
}: ClauseTypeSelectorProps) {
  return (
    <div
      style={{
        background: "var(--color-surface)",
        border: "1px solid var(--color-border)",
        borderRadius: "var(--radius-md)",
        padding: "0.75rem 1rem",
        marginBottom: "1rem",
        display: "flex",
        flexWrap: "wrap",
        alignItems: "center",
        justifyContent: "space-between",
        gap: "1rem",
      }}
    >
      {/* Search Input */}
      <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", flex: "1", minWidth: "240px", maxWidth: "400px" }}>
        <Search size={16} style={{ color: "var(--color-text-secondary)" }} aria-hidden="true" />
        <input
          id="flow-search-input"
          type="text"
          className="input-field"
          style={{ padding: "0.35rem 0.6rem", fontSize: "0.85rem", width: "100%" }}
          placeholder="Search legal clause categories (e.g. Indemnity, Term, Notices)..."
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
        />
        {searchQuery && (
          <button
            className="btn btn-secondary"
            style={{ padding: "0.25rem 0.5rem", fontSize: "0.75rem" }}
            onClick={() => onSearchChange("")}
            title="Clear search"
          >
            Clear
          </button>
        )}
      </div>

      {/* Preset Filters */}
      <div style={{ display: "flex", alignItems: "center", gap: "0.4rem", flexWrap: "wrap" }}>
        <span style={{ fontSize: "0.8rem", color: "var(--color-text-secondary)", marginRight: "0.25rem" }}>
          <Filter size={14} style={{ display: "inline", verticalAlign: "middle", marginRight: "0.2rem" }} />
          View Presets:
        </span>
        <button
          id="flow-preset-all-btn"
          className={`btn ${presetFilter === "all" ? "btn-primary" : "btn-secondary"}`}
          style={{ padding: "0.3rem 0.6rem", fontSize: "0.8rem" }}
          onClick={() => onPresetChange("all")}
        >
          Full Matrix (66 × 66)
        </button>
        <button
          id="flow-preset-core-btn"
          className={`btn ${presetFilter === "core" ? "btn-primary" : "btn-secondary"}`}
          style={{ padding: "0.3rem 0.6rem", fontSize: "0.8rem" }}
          onClick={() => onPresetChange("core")}
        >
          Core Commercial (12)
        </button>
        <button
          id="flow-preset-boilerplate-btn"
          className={`btn ${presetFilter === "boilerplate" ? "btn-primary" : "btn-secondary"}`}
          style={{ padding: "0.3rem 0.6rem", fontSize: "0.8rem" }}
          onClick={() => onPresetChange("boilerplate")}
        >
          Boilerplate (10)
        </button>
      </div>

      <div style={{ fontSize: "0.8rem", color: "var(--color-text-secondary)", whiteSpace: "nowrap" }}>
        Displaying: <strong>{selectedIndicesCount}</strong> of <strong>{clauseTypes.length}</strong> categories ({selectedIndicesCount * selectedIndicesCount} cells)
      </div>
    </div>
  );
}
