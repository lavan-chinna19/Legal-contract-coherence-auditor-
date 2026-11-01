# Phase 4D Resource Limit and Bounded Execution Verification

## 1. Resource Limits Specification
To safeguard the LexAudit backend against denial-of-service, unbounded memory consumption, or catastrophic GPU/CPU allocation during adversarial testing, strict resource boundaries are enforced in `src/api/v1/router.py`:
- `MAX_REDTEAM_CLAUSES = 100`: Contracts with $>100$ clauses are rejected with `HTTP 400 Bad Request`.
- `MAX_CLAUSE_CHARS = 25000`: Clauses exceeding 25,000 characters are rejected with `HTTP 400 Bad Request`.
- `MAX_PARAMS_SIZE = 10000`: Complex malicious parameter payloads are bounded.
- Synchronous In-Memory Execution: Bounded by Python's transient garbage collection; no background threads or infinite loops.

## 2. Latency Profiling Results
Measured end-to-end execution latency across canonical scenarios (`research/redteam_robustness/latency_results.csv`):
- Mean Total Experiment Time: **685.2 ms** (Range: 550.0 ms – 941.9 ms)
- Mean Transformation Time: **0.18 ms**
- Mean Oracle Validation Time: **0.12 ms**
- Mean Frozen Auditor Time: **684.9 ms** (Embedding generation + pair scoring + rule checks)

All requests execute comfortably within responsive browser interaction budgets.
