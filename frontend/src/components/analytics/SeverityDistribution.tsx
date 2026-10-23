"use client";

import { AlertOctagon, AlertTriangle, CheckCircle2, ShieldAlert } from "lucide-react";

interface SeverityDistributionProps {
  totalClauses: number;
  highCount: number;
  mediumCount: number;
  lowCount: number;
}

export function SeverityDistribution({
  totalClauses,
  highCount,
  mediumCount,
  lowCount,
}: SeverityDistributionProps) {
  // Count CLEAN clauses: totalClauses - (high + medium + low)
  const cleanCount = Math.max(0, totalClauses - (highCount + mediumCount + lowCount));

  // Percentages
  const highPct = totalClauses > 0 ? (highCount / totalClauses) * 100 : 0;
  const medPct = totalClauses > 0 ? (mediumCount / totalClauses) * 100 : 0;
  const lowPct = totalClauses > 0 ? (lowCount / totalClauses) * 100 : 0;
  const cleanPct = totalClauses > 0 ? (cleanCount / totalClauses) * 100 : 0;

  const severityTiers = [
    {
      tier: "HIGH",
      label: "High Severity",
      count: highCount,
      percent: highPct,
      color: "var(--sev-high-text)",
      bg: "var(--sev-high-bg)",
      border: "var(--sev-high-border)",
      icon: AlertOctagon,
      desc: "HIGH classification from the configured combined-score and channel-specific rules",
    },
    {
      tier: "MEDIUM",
      label: "Medium Severity",
      count: mediumCount,
      percent: medPct,
      color: "var(--sev-med-text)",
      bg: "var(--sev-med-bg)",
      border: "var(--sev-med-border)",
      icon: AlertTriangle,
      desc: "MEDIUM classification; a channel-specific threshold may trigger review at a lower combined score",
    },
    {
      tier: "LOW",
      label: "Low Severity",
      count: lowCount,
      percent: lowPct,
      color: "var(--color-warning)",
      bg: "rgba(234, 179, 8, 0.15)",
      border: "rgba(234, 179, 8, 0.4)",
      icon: ShieldAlert,
      desc: "Mild structural irregularity or edge threshold warning",
    },
    {
      tier: "CLEAN",
      label: "Clean Clauses",
      count: cleanCount,
      percent: cleanPct,
      color: "var(--color-success)",
      bg: "var(--sev-clean-bg)",
      border: "var(--sev-clean-border)",
      icon: CheckCircle2,
      desc: "No configured statistical severity threshold triggered; legal correctness is unverified",
    },
  ];

  return (
    <div
      className="card analytics-severity-card"
      role="region"
      aria-label="Clause Severity Classification Breakdown"
      style={{ height: "100%", display: "flex", flexDirection: "column" }}
    >
      <div style={{ marginBottom: "1rem" }}>
        <h3 style={{ fontSize: "1.05rem", fontWeight: 600, color: "var(--color-text-primary)", margin: 0 }}>
          Severity Class Distribution
        </h3>
        <p style={{ fontSize: "0.8rem", color: "var(--color-text-secondary)", margin: "0.25rem 0 0 0" }}>
          Segmented breakdown of {totalClauses} clauses across discrete calibrated risk tiers.
        </p>
      </div>

      {/* Accessible Segmented Bar */}
      <div
        role="progressbar"
        aria-label="Severity proportions"
        aria-valuemin={0}
        aria-valuemax={100}
        aria-valuenow={100}
        style={{
          display: "flex",
          height: "24px",
          width: "100%",
          borderRadius: "6px",
          overflow: "hidden",
          background: "var(--color-surface-raised)",
          border: "1px solid var(--color-border)",
          marginBottom: "1.25rem",
        }}
      >
        {highPct > 0 && (
          <div
            title={`High Severity: ${highCount} clauses (${highPct.toFixed(1)}%)`}
            style={{
              width: `${highPct}%`,
              background: "var(--sev-high-text)",
              transition: "width 0.3s ease",
            }}
          />
        )}
        {medPct > 0 && (
          <div
            title={`Medium Severity: ${mediumCount} clauses (${medPct.toFixed(1)}%)`}
            style={{
              width: `${medPct}%`,
              background: "var(--sev-med-text)",
              transition: "width 0.3s ease",
            }}
          />
        )}
        {lowPct > 0 && (
          <div
            title={`Low Severity: ${lowCount} clauses (${lowPct.toFixed(1)}%)`}
            style={{
              width: `${lowPct}%`,
              background: "var(--color-warning)",
              transition: "width 0.3s ease",
            }}
          />
        )}
        {cleanPct > 0 && (
          <div
            title={`Clean: ${cleanCount} clauses (${cleanPct.toFixed(1)}%)`}
            style={{
              width: `${cleanPct}%`,
              background: "var(--color-success)",
              transition: "width 0.3s ease",
            }}
          />
        )}
      </div>

      {/* Textual Count Table (Non-color reliant) */}
      <div style={{ flex: 1, overflowX: "auto" }}>
        <table
          style={{
            width: "100%",
            borderCollapse: "collapse",
            fontSize: "0.85rem",
          }}
          aria-label="Clause severity counts and proportions"
        >
          <thead>
            <tr style={{ borderBottom: "1px solid var(--color-border)", textAlign: "left", color: "var(--color-text-secondary)" }}>
              <th style={{ padding: "0.5rem 0.5rem 0.5rem 0", fontWeight: 600 }}>Severity Tier</th>
              <th style={{ padding: "0.5rem", fontWeight: 600, textAlign: "right" }}>Count</th>
              <th style={{ padding: "0.5rem", fontWeight: 600, textAlign: "right" }}>Ratio</th>
              <th style={{ padding: "0.5rem 0 0.5rem 0.5rem", fontWeight: 600 }}>Interpretation</th>
            </tr>
          </thead>
          <tbody>
            {severityTiers.map((t) => {
              const Icon = t.icon;
              return (
                <tr
                  key={t.tier}
                  style={{
                    borderBottom: "1px solid var(--color-border)",
                    color: "var(--color-text-primary)",
                  }}
                >
                  <td style={{ padding: "0.6rem 0.5rem 0.6rem 0" }}>
                    <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                      <span
                        style={{
                          display: "inline-flex",
                          alignItems: "center",
                          justifyContent: "center",
                          width: "20px",
                          height: "20px",
                          borderRadius: "4px",
                          background: t.bg,
                          color: t.color,
                        }}
                      >
                        <Icon size={12} aria-hidden="true" />
                      </span>
                      <span style={{ fontWeight: 600, color: t.color }}>{t.label}</span>
                    </div>
                  </td>
                  <td style={{ padding: "0.6rem 0.5rem", textAlign: "right", fontWeight: 700 }}>
                    {t.count}
                  </td>
                  <td style={{ padding: "0.6rem 0.5rem", textAlign: "right", color: "var(--color-text-muted)" }}>
                    {t.percent.toFixed(1)}%
                  </td>
                  <td style={{ padding: "0.6rem 0 0.6rem 0.5rem", fontSize: "0.75rem", color: "var(--color-text-secondary)" }}>
                    {t.desc}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <div style={{ marginTop: "1rem", fontSize: "0.75rem", color: "var(--color-text-muted)" }}>
        Counts cover clause model classifications only. Rule candidates are counted separately. Severity rules and synthetic calibration do not establish legal compliance.
      </div>
    </div>
  );
}
