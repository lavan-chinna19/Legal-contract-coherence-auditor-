# Page Wireframes & Spatial Layout Architecture — Phase 1

**Module:** UI Redesign Program — Phase 1  
**Authors:** Senior LegalTech UX Architect & Responsive Design Specialist  
**Date:** October 10, 2026  
**Status:** COMPLETE (Page Wireframes)  

---

## 1. Desktop Wireframe (1440px Viewport) — Flagship Split-Screen Reviewer

```text
+----------------------------------------------------------------------------------------------------------------------------------------------------+
| [LexAudit] ⚖️ Legal Contract Coherence Auditor      [Research Prototype]          Backend: Online ●  [API Key 🔑]  [Theme ☼/☾]                      |
+----------------------------------------------------------------------------------------------------------------------------------------------------+
|  SIDEBAR (220px)  |  CONTRACT DOCUMENT VIEWER (55% Width, ~650px)            |  AUDIT FINDINGS INSPECTOR (45% Width, ~530px)                       |
|                   |                                                          |                                                                     |
|  [🏠 Overview]    |  [File: commercial_lease_v2.txt]  [Total: 18 Clauses]    |  SELECTED CLAUSE: § 4.2 (clause_4_2)  [HIGH SEVERITY 🔴]            |
|  [📄 Reviewer *]  |  [Filter: All (18) | High (3) | Rules (1)] [Search 🔍]   |  -----------------------------------------------------------------  |
|  [📊 Analytics]   |  ------------------------------------------------------  |  COMPOSITE ANOMALY SCORE: 0.784                                     |
|  [🔬 Explain XAI] |  § 1. PREAMBLE & PARTIES                                 |  [=======================>        ] 95% CI: [0.68, 0.88]            |
|  [📝 Feedback]    |  This Commercial Lease Agreement (the "Agreement") is    |  Calibration Source: SYNTHETIC_SHUFFLE_PERMUTATION                  |
|                   |  entered into as of October 1, 2026, by and between...   |  -----------------------------------------------------------------  |
|                   |  [Severity: CLEAN ✓]                                     |  DUAL-CHANNEL DECOMPOSITION:                                        |
|                   |                                                          |  * Channel A (Semantic OOD): 0.812 (Distance: 1.42)                 |
|                   |  § 2. DEMISED PREMISES                                   |    - Nearest LEDGAR Centroid: INDEMNIFICATION                       |
|                   |  Landlord hereby leases to Tenant, and Tenant hereby...  |    - OOD Status: TRUE (Out of Distribution)                         |
|                   |  [Severity: CLEAN ✓]                                     |  * Channel B (Discourse Transition): 0.741                          |
|                   |                                                          |    - Transition Inflow (from § 4.1): 12.4% Probability              |
|                   |  § 4.2. INDEMNIFICATION & CASUALTY                       |    - Transition Outflow (to § 5.0): 8.1% Probability                |
|                   |  +----------------------------------------------------+  |  -----------------------------------------------------------------  |
|                   |  | Tenant agrees to indemnify, defend and hold harmless|  |  DETERMINISTIC RULE FINDINGS: (1 Flag)                              |
|                   |  | Landlord against all liabilities pursuant to       |  |  [!] Broken Reference: Points to non-existent Section 19.4          |
|                   |  | Section 19.4... [SELECTED]                         |  |  -----------------------------------------------------------------  |
|                   |  +----------------------------------------------------+  |  QUICK REVIEWER ACTION:                                             |
|                   |  [Severity: HIGH 🔴] [Broken Ref ⚠️]                     |  [✓ CONFIRM_ANOMALY]   [✕ REJECT_ANOMALY]   [Provenance: REAL ▼]    |
|                   |                                                          |  [< Previous Clause (§ 4.1)]            [Next Clause (§ 5.0) >]     |
+-------------------+----------------------------------------------------------+---------------------------------------------------------------------+
| Research Prototype — Not Legal Advice | Process-Local Queue (workers=1) | 24h Data Retention Purge Active                                          |
+----------------------------------------------------------------------------------------------------------------------------------------------------+
```

---

## 2. Desktop Wireframe (1440px Viewport) — Overview Dashboard (View 1)

