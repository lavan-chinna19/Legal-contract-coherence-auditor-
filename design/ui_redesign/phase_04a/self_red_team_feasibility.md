# LexAudit Phase 4A — Self Red-Team Feasibility Audit & Mutation Taxonomy

## 1. Executive Summary & Policy Notice
- **Feasibility Verdict**: **PARTIALLY IMPLEMENTED (Tier 1 Rule & Shuffle Mutations Existing)**.
- **Phase Restriction**: Read-only evaluation and architectural taxonomy. **Zero automated perturbations or mutation tools are implemented during Phase 4A.**
- **Scientific Integrity Mandate**: A mutation is only classified as "detectable" if a specific, validated subsystem (scoring or deterministic rules) possesses an empirical mechanism to trigger on that defect.

---

## 2. Mutation Classification & Capability Taxonomy

| Mutation Name | Current Implementation Status | Source Function / Script | Detection Mechanism | Expected System Response | Detection Caveat & Boundary Limitation |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Dangling Section Reference** | **Implemented** | `src/rules/references.py`, `tests/test_rules.py:test_reference_checker_broken_ref_doc_1` | Deterministic cross-reference regex parser | Rule Flag: `HIGH` severity (`BROKEN_INTERNAL_REFERENCE`) | Detected if section number exceeds maximum parsed section. Does not detect semantic reference shifts. |
| **Broken Exhibit Citation** | **Implemented** | `src/rules/references.py`, `tests/test_rules.py:test_reference_checker_broken_ref_doc_2` | Deterministic exhibit schedule parser | Rule Flag: `MEDIUM` severity (`MISSING_SCHEDULE_EXHIBIT`) | Detected if text cites Exhibit [X] that is absent from document schedule. |
| **Chronological Date Inversion** | **Implemented** | `src/rules/dates.py`, `tests/test_rules.py:test_date_checker_inverted_term_doc_3` | Regex date extractor & datetime comparison | Rule Flag: `HIGH` severity (`INVERTED_TERM_DATES`) | Detected only if both Effective Date and Expiration Date are parsed in explicit standard formats. |
| **Block Shuffle / Pairwise Swap** | **Implemented (Benchmark)** | `src/evaluation/benchmarks.py:perturb_blocks`, `tests/test_cuad_order.py` | Channel B transition discontinuity | Score Surge: $S_B \ge 0.65$ across boundary clauses | Detects severe discontinuity between mismatched topics. Weak detection for adjacent interchangeable boilerplate. |
| **Clause Displacement (Relocation)** | **Proposed (Design Only)** | Blueprint in Phase 4A Section 8 | Channel B incoming/outgoing flow disruption | $\Delta S_B > 0.30$ at insertion point | Detectable if moved into incompatible topic cluster; undetectable if moved between homogeneous sections. |
| **Clause Duplication** | **Proposed (Design Only)** | Blueprint for Phase 4B Robustness Lab | Pairwise cosine distance $d(u_i, u_j) \approx 0.0$ | Duplicate clause warning flag | Channel B may not detect duplication if the clause is self-compatible (e.g. repeated boilerplate). |
| **Clause Deletion** | **Unsupported (by Scorer)** | N/A (Scorer has no sequence completeness model) | Completeness Checklist (`src/completeness/`) | **UNSUPPORTED** by dual-channel scorer | **CRITICAL LIMITATION:** The frozen scoring pipeline evaluates relative transitions. Deleting a clause does not produce an anomaly unless the resulting bridge transition $(c_{i-1} \to c_{i+1})$ is itself improbable, or a completeness checklist rule explicitly tests for the missing clause. |

---

## 3. Operational Requirements for Future "Robustness Lab"

### 3.1 Contract Preservation & Ephemeral Mutation
- Original contract plaintext must remain immutable in React memory.
- Any perturbation experiment must execute against an ephemeral, deep-copied copy in memory with an explicit label: `[SYNTHETIC_MUTATION_SIMULATION]`.
- Mutated documents must never overwrite authoritative audit reports or client storage.

### 3.2 Computational Overhead & Privacy Safeguards
- Re-scoring a mutated contract requires full tokenization and model inference (~1.5 to 3.0s per run).
- Must run strictly client-side or within existing ephemeral FastAPI pipeline sessions.
- Zero mutation text or simulated bugs may be transmitted to external telemetry.

### 3.3 Opt-in UI Workflow (Phase 4B Blueprint)
```
[Auditor Workspace] 
       │
       ▼
"Test System Robustness" (Opt-In Modal)
       ├── 1. Select Mutation Type (e.g., Invert Dates / Swap Sections 2 & 5)
       ├── 2. Preview Synthetic Perturbation Diff
       ├── 3. Execute Diagnostic Re-Scoring
       └── 4. Verification Report: Did LexAudit catch the injected defect?
```
