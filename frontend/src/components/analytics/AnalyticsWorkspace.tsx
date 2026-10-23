"use client";

import React, { useState } from "react";
import { DocumentResult } from "./types";
import { AnalyticsSummary } from "./AnalyticsSummary";
import { ClauseScoreDistribution } from "./ClauseScoreDistribution";
import { SeverityDistribution } from "./SeverityDistribution";
import { ChannelEvidenceComparison } from "./ChannelEvidenceComparison";
import { RuleFindingsSummary } from "./RuleFindingsSummary";
import { CalibrationTransparency } from "./CalibrationTransparency";
import { AnalyticsEmptyState } from "./AnalyticsEmptyState";
import { LearnedCompatibilityWorkspace } from "../flow/LearnedCompatibilityWorkspace";
import { BookOpenCheck, ArrowRight, Grid, BarChart3 } from "lucide-react";

interface AnalyticsWorkspaceProps {
  documentResult: DocumentResult | null;
  selectedClauseId: string;
  onSelectClauseId: (clauseId: string) => void;
  onNavigateToReview?: () => void;
  onNavigateToUpload?: () => void;
  onNavigateToXai?: () => void;
  onNavigateToFeedback?: () => void;
}

export function AnalyticsWorkspace({
  documentResult,
  selectedClauseId,
  onSelectClauseId,
  onNavigateToReview,
  onNavigateToUpload,
}: AnalyticsWorkspaceProps) {
  const [activeSubView, setActiveSubView] = useState<"contract" | "flow">("contract");

  if (!documentResult && activeSubView === "contract") {
    return (
      <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
        {/* Sub-view switcher bar allowing access to Pretrained Flow Map even before ingestion */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            flexWrap: "wrap",
            gap: "0.5rem",
            background: "var(--color-surface)",
            padding: "0.75rem 1rem",
            borderRadius: "var(--radius-md)",
            border: "1px solid var(--color-border)",
          }}
        >
          <div style={{ fontSize: "0.85rem", color: "var(--color-text-secondary)" }}>
            Select Analytics Workspace Track:
          </div>
          <div style={{ display: "flex", gap: "0.5rem" }}>
            <button
              id="analytics-subview-contract-btn"
              className="btn btn-primary"
              style={{ padding: "0.35rem 0.75rem", fontSize: "0.85rem", display: "inline-flex", alignItems: "center", gap: "0.4rem" }}
              onClick={() => setActiveSubView("contract")}
            >
              <BarChart3 size={15} /> Contract Findings (Requires Document)
            </button>
            <button
              id="analytics-subview-flow-btn"
              className="btn btn-secondary"
              style={{ padding: "0.35rem 0.75rem", fontSize: "0.85rem", display: "inline-flex", alignItems: "center", gap: "0.4rem" }}
              onClick={() => setActiveSubView("flow")}
            >
              <Grid size={15} /> Learned Clause Compatibility Map (Track A)
            </button>
          </div>
        </div>

        <AnalyticsEmptyState onNavigateToUpload={onNavigateToUpload} />
      </div>
    );
  }

  const clauses = documentResult?.scoring_result?.clauses ?? [];
  const selectedClause = clauses.find((c) => c.clause_id === selectedClauseId) || clauses[0];

  return (
    <div
      className="analytics-workspace-container"
      role="region"
      aria-label="Professional Analytics & Findings Workspace"
      style={{
        display: "flex",
        flexDirection: "column",
        gap: "1.25rem",
        width: "100%",
        paddingBottom: "2.5rem",
      }}
    >
      {/* Workspace Header Strip */}
      <div
        className="card analytics-header-strip"
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexWrap: "wrap",
          gap: "1rem",
          padding: "1rem 1.25rem",
          background: "var(--color-surface)",
          border: "1px solid var(--color-border)",
          borderRadius: "8px",
        }}
      >
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.25rem" }}>
            <span
              style={{
                fontSize: "0.72rem",
                fontWeight: 700,
                letterSpacing: "0.05em",
                textTransform: "uppercase",
                padding: "0.15rem 0.45rem",
                borderRadius: "3px",
                background: "var(--color-accent-subtle, rgba(59, 130, 246, 0.15))",
                color: "var(--color-accent)",
              }}
            >
              Professional Analytics &bull; Phase 4B
            </span>
            <span style={{ fontSize: "0.75rem", color: "var(--color-text-muted)" }}>
              Synchronized with Memory State
            </span>
          </div>
          <h2 style={{ fontSize: "1.2rem", fontWeight: 700, color: "var(--color-text-primary)", margin: 0 }}>
            {activeSubView === "contract"
              ? "Contract Structural Coherence & Statistical Findings"
              : "Pretrained Model Learned Clause-Pair Compatibility Map"}
          </h2>
        </div>

        {/* Sub-view switcher and Review navigation */}
        <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", flexWrap: "wrap" }}>
          <div
            style={{
              display: "flex",
              gap: "0.3rem",
              background: "var(--color-bg)",
              padding: "0.25rem",
              borderRadius: "6px",
              border: "1px solid var(--color-border)",
            }}
          >
            <button
              id="analytics-view-findings-btn"
              type="button"
              className={`btn ${activeSubView === "contract" ? "btn-primary" : "btn-secondary"}`}
              style={{ padding: "0.3rem 0.65rem", fontSize: "0.8rem", display: "inline-flex", alignItems: "center", gap: "0.3rem" }}
              onClick={() => setActiveSubView("contract")}
            >
              <BarChart3 size={14} /> Contract Findings
            </button>
            <button
              id="analytics-view-learned-flow-btn"
              type="button"
              className={`btn ${activeSubView === "flow" ? "btn-primary" : "btn-secondary"}`}
              style={{ padding: "0.3rem 0.65rem", fontSize: "0.8rem", display: "inline-flex", alignItems: "center", gap: "0.3rem" }}
              onClick={() => setActiveSubView("flow")}
            >
              <Grid size={14} /> Compatibility Map (66×66)
            </button>
          </div>

          {onNavigateToReview && (
            <button
              type="button"
              className="btn"
              id="analytics-top-open-review-btn"
              onClick={onNavigateToReview}
              style={{ display: "inline-flex", alignItems: "center", gap: "0.4rem", fontSize: "0.85rem" }}
            >
              <BookOpenCheck size={16} aria-hidden="true" />
              <span>Open Split-Screen Reviewer</span>
              <ArrowRight size={14} aria-hidden="true" />
            </button>
          )}
        </div>
      </div>

      {/* Render Selected Sub-view */}
      {activeSubView === "flow" ? (
        <LearnedCompatibilityWorkspace />
      ) : documentResult ? (
        <>
          {/* 1. Document KPI Summary Cards */}
          <AnalyticsSummary documentResult={documentResult} />

          {/* 2. Interactive Clause Anomaly Score Distribution (Timeline / Sequence) */}
          <ClauseScoreDistribution
            clauses={clauses}
            selectedClauseId={selectedClauseId}
            onSelectClauseId={onSelectClauseId}
            onNavigateToReview={onNavigateToReview}
          />

          {/* 3. Dual-Column Diagnostic Section: Severity Distribution + Channel Evidence */}
          <div
            className="analytics-two-col-grid"
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(360px, 1fr))",
              gap: "1.25rem",
              alignItems: "stretch",
            }}
          >
            <SeverityDistribution
              totalClauses={documentResult.total_clauses}
              highCount={clauses.filter(c => c.severity === "HIGH").length}
              mediumCount={clauses.filter(c => c.severity === "MEDIUM").length}
              lowCount={clauses.filter(c => c.severity === "LOW").length}
            />

            <ChannelEvidenceComparison selectedClause={selectedClause} />
          </div>

          {/* 4. Deterministic Rule Violations Breakdown */}
          <RuleFindingsSummary
            ruleFlags={documentResult.rule_flags ?? []}
            clauses={clauses}
            onSelectClauseId={onSelectClauseId}
            onNavigateToReview={onNavigateToReview}
          />

          {/* 5. Calibration Transparency & Methodological Limitations */}
          <CalibrationTransparency
            scoringResult={documentResult.scoring_result}
            selectedClause={selectedClause}
          />
        </>
      ) : (
        <AnalyticsEmptyState onNavigateToUpload={onNavigateToUpload} />
      )}
    </div>
  );
}