```text
+----------------------------------------------------------------------------------------------------------------------------------------------------+
| [LexAudit] ⚖️ Legal Contract Coherence Auditor      [Research Prototype]          Backend: Online ●  [API Key 🔑]  [Theme ☼/☾]                      |
+----------------------------------------------------------------------------------------------------------------------------------------------------+
|  SIDEBAR (220px)  |  OVERVIEW DASHBOARD WORKSPACE (~1180px Width)                                                                                  |
|                   |                                                                                                                                |
|  [🏠 Overview *]  |  +--------------------------------------------------------------------------------------------------------------------------+  |
|  [📄 Reviewer]    |  | ⚠️ ACADEMIC RESEARCH PROTOTYPE — NOT LEGAL ADVICE                                                                        |  |
|  [📊 Analytics]   |  | This platform audits structural coherence using dual-channel anomaly scoring. Models do not guarantee statutory validity.  |  |
|  [🔬 Explain XAI] |  +--------------------------------------------------------------------------------------------------------------------------+  |
|  [📝 Feedback]    |                                                                                                                                |
|                   |  +--------------------------------------------------------------------------------------------------------------------------+  |
|                   |  | 📤 UPLOAD CONTRACT DOCUMENT (.txt)                                                                                       |  |
|                   |  |                                                                                                                          |  |
|                   |  |        [ Drag & drop legal contract (.txt) file here, or click to browse ]                                              |  |
|                   |  |                                                                                                                          |  |
|                   |  |  [X] I acknowledge that contract text will be encrypted at rest (AES-128) and purged after 24h (Prompt 16 Retention)     |  |
|                   |  |                                                                                                                          |  |
|                   |  |  [ ⚡ Start Coherence Audit ]  (Active when file is selected and privacy is acknowledged)                                 |  |
|                   |  +--------------------------------------------------------------------------------------------------------------------------+  |
|                   |                                                                                                                                |
|                   |  RECENT IN-SESSION AUDITS (Browser Session Memory)                                                                             |
|                   |  +--------------------------------------------+  +--------------------------------------------+                            |
|                   |  | valid_multiclause.txt (5 Clauses)          |  | commercial_lease_v2.txt (18 Clauses)       |                            |
|                   |  | Anomalies: 2 (High: 2) | Score: 0.341      |  | Anomalies: 3 (High: 1) | Score: 0.512      |                            |
|                   |  | [ Open in Reviewer Workspace -> ]          |  | [ Open in Reviewer Workspace -> ]          |                            |
|                   |  +--------------------------------------------+  +--------------------------------------------+                            |
+----------------------------------------------------------------------------------------------------------------------------------------------------+
```

---

## 3. Desktop Wireframe (1440px Viewport) — Explainability (XAI) Workspace (View 4)

```text
+----------------------------------------------------------------------------------------------------------------------------------------------------+
| [LexAudit] ⚖️ Legal Contract Coherence Auditor      [Research Prototype]          Backend: Online ●  [API Key 🔑]  [Theme ☼/☾]                      |
+----------------------------------------------------------------------------------------------------------------------------------------------------+
|  SIDEBAR (220px)  |  EXPLAINABILITY & FEATURE ATTRIBUTION WORKSPACE                                                                                |
|                   |                                                                                                                                |
|  [🏠 Overview]    |  Select Flagged Clause: [ § 4.2. INDEMNIFICATION & CASUALTY (clause_4_2) ▼ ]   Mode: [ Token Attributions (IG) | Sensitivity ]  |
|  [📄 Reviewer]    |  ----------------------------------------------------------------------------------------------------------------------------  |
|  [📊 Analytics]   |  INTEGRATED GRADIENTS TOKEN-LEVEL ATTRIBUTION (Channel A Semantic OOD)                                                         |
|  [🔬 Explain *]   |  +--------------------------------------------------------------------------------------------------------------------------+  |
|  [📝 Feedback]    |  | [Tenant (0.04)] [agrees (0.01)] [to (0.01)] [indemnify (0.42)] [defend (0.38)] [and (0.02)] [hold (0.11)]                  |  |
|                   |  | [harmless (0.35)] [Landlord (0.08)] [against (0.05)] [all (0.04)] [liabilities (0.28)] [pursuant (0.09)]                  |  |
|                   |  | [to (0.02)] [Section (0.19)] [19 (0.18)] [. (0.01)] [4 (0.22)]                                                             |  |
|                   |  +--------------------------------------------------------------------------------------------------------------------------+  |
|                   |  Legend: [ Light Green = Neutral (0.00-0.10) ]   [ Medium Green = Moderate (0.10-0.30) ]   [ Dark Green = High Impact (>0.30) ]   |
|                   |                                                                                                                                |
|                   |  CHANNEL B NEIGHBORHOOD PERTURBATION SENSITIVITY                                                                               |
|                   |  Baseline Transition Score: 0.741  |  Perturbed Score (Neighbor Shuffled): 0.599  |  Sensitivity Delta: -0.142                    |
|                   |                                                                                                                                |
|                   |  +--------------------------------------------------------------------------------------------------------------------------+  |
|                   |  | ℹ️ CLAIM SCOPE & SCIENTIFIC BOUNDARIES (Prompt 12 Disclosure)                                                            |  |
|                   |  | What this shows: Model-internal gradient activations indicating words that deviate from LEDGAR corpus clause centroids.    |  |
|                   |  | What this does not show: Statutory enforceability, compliance with common law doctrine, or industry consensus.           |  |
|                   |  +--------------------------------------------------------------------------------------------------------------------------+  |
+----------------------------------------------------------------------------------------------------------------------------------------------------+
```

