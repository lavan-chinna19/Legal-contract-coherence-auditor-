# Phase 4B — Cross-Workspace Identity & Stale Response Protection Audit

**Project:** Legal Contract Coherence Auditor (LexAudit)  
**Phase:** 4B — Professional Explainability Workspace  
**Date:** 2026-10-14  
**Author:** Senior Next.js/React Architect & Security Reviewer  
**Status:** PASS — VERIFIED & ROBUST  

---

## 1. Single Source of Truth in React Memory

In strict adherence to Phase 3A/4A/4B architecture, the active clause selection is maintained in root React memory:
```typescript
const [selectedClauseId, setSelectedClauseId] = useState<string>("");
```
- **Session-Only Confinement:** Neither `doc_id`, `selectedClauseId`, nor contract plaintext is ever written to `localStorage` or `sessionStorage`.
- **Authoritative Flow:** Selection propagates down into:
  1. **Contract Review Workspace:** Synchronizes split-screen clause card and source text scroll highlight.
  2. **Analytics & Findings Workspace:** Highlights the active clause in the sequence timeline and channel decomposition card.
  3. **Explainability Workspace (Phase 4B):** Targets `GET /v1/xai/attribution` and `GET /v1/xai/sensitivity` to the active clause ID.
  4. **Reviewer Recalibration Interface:** Auto-populates the feedback form dropdown with the active clause.

---

## 2. Cross-Workspace Navigation Flow

From the Explainability workspace, legal reviewers can seamlessly transition across views without losing context:
1. **Explainability $\to$ Contract Review (`#xai-nav-review-btn`):**
   - Transports the reviewer directly to the split-screen contract reviewer focused on the exact selected clause.
2. **Explainability $\to$ Reviewer Feedback (`#xai-nav-feedback-btn`):**
   - Opens the recalibration interface with the clause pre-selected, ready for verdict entry (`CONFIRM_ANOMALY` / `REJECT_ANOMALY`).
3. **Analytics Timeline $\to$ Explainability:**
   - Reviewing an anomaly in Analytics allows clicking into Explainability for instant token-level attribution.

---

## 3. Stale Response & Race Condition Safeguard

Because Integrated Gradients computation takes several seconds over PyTorch embedding tensors, rapidly clicking different clauses (§ 0 $\to$ § 1 $\to$ § 2) introduces a risk that an earlier, delayed response might arrive late and overwrite a newer selection.

### Implementation Pattern in `ExplainabilityWorkspace.tsx`:
```typescript
const activeClauseIdRef = useRef(selectedClauseId);
useEffect(() => {
  activeClauseIdRef.current = selectedClauseId;
}, [selectedClauseId]);

useEffect(() => {
  const currentTarget = selectedClauseId;
  let cancelled = false;

  const fetchAttribution = async () => {
    try {
      const res = await fetch(`/v1/xai/attribution?...`);
      const data = await res.json();
      // STALE GUARD: Only update state if selection hasn't changed
      if (!cancelled && activeClauseIdRef.current === currentTarget) {
        setAttributionData(data);
      }
    } finally {
      if (!cancelled && activeClauseIdRef.current === currentTarget) {
        setLoadingAttribution(false);
      }
    }
  };

  fetchAttribution();
  return () => {
    cancelled = true;
  };
}, [selectedClauseId, ...]);
```

### Automated CDP Verification:
During the automated browser test, rapid switching from § 0 to § 1 verified that:
1. The pending request for § 0 was discarded.
2. The UI immediately reflected § 1 without flickering or displaying mismatched § 0 token attributions.
3. Outcome logged as `xai_stale_guard_verified: PASS`.
