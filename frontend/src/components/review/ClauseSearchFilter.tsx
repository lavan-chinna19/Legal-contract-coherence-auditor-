"use client";

import React from "react";
import { Search, X, Filter } from "lucide-react";
import { SeverityFilter } from "./types";

interface ClauseSearchFilterProps {
  searchQuery: string;
  onSearchChange: (q: string) => void;
  severityFilter: SeverityFilter;
  onSeverityFilterChange: (f: SeverityFilter) => void;
  visibleCount: number;
  totalCount: number;
  onClearFilters: () => void;
}

export function ClauseSearchFilter({
  searchQuery,
  onSearchChange,
  severityFilter,
  onSeverityFilterChange,
  visibleCount,
  totalCount,
  onClearFilters,
}: ClauseSearchFilterProps) {
  const isFiltered = searchQuery.trim().length > 0 || severityFilter !== "ALL";

  return (
    <div
      className="clause-search-filter"
      role="search"
      aria-label="Clause Text Search and Severity Filter"
      style={{
        padding: "0.75rem 1rem",
        background: "var(--color-surface)",
        borderBottom: "1px solid var(--color-border)",
        display: "flex",
        flexDirection: "column",
        gap: "0.6rem",
      }}
    >
      <div style={{ display: "flex", gap: "0.5rem", alignItems: "center" }}>
        <div style={{ position: "relative", flexGrow: 1 }}>
          <label htmlFor="clause-search-input" className="sr-only" style={{ display: "none" }}>
            Search clause text
          </label>
          <Search
            size={15}
            style={{
              position: "absolute",
              left: "10px",
              top: "50%",
              transform: "translateY(-50%)",
              color: "var(--color-text-muted)",
              pointerEvents: "none",
            }}
            aria-hidden="true"
          />
          <input
            id="clause-search-input"
            type="text"
            placeholder="Search clause text..."
            aria-label="Search clause text"
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            className="input-field"
            style={{
              paddingLeft: "2rem",
              paddingRight: searchQuery ? "2rem" : "0.75rem",
              paddingTop: "0.45rem",
              paddingBottom: "0.45rem",
              fontSize: "0.85rem",
              height: "36px",
            }}
          />
          {searchQuery && (
            <button
              type="button"
              aria-label="Clear search input"
              onClick={() => onSearchChange("")}
              style={{
                position: "absolute",
                right: "8px",
                top: "50%",
                transform: "translateY(-50%)",
                background: "transparent",
                border: "none",
                cursor: "pointer",
                color: "var(--color-text-muted)",
                display: "flex",
                alignItems: "center",
                padding: "2px",
              }}
            >
              <X size={14} />
            </button>
          )}
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "0.35rem" }}>
          <Filter size={14} style={{ color: "var(--color-text-muted)" }} aria-hidden="true" />
          <label htmlFor="severity-filter-select" className="sr-only" style={{ display: "none" }}>
            Filter by severity
          </label>
          <select
            id="severity-filter-select"
            aria-label="Filter clauses by severity"
            value={severityFilter}
            onChange={(e) => onSeverityFilterChange(e.target.value as SeverityFilter)}
            className="input-field"
            style={{
              padding: "0.45rem 0.6rem",
              fontSize: "0.8rem",
              height: "36px",
              width: "auto",
              minWidth: "125px",
            }}
          >
            <option value="ALL">All Clauses</option>
            <option value="FLAGGED">All Anomalies</option>
            <option value="HIGH">High Severity</option>
            <option value="MEDIUM">Medium Severity</option>
            <option value="LOW">Low Severity</option>
            <option value="CLEAN">Clean / Normal</option>
          </select>
        </div>
      </div>

      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          fontSize: "0.75rem",
          color: "var(--color-text-secondary)",
        }}
      >
        <span>
          Showing <strong>{visibleCount}</strong> of <strong>{totalCount}</strong> clauses
          {isFiltered && <span style={{ marginLeft: "0.25rem", color: "var(--color-accent)" }}>(filtered)</span>}
        </span>

        {isFiltered && (
          <button
            type="button"
            id="clear-filters-btn"
            onClick={onClearFilters}
            style={{
              background: "transparent",
              border: "none",
              color: "var(--color-accent)",
              cursor: "pointer",
              fontSize: "0.75rem",
              fontWeight: 600,
              textDecoration: "underline",
              padding: "0",
            }}
          >
            Clear Filters
          </button>
        )}
      </div>
    </div>
  );
}
