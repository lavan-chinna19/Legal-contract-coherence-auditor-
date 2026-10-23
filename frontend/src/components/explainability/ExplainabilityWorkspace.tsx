"use client";

import React, { useState, useEffect, useRef } from "react";
import { ExplainabilityWorkspaceProps, XaiResponse } from "./types";
import { ClauseExplanationHeader } from "./ClauseExplanationHeader";
import { AttributionLegend } from "./AttributionLegend";
import { SignedAttributionViewer } from "./SignedAttributionViewer";
import { TokenDetailPanel } from "./TokenDetailPanel";
import { SensitivityComparison } from "./SensitivityComparison";
import { ExplanationLimitations } from "./ExplanationLimitations";
import { ExplainabilityEmptyState } from "./ExplainabilityEmptyState";
import { WordGroup } from "./wordpieceGrouping";
import { Cpu, ArrowRightLeft, RefreshCw } from "lucide-react";

export function ExplainabilityWorkspace({
  documentResult,
  selectedClauseId,
  backendUrl,
  apiKey,
  onSelectClauseId,
  onNavigateToReview,
  onNavigateToFeedback,
  onNavigateToUpload,
}: ExplainabilityWorkspaceProps) {
  const [activeXaiTab, setActiveXaiTab] = useState<"attribution" | "sensitivity" | "retrieval">("attribution");
  const [loadingAttribution, setLoadingAttribution] = useState(false);
  const [loadingSensitivity, setLoadingSensitivity] = useState(false);
  const [attributionData, setAttributionData] = useState<XaiResponse | null>(null);
  const [sensitivityData, setSensitivityData] = useState<XaiResponse | null>(null);
  const [selectedTokenGroup, setSelectedTokenGroup] = useState<WordGroup | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Stale response guard updated inside effect
  const activeClauseIdRef = useRef(selectedClauseId);
  useEffect(() => {
    activeClauseIdRef.current = selectedClauseId;
  }, [selectedClauseId]);

  const clauses = documentResult?.scoring_result?.clauses || [];
  const selectedClause = clauses.find((c) => c.clause_id === selectedClauseId) || clauses[0];

  // Fetch Attribution
  useEffect(() => {
    if (!documentResult || !selectedClauseId || !apiKey.trim() || activeXaiTab !== "attribution") {
      return;
    }

    const currentTarget = selectedClauseId;
    let cancelled = false;

    queueMicrotask(() => {
      if (!cancelled) {
        setLoadingAttribution(true);
        setErrorMessage(null);
        setSelectedTokenGroup(null);
      }
    });

    const fetchAttribution = async () => {
      try {
        const res = await fetch(
          `${backendUrl}/v1/xai/attribution?doc_id=${documentResult.doc_id}&clause_id=${currentTarget}`,
          { headers: { "X-API-Key": apiKey.trim() } }
        );

        if (!res.ok) {
          throw new Error(`Failed to fetch attribution (${res.status})`);
        }

        const data: XaiResponse = await res.json();
        // Stale response check: only update if user hasn't switched clause
        if (!cancelled && activeClauseIdRef.current === currentTarget) {
          setAttributionData(data);
        }
      } catch (err: unknown) {
        if (!cancelled && activeClauseIdRef.current === currentTarget) {
          const msg = err instanceof Error ? err.message : "Attribution fetch error";
          setErrorMessage(msg);
        }
      } finally {
        if (!cancelled && activeClauseIdRef.current === currentTarget) {
          setLoadingAttribution(false);
        }
      }
    };

    fetchAttribution();

    return () => {
      cancelled = true;
    };
  }, [documentResult, selectedClauseId, backendUrl, apiKey, activeXaiTab]);

  // Fetch Sensitivity
  useEffect(() => {
    if (!documentResult || !selectedClauseId || !apiKey.trim() || activeXaiTab !== "sensitivity") {
      return;
    }

    const currentTarget = selectedClauseId;
    let cancelled = false;

    queueMicrotask(() => {
      if (!cancelled) {
        setLoadingSensitivity(true);
      }
    });

    const fetchSensitivity = async () => {
      try {
        const res = await fetch(
          `${backendUrl}/v1/xai/sensitivity?doc_id=${documentResult.doc_id}&clause_id=${currentTarget}`,
          { headers: { "X-API-Key": apiKey.trim() } }
        );

        if (!res.ok) {
          throw new Error(`Failed to fetch sensitivity (${res.status})`);
        }

        const data: XaiResponse = await res.json();
        if (!cancelled && activeClauseIdRef.current === currentTarget) {
          setSensitivityData(data);
        }
      } catch (err: unknown) {
        if (!cancelled && activeClauseIdRef.current === currentTarget) {
          setErrorMessage(err instanceof Error ? err.message : "Sensitivity explanation unavailable");
        }
      } finally {
        if (!cancelled && activeClauseIdRef.current === currentTarget) {
          setLoadingSensitivity(false);
        }
      }
    };

    fetchSensitivity();

    return () => {
      cancelled = true;
    };
  }, [documentResult, selectedClauseId, backendUrl, apiKey, activeXaiTab]);

  if (!documentResult) {
    return <ExplainabilityEmptyState onNavigateToUpload={onNavigateToUpload} />;
  }

  return (
    <div
      id="xai-workspace-container"
      role="region"
      aria-label="Diagnostic Explainability (XAI) Workspace"
      style={{ paddingBottom: "2rem" }}
    >
      {/* Header and Cross-Navigation */}
      <ClauseExplanationHeader
        selectedClause={selectedClause}
        docId={documentResult.doc_id}
        onNavigateToReview={onNavigateToReview}
        onNavigateToFeedback={onNavigateToFeedback}
      />

      {/* Clause Selector Strip */}
      <div
        style={{
          background: "var(--color-surface)",
          border: "1px solid var(--color-border)",
          borderRadius: "var(--radius-md)",
          padding: "0.75rem 1rem",
          marginBottom: "1rem",
          display: "flex",
          alignItems: "center",
          gap: "0.75rem",
          overflowX: "auto",
        }}
      >
        <span style={{ fontSize: "0.85rem", fontWeight: 600, color: "var(--color-text-secondary)", whiteSpace: "nowrap" }}>
          Select Clause:
        </span>
        <div style={{ display: "flex", gap: "0.4rem" }}>
          {clauses.map((c) => {
            const isSelected = c.clause_id === selectedClauseId;
            return (
              <button
                key={c.clause_id}
                id={`xai-select-clause-${c.sequence_idx}`}
                className={`btn ${isSelected ? "btn-primary" : "btn-secondary"}`}
                style={{
                  padding: "0.25rem 0.55rem",
                  fontSize: "0.8rem",
                  whiteSpace: "nowrap",
                }}
                onClick={() => onSelectClauseId(c.clause_id)}
              >
                § {c.sequence_idx}
              </button>
            );
          })}
        </div>
      </div>

      {/* XAI Mode Subtabs */}
      <div
        style={{
          display: "flex",
          flexWrap: "wrap",
          gap: "0.5rem",
          marginBottom: "1rem",
          borderBottom: "1px solid var(--color-border)",
          paddingBottom: "0.5rem",
        }}
      >
        <button
          id="xai-tab-attribution"
          className={`btn ${activeXaiTab === "attribution" ? "btn-primary" : "btn-secondary"}`}
          style={{ display: "inline-flex", alignItems: "center", gap: "0.35rem", fontSize: "0.85rem" }}
          onClick={() => setActiveXaiTab("attribution")}
        >
          <Cpu size={15} aria-hidden="true" />
          <span>Integrated Gradients Attribution</span>
        </button>
        <button
          id="xai-tab-sensitivity"
          className={`btn ${activeXaiTab === "sensitivity" ? "btn-primary" : "btn-secondary"}`}
          style={{ display: "inline-flex", alignItems: "center", gap: "0.35rem", fontSize: "0.85rem" }}
          onClick={() => setActiveXaiTab("sensitivity")}
        >
          <ArrowRightLeft size={15} aria-hidden="true" />
          <span>Channel B Neighbor Sensitivity</span>
        </button>
      </div>

      {errorMessage && (
        <div
          style={{
            background: "rgba(220, 38, 38, 0.1)",
            border: "1px solid #dc2626",
            borderRadius: "var(--radius-sm)",
            padding: "0.75rem 1rem",
            color: "#dc2626",
            fontSize: "0.85rem",
            marginBottom: "1rem",
          }}
        >
          {errorMessage}
        </div>
      )}

      {/* Tab 1: Integrated Gradients */}
      {activeXaiTab === "attribution" && (
        <>
          <AttributionLegend />

          {loadingAttribution ? (
            <div
              style={{
                background: "var(--color-surface)",
                border: "1px solid var(--color-border)",
                borderRadius: "var(--radius-md)",
                padding: "2rem",
                textAlign: "center",
                color: "var(--color-text-secondary)",
              }}
            >
              <RefreshCw size={24} className="spin" style={{ marginBottom: "0.5rem", color: "var(--color-accent)" }} />
              <p style={{ margin: 0, fontSize: "0.9rem" }}>Computing Integrated Gradients token attributions (50 steps)...</p>
            </div>
          ) : attributionData?.ig_payload ? (
            <>
              <SignedAttributionViewer
                tokens={attributionData.ig_payload.tokens}
                attributions={attributionData.ig_payload.attributions}
                targetScore={attributionData.ig_payload.target_score}
                baselineScore={attributionData.ig_payload.baseline_score}
                selectedTokenGroup={selectedTokenGroup}
                onSelectTokenGroup={setSelectedTokenGroup}
              />

              <TokenDetailPanel
                selectedGroup={selectedTokenGroup}
                onClose={() => setSelectedTokenGroup(null)}
              />
            </>
          ) : (
            <div
              style={{
                background: "var(--color-surface)",
                border: "1px solid var(--color-border)",
                borderRadius: "var(--radius-md)",
                padding: "1.5rem",
                textAlign: "center",
                color: "var(--color-text-secondary)",
              }}
            >
              No attribution payload returned for this clause.
            </div>
          )}
        </>
      )}

      {/* Tab 2: Perturbation Sensitivity */}
      {activeXaiTab === "sensitivity" && (
        <SensitivityComparison
          sensitivityData={sensitivityData?.sensitivity_payload || null}
          loading={loadingSensitivity}
        />
      )}

      {/* Claim Boundaries & Methodology */}
      <ExplanationLimitations
        claimScope={attributionData?.claim_scope || sensitivityData?.claim_scope}
      />
    </div>
  );
}
