# LexAudit Phase 4C — Frontend UI Integration & User Experience Review

## 1. Component Architecture (`frontend/src/components/repair/`)

The counterfactual repositioning experience was constructed as an isolated, modular component tree under `frontend/src/components/repair/`:

```
frontend/src/components/repair/
├── CounterfactualRepairWorkspace.tsx   # Top-level workspace modal & state orchestrator
├── RepairCandidateList.tsx             # Interactive candidate rank list with delta badges
├── RepairScoreComparison.tsx           # Side-by-side baseline vs candidate metrics
├── RepairClausePreview.tsx             # Surrounding clause context preview
├── RepairAbstentionNotice.tsx          # Structured scientific abstention callout
├── RepairMethodology.tsx               # Collapsible mathematical & legal disclaimer drawer
├── RepairEmptyState.tsx                # Error/fallback handling state
├── types.ts                            # Strict TypeScript interface definitions
└── index.ts                            # Clean barrel export
```

---

## 2. Integration with Existing Workspaces

### 2.1 Trigger from Findings Inspector (`FindingsInspector.tsx`)
In the Contract Review workspace, when an attorney or legal auditor selects a clause with anomalous flow, the Findings Inspector action toolbar displays a secondary action:
- **Button Label**: `Explore alternative positions`
- **Icon**: `GitBranch` / `Sliders` icon indicating exploratory branching.
- **Action**: Opens `CounterfactualRepairWorkspace` modal seeded with the authoritative `selectedClauseId` and current document clauses.

### 2.2 Strict Contract Integrity Preservation
- **Zero Automatic Modification**: There is deliberately **no** "Apply Repair" or "Accept Move" button that overwrites contract text or re-orders clauses.
- **Qualified Language Enforced**: All recommendations use qualified, scientifically accurate terminology:
  - `"Model-suggested position"`
  - `"Experimental coherence improvement"`
  - `"Requires human review"`
  - Prohibited: `"Legally correct"`, `"Guaranteed fix"`, `"Compliant ordering"`.
- **Dismissal**: Users can close the modal at any time via the close button, keyboard `Escape`, or backdrop click, returning seamlessly to the Contract Review workspace with document ordering 100% unchanged.

---

## 3. UI Features & Information Architecture

### 3.1 Candidate Ranking List (`RepairCandidateList.tsx`)
- Displays all $N$ evaluated insertion positions sorted by measured coherence improvement ($\Delta J$).
- Highlights the current original position as `"Current position (Baseline)"`.
- Displays relative placement labels (e.g., `"Document start (before §1: [Title])"`, `"Between §3 and §4"`).
- Color-coded badges: Green for positive improvement ($\Delta J > 0$), Gray for baseline/no improvement ($\Delta J \le 0$).

### 3.2 Side-by-Side Metric Comparison (`RepairScoreComparison.tsx`)
- Compares:
  1. **Baseline Document Anomaly**: Production combined anomaly $J(D^{\text{orig}})$.
  2. **Hypothetical Document Anomaly**: Candidate combined anomaly $J(D^{(p)})$.
  3. **Net Anomaly Delta ($\Delta J$)**: Exact improvement percentage.
- Real-time reactivity: Clicking any candidate slot in the list immediately updates the comparison panel.

### 3.3 Surrounding Context Preview (`RepairClausePreview.tsx`)
Shows how the clause would sit between its new neighbors:
- Preceding Clause (with section number and preview text).
- Selected Clause (highlighted card).
- Following Clause (with section number and preview text).

### 3.4 Scientific Abstention Notice (`RepairAbstentionNotice.tsx`)
When the model determines that no candidate meaningfully improves coherence or that the document's drafting order is already optimal, a dedicated callout explains the exact reason (e.g., `ORIGINAL_POSITION_ALREADY_OPTIMAL` or `IMPROVEMENT_BELOW_THRESHOLD`).

### 3.5 Methodology & Transparency Drawer (`RepairMethodology.tsx`)
An expandable panel details:
- The frozen BERT + MLP scoring architecture.
- The primary objective formula $J(D) = \frac{1}{N} \sum [0.5 S_A + 0.5 S_B]$.
- The non-destructive decision-support mandate.
- Explicit reminder that structural constraints and legal enforceability must be determined by a qualified attorney.
