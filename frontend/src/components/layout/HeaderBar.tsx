"use client";
import { Menu } from "lucide-react";
import { NavSection, SECTION_TITLES } from "./SidebarNav";
export function HeaderBar({ activeSection, backendStatus, authenticated, localEngine, onOpenMobileNav, onSettings }: {
  activeSection: NavSection; backendStatus: "online" | "offline" | "checking"; authenticated: boolean; localEngine: boolean;
  onOpenMobileNav: () => void; onSettings: () => void;
}) {
  const status = backendStatus === "online" ? authenticated ? `${localEngine ? "Local" : "Configured"} engine connected` : "Engine available" : backendStatus === "checking" ? "Checking engine" : "Engine unavailable";
  return <header className="header-bar"><div className="header-left"><button type="button" className="mobile-nav-toggle" aria-label="Open navigation" aria-controls="app-sidebar" onClick={onOpenMobileNav}><Menu size={21} /></button>
    <h1 id="page-title" tabIndex={-1}>{SECTION_TITLES[activeSection]}</h1></div>
    <button className="engine-status" type="button" onClick={onSettings} aria-label={`${status}. Open Settings`}><span className={`status-dot ${backendStatus}`} aria-hidden="true" /><span id="backend-status-pill" role="status">{status}</span></button>
  </header>;
}
