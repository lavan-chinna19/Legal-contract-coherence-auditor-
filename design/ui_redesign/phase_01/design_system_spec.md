# Design System Specification — Light/Dark Theme System

**Module:** UI Redesign Program — Phase 1  
**Authors:** Design System Engineer & Accessibility Specialist  
**Date:** October 10, 2026  
**Status:** COMPLETE (Design System Specification)  

---

## 1. Design System Philosophy

The **LexAudit Design System** provides a dual-theme, high-legibility foundation engineered specifically for reading, evaluating, and annotating dense legal documents. Unlike generic consumer web apps, a legal intelligence workspace demands:
- High contrast and crisp typographic hierarchy.
- Restrained color application that reserves chromatic intensity for anomaly severity.
- Clear non-color indicators (icons and textual pills) for accessibility.
- Zero hydration flicker when loading user theme preferences.

---

## 2. Semantic Color Token Matrix

### 2.1 Complete Token Definitions

| Token Name | Light Theme (Default) | Dark Theme | Purpose / Usage | WCAG AA Contrast |
|---|:---:|:---:|---|:---:|
| `--bg-canvas` | `#F7F9FC` | `#0B1220` | Root application background | Baseline |
| `--bg-surface` | `#FFFFFF` | `#111C2D` | Main content panels, review workspace | > 14:1 vs canvas |
| `--bg-surface-elevated` | `#F1F5F9` | `#1A2940` | Modals, dropdowns, sticky headers | High contrast |
| `--bg-sidebar` | `#101C32` | `#080F1D` | Lateral primary navigation bar | Dark in both themes |
| `--text-primary` | `#0F172A` | `#F1F5F9` | Main clause text, card headers, table data | > 12:1 (AAA) |
| `--text-secondary` | `#475569` | `#94A3B8` | Subheaders, metadata, timestamps, notes | > 5.5:1 (AA) |
| `--text-muted` | `#64748B` | `#64748B` | Footers, disabled labels, placeholders | > 4.5:1 (AA) |
| `--text-inverse` | `#FFFFFF` | `#0B1220` | Text on solid accent buttons | > 7:1 (AAA) |
| `--border-subtle` | `#E2E8F0` | `#1E293B` | Clause dividers, card boundaries | Structural |
| `--border-strong` | `#CBD5E1` | `#2B3B53` | Input fields, active tab dividers | Structural |
| `--accent-primary` | `#2563EB` | `#60A5FA` | Primary buttons, active clause highlight | > 4.8:1 (AA) |
| `--accent-hover` | `#1D4ED8` | `#3B82F6` | Interactive hover states | High |
| `--accent-subtle` | `#EFF6FF` | `#1E3A8A` | Active tab backgrounds, clause selection | Soft fill |
| `--focus-ring` | `#2563EB` | `#60A5FA` | Keyboard focus ring (2px solid, offset 2px) | Accessible focus |

### 2.2 Severity Status Tokens (Multi-Channel Encoding)

Color alone is **never** used as the sole indicator of severity. Each severity level combines a dedicated chromatic token, a background fill, an explicit text label, and an accompanying non-color geometric indicator.

| Severity Level | Non-Color Pip | Light Theme Tokens | Dark Theme Tokens | Visual Encoding |
|---|:---:|---|---|---|
| **HIGH** | `[!]` / 🔴 | Text: `#B91C1C`<br>Bg: `#FEE2E2`<br>Border: `#FCA5A5` | Text: `#F87171`<br>Bg: `rgba(248, 113, 113, 0.15)`<br>Border: `#EF4444` | Solid red left clause pip (4px width) + Bold uppercase tag |
| **MEDIUM** | `[^]` / ⚠️ | Text: `#B45309`<br>Bg: `#FEF3C7`<br>Border: `#FDE68A` | Text: `#FBBF24`<br>Bg: `rgba(251, 191, 36, 0.15)`<br>Border: `#F59E0B` | Solid amber left clause pip (4px width) + Outlined tag |
| **LOW** | `[~]` / ℹ️ | Text: `#1D4ED8`<br>Bg: `#EFF6FF`<br>Border: `#BFDBFE` | Text: `#60A5FA`<br>Bg: `rgba(96, 165, 250, 0.15)`<br>Border: `#3B82F6` | Subtle blue left clause pip (2px width) + Subtle tag |
| **CLEAN** | `[✓]` / 🟢 | Text: `#15803D`<br>Bg: `#DCFCE7`<br>Border: `#86EFAC` | Text: `#4ADE80`<br>Bg: `rgba(74, 222, 128, 0.15)`<br>Border: `#22C55E` | Thin neutral left border (1px) + Green verification badge |

