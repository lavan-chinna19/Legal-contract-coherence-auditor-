"use client";

import React, { useEffect, useRef } from "react";
import { EnrichedClause, SeverityFilter } from "./types";
import { ClauseCard } from "./ClauseCard";
import { ClauseSearchFilter } from "./ClauseSearchFilter";
import { ReviewEmptyState } from "./ReviewEmptyState";
import { FileText } from "lucide-react";

interface ClauseDocumentViewerProps {
  clauses: EnrichedClause[];
  filteredClauses: EnrichedClause[];
  selectedClauseId: string | null;
  onSelectClause: (clauseId: string) => void;
  docId: string;
  searchQuery: string;
  onSearchChange: (q: string) => void;
  severityFilter: SeverityFilter;
  onSeverityFilterChange: (f: SeverityFilter) => void;
  onClearFilters: () => void;
}

export function ClauseDocumentViewer({
  clauses,
  filteredClauses,
  selectedClauseId,
  onSelectClause,
  docId,
  searchQuery,
  onSearchChange,
  severityFilter,
  onSeverityFilterChange,
  onClearFilters,
}: ClauseDocumentViewerProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const isAutoScrollingRef = useRef(false);

  // Auto-scroll selected clause card into view smoothly
  useEffect(() => {
    if (!selectedClauseId || !containerRef.current) return;

    const selectedCard = containerRef.current.querySelector(`#clause-card-${selectedClauseId}`);
    if (selectedCard) {
      isAutoScrollingRef.current = true;
      selectedCard.scrollIntoView({
        behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth",
        block: "nearest",
      });
      const timer = setTimeout(() => {
        isAutoScrollingRef.current = false;
      }, 400);
      return () => clearTimeout(timer);
    }
  }, [selectedClauseId]);

  return (
    <div
      className="clause-document-viewer"
      role="region"
      aria-label="Contract Document Viewer"
      style={{
        display: "flex",
        flexDirection: "column",
        height: "100%",
        background: "var(--color-surface)",
        borderRadius: "8px",
        border: "1px solid var(--color-border)",
        overflow: "hidden",
      }}
    >
      {/* Document Header Bar */}
      <div
        style={{
          padding: "0.85rem 1rem",
          borderBottom: "1px solid var(--color-border)",
          background: "var(--color-surface-raised)",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexWrap: "wrap",
          gap: "0.5rem",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", flexWrap: "wrap", minWidth: 0, maxWidth: "100%" }}>
          <FileText size={16} style={{ color: "var(--color-accent)" }} aria-hidden="true" />
          <h3 style={{ fontSize: "0.95rem", fontWeight: 700, color: "var(--color-text-primary)", margin: 0 }}>
            Contract Document
          </h3>
          <details className="source-details"><summary>Document details</summary><code>{docId}</code></details>
        </div>

        <div style={{ fontSize: "0.75rem", color: "var(--color-text-muted)" }}>
          {clauses.length} clauses
        </div>
      </div>

      {/* Search & Filter Toolbar */}
      <ClauseSearchFilter
        searchQuery={searchQuery}
        onSearchChange={onSearchChange}
        severityFilter={severityFilter}
        onSeverityFilterChange={onSeverityFilterChange}
        visibleCount={filteredClauses.length}
        totalCount={clauses.length}
        onClearFilters={onClearFilters}
      />

      {/* Clause Cards Scrollable List */}
      <div
        ref={containerRef}
        id="clause-list-scroll-container"
        style={{
          padding: "1rem",
          overflowY: "auto",
          flexGrow: 1,
        }}
      >
        {filteredClauses.length === 0 ? (
          <ReviewEmptyState
            type="no-search-results"
            onAction={onClearFilters}
          />
        ) : (
          filteredClauses.map((clause) => (
            <ClauseCard
              key={clause.clause_id}
              clause={clause}
              isSelected={clause.clause_id === selectedClauseId}
              onSelect={onSelectClause}
            />
          ))
        )}
      </div>
    </div>
  );
}
