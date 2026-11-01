"use client";

import React from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { Button } from "../ui/Button";

interface ClauseNavigatorProps {
  currentIndex: number;
  totalClauses: number;
  onPrevious: () => void;
  onNext: () => void;
  hasPrevious: boolean;
  hasNext: boolean;
  currentClauseNumber?: number;
}

export function ClauseNavigator({
  currentIndex,
  totalClauses,
  onPrevious,
  onNext,
  hasPrevious,
  hasNext,
  currentClauseNumber,
}: ClauseNavigatorProps) {
  const displayNum = currentClauseNumber !== undefined ? currentClauseNumber + 1 : currentIndex + 1;

  return (
    <div
      className="clause-navigator"
      role="group"
      aria-label="Clause Sequence Navigation"
      style={{
        display: "flex",
        alignItems: "center",
        gap: "0.5rem",
      }}
    >
      <Button
        id="prev-clause-btn"
        variant="secondary"
        size="sm"
        disabled={!hasPrevious}
        onClick={onPrevious}
        aria-label="Navigate to previous clause"
        style={{ padding: "0.3rem 0.5rem", height: "30px" }}
      >
        <ChevronLeft size={16} aria-hidden="true" />
        <span style={{ fontSize: "0.75rem" }}>Prev</span>
      </Button>

      <span
        title={`Clause ${displayNum}`}
        style={{
          fontSize: "0.78rem",
          fontWeight: 600,
          color: "var(--color-text-secondary)",
          padding: "0 0.35rem",
          whiteSpace: "nowrap",
          fontFamily: "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace",
        }}
      >
        {currentIndex + 1}/{totalClauses}
      </span>

      <Button
        id="next-clause-btn"
        variant="secondary"
        size="sm"
        disabled={!hasNext}
        onClick={onNext}
        aria-label="Navigate to next clause"
        style={{ padding: "0.3rem 0.5rem", height: "30px" }}
      >
        <span style={{ fontSize: "0.75rem" }}>Next</span>
        <ChevronRight size={16} aria-hidden="true" />
      </Button>
    </div>
  );
}
