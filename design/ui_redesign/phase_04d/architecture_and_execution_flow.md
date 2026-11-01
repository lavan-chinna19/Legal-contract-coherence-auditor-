# Phase 4D Architecture and Execution Flow

## 1. System Topology
The Self Red-Team Robustness Laboratory is integrated as an isolated, privacy-preserving research module:

```
[React Frontend (Robustness Lab)]
       │
       │ HTTP POST /v1/experimental/redteam
       │ Headers: X-API-Key, Content-Type: application/json
       ▼
[FastAPI Router (src/api/v1/router.py)]
       │
       ├─► 1. Auth Guard: verify_api_key (dev_auditor_key_12345)
       ├─► 2. Tenant Isolation: verify doc_id belongs to client
       ├─► 3. Explicit Opt-in: strict assertion (experimental == True)
       ├─► 4. Bounds Enforcement: clause count <= 100, length <= 25,000 chars
       │
       ▼
[RedTeamExperimentRunner (src/redteam/runner.py)]
       │
       ├─► 5. Ephemeral In-Memory Copy Creation (Zero Contract Mutation)
       ├─► 6. Apply Pure Transformation (P1–P10) (src/redteam/transformations.py)
       ├─► 7. Independent Ground-Truth Oracle Validation (src/redteam/oracle.py)
       │       (Regex / datetime parsing; zero circular checker calls)
       │
       ├─► 8. Frozen LexAudit UnifiedAuditor Execution (src/rules/unified_pipeline.py)
       │       Run A: Baseline Original Document
       │       Run B: Ephemeral Modified Copy
       │
       ├─► 9. Differential Metric Extraction (src/redteam/runner.py)
       │       - Delta Mean Anomaly (ΔS̄)
       │       - Max Transition Shift (ΔS_B)
       │       - New Deterministic Rule Flags (ΔRules)
       │       - Channel Ablations (Ch A only, Ch B only, Combined, Rules only)
       │       - Attribution Validity (Span/Clause ID match)
       │       - Scientific Failure Diagnosis (if undetected)
       │
       ▼
[JSON Response: RedTeamCaseResponse]
       │
       ▼
[React UI Rendering (Robustness Lab)]
       ├─► Detection Outcome Badge & Attribution Tag
       ├─► Side-by-Side Diff & SHA-256 Immutability Ledger
       ├─► Channel Response & Ablation Deltas
       ├─► Deterministic Rule Violations Inspector
       └─► Scientific Methodology & Limitations Notice
```

## 2. In-Memory Copy-on-Write Guarantees
- The original document sequence and text are treated as strictly immutable.
- Checksums (`SHA-256`) of both original and modified sequences are computed and displayed to the user.
- Transformations only return modified copies with new experimental clause IDs (`dup_...` or `variant_...`).
- Zero records are written to production document stores, feedback tables, or client caches.
