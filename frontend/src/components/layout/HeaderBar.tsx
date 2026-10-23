"use client";

import React, { useState } from "react";
import { Menu, Settings, Server, KeyRound, ChevronDown, ChevronUp } from "lucide-react";
import { ThemeToggle } from "./ThemeToggle";
import { NavSection } from "./SidebarNav";

interface HeaderBarProps {
  activeSection: NavSection;
  backendStatus: "online" | "offline" | "checking";
  backendUrl: string;
  onBackendUrlChange: (url: string) => void;
  apiKey: string;
  onApiKeyChange: (key: string) => void;
  onOpenMobileNav: () => void;
}

export function HeaderBar({
  activeSection,
  backendStatus,
  backendUrl,
  onBackendUrlChange,
  apiKey,
  onApiKeyChange,
  onOpenMobileNav,
}: HeaderBarProps) {
  const [showSettings, setShowSettings] = useState(false);

  const sectionMeta: Record<NavSection, { title: string; subtitle: string }> = {
    overview: {
      title: "Overview & Contract Ingestion",
      subtitle: "Secure document upload, privacy acknowledgment & coherence pipeline execution",
    },
    "contract-review": {
      title: "Contract Review Workspace",
      subtitle: "Dual-channel anomaly inspection, sequence coherence & clause navigation",
    },
    analytics: {
      title: "Analytics & Structural Findings",
      subtitle: "Deterministic rule flags, completeness coverage & conformal confidence bounds",
    },
    explainability: {
      title: "Explainability Workspace (XAI)",
      subtitle: "Integrated Gradients token attribution & Channel B neighbor sensitivity",
    },
    feedback: {
      title: "Reviewer Recalibration",
      subtitle: "Reviewer observations with self-reported provenance",
    },
    "robustness-lab": {
      title: "Self Red-Team Robustness Laboratory",
      subtitle: "Controlled contract perturbations, sensitivity evaluation & zero-mutation guarantees",
    },
    transparency: {
      title: "Model Transparency & Benchmarks",
      subtitle: "Unbiased empirical baselines, clean SEC false positive rates & research limitations",
    },
  };

  const currentMeta = sectionMeta[activeSection] || sectionMeta.overview;

  return (
    <>
      <header className="header-bar" role="banner">
        <div className="header-left">
          <button
            type="button"
            className="mobile-nav-toggle"
            aria-label="Open lateral navigation"
            onClick={onOpenMobileNav}
          >
            <Menu size={20} />
          </button>
          <div className="header-title-group">
            <h1>{currentMeta.title}</h1>
            <p>{currentMeta.subtitle}</p>
          </div>
        </div>

        <div className="header-right">
          {/* Real Backend Status Indicator */}
          <div
            id="backend-status-pill"
            className="status-pill"
            role="status"
            aria-live="polite"
            title={`Backend status: ${backendStatus}`}
          >
            <span
              className={`status-dot ${backendStatus}`}
              aria-hidden="true"
            />
            <span style={{ textTransform: "capitalize" }}>
              API: {backendStatus}
            </span>
          </div>

          {/* Connection / API Key Toggle */}
          <button
            id="connection-settings-toggle"
            type="button"
            className="btn btn-secondary"
            style={{ padding: "0.35rem 0.65rem", fontSize: "0.78rem" }}
            onClick={() => setShowSettings(!showSettings)}
            aria-expanded={showSettings}
            aria-controls="connection-settings-panel"
            aria-label="Toggle backend API connection settings"
          >
            <Settings size={14} aria-hidden="true" />
            <span>Connection</span>
            {showSettings ? <ChevronUp size={12} aria-hidden="true" /> : <ChevronDown size={12} aria-hidden="true" />}
          </button>

          {/* Theme Toggle (3-way) */}
          <ThemeToggle />
        </div>
      </header>

      {/* Connection Settings Drawer (Always rendered in DOM for selector continuity) */}
      <section
        id="connection-settings-panel"
        className="settings-drawer"
        role="region"
        aria-label="Backend Connection Configuration"
        style={{ display: showSettings ? "flex" : "none" }}
      >
          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <Server size={14} style={{ color: "var(--color-text-secondary)" }} aria-hidden="true" />
            <label
              htmlFor="backend-url-input"
              style={{ fontSize: "0.78rem", fontWeight: 600, color: "var(--color-text-secondary)" }}
            >
              API URL:
            </label>
            <input
              id="backend-url-input"
              type="text"
              aria-label="API Backend URL"
              value={backendUrl}
              onChange={(e) => onBackendUrlChange(e.target.value)}
              className="input-field"
              style={{ width: "220px", fontSize: "0.8rem", padding: "0.35rem 0.6rem" }}
            />
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <KeyRound size={14} style={{ color: "var(--color-text-secondary)" }} aria-hidden="true" />
            <label
              htmlFor="api-key-input"
              style={{ fontSize: "0.78rem", fontWeight: 600, color: "var(--color-text-secondary)" }}
            >
              API Key:
            </label>
            <input
              id="api-key-input"
              type="password"
              aria-label="API Key (X-API-Key)"
              value={apiKey}
              onChange={(e) => onApiKeyChange(e.target.value)}
              placeholder="X-API-Key header"
              className="input-field"
              style={{ width: "200px", fontSize: "0.8rem", padding: "0.35rem 0.6rem" }}
            />
          </div>

          <small style={{ fontSize: "0.72rem", color: "var(--color-text-muted)" }}>
            * Credentials remain in memory during local session; never stored to localStorage.
          </small>
        </section>
    </>
  );
}
