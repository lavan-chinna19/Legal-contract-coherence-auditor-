"use client";

import React from "react";
import { FileQuestion, SearchX, ArrowRight, RotateCcw } from "lucide-react";
import { Button } from "../ui/Button";

interface ReviewEmptyStateProps {
  type?: "no-document" | "no-search-results";
  title?: string;
  description?: string;
  onAction?: () => void;
  actionText?: string;
}

export function ReviewEmptyState({
  type = "no-document",
  title,
  description,
  onAction,
  actionText,
}: ReviewEmptyStateProps) {
  if (type === "no-search-results") {
    return (
      <div className="empty-state search-empty-state" role="region" aria-label="No search results">
        <div className="empty-state-icon" aria-hidden="true" style={{ color: "var(--color-text-muted)" }}>
          <SearchX size={44} />
        </div>
        <h3 className="empty-state-title">{title || "No Matching Clauses Found"}</h3>
        <p className="empty-state-description">
          {description || "No clauses match your current query or severity filter criteria. Try adjusting or clearing your filters."}
        </p>
        {onAction && (
          <Button variant="secondary" size="sm" onClick={onAction} icon={<RotateCcw size={14} />}>
            {actionText || "Reset Search & Filters"}
          </Button>
        )}
      </div>
    );
  }

  return (
    <div className="empty-state" role="region" aria-label="Review workspace empty state">
      <div className="empty-state-icon" aria-hidden="true" style={{ color: "var(--color-text-muted)" }}>
        <FileQuestion size={48} />
      </div>
      <h3 className="empty-state-title">{title || "No Active Contract in Review"}</h3>
      <p className="empty-state-description">
        {description || "Please ingest and analyze a contract document in Overview to inspect sequence coherence, clause anomalies, and diagnostic findings."}
      </p>
      {onAction && (
        <Button variant="primary" size="md" onClick={onAction} icon={<ArrowRight size={16} />}>
          {actionText || "Go to Ingestion & Upload"}
        </Button>
      )}
    </div>
  );
}
