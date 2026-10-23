"use client";

import React from "react";
import {
  LayoutDashboard,
  BookOpenCheck,
  BarChart3,
  BrainCircuit,
  MessageSquareCheck,
  ShieldCheck,
  Scale,
  X,
  FlaskConical,
} from "lucide-react";

export type NavSection =
  | "overview"
  | "contract-review"
  | "analytics"
  | "explainability"
  | "feedback"
  | "robustness-lab"
  | "transparency";

interface SidebarNavProps {
  activeSection: NavSection;
  onSelectSection: (section: NavSection) => void;
  mobileOpen: boolean;
  onCloseMobile: () => void;
  documentLoaded: boolean;
}

export function SidebarNav({
  activeSection,
  onSelectSection,
  mobileOpen,
  onCloseMobile,
  documentLoaded,
}: SidebarNavProps) {
  const primaryNavItems: {
    id: NavSection;
    label: string;
    icon: React.ComponentType<{ size?: number; className?: string; "aria-hidden"?: boolean | "true" | "false" }>;
    badge?: string;
  }[] = [
    { id: "overview", label: "Overview", icon: LayoutDashboard },
    {
      id: "contract-review",
      label: "Contract Review",
      icon: BookOpenCheck,
      badge: documentLoaded ? "Ready" : undefined,
    },
    { id: "analytics", label: "Analytics & Findings", icon: BarChart3 },
    { id: "explainability", label: "Explainability", icon: BrainCircuit },
    { id: "feedback", label: "Reviewer Feedback", icon: MessageSquareCheck },
    {
      id: "robustness-lab",
      label: "Robustness Lab",
      icon: FlaskConical,
      badge: "P4D",
    },
  ];

  const handleNavClick = (sectionId: NavSection) => {
    onSelectSection(sectionId);
    if (mobileOpen) {
      onCloseMobile();
    }
  };

  return (
    <aside
      id="app-sidebar"
      className={`sidebar ${mobileOpen ? "mobile-open" : ""}`}
      aria-label="Application Lateral Navigation"
    >
      <div className="sidebar-header">
        <div className="sidebar-brand">
          <div className="brand-icon" aria-hidden="true">
            <Scale size={18} />
          </div>
          <div>
            <div className="brand-title">LexAudit</div>
            <div className="brand-subtitle">Contract Intelligence</div>
          </div>
        </div>
        {mobileOpen && (
          <button
            type="button"
            className="mobile-nav-toggle"
            aria-label="Close lateral navigation"
            onClick={onCloseMobile}
          >
            <X size={18} />
          </button>
        )}
      </div>

      <nav className="sidebar-nav" aria-label="Primary Navigation">
        <div className="nav-section-title">Audit Workspace</div>
        {primaryNavItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeSection === item.id;
          return (
            <button
              key={item.id}
              id={`nav-${item.id}`}
              type="button"
              className={`sidebar-link ${isActive ? "active" : ""}`}
              onClick={() => handleNavClick(item.id)}
              aria-current={isActive ? "page" : undefined}
            >
              <Icon size={18} className="nav-icon" aria-hidden={true} />
              <span style={{ flexGrow: 1 }}>{item.label}</span>
              {item.badge && (
                <span
                  style={{
                    fontSize: "0.65rem",
                    padding: "0.1rem 0.4rem",
                    borderRadius: "4px",
                    background: isActive ? "rgba(255,255,255,0.2)" : "rgba(37,99,235,0.2)",
                    color: isActive ? "#FFFFFF" : "#60A5FA",
                    fontWeight: 700,
                  }}
                >
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}

        <div className="nav-section-title" style={{ marginTop: "1rem" }}>
          Governance &amp; Science
        </div>
        <button
          id="nav-transparency"
          type="button"
          className={`sidebar-link ${activeSection === "transparency" ? "active" : ""}`}
          onClick={() => handleNavClick("transparency")}
          aria-current={activeSection === "transparency" ? "page" : undefined}
        >
          <ShieldCheck size={18} className="nav-icon" aria-hidden={true} />
          <span>Transparency &amp; Benchmarks</span>
        </button>
      </nav>

      <div className="sidebar-footer">
        <div className="sidebar-badge">
          <strong>Academic Prototype</strong>
          <br />
          Dual-Channel Coherence v1.0
        </div>
      </div>
    </aside>
  );
}
