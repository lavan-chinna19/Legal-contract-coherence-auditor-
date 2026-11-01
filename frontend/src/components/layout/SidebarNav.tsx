"use client";
import { useEffect, useRef } from "react";
import { FilePlus2, BookOpenCheck, Files, Settings, FlaskConical, Scale, X } from "lucide-react";
export type NavSection = "new-audit" | "audit-results" | "reports-history" | "settings" | "research-tools";
export const SECTION_TITLES: Record<NavSection, string> = {
  "new-audit": "New Audit", "audit-results": "Audit Results", "reports-history": "Reports & History", settings: "Settings", "research-tools": "Research Tools",
};
export function SidebarNav({ activeSection, onSelectSection, mobileOpen, onCloseMobile }: {
  activeSection: NavSection; onSelectSection: (section: NavSection) => void; mobileOpen: boolean; onCloseMobile: () => void;
}) {
  const ref = useRef<HTMLElement>(null);
  useEffect(() => { if (mobileOpen) ref.current?.querySelector<HTMLButtonElement>(".mobile-close")?.focus(); }, [mobileOpen]);
  const items = [{ id: "new-audit", icon: FilePlus2 }, { id: "audit-results", icon: BookOpenCheck }, { id: "reports-history", icon: Files }, { id: "settings", icon: Settings }] as const;
  return <aside ref={ref} id="app-sidebar" className={`sidebar ${mobileOpen ? "mobile-open" : ""}`}
    role={mobileOpen ? "dialog" : undefined} aria-modal={mobileOpen || undefined} aria-label="LexAudit navigation"
    onKeyDown={e => {
      if (!mobileOpen) return;
      if (e.key === "Escape") { e.preventDefault(); onCloseMobile(); }
      if (e.key === "Tab") {
        const buttons = Array.from(ref.current?.querySelectorAll<HTMLButtonElement>("button") || []);
        const first = buttons[0], last = buttons[buttons.length - 1];
        if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last?.focus(); }
        else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first?.focus(); }
      }
    }}>
    <div className="sidebar-header"><div className="sidebar-brand"><Scale size={24} aria-hidden="true" /><span className="brand-title">LexAudit</span></div>
      <button type="button" className="mobile-nav-toggle mobile-close" aria-label="Close navigation" onClick={onCloseMobile}><X size={20} /></button></div>
    <nav className="sidebar-nav" aria-label="Primary navigation">{items.map(({ id, icon: Icon }) => <button key={id} id={`nav-${id}`} type="button"
      className={`sidebar-link ${activeSection === id ? "active" : ""}`} aria-current={activeSection === id ? "page" : undefined}
      onClick={() => onSelectSection(id)}><Icon size={18} aria-hidden="true" />{SECTION_TITLES[id]}</button>)}</nav>
    <div className="sidebar-footer"><button id="nav-research-tools" type="button" className={`sidebar-link ${activeSection === "research-tools" ? "active" : ""}`}
      aria-current={activeSection === "research-tools" ? "page" : undefined} onClick={() => onSelectSection("research-tools")}><FlaskConical size={18} aria-hidden="true" />Research Tools</button>
      <p className="sidebar-note">Optional research workspaces</p></div>
  </aside>;
}
