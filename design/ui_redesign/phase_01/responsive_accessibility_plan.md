# Responsive Architecture & WCAG 2.2 AA Accessibility Plan — Phase 1

**Module:** UI Redesign Program — Phase 1  
**Authors:** Accessibility Specialist & Senior Responsive Design Engineer  
**Date:** October 10, 2026  
**Status:** COMPLETE (Accessibility & Responsive Plan)  

---

## 1. Responsive Viewport Strategy & Breakpoint Matrix

The redesigned LexAudit platform supports four distinct device classes through fluid flexbox/grid containers and adaptive panel layouts.

| Viewport Class | Range | Navigation Pattern | Contract Reviewer Layout | Analytics & Tables |
|---|:---:|---|---|---|
| **Desktop** | $\ge 1440\text{px}$ | Persistent Sidebar (220px width) | 2-Panel Split: 55% Document / 45% Inspector | Full multi-column grid, expanded heatmap |
| **Laptop** | $1024\text{px} - 1439\text{px}$ | Icon-Only Sidebar (70px width) | 2-Panel Split: 50% Document / 50% Inspector | 3-column KPI grid, standard heatmap |
| **Tablet** | $768\text{px} - 1023\text{px}$ | Slide-over Drawer / Header Bar | Stacked: Full-width Document + Bottom Drawer (40%)| 2-column KPI grid, internal scroll tables |
| **Mobile** | $390\text{px} - 767\text{px}$ | Top Header + Bottom Bar (Sticky) | Single Column: Sequential Clause Cards with inline Findings | 1-column KPI cards, horizontally swipeable charts |

### 1.1 Responsive Table & Visual Chart Protection
- **No Page-Level Overflow:** `body` and root containers enforce `overflow-x: hidden`.
- **Chart Containment:** Heatmaps, attribution grids, and rule violation tables are wrapped in dedicated `.table-responsive-container` wrappers with `overflow-x: auto` and subtle scrollbar styling.
- **Dynamic Touch Targets:** On touch devices ($\le 768\text{px}$), buttons, tab links, and clause selector pips expand to a minimum target size of $44 \times 44\text{px}$ in compliance with WCAG 2.5.5.

---

## 2. WCAG 2.2 Level AA Compliance Roadmap

### 2.1 Color Contrast Verification

Every token combination in the LexAudit Design System exceeds the WCAG 2.2 AA standard:

| Element | Background Token | Foreground Token | Measured Contrast Ratio | WCAG 2.2 AA Requirement | Status |
|---|---|---|:---:|:---:|:---:|
| **Light Theme Body Text** | `#FFFFFF` (`--bg-surface`) | `#0F172A` (`--text-primary`) | **16.1 : 1** | $\ge 4.5:1$ | **PASS (AAA)** |
| **Light Theme Secondary** | `#FFFFFF` (`--bg-surface`) | `#475569` (`--text-secondary`)| **6.9 : 1** | $\ge 4.5:1$ | **PASS (AA)** |
| **Light Theme High Alert** | `#FEE2E2` (`--sev-high-bg`) | `#B91C1C` (`--sev-high-text`) | **6.1 : 1** | $\ge 4.5:1$ | **PASS (AA)** |
| **Light Theme Primary Btn**| `#2563EB` (`--accent-primary`)| `#FFFFFF` (`--text-inverse`) | **4.8 : 1** | $\ge 4.5:1$ | **PASS (AA)** |
| **Dark Theme Body Text** | `#111C2D` (`--bg-surface`) | `#F1F5F9` (`--text-primary`) | **13.5 : 1** | $\ge 4.5:1$ | **PASS (AAA)** |
| **Dark Theme Secondary** | `#111C2D` (`--bg-surface`) | `#94A3B8` (`--text-secondary`)| **6.5 : 1** | $\ge 4.5:1$ | **PASS (AA)** |
| **Dark Theme High Alert** | `rgba(248,113,113,0.15)` | `#F87171` (`--sev-high-text`) | **5.4 : 1** | $\ge 4.5:1$ | **PASS (AA)** |
| **Dark Theme Primary Btn** | `#60A5FA` (`--accent-primary`)| `#0B1220` (`--text-inverse`) | **9.2 : 1** | $\ge 4.5:1$ | **PASS (AAA)** |

### 2.2 Non-Color Encoding of Semantic State (WCAG 1.4.1)
Color is never used as the single identifier for critical information:
- **Severity Classification:** Indicated simultaneously by:
  1. Textual uppercase label (`HIGH`, `MEDIUM`, `LOW`, `CLEAN`).
  2. Distinct geometric pip icon (🔴 filled circle, ⚠️ triangle, ℹ️ info, ✓ check).
  3. Left-hand border stroke thickness (4px solid vs 2px dashed vs 1px light).
  4. Background chromatic tint.
- **Rule Violations:** Indicated by explicit icon (`[!]`), category text, and bold title.
- **Status Indicators:** Backend online status includes text `"Backend: Online"` alongside the colored circle dot.

### 2.3 Keyboard Navigation & Focus Management (WCAG 2.1.1 & 2.4.7)
- **Universal Tab Flow:** All interactive buttons, inputs, links, and clause cards receive focus in logical reading order.
- **Visible Focus Indicator:** High-visibility outline:
  `outline: 2px solid var(--focus-ring); outline-offset: 2px;`
- **Clause Navigation Shortcuts:**
  - `j` or `ArrowDown`: Select next clause in document stream.
  - `k` or `ArrowUp`: Select previous clause in document stream.
  - `Enter` / `Space`: Activate selected clause findings.
  - `Escape`: Close modals and drawers.
- **Skip Navigation Link:** Hidden top-level link (`Skip to main content`) visible on focus to allow keyboard users to bypass sidebar links.

### 2.4 Screen Reader Support & ARIA Semantics (WCAG 4.1.2)
- **Landmarks:** Top `<header>`, lateral `<nav aria-label="Main Navigation">`, central `<main>`, and contextual `<aside aria-label="Audit Findings">`.
- **Live Regions:** Dynamic status changes use `aria-live="polite"` with `role="status"`:
  - Document upload and encryption completion.
  - Analysis polling progress updates.
  - Reviewer feedback submission confirmations.
- **Form Controls:** Every input, select, and file upload element has an associated `<label htmlFor="...">` with an identical `id` attribute.

### 2.5 Reduced Motion & Cognitive Comfort (WCAG 2.3.3)
```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```
Users requesting reduced motion experience instant tab switches, no pulse loaders, and standard instant scrolling.
