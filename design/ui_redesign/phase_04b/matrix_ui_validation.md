# Phase 4B — Track A Heatmap UI Implementation & Representation Audit

**Project:** Legal Contract Coherence Auditor (LexAudit)  
**Phase:** 4B — Learned Clause-Pair Compatibility Map  
**Date:** 2026-10-14  
**Author:** Senior Next.js/React Architect & Scientific Visualization Designer  
**Status:** PASS  

---

## 1. Component Architecture & Modular Layout

The Track A visualization was implemented under `frontend/src/components/flow/` as an autonomous, evidence-grounded research workspace:

1. **`LearnedCompatibilityWorkspace.tsx`:** Master container managing artifact loading, state filtering, selection tracking, error boundaries, and empty/loading states.
2. **`ClauseTypeSelector.tsx`:** Category search bar and quick-preset switcher:
   - **Full Matrix:** $66 \times 66 = 4,356$ cells.
   - **Core Commercial:** 12 primary contractual clauses ($12 \times 12 = 144$ cells) including Entire Agreement, Governing Laws, Counterparts, Term, Notices, Indemnifications, Representations, and Confidentiality.
   - **Boilerplate:** 10 standard legal boilerplate categories ($10 \times 10 = 100$ cells).
3. **`CompatibilityMatrixLegend.tsx`:** Continuous scientific 4-stop gradient strip (#991b1b $\to$ #d97706 $\to$ #15803d $\to$ #2563eb) mapping low compatibility (high discontinuity) to high compatibility (coherent transition).
4. **`CompatibilityHeatmap.tsx`:** Interactive SVG/CSS grid visualizer with hover tooltips, cell selection rings, keyboard navigation (Tab, Enter, Space), and a one-click toggle to an **Accessible Table Alternative**.
5. **`CompatibilityDetails.tsx`:** Detailed cell inspector showing forward score $P(A \to B)$, reverse score $P(B \to A)$, directional asymmetry delta $\Delta$, and Channel B anomaly equivalence ($1.0 - P$).
6. **`CompatibilityMethodology.tsx`:** Collapsible technical specification detailing mathematical feature formulation, checkpoint provenance, and strict non-empirical/non-Markov disclosures.

---

## 2. Representation Fidelity & Interpretability Safeguards

1. **Axes Representation:**
   - **Vertical Axis (Rows):** Preceding / Antecedent Clause Category ($c_i$).
   - **Horizontal Axis (Columns):** Following / Successor Clause Category ($c_j$).
2. **Directional Sensitivity:**
   Clicking a cell ($c_i \to c_j$) immediately evaluates the transpose cell ($c_j \to c_i$), computing the directional asymmetry $\Delta = M_{ij} - M_{ji}$ and highlighting which ordering the frozen neural head favors.
3. **No Fabricated Legal Supercategories:**
   Displays genuine LexGLUE LEDGAR labels directly without inventing artificial legal taxonomy buckets.
4. **Distinction from Empirical Frequency:**
   The UI clearly emphasizes that cell scores reflect neural embedding similarity and feature compatibility learned under binary cross-entropy, not observed frequencies in historical contracts.

---

## 3. Accessibility & Responsive Verification

- **Accessible Table Alternative:** Provides full textual and tabular parity for screen readers and keyboard users, rendering sortable columns for Antecedent, Successor, Forward Compatibility, Reverse Compatibility, and Asymmetry Delta.
- **Responsive Layout:**
  - On desktop (1440x900 and 1024x768), cells render with legible labels and hover tooltips.
  - On mobile (390x844), horizontal scrolling is contained within `#flow-heatmap-container` using custom scrollbars, preventing page-level horizontal overflow (`document.documentElement.scrollWidth <= window.innerWidth`).
- **Theme Support:** Fully verified in both Light and Dark modes (`data-theme="light"` and `data-theme="dark"`).
