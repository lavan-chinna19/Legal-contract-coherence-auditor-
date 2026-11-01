# UI cleanup audit

Audit date: 2026-10-26. Baseline: personal release `0106f32` on local branch
`codex/lexaudit-personal-release`. Existing uncommitted research work and the
load-test fixture modification are outside this refactor. No Git publication
or deployment is authorized.

## Inventory and findings

| Area | Existing implementation | Issue and intended change |
| --- | --- | --- |
| Navigation | Seven sidebar destinations plus six global tabs; `activeSection` and `activeTab` synchronized manually | Duplicate routes, inconsistent labels and disabled states. Use one primary section state: New Audit, Audit Results, Reports & History, Settings; optional Research Tools. |
| Shell | Large disclaimer, verbose header/subtitle, Connection drawer and header theme selector | Technical controls and repeated explanations compete with the document. Compact visible disclaimer; setup and appearance in Settings. |
| Session/report card | Always visible sign-in, history refresh, exports and dependency graph in `ReleaseTools` | Four unrelated responsibilities. Separate Settings authentication, Reports & History, and reference evidence within Results. |
| Upload | Combined upload/analyze and parse-preview actions, long disclosure, raw IDs/offsets | Competing paths skip review. Make Upload → Preview → Analyze the default; retain concise consent and expandable limits/technical source details. |
| Results | Separate review/analytics/explanation destinations; five repeated KPIs; inspector repair actions | Consolidate result views in one contextual workspace, preserving selected-clause identity. Separate textual conflicts, other rule candidates, statistical anomalies and unresolved references. |
| Analytics | Compatibility map switcher embedded in current-document analytics | Historical/pretrained model information mixed with document evidence. Move map to Research Tools; retain current-document charts and score interpretation. |
| Feedback | Recalibration terminology, internal enum labels and API-oriented submit text | Use Reviewer Feedback with plain verdicts and clear self-reported provenance; no retraining claim. |
| Research | Robustness Lab always in primary navigation with P4D badge; model evaluation has internal phase/prompt names | Optional Research Tools; preserve opt-in, negative controls, historical numerical values and scientific caveats. Remove phase badges and decorative emojis. |
| Naming | Ingestion, Coherence Heatmap, XAI, Counterfactual Repositioning and laboratory terminology | Use brief task labels, Explanations, Reference Consistency Check (Experimental), Suggested Clause Positions (Experimental), Robustness Testing (Research). |
| Components/styles | Shared buttons mixed with inline variants, extra heading strips and card nesting | Retain working evidence components; simplify wrappers and apply one form/button system, neutral palette and consistent spacing. |
| Accessibility | Heatmap already uses buttons; global tabs lack complete arrow-key semantics; sidebar mobile focus management incomplete | Preserve source alignment and keyboard clause selection; add proper contextual tabs, focus-managed mobile menu, visible focus, status/error announcements and responsive checks. |
| Tests | 17 alignment assertions plus prior real browser/CDP scripts with legacy selectors | Preserve all alignment cases; add workflow/security checks and a new real browser acceptance run using the updated navigation. Do not remove assertions to hide regressions. |

## API architecture and security decision

FastAPI uses API keys to derive document ownership; report, history, preview,
analysis, explanations and experiments are authenticated. The frontend calls
that API directly. `/health` is unauthenticated; `/v1/session` checks identity.
There is no existing server-side per-browser session broker. A universal key
embedded in frontend code, browser storage or a public environment variable
would compromise the existing boundary.

Use the brief's permitted fallback: one key entry in Settings per page session,
kept only in React memory. A trusted public application setting supplies the
initial engine URL; changing an address is an explicit Settings action and clears
the current identity/document. Validate configured URLs before sending a key;
allow HTTPS or loopback HTTP, reject URL credentials/query/fragment. Authentication,
owner checks and downloads remain enforced by the existing backend. No external
inference provider, automatic public demo credential or insecure auth bypass is
introduced. Reload requires reconnection; a future secure persistent session
requires a separate design for per-user ownership, cookies, CSRF and key lifecycle.

## Preservation and verification plan

Keep existing models, centroids, scoring thresholds, research records, APIs and
experimental algorithms unchanged. Research functionality is moved, not removed.
Run lint, types, production build, original alignment cases, meaningful new
workflow checks, relevant API/security tests and real browser TXT/PDF/DOCX,
explanation/experiment/export/history/denial workflows. Check desktop, tablet,
mobile and Docker smoke if available. Record actual results and limitations in
UI_REDESIGN_COMPLETION_REPORT.md; unexecuted checks remain unverified.
