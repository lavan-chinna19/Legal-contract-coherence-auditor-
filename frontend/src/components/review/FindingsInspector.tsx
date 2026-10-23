"use client";

import React, { useState } from "react";
import { EnrichedClause, RuleFlag } from "./types";
import { ScoreEvidencePanel } from "./ScoreEvidencePanel";
import { RuleFindingsPanel } from "./RuleFindingsPanel";
import { ClauseNavigator } from "./ClauseNavigator";
import { Button } from "../ui/Button";
import { Badge } from "../ui/Badge";
import { BrainCircuit, MessageSquareCheck, BarChart2, ShieldAlert, ArrowRightLeft } from "lucide-react";

interface FindingsInspectorProps {
  selectedClause: EnrichedClause | null;
  currentIndex: number;
  totalClauses: number;
  onPrevious: () => void;
  onNext: () => void;
  hasPrevious: boolean;
  hasNext: boolean;
  documentRules: RuleFlag[];
  onNavigateToXai?: () => void;
  onNavigateToFeedback?: () => void;
  onExploreRepositioning?: () => void;
}

export function FindingsInspector({
  selectedClause,
  currentIndex,
  totalClauses,
  onPrevious,
  onNext,
  hasPrevious,
  hasNext,
  documentRules,
  onNavigateToXai,
  onNavigateToFeedback,
  onExploreRepositioning,
}: FindingsInspectorProps) {
  const [activeInspectorTab, setActiveInspectorTab] = useState<"scores" | "rules">("scores");

  if (!selectedClause) {
    return (
      <div
        className="findings-inspector"
        role="region"
        aria-label="Audit Findings Inspector"
        style={{
          padding: "2rem",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          height: "100%",
          color: "var(--color-text-muted)",
          textAlign: "center",
        }}
      >
        <p>Select a clause in the document viewer to inspect findings and evidence.</p>
      </div>
    );
  }

  const clauseRules = selectedClause.associated_rules || [];
  const severityVariant =
    selectedClause.severity === "HIGH"
      ? "high"
      : selectedClause.severity === "MEDIUM"
      ? "medium"
      : selectedClause.severity === "LOW"
      ? "low"
      : "clean";

  return (
    <div
      className="findings-inspector"
      role="region"
      aria-label={`Audit Findings for Clause § ${selectedClause.sequence_idx}`}
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
      {/* Inspector Header */}
      <div
        style={{
          padding: "1rem 1.25rem",
          borderBottom: "1px solid var(--color-border)",
          background: "var(--color-surface-raised)",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexWrap: "wrap",
          gap: "0.75rem",
        }}
      >
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <h3 style={{ fontSize: "1.05rem", fontWeight: 700, color: "var(--color-text-primary)", margin: 0 }}>
              Clause § {selectedClause.sequence_idx}
            </h3>
            <Badge variant={severityVariant} className="inspector-severity-badge" />
          </div>
          <div
            style={{
              fontSize: "0.72rem",
              color: "var(--color-text-muted)",
              marginTop: "0.2rem",
              fontFamily: "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace",
            }}
          >
            ID: {selectedClause.clause_id}
          </div>
        </div>

        {/* Clause Previous/Next Navigator */}
        <ClauseNavigator
          currentIndex={currentIndex}
          totalClauses={totalClauses}
          onPrevious={onPrevious}
          onNext={onNext}
          hasPrevious={hasPrevious}
          hasNext={hasNext}
          currentClauseNumber={selectedClause.sequence_idx}
        />
      </div>

      {/* Selected Clause Evidence Excerpt */}
      <div
        className="inspector-evidence-excerpt"
        style={{
          padding: "0.75rem 1.25rem",
          borderBottom: "1px solid var(--color-border)",
          background: "var(--color-surface)",
          fontSize: "0.82rem",
          lineHeight: 1.5,
          color: "var(--color-text-primary)",
          maxHeight: "130px",
          overflowY: "auto",
        }}
      >
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginBottom: "0.35rem",
            fontSize: "0.7rem",
            color: "var(--color-text-muted)",
          }}
        >
          <span style={{ fontWeight: 600 }}>EVIDENCE EXCERPT</span>
          <span
            style={{
              padding: "0.1rem 0.35rem",
              borderRadius: "3px",
              background:
                selectedClause.alignment_status === "VERIFIED_FULL_TEXT"
                  ? "rgba(16, 185, 129, 0.1)"
                  : selectedClause.alignment_status === "PREVIEW_ONLY_AMBIGUOUS"
                  ? "rgba(245, 158, 11, 0.1)"
                  : "rgba(107, 114, 128, 0.1)",
              color:
                selectedClause.alignment_status === "VERIFIED_FULL_TEXT"
                  ? "var(--color-success)"
                  : selectedClause.alignment_status === "PREVIEW_ONLY_AMBIGUOUS"
                  ? "var(--color-warning)"
                  : "var(--color-text-muted)",
              fontWeight: 600,
            }}
          >
            {selectedClause.alignment_status === "VERIFIED_FULL_TEXT"
              ? "Verified Full Text"
              : selectedClause.alignment_status === "PREVIEW_ONLY_AMBIGUOUS"
              ? "Preview Only (Ambiguous Boundary)"
              : "Preview Only (Unverified)"}
          </span>
        </div>
        <p
          style={{
            margin: 0,
            whiteSpace: "pre-wrap",
            wordBreak: "break-word",
            fontStyle: selectedClause.is_full_text ? "normal" : "italic",
          }}
        >
          {selectedClause.full_text || selectedClause.text_preview}
        </p>
      </div>

      {/* Inspector Section Tab Buttons */}
      <div
        role="tablist"
        aria-label="Inspector Sections"
        style={{
          display: "flex",
          borderBottom: "1px solid var(--color-border)",
          background: "var(--color-surface)",
        }}
      >
        <button
          type="button"
          role="tab"
          onClick={() => setActiveInspectorTab("scores")}
          className={`tab-btn ${activeInspectorTab === "scores" ? "active" : ""}`}
          style={{ flex: 1, padding: "0.6rem 0.75rem", fontSize: "0.82rem" }}
          aria-selected={activeInspectorTab === "scores"}
        >
          <BarChart2 size={14} style={{ display: "inline", marginRight: "0.35rem" }} aria-hidden="true" />
          <span>Coherence Evidence</span>
        </button>

        <button
          type="button"
          role="tab"
          onClick={() => setActiveInspectorTab("rules")}
          className={`tab-btn ${activeInspectorTab === "rules" ? "active" : ""}`}
          style={{ flex: 1, padding: "0.6rem 0.75rem", fontSize: "0.82rem" }}
          aria-selected={activeInspectorTab === "rules"}
        >
          <ShieldAlert size={14} style={{ display: "inline", marginRight: "0.35rem" }} aria-hidden="true" />
          <span>Rule Findings ({clauseRules.length})</span>
        </button>
      </div>

      {/* Inspector Content Body */}
      <div
        style={{
          padding: "1.25rem",
          overflowY: "auto",
          flexGrow: 1,
        }}
      >
        {activeInspectorTab === "scores" ? (
          <ScoreEvidencePanel clause={selectedClause} />
        ) : (
          <RuleFindingsPanel
            clauseRules={clauseRules}
            documentRules={documentRules}
            selectedClauseId={selectedClause.clause_id}
          />
        )}
      </div>

      {/* Cross-Workspace Action Toolbar */}
      <div
        style={{
          padding: "0.85rem 1.25rem",
          borderTop: "1px solid var(--color-border)",
          background: "var(--color-surface-raised)",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          gap: "0.75rem",
          flexWrap: "wrap",
        }}
      >
        <div style={{ fontSize: "0.75rem", color: "var(--color-text-secondary)" }}>
          Cross-Workspace Actions:
        </div>
        <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
          {onExploreRepositioning && (
            <Button
              id="inspector-explore-reposition-btn"
              variant="primary"
              size="sm"
              onClick={onExploreRepositioning}
              icon={<ArrowRightLeft size={14} />}
              style={{ fontSize: "0.78rem", padding: "0.35rem 0.65rem" }}
              aria-label={`Explore alternative positions for clause § ${selectedClause.sequence_idx}`}
            >
              Explore alternative positions
            </Button>
          )}

          {onNavigateToXai && (
            <Button
              id="inspector-open-xai-btn"
              variant="secondary"
              size="sm"
              onClick={onNavigateToXai}
              icon={<BrainCircuit size={14} />}
              style={{ fontSize: "0.78rem", padding: "0.35rem 0.65rem" }}
              aria-label={`Investigate XAI for clause § ${selectedClause.sequence_idx}`}
            >
              Explain Clause (XAI)
            </Button>
          )}

          {onNavigateToFeedback && (
            <Button
              id="inspector-open-feedback-btn"
              variant="outline"
              size="sm"
              onClick={onNavigateToFeedback}
              icon={<MessageSquareCheck size={14} />}
              style={{ fontSize: "0.78rem", padding: "0.35rem 0.65rem" }}
              aria-label={`Submit feedback for clause § ${selectedClause.sequence_idx}`}
            >
              Submit Feedback
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
