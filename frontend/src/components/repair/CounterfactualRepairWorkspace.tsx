"use client";

import React, { useState, useEffect, useRef } from "react";
import { RepositionResponse, RepositionCandidate } from "./types";
import { RepairCandidateList } from "./RepairCandidateList";
import { RepairScoreComparison } from "./RepairScoreComparison";
import { RepairClausePreview } from "./RepairClausePreview";
import { RepairAbstentionNotice } from "./RepairAbstentionNotice";
import { RepairMethodology } from "./RepairMethodology";
import { RepairEmptyState } from "./RepairEmptyState";
import {
  ArrowRightLeft,
  X,
  RefreshCw,
  AlertTriangle,
  BrainCircuit,
  MessageSquareCheck,
  Clock,
} from "lucide-react";

interface ClauseSnippet {
  clause_id: string;
  sequence_idx: number;
  text_preview: string;
}

interface CounterfactualRepairWorkspaceProps {
  docId: string;
  targetClauseId: string;
  backendUrl: string;
  apiKey: string;
  allClauses: ClauseSnippet[];
  onClose: () => void;
  onNavigateToXai?: () => void;
  onNavigateToFeedback?: () => void;
}

export function CounterfactualRepairWorkspace({
  docId,
  targetClauseId,
  backendUrl,
  apiKey,
  allClauses,
  onClose,
  onNavigateToXai,
  onNavigateToFeedback,
}: CounterfactualRepairWorkspaceProps) {
  const [loading, setLoading] = useState<boolean>(Boolean(docId && targetClauseId && apiKey.trim()));
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<RepositionResponse | null>(null);
  const [selectedCandidateIdx, setSelectedCandidateIdx] = useState<number | null>(null);
  const [reloadNonce, setReloadNonce] = useState(0);

  // Stale-response protection: track active targetClauseId across async calls
  const activeTargetRef = useRef<string>(targetClauseId);
  useEffect(() => {
    activeTargetRef.current = targetClauseId;
  }, [targetClauseId]);

  useEffect(() => {
    if (!docId || !targetClauseId || !apiKey.trim()) {
      return;
    }

    let isMounted = true;
    queueMicrotask(() => {
      if (isMounted) {
        setLoading(true);
        setError(null);
      }
    });
    const reqClauseId = targetClauseId;

    fetch(`${backendUrl}/v1/experimental/reposition`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": apiKey.trim(),
      },
      body: JSON.stringify({
        doc_id: docId,
        clause_id: reqClauseId,
        experimental: true,
        min_delta_threshold: 0.005,
      }),
    })
      .then(async (res) => {
        if (!res.ok) {
          const errJson = await res.json().catch(() => null);
          throw new Error(errJson?.detail || `Server returned HTTP ${res.status}`);
        }
        return res.json();
      })
      .then((resData: RepositionResponse) => {
        if (!isMounted || activeTargetRef.current !== reqClauseId) return;
        setData(resData);
        if (resData.best_candidate_idx !== null && resData.best_candidate_idx !== undefined) {
          setSelectedCandidateIdx(resData.best_candidate_idx);
        } else if (resData.candidates.length > 0) {
          setSelectedCandidateIdx(resData.candidates[0].position_idx);
        }
      })
      .catch((err: unknown) => {
        if (!isMounted || activeTargetRef.current !== reqClauseId) return;
        const msg = err instanceof Error ? err.message : "Repositioning evaluation failed";
        setError(msg);
      })
      .finally(() => {
        if (isMounted && activeTargetRef.current === reqClauseId) {
          setLoading(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, [docId, targetClauseId, backendUrl, apiKey, reloadNonce]);

  const targetClauseSnippet = allClauses.find((c) => c.clause_id === targetClauseId) || {
    clause_id: targetClauseId,
    sequence_idx: data?.target_clause_idx ?? 0,
    text_preview: "Target clause content",
  };

  const selectedCandidate: RepositionCandidate | null =
    data && selectedCandidateIdx !== null
      ? data.candidates.find((c) => c.position_idx === selectedCandidateIdx) || data.candidates[0]
      : null;

  return (
    <div
      className="counterfactual-repair-workspace"
      role="region"
      aria-label="Suggested Clause Positions (Experimental)"
      style={{
        display: "flex",
        flexDirection: "column",
        height: "100%",
        background: "var(--color-surface, #ffffff)",
        borderRadius: "8px",
        border: "1px solid var(--color-border, #e2e8f0)",
        overflow: "hidden",
      }}
    >
      {/* Header */}
      <div
        style={{
          padding: "1rem 1.25rem",
          background: "var(--color-surface-raised, #f8fafc)",
          borderBottom: "1px solid var(--color-border, #e2e8f0)",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexWrap: "wrap",
          gap: "0.75rem",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "0.6rem" }}>
          <div
            style={{
              width: "32px",
              height: "32px",
              borderRadius: "6px",
              background: "rgba(37, 99, 235, 0.1)",
              color: "var(--color-accent, #2563eb)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <ArrowRightLeft size={18} aria-hidden="true" />
          </div>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
              <h3 style={{ fontSize: "1.05rem", fontWeight: 700, margin: 0, color: "var(--color-text-primary, #0f172a)" }}>
                Alternative Positions for Clause §{targetClauseSnippet.sequence_idx}
              </h3>
              <span
                style={{
                  fontSize: "0.7rem",
                  padding: "0.15rem 0.45rem",
                  borderRadius: "4px",
                  background: "rgba(37, 99, 235, 0.1)",
                  color: "var(--color-accent, #2563eb)",
                  fontWeight: 700,
                  textTransform: "uppercase",
                  letterSpacing: "0.03em",
                }}
              >
                Experimental
              </span>
            </div>
            <div style={{ fontSize: "0.72rem", color: "var(--color-text-muted, #94a3b8)", marginTop: "0.15rem" }}>
              ID: {targetClauseId}
            </div>
          </div>
        </div>

        {/* Header Action Buttons */}
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
          <button
            type="button"
            onClick={() => setReloadNonce((n) => n + 1)}
            disabled={loading}
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: "0.35rem",
              fontSize: "0.78rem",
              padding: "0.4rem 0.75rem",
              borderRadius: "6px",
              border: "1px solid var(--color-border, #e2e8f0)",
              background: "var(--color-surface, #ffffff)",
              color: "var(--color-text-secondary, #64748b)",
              cursor: loading ? "not-allowed" : "pointer",
            }}
            aria-label="Re-evaluate candidate positions"
          >
            <RefreshCw size={13} className={loading ? "spin" : ""} aria-hidden="true" />
            <span>Re-evaluate</span>
          </button>

          <button
            type="button"
            onClick={onClose}
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: "0.35rem",
              fontSize: "0.78rem",
              padding: "0.4rem 0.75rem",
              borderRadius: "6px",
              border: "1px solid var(--color-border, #e2e8f0)",
              background: "var(--color-surface, #ffffff)",
              color: "var(--color-text-primary, #0f172a)",
              fontWeight: 600,
              cursor: "pointer",
            }}
            aria-label="Close repositioning workspace and return to review"
          >
            <X size={14} aria-hidden="true" />
            <span>Close Workspace</span>
          </button>
        </div>
      </div>

      {/* Experimental Qualified Warning Strip */}
      <div
        style={{
          padding: "0.5rem 1.25rem",
          background: "rgba(245, 158, 11, 0.08)",
          borderBottom: "1px solid rgba(245, 158, 11, 0.2)",
          display: "flex",
          alignItems: "center",
          gap: "0.5rem",
          fontSize: "0.76rem",
          color: "var(--sev-med-text, #d97706)",
        }}
      >
        <AlertTriangle size={14} style={{ flexShrink: 0 }} aria-hidden="true" />
        <span>
          <strong>Decision-Support Notice:</strong> Evaluates document coherence under the frozen neural scorer. Does NOT determine legal drafting correctness or enforceability. Original contract remains completely unchanged.
        </span>
      </div>

      {/* Main Body */}
      <div style={{ flexGrow: 1, overflowY: "auto", padding: "1.25rem" }}>
        {loading && (
          <div
            style={{
              padding: "3rem 1.5rem",
              textAlign: "center",
              color: "var(--color-text-secondary, #64748b)",
            }}
          >
            <RefreshCw
              size={24}
              className="spin"
              style={{ margin: "0 auto 1rem", color: "var(--color-accent, #2563eb)" }}
            />
            <p style={{ fontSize: "0.88rem", fontWeight: 600, margin: "0 0 0.25rem" }}>
              Evaluating Alternative Insertion Positions...
            </p>
            <p style={{ fontSize: "0.75rem", color: "var(--color-text-muted, #94a3b8)", margin: 0 }}>
              Testing {allClauses.length} candidate slots via frozen coherence neural head.
            </p>
          </div>
        )}

        {error && (
          <div
            style={{
              padding: "1.5rem",
              borderRadius: "6px",
              background: "rgba(239, 68, 68, 0.08)",
              border: "1px solid rgba(239, 68, 68, 0.25)",
              color: "var(--sev-high-text, #ef4444)",
              fontSize: "0.82rem",
            }}
          >
            <strong>Evaluation Error:</strong> {error}
          </div>
        )}

        {!loading && !error && data && (
          <>
            {/* Abstention Notice if Model Abstains */}
            {data.is_abstaining && (
              <RepairAbstentionNotice reason={data.abstention_reason} />
            )}

            {/* Candidate List & Detailed Inspection Layout */}
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "1fr 1fr",
                gap: "1.25rem",
              }}
            >
              {/* Left Column: Ranked Candidates */}
              <div>
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    marginBottom: "0.6rem",
                  }}
                >
                  <span
                    style={{
                      fontSize: "0.78rem",
                      fontWeight: 700,
                      color: "var(--color-text-secondary, #64748b)",
                      textTransform: "uppercase",
                      letterSpacing: "0.03em",
                    }}
                  >
                    Ranked Positions ({data.candidates.length} Slots)
                  </span>
                  <span
                    style={{
                      fontSize: "0.72rem",
                      color: "var(--color-text-muted, #94a3b8)",
                      display: "flex",
                      alignItems: "center",
                      gap: "0.25rem",
                    }}
                  >
                    <Clock size={12} aria-hidden="true" />
                    {data.evaluation_time_ms.toFixed(1)} ms
                  </span>
                </div>

                <RepairCandidateList
                  candidates={data.candidates}
                  selectedCandidateIdx={selectedCandidateIdx}
                  onSelectCandidate={setSelectedCandidateIdx}
                />
              </div>

              {/* Right Column: Score Comparison & Context Preview */}
              <div>
                {selectedCandidate ? (
                  <>
                    <RepairScoreComparison
                      originalMeanScore={data.original_mean_combined_score}
                      originalTargetSb={data.original_target_sb}
                      candidate={selectedCandidate}
                    />

                    <RepairClausePreview
                      targetClause={targetClauseSnippet}
                      allClauses={allClauses}
                      candidate={selectedCandidate}
                    />
                  </>
                ) : (
                  <RepairEmptyState message="Select a candidate position slot to inspect score comparison and surrounding clause flow." />
                )}
              </div>
            </div>

            {/* Scientific Disclosures and Methodology */}
            <RepairMethodology />
          </>
        )}
      </div>

      {/* Footer Navigation Strip */}
      <div
        style={{
          padding: "0.85rem 1.25rem",
          borderTop: "1px solid var(--color-border, #e2e8f0)",
          background: "var(--color-surface-raised, #f8fafc)",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexWrap: "wrap",
          gap: "0.75rem",
        }}
      >
        <div style={{ fontSize: "0.75rem", color: "var(--color-text-secondary, #64748b)" }}>
          Cross-Workspace Navigation:
        </div>
        <div style={{ display: "flex", gap: "0.5rem" }}>
          {onNavigateToXai && (
            <button
              type="button"
              onClick={onNavigateToXai}
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: "0.35rem",
                fontSize: "0.78rem",
                padding: "0.35rem 0.65rem",
                borderRadius: "5px",
                border: "1px solid var(--color-border, #e2e8f0)",
                background: "var(--color-surface, #ffffff)",
                color: "var(--color-text-primary, #0f172a)",
                cursor: "pointer",
              }}
              aria-label="Explain clause via XAI"
            >
              <BrainCircuit size={13} aria-hidden="true" />
              <span>Explain clause</span>
            </button>
          )}

          {onNavigateToFeedback && (
            <button
              type="button"
              onClick={onNavigateToFeedback}
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: "0.35rem",
                fontSize: "0.78rem",
                padding: "0.35rem 0.65rem",
                borderRadius: "5px",
                border: "1px solid var(--color-border, #e2e8f0)",
                background: "var(--color-surface, #ffffff)",
                color: "var(--color-text-primary, #0f172a)",
                cursor: "pointer",
              }}
              aria-label="Submit reviewer feedback"
            >
              <MessageSquareCheck size={13} aria-hidden="true" />
              <span>Submit Feedback</span>
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
