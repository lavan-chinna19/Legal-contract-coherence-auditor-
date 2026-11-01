# Product UX Blueprint — Legal Contract Coherence Auditor ("LexAudit")

**Module:** UI Redesign Program — Phase 1  
**Authors:** Principal Product Designer & Senior LegalTech UX Architect  
**Date:** October 10, 2026  
**Status:** COMPLETE (Product Experience Blueprint)  

---

## 1. Product Identity & Design Vision

### 1.1 Brand Identity & Positioning
- **Primary Name:** **Legal Contract Coherence Auditor**
- **Short Brand Identifier:** **LexAudit**
- **Scientific Disclosure:** **Academic Research Prototype — Not Legal Advice**
- **Positioning Statement:** An executive-grade, AI-assisted workspace enabling legal counsels, compliance auditors, and NLP researchers to rapidly diagnose structural disorganization, semantic out-of-distribution clauses, dangling section references, and chronological contradictions in commercial agreements.

### 1.2 Core Design Tenets
1. **Document-Centric Integrity:** Legal agreements are not arbitrary cards; they are continuous legal instruments. The text must be preserved, readable, and presented in its authentic structural hierarchy.
2. **Bidirectional Coherence:** Clicking an anomaly finding immediately navigates to and highlights the clause in the document viewer; clicking a clause immediately focuses the corresponding diagnostic evidence.
3. **Traceable Scientific Transparency:** Every score is decomposed into its constituent channels (Semantic OOD vs. Discourse Transition), accompanied by conformal confidence intervals and bounded claim scopes.
4. **Professional Cognitive Ergonomics:** Clean light-mode default optimized for high-density reading of 50+ page agreements, paired with an elegant dark theme for extended nocturnal auditing sessions.
5. **No Decorative Distractions:** Zero cryptocurrency-style neon glows, glassmorphic blurs, or distracting animations. Every visual token serves document readability or diagnostic clarity.

---

## 2. Target User Personas & Core Journeys

```text
┌─────────────────────────┐   ┌──────────────────────────┐   ┌─────────────────────────┐
│ Senior Legal Counsel    │   │ NLP / AI Researcher      │   │ Contract QA Reviewer    │
│ - Audits draft M&A/SaaS │   │ - Validates embeddings   │   │ - Reviews flagged flags │
│ - Identifies broken §   │   │ - Evaluates XAI tokens   │   │ - Submits verdicts      │
│ - Verifies dates/terms  │   │ - Tests transfer bounds  │   │ - Calibrates thresholds │
└────────────┬────────────┘   └────────────┬─────────────┘   └────────────┬────────────┘
             │                             │                              │
             └───────────────────────┬─────┴──────────────────────────────┘
                                     ▼
                  ┌─────────────────────────────────────┐
                  │ 1. Document Upload & Privacy Guard  │
                  └──────────────────┬──────────────────┘
                                     ▼
                  ┌─────────────────────────────────────┐
                  │ 2. Asynchronous Polling (~3.0s)     │
                  └──────────────────┬──────────────────┘
                                     ▼
                  ┌─────────────────────────────────────┐
                  │ 3. Split-Screen Review Workspace    │
                  │   [Contract Doc] ◄► [Findings Panel]│
                  └──────────────────┬──────────────────┘
                                     ▼
               ┌─────────────────────┴─────────────────────┐
               ▼                                           ▼
┌─────────────────────────────┐             ┌─────────────────────────────┐
│ 4. Explainability (XAI)     │             │ 5. Reviewer Feedback Loop   │
│   Token-Level Gradients     │             │   CONFIRM / REJECT ANOMALY  │
└─────────────────────────────┘             └─────────────────────────────┘
```

---

## 3. Information Architecture (Five Core Application Views)

The redesigned LexAudit platform organizes user workflows into five specialized, high-cohesion views managed via a stable lateral navigation bar.

```text
┌──────────────┬─────────────────────────────────────────────────────────────────────────┐
│              │ [LexAudit]  Header (API Status ● | Privacy Modal | Dark Mode Toggle ☼/☾)│
│              ├─────────────────────────────────────────────────────────────────────────┤
│  NAVBAR      │                                                                         │
│  [Overview]  │                                                                         │
│  [Reviewer]  │                         PRIMARY WORKSPACE                               │
│  [Analytics] │                         (Selected View Content)                         │
│  [XAI]       │                                                                         │
│  [Feedback]  │                                                                         │
│              ├─────────────────────────────────────────────────────────────────────────┤
│  [Footer]    │ Research Prototype — Not Legal Advice | Retention Purge: Active (24h)   │
└──────────────┴─────────────────────────────────────────────────────────────────────────┘
```

