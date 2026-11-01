# Phase 4D Cross-Workspace Identity & State Validation

## 1. Document Identity & State Isolation
When a user switches between workspaces or uploads a new document:
- **Active Document Invalidation**: Switching the active contract automatically clears any stale red-team experimental results to prevent cross-contract state confusion.
- **Stable Clause ID Tracking**: Existing clause IDs remain constant across all views.
- **Copy-on-Write Experimental IDs**: Newly inserted clauses (P3/P4) receive unique IDs with `dup_` or `variant_` prefixes, preventing key collision in React lists.
- **Zero Cross-Contamination**: Uploading or reviewing an active document never overwrites synthetic fixtures, and running red-team tests never modifies the active document's analysis cache.

## 2. Navigation Integrity
As verified in automated CDP browser testing (`09_cross_workspace_preservation.png`), navigating through Overview, Contract Review, Analytics, Explainability, Feedback, and Robustness Lab causes zero console errors and preserves all component trees intact.
