# Phase 2 Navigation Compatibility & View Mapping Matrix

**Project:** Legal Contract Coherence Auditor (`LexAudit`)  
**Scope:** New 5-Section Sidebar Navigation vs. Legacy Tabs Continuity  

---

## 1. Navigation Mapping Table

Phase 2 introduces a persistent lateral navigation structure while maintaining 100% backward compatibility with all legacy test selectors (`.tab-nav`, `.tab-btn`, `#tab-upload`, etc.).

| Sidebar Navigation Section | DOM ID | Icon (Lucide) | Target Functional View | Legacy In-Workspace Tab | Unloaded Behavior |
|---|---|---|---|---|---|
| **Overview** | `#nav-overview` | `LayoutDashboard` | Ingest Contract, Confidentiality Disclosure, Privacy Consent Checkbox, Upload & Pipeline Trigger | `1. Upload & Ingest` (`#tab-upload`) | Fully interactive upload form |
| **Contract Review** | `#nav-contract-review` | `BookOpenCheck` | Sequence Coherence Heatmap, Interactive Clause Findings List, Agreement Metrics | `2. Coherence Heatmap & Findings` (`#tab-results`) | Displays `EmptyState`: "No Active Contract in Review" with CTA button |
| **Analytics & Findings** | `#nav-analytics` | `BarChart3` | KPI Summary Cards, Rule-Based Structural Violations List | `2. Coherence Heatmap & Findings` (`#tab-results`) | Displays `EmptyState`: "No Active Contract in Review" with CTA button |
| **Explainability** | `#nav-explainability` | `BrainCircuit` | Integrated Gradients Token Attribution, Channel B Perturbation Sensitivity | `3. Explainability (XAI)` (`#tab-xai`) | Displays `EmptyState`: "Explainability Unavailable" with CTA button |
| **Reviewer Feedback** | `#nav-feedback` | `MessageSquareCheck` | Clause Recalibration Selector, Reviewer Verdict (`CONFIRM_ANOMALY`/`REJECT_ANOMALY`), Signature ID, Provenance | `4. Reviewer Feedback` (`#tab-feedback`) | Displays `EmptyState`: "Feedback Interface Inactive" with CTA button |
| **Transparency & Benchmarks** | `#nav-transparency` | `ShieldCheck` | Empirical Baseline Table, Kendall's Tau, Clean SEC False Positive Rates | `5. Transparency & Baselines` (`#tab-transparency`) | Always accessible regardless of contract upload |

---

## 2. Synchronization Logic

In `frontend/src/app/page.tsx`, `activeSection` and `activeTab` are synchronized bi-directionally:
1. Clicking any lateral navigation link (`#nav-*`) updates both `activeSection` and the corresponding `activeTab`.
2. Clicking any legacy tab button (`#tab-*`) updates both `activeTab` and the corresponding `activeSection`.
3. Selecting a clause in Contract Review preserves `selectedClauseId` across the Explainability and Feedback sections.
4. Uploading and completing a contract analysis automatically advances navigation to `Contract Review` (`activeTab = "results"`).
