# Phase 4D Frontend Integration and Robustness Lab Review

## 1. Workspace Integration Architecture
The Self Red-Team Robustness Laboratory is integrated into the LexAudit web application under `frontend/src/components/redteam/`:
- `RedTeamWorkspace.tsx`: Top-level coordinator managing state, error boundaries, parameter dispatch, and immutability ledger.
- `PerturbationSelector.tsx`: Taxonomy grid (P1–P10) with visual indicators and expected detector tags.
- `PerturbationConfiguration.tsx`: Target document selection (active upload vs. synthetic fixtures), clause targeting, and explicit opt-in checkbox.
- `DetectionOutcomePanel.tsx`: Verdict badges (`DETECTED`, `NOT_DETECTED`, `NOT_APPLICABLE`), attribution validity, and latency readout.
- `OriginalVsPerturbedView.tsx`: Side-by-side and single-column diff view with SHA-256 original vs perturbed checksum comparison.
- `ChannelResponseComparison.tsx`: Multi-channel ablation grid ($\Delta S_A$, $\Delta S_B$, $\Delta S$, rule flag counts).
- `RuleDetectionPanel.tsx`: Deterministic rule violation details with parsed evidence dictionaries.
- `ScenarioEvidenceInspector.tsx`: Oracle validation metadata, transformation details, and candidate remediation.
- `ExperimentLimitations.tsx`: Disclosure that synthetic perturbations do not equal legal invalidity, plus zero-mutation guarantee.
- `RedTeamEmptyState.tsx`: Quick-launch shortcuts for P1, P5, P7, P9.

## 2. Navigation Continuity
Reachable from `SidebarNav.tsx` (`id="nav-robustness-lab"`, badge `"P4D"`) without disrupting existing views (Overview, Contract Review, Analytics, Explainability, Reviewer Feedback).