---

## 3. Typographic System

### 3.1 Font Stacks
- **Interface & Legal Text:**  
  `Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif`  
  *Rationale:* High x-height, neutral letterforms, optimized for dense multi-paragraph legal clause readability.
- **Monospace Code, Section Indices & Hashes:**  
  `"JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace`  
  *Rationale:* Precise alignment for section numbers (e.g., `§ 14.2`), token badges, and SHA-256 hashes.

### 3.2 Type Hierarchy Scale

| Semantic Element | Font Size | Line Height | Weight | Letter Spacing | Usage |
|---|---|---|---|---|---|
| **Display Header** | `1.5rem` (24px) | `1.3` (31px) | 700 (Bold) | `-0.02em` | Application Title, Page Headings |
| **Section Title (H2)**| `1.125rem` (18px) | `1.4` (25px) | 600 (Semibold) | `-0.01em` | Panel titles, Workspace card headers |
| **Subheader (H3)** | `0.9375rem` (15px)| `1.4` (21px) | 600 (Semibold) | `0` | Finding cards, Clause index headers |
| **Legal Clause Body** | `0.875rem` (14px) | `1.65` (23px) | 400 (Regular) | `0` | Continuous contract text reading |
| **UI Body / Metadata**| `0.875rem` (14px) | `1.5` (21px) | 400 (Regular) | `0` | Inspector details, table rows |
| **Caption / Labels** | `0.75rem` (12px) | `1.4` (17px) | 500 (Medium) | `+0.02em` | Metric labels, form input labels |
| **Micro / Badges** | `0.6875rem` (11px)| `1.2` (13px) | 700 (Bold) | `+0.05em` | Severity tags, token badge scores |

---

## 4. Spacing, Layout & Elevation Scale

### 4.1 4px Spatial Grid
- `space-1`: `4px` (Inline icon gaps, badge padding)
- `space-2`: `8px` (Input padding, list item gaps)
- `space-3`: `12px` (Card padding compact, toolbar gaps)
- `space-4`: `16px` (Standard card padding, form grid gap)
- `space-6`: `24px` (Major panel padding, workspace gutters)
- `space-8`: `32px` (Section dividing gaps)

### 4.2 Elevation & Border Radii
- **Subtle Elevation (`shadow-sm`):** `0 1px 2px 0 rgba(0, 0, 0, 0.05)` (Cards in light mode)
- **Modal Elevation (`shadow-lg`):** `0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)`
- **Border Radii:**
  - `radius-sm`: `4px` (Badges, tags, pips)
  - `radius-md`: `6px` (Input fields, buttons)
  - `radius-lg`: `8px` (Cards, panels, inspectors)
  - `radius-full`: `9999px` (Status indicators, pill counters)

---

## 5. Theme Switching & Hydration Safety Architecture

To guarantee zero flash of unstyled content (FOUC) or hydration mismatches:

1. **Storage Mechanism:** Theme choice (`"light"` | `"dark"`) is persisted in `localStorage.getItem("lexaudit_theme")`.
2. **System Preference Fallback:** If unset, falls back to `window.matchMedia("(prefers-color-scheme: dark)").matches`.
3. **Flicker-Free Head Script:** A minimal inline synchronous script in `frontend/src/app/layout.tsx` reads `localStorage` before the first paint and immediately injects `data-theme="light"` or `data-theme="dark"` onto the `<html>` root:
   ```html
   <script>
     (function() {
       try {
         var t = localStorage.getItem('lexaudit_theme');
         if (!t) t = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
         document.documentElement.setAttribute('data-theme', t);
       } catch (e) {}
     })();
   </script>
   ```
4. **CSS Token Switching:** All styles are bound directly to `html[data-theme="light"]` and `html[data-theme="dark"]` custom properties, ensuring 100% instantaneous, flicker-free rendering.
