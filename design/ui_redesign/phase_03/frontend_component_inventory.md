# Frontend Component Inventory — Phase 3
**Directory: `frontend/src/components/review/`**

## 1. Overview
Phase 3 created 10 dedicated components and type definitions under `frontend/src/components/review/`, fully integrating with the Phase 2 atomic UI components (`Button`, `Badge`) and global CSS design tokens.

---

## 2. Component Roster

| Component | File Path | Primary Responsibility | Key Props / Interfaces |
|---|---|---|---|
| **`types.ts`** | `frontend/src/components/review/types.ts` | Authoritative TypeScript interfaces matching FastAPI models and frontend states | `ClauseResult`, `RuleFlag`, `DocumentResult`, `EnrichedClause`, `SeverityFilter` |
| **`ContractReviewWorkspace.tsx`** | `frontend/src/components/review/ContractReviewWorkspace.tsx` | Main split-screen container coordinating viewer, inspector, in-memory full text alignment, and macro heatmap | `documentResult`, `rawContractText`, `selectedClauseId`, `onSelectClauseId`, `onNavigateToXai`, `onNavigateToFeedback` |
| **`ClauseDocumentViewer.tsx`** | `frontend/src/components/review/ClauseDocumentViewer.tsx` | Left panel (55% desktop) displaying continuous clause stream, auto-scrolling, and search toolbar | `clauses`, `filteredClauses`, `selectedClauseId`, `onSelectClause`, `searchQuery`, `severityFilter` |
| **`ClauseCard.tsx`** | `frontend/src/components/review/ClauseCard.tsx` | Interactive numbered clause card with accessible ARIA semantics, non-color severity tag, and full text body | `clause: EnrichedClause`, `isSelected: boolean`, `onSelect: (id: string) => void` |
| **`FindingsInspector.tsx`** | `frontend/src/components/review/FindingsInspector.tsx` | Right panel (45% desktop) displaying header metadata, sequential navigation, tabbed inspector, and cross-workspace actions | `selectedClause`, `currentIndex`, `totalClauses`, `onPrevious`, `onNext`, `clauseRules`, `documentRules`, `onNavigateToXai`, `onNavigateToFeedback` |
| **`ClauseNavigator.tsx`** | `frontend/src/components/review/ClauseNavigator.tsx` | Prev/Next sequential stepper with section indicator (`§ {idx}`) and automatic boundary disabling | `currentIndex`, `totalClauses`, `onPrevious`, `onNext`, `hasPrevious`, `hasNext`, `currentClauseNumber` |
| **`ClauseSearchFilter.tsx`** | `frontend/src/components/review/ClauseSearchFilter.tsx` | Client-side filter bar featuring text search input, severity dropdown, match counter, and clear action | `searchQuery`, `onSearchChange`, `severityFilter`, `onSeverityFilterChange`, `visibleCount`, `totalCount`, `onClearFilters` |
| **`ScoreEvidencePanel.tsx`** | `frontend/src/components/review/ScoreEvidencePanel.tsx` | Scientific inspector tab rendering real Combined Score, Channel A Centroid Distance / OOD, Channel B Markov transitions, and Conformal CI | `clause: EnrichedClause` |
| **`RuleFindingsPanel.tsx`** | `frontend/src/components/review/RuleFindingsPanel.tsx` | Deterministic inspector tab partitioning clause-specific rule violations from document-level rule findings | `clauseRules: RuleFlag[]`, `documentRules: RuleFlag[]`, `selectedClauseId: string` |
| **`ReviewEmptyState.tsx`** | `frontend/src/components/review/ReviewEmptyState.tsx` | Accessible empty states for unanalyzed contracts and zero-search query matches | `type: "no-document" \| "no-search-results"`, `title`, `description`, `onAction`, `actionText` |

---

## 3. Design Token & CSS Binding
All Phase 3 review components adhere strictly to the dual-theme CSS variables defined in `frontend/src/app/globals.css`:
- `--color-surface` and `--color-surface-raised` for cards and panels.
- `--color-border` and `--color-border-subtle` for structural separation.
- `--color-accent` and `--color-accent-subtle` for active clause card highlights.
- `--sev-high-bg`, `--sev-high-border`, `--sev-high-text` for High severity alerts.
- `--sev-med-bg`, `--sev-med-border`, `--sev-med-text` for Medium severity alerts.
- `--color-success-bg`, `--color-success-border`, `--color-success` for Clean clauses.
- System monospace font stack (`ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace`) for scores, clause numbers, and IDs.
