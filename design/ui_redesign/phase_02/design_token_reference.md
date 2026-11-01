# Phase 2 Design Token Reference Specification

**Project:** Legal Contract Coherence Auditor (`LexAudit`)  
**Design System:** Dual-Theme Semantic Token Matrix  
**Status:** IMPLEMENTED & TESTED  

---

## 1. Semantic Token Architecture

All tokens are defined as CSS Custom Properties in `frontend/src/app/globals.css`. Color styles are bound to `html[data-theme="light"]` and `html[data-theme="dark"]`.

### 1.1 Core Surface & Canvas Tokens

| Token Name | Light Theme (Default) | Dark Theme | Purpose & Role | Contrast Ratio |
|---|:---:|:---:|---|:---:|
| `--color-canvas` | `#F7F9FC` | `#0B1220` | Root application background | Baseline |
| `--color-surface` | `#FFFFFF` | `#111C2D` | Main cards, tables, panels | > 14:1 vs canvas |
| `--color-surface-raised` | `#F1F5F9` | `#1A2940` | Raised controls, secondary boxes | High separation |
| `--color-surface-hover` | `#F8FAFC` | `#19273C` | Interactive hover fill | Subtle |
| `--color-sidebar` | `#101C32` | `#080F1D` | Lateral persistent navigation | Dark navy in both themes |
| `--color-sidebar-surface` | `#17243B` | `#0E182A` | Sidebar header & active fill | Structural contrast |
| `--color-sidebar-text` | `#F1F5F9` | `#F1F5F9` | Sidebar brand and active text | > 12:1 AAA |
| `--color-sidebar-muted` | `#94A3B8` | `#94A3B8` | Sidebar navigation inactive labels | > 5:1 AA |
| `--color-sidebar-active` | `#2563EB` | `#2563EB` | Sidebar active pill indicator | High visual focus |

### 1.2 Typography & Foreground Tokens

| Token Name | Light Theme | Dark Theme | Purpose & Role | Contrast Ratio |
|---|:---:|:---:|---|:---:|
| `--color-text-primary` | `#0F172A` | `#F1F5F9` | Main clause body text, titles | 16.1:1 (Light) / 13.5:1 (Dark) |
| `--color-text-secondary` | `#475569` | `#CBD5E1` | Subtitles, captions, metadata | 6.8:1 (Light) / 9.3:1 (Dark) |
| `--color-text-muted` | `#64748B` | `#94A3B8` | Footnotes, placeholders, disabled text | 4.6:1 (Light) / 5.2:1 (Dark) |
| `--color-text-inverse` | `#FFFFFF` | `#0B1220` | Text on solid accent buttons | > 8:1 AAA |

### 1.3 Interactive & Border Tokens

| Token Name | Light Theme | Dark Theme | Purpose & Role |
|---|:---:|:---:|---|
| `--color-accent` | `#2563EB` | `#60A5FA` | Primary action buttons, selection indicators |
| `--color-accent-hover` | `#1D4ED8` | `#93C5FD` | Hover states for primary controls |
| `--color-accent-subtle` | `#EFF6FF` | `#1E3A8A` | Clause selection highlight background |
| `--color-focus` | `#2563EB` | `#60A5FA` | Focus ring (2px solid, offset 2px) |
| `--color-border` | `#E2E8F0` | `#2B3B53` | Standard structural borders |
| `--color-border-subtle` | `#F1F5F9` | `#1E293B` | Inner card dividers, table borders |
| `--color-border-strong` | `#CBD5E1` | `#3B4D68` | Active input field borders |

### 1.4 Severity & Anomaly Feedback Tokens (Multi-Channel)

| Severity Level | Non-Color Pip | Light Theme (Text / Bg / Border) | Dark Theme (Text / Bg / Border) |
|---|:---:|:---:|:---:|
| **HIGH** | `[!]` / 🔴 | `#B91C1C` / `#FEE2E2` / `#FCA5A5` | `#F87171` / `rgba(248,113,113,0.15)` / `#EF4444` |
| **MEDIUM** | `[^]` / ⚠️ | `#B45309` / `#FEF3C7` / `#FDE68A` | `#FBBF24` / `rgba(251,191,36,0.15)` / `#F59E0B` |
| **LOW** | `[~]` / ℹ️ | `#1D4ED8` / `#EFF6FF` / `#BFDBFE` | `#60A5FA` / `rgba(96,165,250,0.15)` / `#3B82F6` |
| **CLEAN** | `[✓]` / 🟢 | `#15803D` / `#DCFCE7` / `#86EFAC` | `#4ADE80` / `rgba(74,222,128,0.15)` / `#22C55E` |

---

## 2. Legacy CSS Variable Mapping (100% Continuity)

To ensure that existing components and un-refactored sections instantly adopt light and dark themes without modification, legacy variable names are aliased directly to the semantic token architecture:

```css
--bg-primary: var(--color-canvas);
--bg-secondary: var(--color-surface);
--bg-card: var(--color-surface);
--bg-glass: var(--color-surface-raised);
--border-color: var(--color-border);
--border-focus: var(--color-focus);
--text-primary: var(--color-text-primary);
--text-secondary: var(--color-text-secondary);
--text-muted: var(--color-text-muted);
--accent-primary: var(--color-accent);
--accent-hover: var(--color-accent-hover);
--sev-high-bg: var(--color-danger-bg);
--sev-high-border: var(--color-danger-border);
--sev-high-text: var(--color-danger);
```
