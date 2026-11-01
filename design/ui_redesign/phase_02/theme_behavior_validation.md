# Phase 2 Theme Behavior & Hydration Validation

**Project:** Legal Contract Coherence Auditor (`LexAudit`)  
**Validation Suite:** Theme Switching, Persistence & Zero-Flicker Hydration  
**Verification Tool:** Chrome DevTools Protocol (CDP) Automation  
**Evidence Artifacts:** `theme_01_dark_mode_1440x900.png`, `theme_02_reload_persistence_dark.png`  

---

## 1. Theme State Resolution Matrix

| Scenario | `localStorage["lexaudit_theme"]` | OS `prefers-color-scheme` | Resolved `data-theme` | Resolved `color-scheme` | Verified Behavior |
|---|:---:|:---:|:---:|:---:|---|
| **Fresh Visitor (No Saved Pref)** | `null` | Any (`dark` or `light`) | `light` | `light` | Default light theme rendered |
| **Explicit Light Selection** | `"light"` | Any | `light` | `light` | Light theme applied & persisted |
| **Explicit Dark Selection** | `"dark"` | Any | `dark` | `dark` | Dark theme applied & persisted |
| **System Selection (OS Dark)** | `"system"` | `dark` | `dark` | `dark` | Dynamically tracks OS dark |
| **System Selection (OS Light)** | `"system"` | `light` | `light` | `light` | Dynamically tracks OS light |
| **Hard Reload after Dark Choice** | `"dark"` | Any | `dark` | `dark` | 0ms flicker pre-paint application |

---

## 2. Zero-Flicker Pre-Hydration Architecture

### 2.1 The Hydration FOUC Problem
In standard Next.js App Router applications, relying on a client-side `useEffect` hook to read `localStorage` causes a visible flash of unstyled content (FOUC). The server initially delivers light mode HTML, the browser paints it, React hydrates 100-300ms later, and only then switches the class to dark mode, jarring the user.

### 2.2 Implemented LexAudit Solution
1. **HTML Server Default:** `<html lang="en" data-theme="light" suppressHydrationWarning ...>`
2. **Synchronous Head Script:** A blocking inline JavaScript script is placed in `<head>` and at the opening of `<body>` before any UI markup is evaluated:
   ```javascript
   (function() {
     try {
       var stored = localStorage.getItem('lexaudit_theme');
       var resolved = 'light';
       if (stored === 'dark') {
         resolved = 'dark';
       } else if (stored === 'system') {
         resolved = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
       } else {
         resolved = 'light';
       }
       document.documentElement.setAttribute('data-theme', resolved);
       document.documentElement.setAttribute('data-theme-preference', stored || 'light');
       document.documentElement.style.colorScheme = resolved;
     } catch (e) {}
   })();
   ```
3. **Outcome:** When the browser parses the HTML stream, the script executes immediately. By the time the browser renders the first pixel (First Contentful Paint), `data-theme` is already set to the user's preference.

---

## 3. Storage Privacy & Security Enforcement

Inspection of `ThemeContext.tsx` and runtime browser storage confirms:
- The only key written to `localStorage` is `lexaudit_theme`.
- Permitted values are strictly validated to: `"light"`, `"dark"`, `"system"`.
- Zero contract plaintext, uploaded files, API tokens, or analysis outputs are written to browser persistent storage.
