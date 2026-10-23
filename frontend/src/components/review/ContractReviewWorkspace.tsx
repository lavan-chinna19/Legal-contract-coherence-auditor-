"use client";

import React, { useState, useMemo } from "react";
import { DocumentResult, EnrichedClause, SeverityFilter, RuleFlag, ClauseAlignmentResult, ClauseAlignmentStatus } from "./types";
import { ClauseDocumentViewer } from "./ClauseDocumentViewer";
import { FindingsInspector } from "./FindingsInspector";
import { alignClausesWithRawText } from "./alignment";
import { CounterfactualRepairWorkspace } from "../repair";

interface ContractReviewWorkspaceProps {
  documentResult: DocumentResult;
  rawContractText?: string;
  selectedClauseId: string | null;
  onSelectClauseId: (clauseId: string) => void;
  onNavigateToXai?: () => void;
  onNavigateToFeedback?: () => void;
  backendUrl?: string;
  apiKey?: string;
}

export function ContractReviewWorkspace({
  documentResult,
  rawContractText = "",
  selectedClauseId,
  onSelectClauseId,
  onNavigateToXai,
  onNavigateToFeedback,
  backendUrl = "http://localhost:8000",
  apiKey = "",
}: ContractReviewWorkspaceProps) {
  const [searchQuery, setSearchQuery] = useState("");
  const [severityFilter, setSeverityFilter] = useState<SeverityFilter>("ALL");
  const [showRepositionWorkspace, setShowRepositionWorkspace] = useState(false);

  // Step 1: Enrich clauses with source document text and rule associations
  const enrichedClauses: EnrichedClause[] = useMemo(() => {
    const clauses = documentResult.scoring_result?.clauses || [];
    const allRuleFlags = documentResult.rule_flags || [];

    // Authoritative alignment against raw contract text using alignment engine
    const alignments = alignClausesWithRawText(clauses, rawContractText, {
      documentId: documentResult.doc_id,
    });
    const alignmentMap = new Map<string, ClauseAlignmentResult>();
    for (const res of alignments) {
      alignmentMap.set(res.clauseId, res);
    }

    return clauses.map((c) => {
      // Find rules specifically matching this clause
      const matchedRules: RuleFlag[] = allRuleFlags.filter(
        (r) =>
          r.clause_id === c.clause_id ||
          (r.involved_clause_ids && r.involved_clause_ids.includes(c.clause_id))
      );

      let alignRes = alignmentMap.get(c.clause_id);
      const authoritative = documentResult.metadata?.clause_inventory?.find(item => item.clause_id === c.clause_id);
      if (authoritative && authoritative.doc_id === documentResult.doc_id && authoritative.sequence_idx === c.sequence_idx &&
          rawContractText.slice(authoritative.char_start, authoritative.char_end) === authoritative.text) {
        alignRes = { clauseId: c.clause_id, sequenceIdx: c.sequence_idx, status: "VERIFIED_FULL_TEXT",
          displayText: authoritative.text, sourceStart: authoritative.char_start, sourceEnd: authoritative.char_end,
          explanation: "Verified against the backend clause identity and normalized source offsets." };
      }
      const isFull = alignRes ? alignRes.status === "VERIFIED_FULL_TEXT" : false;
      const status: ClauseAlignmentStatus = alignRes
        ? alignRes.status
        : "PREVIEW_ONLY_INSUFFICIENT_EVIDENCE";
      const explanation = alignRes
        ? alignRes.explanation
        : "No alignment result found.";
      const displayText = alignRes ? alignRes.displayText : c.text_preview;

      return {
        ...c,
        full_text: displayText,
        is_full_text: isFull,
        alignment_status: status,
        alignment_explanation: explanation,
        source_start: alignRes?.sourceStart,
        source_end: alignRes?.sourceEnd,
        associated_rules: matchedRules,
      };
    });
  }, [documentResult, rawContractText]);

  // Step 2: Separate document-level rule flags (unassigned to a single clause)
  const documentLevelRules: RuleFlag[] = useMemo(() => {
    const allRuleFlags = documentResult.rule_flags || [];
    return allRuleFlags.filter(
      (r) => !r.clause_id && (!r.involved_clause_ids || r.involved_clause_ids.length === 0)
    );
  }, [documentResult]);

  // Step 3: Filter clauses based on query and severity filter
  const filteredClauses: EnrichedClause[] = useMemo(() => {
    const query = searchQuery.trim().toLowerCase();

    return enrichedClauses.filter((c) => {
      // Severity filter check
      if (severityFilter === "HIGH" && c.severity !== "HIGH") return false;
      if (severityFilter === "MEDIUM" && c.severity !== "MEDIUM") return false;
      if (severityFilter === "LOW" && c.severity !== "LOW") return false;
      if (severityFilter === "FLAGGED" && !c.is_anomaly && c.associated_rules.length === 0) return false;
      if (severityFilter === "CLEAN" && (c.is_anomaly || c.associated_rules.length > 0 || c.severity === "HIGH" || c.severity === "MEDIUM")) {
        return false;
      }

      // Text query check
      if (query.length > 0) {
        const textToSearch = (c.full_text || c.text_preview).toLowerCase();
        const matchesText = textToSearch.includes(query);
        const matchesSection = `§ ${c.sequence_idx}`.toLowerCase().includes(query);
        const matchesId = c.clause_id.toLowerCase().includes(query);
        return matchesText || matchesSection || matchesId;
      }

      return true;
    });
  }, [enrichedClauses, searchQuery, severityFilter]);

  // Step 4: Ensure authoritative selected clause
  const activeSelectedClause = useMemo(() => {
    if (selectedClauseId) {
      const found = enrichedClauses.find((c) => c.clause_id === selectedClauseId);
      if (found) return found;
    }
    return filteredClauses[0] || enrichedClauses[0] || null;
  }, [selectedClauseId, enrichedClauses, filteredClauses]);

  // Sequential previous / next navigation across the filtered list
  const currentNavIndex = useMemo(() => {
    if (!activeSelectedClause) return -1;
    return filteredClauses.findIndex((c) => c.clause_id === activeSelectedClause.clause_id);
  }, [activeSelectedClause, filteredClauses]);

  const hasPrevious = currentNavIndex > 0;
  const hasNext = currentNavIndex !== -1 && currentNavIndex < filteredClauses.length - 1;

  const handlePrevious = () => {
    if (hasPrevious) {
      onSelectClauseId(filteredClauses[currentNavIndex - 1].clause_id);
    }
  };

  const handleNext = () => {
    if (hasNext) {
      onSelectClauseId(filteredClauses[currentNavIndex + 1].clause_id);
    }
  };

  const handleClearFilters = () => {
    setSearchQuery("");
    setSeverityFilter("ALL");
  };

  return (
    <div
      className="contract-review-workspace"
      role="region"
      aria-label="Split-Screen Contract Review Workspace"
      style={{
        display: "flex",
        flexDirection: "column",
        gap: "1rem",
        width: "100%",
      }}
    >
      {/* Sequence Coherence Heatmap Bar (Interactive mini-map) */}
      <div
        className="card"
        style={{
          padding: "0.85rem 1.25rem",
          margin: 0,
          background: "var(--color-surface)",
          border: "1px solid var(--color-border)",
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.5rem" }}>
          <div style={{ fontSize: "0.82rem", fontWeight: 700, color: "var(--color-text-primary)" }}>
            Sequence Coherence Heatmap
          </div>
          <div style={{ display: "flex", gap: "1rem", fontSize: "0.75rem", color: "var(--color-text-secondary)" }}>
            <span><strong style={{ color: "var(--color-danger)" }}>■</strong> High</span>
            <span><strong style={{ color: "var(--color-warning)" }}>■</strong> Medium</span>
            <span><strong style={{ color: "var(--color-accent)" }}>■</strong> No score flag</span>
          </div>
        </div>

        <div className="heatmap-bar" style={{ margin: "0.25rem 0", height: "24px" }}>
          {enrichedClauses.map((c) => {
            const isSelected = c.clause_id === activeSelectedClause?.clause_id;
            const bg =
              c.severity === "HIGH"
                ? "var(--color-danger)"
                : c.severity === "MEDIUM"
                ? "var(--color-warning)"
                : "var(--color-accent)";
            return (
              <button
                type="button"
                aria-label={`Select clause ${c.sequence_idx + 1}, severity ${c.severity}`}
                aria-pressed={isSelected}
                key={c.clause_id}
                className="heatmap-cell"
                style={{
                  background: bg,
                  padding: 0,
                  opacity: isSelected ? 1 : 0.7,
                  border: isSelected ? "2px solid #FFFFFF" : "none",
                  boxShadow: isSelected ? "0 0 6px rgba(0,0,0,0.4)" : "none",
                }}
                title={`§ ${c.sequence_idx}: ${c.combined_score.toFixed(3)} (${c.severity})`}
                onClick={() => onSelectClauseId(c.clause_id)}
              />
            );
          })}
        </div>
        <p style={{ fontSize: "0.75rem", color: "var(--color-text-secondary)" }}>Colors use the reported severity. A Channel B flag can require review even when the combined score is lower.</p>
      </div>

      {/* Flagship Split-Screen Layout Grid */}
      <div className="review-split-grid">
        {/* Left Panel: Document Viewer (55%) */}
        <div className="review-left-column">
          <ClauseDocumentViewer
            clauses={enrichedClauses}
            filteredClauses={filteredClauses}
            selectedClauseId={activeSelectedClause?.clause_id || null}
            onSelectClause={onSelectClauseId}
            docId={documentResult.doc_id}
            searchQuery={searchQuery}
            onSearchChange={setSearchQuery}
            severityFilter={severityFilter}
            onSeverityFilterChange={setSeverityFilter}
            onClearFilters={handleClearFilters}
          />
        </div>

        {/* Right Panel: Findings Inspector or Counterfactual Repositioning (45%) */}
        <div className="review-right-column">
          {showRepositionWorkspace ? (
            <CounterfactualRepairWorkspace
              docId={documentResult.doc_id}
              targetClauseId={activeSelectedClause?.clause_id || ""}
              backendUrl={backendUrl}
              apiKey={apiKey}
              allClauses={enrichedClauses.map((c) => ({
                clause_id: c.clause_id,
                sequence_idx: c.sequence_idx,
                text_preview: c.text_preview,
              }))}
              onClose={() => setShowRepositionWorkspace(false)}
              onNavigateToXai={onNavigateToXai}
              onNavigateToFeedback={onNavigateToFeedback}
            />
          ) : (
            <FindingsInspector
              selectedClause={activeSelectedClause}
              currentIndex={currentNavIndex !== -1 ? currentNavIndex : 0}
              totalClauses={filteredClauses.length}
              onPrevious={handlePrevious}
              onNext={handleNext}
              hasPrevious={hasPrevious}
              hasNext={hasNext}
              documentRules={documentLevelRules}
              onNavigateToXai={onNavigateToXai}
              onNavigateToFeedback={onNavigateToFeedback}
              onExploreRepositioning={() => setShowRepositionWorkspace(true)}
            />
          )}
        </div>
      </div>

      <style jsx>{`
        .review-split-grid {
          display: grid;
          grid-template-columns: 55fr 45fr;
          gap: 1.25rem;
          height: calc(100vh - 210px);
          min-height: 580px;
        }

        .review-left-column,
        .review-right-column {
          height: 100%;
          min-height: 0;
          overflow: hidden;
        }

        @media (max-width: 1023px) {
          .review-split-grid {
            grid-template-columns: 1fr;
            height: auto;
            min-height: auto;
          }

          .review-left-column {
            height: 480px;
          }

          .review-right-column {
            height: auto;
            min-height: 480px;
          }
        }
      `}</style>
    </div>
  );
}
