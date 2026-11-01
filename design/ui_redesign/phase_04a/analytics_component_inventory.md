# LexAudit Phase 4A — Analytics Component Inventory & Interface Specification

## 1. Component Architecture Overview
All Phase 4A analytics components reside under [frontend/src/components/analytics/](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/frontend/src/components/analytics/) and are exported via `index.ts`. They rely exclusively on React 19, native CSS/SVG, and Lucide React icons.

```
frontend/src/components/analytics/
├── types.ts                        # TypeScript interfaces & prop types
├── index.ts                        # Public module exports
├── AnalyticsWorkspace.tsx          # Master container & navigation sync
├── AnalyticsSummary.tsx            # Document-level 5-card KPI summary
├── ClauseScoreDistribution.tsx     # Sequential timeline & keyboard navigation
├── SeverityDistribution.tsx        # Segmented distribution bar & tabular tiers
├── ChannelEvidenceComparison.tsx   # Channel A vs Channel B diagnostic panels
├── RuleFindingsSummary.tsx         # Deterministic violations & clause linking
├── CalibrationTransparency.tsx     # Conformal uncertainty & academic caveats
└── AnalyticsEmptyState.tsx         # Zero-data guidance & overview navigation
```

---

## 2. Component Specifications

### 1. `AnalyticsWorkspace.tsx`
- **Path**: [AnalyticsWorkspace.tsx](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/frontend/src/components/analytics/AnalyticsWorkspace.tsx)
- **Props**:
  - `documentResult: DocumentResult | null`
  - `selectedClauseId: string`
  - `onSelectClauseId: (clauseId: string) => void`
  - `onNavigateToReview?: () => void`
  - `onNavigateToUpload?: () => void`
  - `onNavigateToXai?: () => void`
  - `onNavigateToFeedback?: () => void`
- **Role**: Coordinates the entire analytics layout, delegates clause selection state, handles empty state switching, and renders workspace header actions.
- **Accessibility**: Enclosed in `role="region"` with `aria-label="Professional Analytics & Findings Workspace"`.

### 2. `AnalyticsSummary.tsx`
- **Path**: [AnalyticsSummary.tsx](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/frontend/src/components/analytics/AnalyticsSummary.tsx)
- **Props**: `documentResult: DocumentResult`
- **Role**: Renders 5 authentic document KPI cards: Total Clauses, Detected Anomalies, High Severity, Rule Violations, and Mean Combined Anomaly Score.
- **IDs**: `#analytics-kpi-total-clauses`, `#analytics-kpi-ml-anomalies`, `#analytics-kpi-high-severity`, `#analytics-kpi-rule-violations`, `#analytics-kpi-mean-score`.
- **Accessibility**: Uses semantic headings (`<h2>`, `<h3>`), aria-labels, and `.kpi-card` classes compatible with existing test harnesses.

### 3. `ClauseScoreDistribution.tsx`
- **Path**: [ClauseScoreDistribution.tsx](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/frontend/src/components/analytics/ClauseScoreDistribution.tsx)
- **Props**:
  - `clauses: ClauseResult[]`
  - `selectedClauseId: string`
  - `onSelectClauseId: (clauseId: string) => void`
  - `onNavigateToReview?: () => void`
- **Role**: Renders an interactive, scrollable sequential bar timeline for clauses § 0 to § N-1. Highlights the selected clause with glow and border; provides contextual bottom strip with instant clause preview and navigation button.
- **Interactions**:
  - Click bar to select clause
  - Keyboard navigation: `ArrowRight`, `ArrowLeft`, `Home`, `End`, `Enter`, `Space`
  - Auto-scrolls selected bar into view via `scrollIntoView`
- **Accessibility**: Each bar has `role="button"`, `tabIndex={0}`, `aria-label`, and `aria-pressed`.

### 4. `SeverityDistribution.tsx`
- **Path**: [SeverityDistribution.tsx](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/frontend/src/components/analytics/SeverityDistribution.tsx)
- **Props**:
  - `totalClauses: number`
  - `highCount: number`
  - `mediumCount: number`
  - `lowCount: number`
- **Role**: Segmented progress bar showing proportional distribution of HIGH, MEDIUM, LOW, and CLEAN clauses, paired with a non-color reliant summary table.
- **Accessibility**: Native `role="progressbar"` with `aria-valuemin`, `aria-valuemax`, `aria-valuenow`, and table markup with column headers.

### 5. `ChannelEvidenceComparison.tsx`
- **Path**: [ChannelEvidenceComparison.tsx](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/frontend/src/components/analytics/ChannelEvidenceComparison.tsx)
- **Props**: `selectedClause?: ClauseResult`
- **Role**: Side-by-side diagnostic decomposition separating Channel A (Legal-BERT Cosine Centroid Distance, domain $[0, 2]$, nearest cluster name, OOD status) from Channel B (Sequential Discourse Flow, domain $[0, 1]$, incoming/outgoing transition probabilities).
- **Caveats**: Includes prominent warning banner detailing metric scale incompatibility.

### 6. `RuleFindingsSummary.tsx`
- **Path**: [RuleFindingsSummary.tsx](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/frontend/src/components/analytics/RuleFindingsSummary.tsx)
- **Props**:
  - `ruleFlags: RuleFlag[]`
  - `clauses: ClauseResult[]`
  - `onSelectClauseId: (clauseId: string) => void`
  - `onNavigateToReview?: () => void`
- **Role**: Groups deterministic rule violations, displays severity badges, category pills, affected clause section markers, and provides deep links to Contract Review.
- **Safeguards**: If zero rule flags exist, renders exact disclaimer: *"No deterministic rule violations were reported by the current rule checks. This notice does not indicate that this contract has no legal defects."*

### 7. `CalibrationTransparency.tsx`
- **Path**: [CalibrationTransparency.tsx](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/frontend/src/components/analytics/CalibrationTransparency.tsx)
- **Props**:
  - `scoringResult: DocumentResult["scoring_result"]`
  - `selectedClause?: ClauseResult`
- **Role**: Displays statistical provenance (`synthetic_shuffle_ledgar`), selected clause 90% conformal prediction interval bounds $[ci_{lo}, ci_{hi}]$, uncertainty width, and research methodology caveats.

### 8. `AnalyticsEmptyState.tsx`
- **Path**: [AnalyticsEmptyState.tsx](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/frontend/src/components/analytics/AnalyticsEmptyState.tsx)
- **Props**: `onNavigateToUpload?: () => void`
- **Role**: High-contrast, accessible empty state displayed when the Analytics workspace is opened before document analysis.
- **Button ID**: `#analytics-empty-upload-btn`.