### 3.1 View 1: Overview Dashboard
- **Purpose:** Onboarding, operational status, project disclosures, and session contract initiation.
- **Header Elements:** System title, research prototype badge, backend connectivity badge (`http://127.0.0.1:8000`), API key input modal.
- **Primary Action Card:** Large drop-zone for `.txt` commercial agreements with explicit drag-and-drop support.
- **Privacy Enforcement Gate:** Mandatory pre-upload checkbox: *"I acknowledge that uploaded text will be encrypted with Fernet AES-128 and purged after 24 hours pursuant to the retention policy."*
- **Truthful Session History:** Shows active in-session audited documents stored in browser `sessionStorage`. (Explicitly avoids claiming persistent server-side document lists).
- **Architecture Highlights:** Brief overview of the Dual-Channel NLP engine and deterministic rule checkers.

### 3.2 View 2: Contract Review Workspace (Flagship Experience)
- **Purpose:** Primary split-screen environment for auditing contract clauses side-by-side with findings.
- **Left Panel (Contract Document Viewer, 55% width):**
  - **Sticky Document Toolbar:** Document ID, filename, total clause counter, quick search input, and severity filter toggles (`All`, `High`, `Medium`, `Clean`).
  - **Continuous Document Stream:** Renders every segmented clause sequentially in full text (not truncated previews).
  - **Clause Container:** Each clause displays its sequence index (e.g., `§ 1`), a subtle left severity border pip (Red for `HIGH`, Amber for `MEDIUM`, Slate for `LOW`), and inline reference/date badges.
  - **Active Selection Highlight:** The currently active clause is highlighted with a high-contrast accent ring (`#2563EB` light / `#60A5FA` dark).
- **Right Panel (Audit Findings Inspector, 45% width):**
  - **Selected Clause Header:** Sequence number, clause ID, and overall severity badge.
  - **Severity Breakdown Card:** Cross-channel agreement status, combined anomaly score with calibrated 95% conformal interval width.
  - **Dual-Channel Diagnostics:**
    - *Channel A (Semantic OOD):* Centroid distance, nearest LEDGAR reference category, and out-of-distribution indicator.
    - *Channel B (Discourse Transition):* Incoming and outgoing transition probabilities from adjacent clauses.
  - **Deterministic Rule Violations:** Rule cards detailing broken internal references (e.g., dangling `Section 4.2`) or chronological date inversions.
  - **Direct Reviewer Feedback Bar:** Embedded quick-action verdict buttons (`CONFIRM_ANOMALY` / `REJECT_ANOMALY`) directly inside the inspector.
  - **Navigation Controls:** `Previous Clause` and `Next Clause` buttons for sequential keyboard audit.

### 3.3 View 3: Analytics & Findings
- **Purpose:** Macro-level executive summary of document health, structural cohesion, and distribution statistics.
- **Executive Metric Cards:**
  - Total Clauses Audited
  - Anomalies Detected (Total ML Flags)
  - Critical Severity Count (`HIGH`)
  - Deterministic Rule Violations (`RULES`)
  - Overall Mean Coherence Score
- **Sequence Coherence Heatmap:** High-resolution interactive visual bar mapping clause positions 1 to $N$, shaded by composite anomaly score, with click-to-navigate functionality.
- **Severity Distribution Breakdown:** Visual ratio bar comparing Clean vs. Medium vs. High severity clauses.
- **Deterministic Violations Ledger:** Tabular registry of all structural errors, categorized by dangling reference pointers and date milestones.

### 3.4 View 4: Explainability Workspace (XAI)
- **Purpose:** Deep diagnostic inspection of model activations for researchers and senior auditors.
- **Clause Selector:** Switch between flagged clauses.
- **Integrated Gradients Token Attribution Map:**
  - Full clause text decomposed into interactive token badges.
  - Background color intensity proportionally mapped to attribution magnitude (green scale for supportive tokens, red/salmon scale for disruptive tokens).
  - Hover tooltip displaying token index, exact float attribution score, and baseline score.
- **Channel B Neighborhood Perturbation Sensitivity:**
  - Graph/table displaying baseline score vs. perturbed score when adjacent clauses are shuffled or masked.
  - Quantifies transition sensitivity delta ($\Delta$).
- **Claim Scope Boundary Box (Prompt 12 Disclosure):**
  - Prominent scientific boundary card explaining:
    - *What this shows:* Model-internal feature projections and gradient paths.
    - *What this does not show:* Legal enforceability, statutory validity, or market standard consensus.

### 3.5 View 5: Reviewer Feedback Workspace
- **Purpose:** Dedicated human-in-the-loop oversight interface for auditing verdicts and calibrating future thresholds.
- **Feedback Registry Table:** Displays recent reviewer submissions stored in `data/processed/feedback.sqlite`.
- **Submission Form:**
  - Clause Selector (bound to current document).
  - Reviewer ID Input (e.g., `auditor_01`).
  - Supported Verdict Selector: `CONFIRM_ANOMALY` (True positive) or `REJECT_ANOMALY` (False positive).
  - Provenance Selector: `REAL` (Human audit) or `SYNTHETIC_TEST` (Dry run).
  - Corrected Severity Option: `HIGH`, `MEDIUM`, `LOW`.
- **Audit Ledger Confirmation:** Real-time feedback ID display and timestamp recording.
- **Scientific Disclosure:** Explicitly notes that feedback collection does not trigger automated online model weight updates.
