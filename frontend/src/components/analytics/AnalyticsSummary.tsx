"use client";

import React from "react";
import { DocumentResult } from "./types";
import { FileText, AlertTriangle, AlertOctagon, Scale, TrendingUp, Info } from "lucide-react";

interface AnalyticsSummaryProps {
  documentResult: DocumentResult;
}

export function AnalyticsSummary({ documentResult }: AnalyticsSummaryProps) {
  const { total_clauses, ml_anomaly_count, high_severity_count, medium_severity_count, scoring_result, rule_flags } =
    documentResult;

  const ruleCount = rule_flags?.length ?? documentResult.rule_violation_count ?? 0;
  const meanScore = scoring_result?.mean_combined_score ?? 0;
  const maxScore = scoring_result?.max_combined_score ?? 0;

  // Real anomaly rate: ml_anomaly_count / total_clauses
  const anomalyRate = total_clauses > 0 ? ((ml_anomaly_count / total_clauses) * 100).toFixed(1) : "0.0";

  return (
    <section
      className="analytics-kpi-section"
      role="region"
      aria-label="Document Audit Key Performance Indicators"
      style={{ marginBottom: "1.75rem" }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: "0.75rem", flexWrap: "wrap", gap: "0.5rem" }}>
        <div>
          <h2 style={{ fontSize: "1.1rem", fontWeight: 600, color: "var(--color-text-primary)", margin: 0 }}>
            Audit Summary &amp; Structural Overview
          </h2>
          <p style={{ fontSize: "0.8rem", color: "var(--color-text-muted)", margin: "0.2rem 0 0 0" }}>
            Document ID: <code style={{ fontSize: "0.75rem", padding: "0.1rem 0.35rem", background: "var(--color-surface-raised)", borderRadius: "3px" }}>{documentResult.doc_id}</code> &bull; Authoritative Model Calibration: <span style={{ fontWeight: 500 }}>{scoring_result?.calibration_source || "synthetic_shuffle_ledgar"}</span>
          </p>
        </div>
        <div style={{ fontSize: "0.75rem", color: "var(--color-text-muted)", display: "flex", alignItems: "center", gap: "0.35rem" }}>
          <Info size={14} aria-hidden="true" />
          <span>Real model outputs &bull; No probabilistic compliance claims</span>
        </div>
      </div>

      <div
        className="grid-kpis"
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
          gap: "1rem",
        }}
      >
        {/* KPI 1: Total Clauses */}
        <div className="kpi-card" id="analytics-kpi-total-clauses">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "0.4rem" }}>
            <span className="kpi-label" style={{ fontSize: "0.75rem", textTransform: "uppercase", letterSpacing: "0.05em", color: "var(--color-text-secondary)", fontWeight: 600 }}>
              Total Clauses
            </span>
            <FileText size={16} style={{ color: "var(--color-text-muted)" }} aria-hidden="true" />
          </div>
          <div className="kpi-value" style={{ fontSize: "1.75rem", fontWeight: 700, color: "var(--color-text-primary)", lineHeight: 1.2 }}>
            {total_clauses}
          </div>
          <div style={{ fontSize: "0.75rem", color: "var(--color-text-muted)", marginTop: "0.35rem" }}>
            Authoritative parsed segments
          </div>
        </div>

        {/* KPI 2: Detected ML Anomalies */}
        <div className="kpi-card" id="analytics-kpi-ml-anomalies">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "0.4rem" }}>
            <span className="kpi-label" style={{ fontSize: "0.75rem", textTransform: "uppercase", letterSpacing: "0.05em", color: "var(--color-text-secondary)", fontWeight: 600 }}>
              Detected Anomalies
            </span>
            <AlertTriangle size={16} style={{ color: "var(--sev-med-text)" }} aria-hidden="true" />
          </div>
          <div className="kpi-value" style={{ fontSize: "1.75rem", fontWeight: 700, color: "var(--sev-med-text)", lineHeight: 1.2 }}>
            {ml_anomaly_count}
          </div>
          <div style={{ fontSize: "0.75rem", color: "var(--color-text-muted)", marginTop: "0.35rem" }}>
            {anomalyRate}% of document ({medium_severity_count + high_severity_count} flagged)
          </div>
        </div>

        {/* KPI 3: High-Severity Findings */}
        <div className="kpi-card" id="analytics-kpi-high-severity">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "0.4rem" }}>
            <span className="kpi-label" style={{ fontSize: "0.75rem", textTransform: "uppercase", letterSpacing: "0.05em", color: "var(--color-text-secondary)", fontWeight: 600 }}>
              High Severity
            </span>
            <AlertOctagon size={16} style={{ color: "var(--sev-high-text)" }} aria-hidden="true" />
          </div>
          <div className="kpi-value" style={{ fontSize: "1.75rem", fontWeight: 700, color: "var(--sev-high-text)", lineHeight: 1.2 }}>
            {high_severity_count}
          </div>
          <div style={{ fontSize: "0.75rem", color: "var(--color-text-muted)", marginTop: "0.35rem" }}>
            Critical OOD or transition shock
          </div>
        </div>

        {/* KPI 4: Deterministic Rule Violations */}
        <div className="kpi-card" id="analytics-kpi-rule-violations">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "0.4rem" }}>
            <span className="kpi-label" style={{ fontSize: "0.75rem", textTransform: "uppercase", letterSpacing: "0.05em", color: "var(--color-text-secondary)", fontWeight: 600 }}>
              Rule Violations
            </span>
            <Scale size={16} style={{ color: ruleCount > 0 ? "var(--color-warning)" : "var(--color-text-muted)" }} aria-hidden="true" />
          </div>
          <div
            className="kpi-value"
            style={{
              fontSize: "1.75rem",
              fontWeight: 700,
              color: ruleCount > 0 ? "var(--color-warning)" : "var(--color-text-primary)",
              lineHeight: 1.2,
            }}
          >
            {ruleCount}
          </div>
          <div style={{ fontSize: "0.75rem", color: "var(--color-text-muted)", marginTop: "0.35rem" }}>
            Deterministic reference/date checks
          </div>
        </div>

        {/* KPI 5: Mean Combined Anomaly Score */}
        <div className="kpi-card" id="analytics-kpi-mean-score">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "0.4rem" }}>
            <span className="kpi-label" style={{ fontSize: "0.75rem", textTransform: "uppercase", letterSpacing: "0.05em", color: "var(--color-text-secondary)", fontWeight: 600 }}>
              Mean Anomaly Score
            </span>
            <TrendingUp size={16} style={{ color: "var(--color-accent)" }} aria-hidden="true" />
          </div>
          <div className="kpi-value" style={{ fontSize: "1.75rem", fontWeight: 700, color: "var(--color-accent)", lineHeight: 1.2 }}>
            {meanScore.toFixed(3)}
          </div>
          <div style={{ fontSize: "0.75rem", color: "var(--color-text-muted)", marginTop: "0.35rem" }}>
            Scale [0, 1] &bull; Max: {maxScore.toFixed(3)}
          </div>
        </div>
      </div>
    </section>
  );
}