---

## 4. Laptop Wireframe (1024px Viewport) — Compact Split Reviewer

```text
+--------------------------------------------------------------------------------------------------------------------+
| [LexAudit] ⚖️                    [Research Prototype]                  Backend: Online ●  [API Key]  [Theme ☼/☾]     |
+--------------------------------------------------------------------------------------------------------------------+
| NAV (70px) | DOCUMENT STREAM (50%, ~470px)                  | FINDINGS INSPECTOR (50%, ~470px)                     |
| [🏠]       | [Doc: lease.txt] [Filter: All ▼] [Search]      | CLAUSE § 4.2 [HIGH 🔴]                               |
| [📄 *]     | ---------------------------------------------- | ---------------------------------------------------  |
| [📊]       | § 1. PREAMBLE                                  | Combined Score: 0.784 (95% CI: [0.68, 0.88])         |
| [🔬]       | Clean text preview...                          | Channel A (Semantic OOD): 0.812 (INDEMNIFICATION)    |
| [📝]       |                                                | Channel B (Discourse): 0.741 (In: 12.4%, Out: 8.1%)  |
|            | § 4.2. INDEMNIFICATION [SELECTED]             | Rules: [!] Dangling Section 19.4                     |
|            | Tenant agrees to indemnify, defend and hold    | ---------------------------------------------------  |
|            | harmless Landlord against all liabilities...   | [✓ CONFIRM_ANOMALY]       [✕ REJECT_ANOMALY]         |
|            |                                                | [< Prev Clause]                       [Next Clause>] |
+--------------------------------------------------------------------------------------------------------------------+
```

---

## 5. Tablet Wireframe (768px Viewport) — Tabbed Inspector Drawer

```text
+---------------------------------------------------------------------------------------+
| [≡] [LexAudit] ⚖️                      [Research Prototype]          [Theme ☼/☾] [API]  |
+---------------------------------------------------------------------------------------+
| DOCUMENT STREAM (Full Width)  [Filter: All ▼] [Search 🔍]                             |
| § 1. PREAMBLE & PARTIES (Clean ✓)                                                     |
|                                                                                       |
| § 4.2. INDEMNIFICATION & CASUALTY [SELECTED]                                          |
| Tenant agrees to indemnify, defend and hold harmless Landlord against liabilities...  |
| [Severity: HIGH 🔴]  [Tap to open Inspector ->]                                       |
|                                                                                       |
| § 5. TERM AND TERMINATION (Clean ✓)                                                   |
+---------------------------------------------------------------------------------------+
| BOTTOM INSPECTOR DRAWER (Collapsible, 40% Height)                                     |
| [^] CLAUSE § 4.2 FINDINGS: Score 0.784 (High 🔴) | Dangling Ref ⚠️                    |
| Actions: [✓ Confirm Anomaly]  [✕ Reject Anomaly]  [Inspect XAI Token Gradients ->]    |
+---------------------------------------------------------------------------------------+
```

---

## 6. Mobile Wireframe (390px Viewport) — Sequential Mobile Layout

```text
+---------------------------------------+
| [≡] LexAudit ⚖️            [☼/☾] [API] |
+---------------------------------------+
| [Overview] [Reviewer *] [Analytics]   |
+---------------------------------------+
| Doc: lease.txt (18 Clauses)           |
| Filter: [ All ▼ ] [Search 🔍]         |
+---------------------------------------+
| § 4.2. INDEMNIFICATION [HIGH 🔴]     |
| Tenant agrees to indemnify, defend... |
|                                       |
| > Combined Anomaly: 0.784             |
| > 95% Confidence: [0.68, 0.88]        |
| > Broken Ref: Section 19.4            |
|                                       |
| Quick Reviewer Action:                |
| [✓ CONFIRM ANOMALY]                   |
| [✕ REJECT ANOMALY]                    |
+---------------------------------------+
| § 5. TERM & TERMINATION [CLEAN ✓]     |
| This Agreement commences on...        |
+---------------------------------------+
| Bottom Nav: [Doc] [Findings] [XAI]    |
+---------------------------------------+
```
