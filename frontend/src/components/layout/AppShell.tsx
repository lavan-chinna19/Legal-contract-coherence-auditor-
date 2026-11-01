"use client";
import { useEffect, useState, type ReactNode } from "react";
import { SidebarNav, NavSection } from "./SidebarNav";
import { HeaderBar } from "./HeaderBar";
export function AppShell({ children, activeSection, onSelectSection, backendStatus, authenticated, localEngine }: {
  children: ReactNode; activeSection: NavSection; onSelectSection: (section: NavSection) => void;
  backendStatus: "online" | "offline" | "checking"; authenticated: boolean; localEngine: boolean;
}) {
  const [mobileOpen, setMobileOpen] = useState(false);
  useEffect(() => { window.scrollTo({ top: 0, behavior: "instant" }); document.getElementById("page-title")?.focus({ preventScroll: true }); }, [activeSection]);
  function navigate(section: NavSection) { window.scrollTo({ top: 0, behavior: "instant" }); onSelectSection(section); setMobileOpen(false); if (section === activeSection) requestAnimationFrame(() => document.getElementById("page-title")?.focus({ preventScroll: true })); }
  function close() { setMobileOpen(false); requestAnimationFrame(() => document.querySelector<HTMLButtonElement>('button[aria-label="Open navigation"]')?.focus()); }
  return <div className="app-shell"><a className="skip-link" href="#main-content">Skip to content</a>
    <SidebarNav activeSection={activeSection} onSelectSection={navigate} mobileOpen={mobileOpen} onCloseMobile={close} />
    {mobileOpen && <button className="mobile-overlay mobile-open" aria-label="Close navigation backdrop" tabIndex={-1} onClick={close} />}
    <div className="main-wrapper" inert={mobileOpen || undefined}><HeaderBar activeSection={activeSection} backendStatus={backendStatus} authenticated={authenticated} localEngine={localEngine} onOpenMobileNav={() => setMobileOpen(true)} onSettings={() => navigate("settings")} />
      <main className="app-content" id="main-content"><p className="compact-disclaimer">Decision support · Not legal advice. Automated findings require human review.</p>{children}</main>
    </div></div>;
}
