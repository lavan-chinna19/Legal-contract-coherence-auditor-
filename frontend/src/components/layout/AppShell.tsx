"use client";

import React, { useState } from "react";
import { SidebarNav, NavSection } from "./SidebarNav";
import { HeaderBar } from "./HeaderBar";
import { AlertTriangle } from "lucide-react";

interface AppShellProps {
  children: React.ReactNode;
  activeSection: NavSection;
  onSelectSection: (section: NavSection) => void;
  backendStatus: "online" | "offline" | "checking";
  backendUrl: string;
  onBackendUrlChange: (url: string) => void;
  apiKey: string;
  onApiKeyChange: (key: string) => void;
  documentLoaded: boolean;
}

export function AppShell({
  children,
  activeSection,
  onSelectSection,
  backendStatus,
  backendUrl,
  onBackendUrlChange,
  apiKey,
  onApiKeyChange,
  documentLoaded,
}: AppShellProps) {
  const [mobileOpen, setMobileOpen] = useState(false);

  const DISCLAIMER_TEXT =
    "Academic Research Prototype — Not Legal Advice: This system is an academic research prototype evaluating structural and semantic coherence in legal contracts. Predictions and anomaly scores do not constitute legal advice, enforceability certification, or formal document review.";

  return (
    <div className="app-shell">
      {/* Lateral Persistent Sidebar */}
      <SidebarNav
        activeSection={activeSection}
        onSelectSection={onSelectSection}
        mobileOpen={mobileOpen}
        onCloseMobile={() => setMobileOpen(false)}
        documentLoaded={documentLoaded}
      />

      {/* Mobile Backdrop Overlay */}
      <div
        className={`mobile-overlay ${mobileOpen ? "mobile-open" : ""}`}
        onClick={() => setMobileOpen(false)}
        aria-hidden="true"
      />

      {/* Main Column */}
      <div className="main-wrapper">
        <HeaderBar
          activeSection={activeSection}
          backendStatus={backendStatus}
          backendUrl={backendUrl}
          onBackendUrlChange={onBackendUrlChange}
          apiKey={apiKey}
          onApiKeyChange={onApiKeyChange}
          onOpenMobileNav={() => setMobileOpen(true)}
        />

        <main className="app-content" id="main-content">
          {/* Prominent Global Disclaimer Banner on Every View */}
          <div
            className="disclaimer-banner"
            role="region"
            aria-label="Academic Research Disclaimer"
          >
            <AlertTriangle size={18} style={{ flexShrink: 0 }} aria-hidden="true" />
            <span>{DISCLAIMER_TEXT}</span>
          </div>

          {children}
        </main>
      </div>
    </div>
  );
}
