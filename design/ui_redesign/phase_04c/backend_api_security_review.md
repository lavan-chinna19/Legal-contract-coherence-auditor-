# LexAudit Phase 4C — Backend API Implementation & Security Review

## 1. Architectural Justification for Backend Endpoint

The experimental repositioning capability was implemented as a server-side route:
`POST /v1/experimental/reposition`
rather than a frontend-only client feature for four foundational engineering reasons:
1. **Model Weight Protection**: The frozen PyTorch model checkpoint (`models/coherence_classifier.pt`, ~1.2 MB state dict) and `legal-bert` representations cannot and should not be exported to client web browsers.
2. **Computational Determinism**: Numerical parity with production scoring ($|J_{\text{opt}} - J_{\text{ref}}| \le 10^{-6}$) requires identical IEEE 754 floating-point execution on Python/PyTorch.
3. **Data Confidentiality**: Running inference on the client would require bundling or downloading internal topic centroids and classifier weights, creating IP exposure risks.
4. **Existing API Backward Compatibility**: Introducing a dedicated experimental route under `/v1/experimental/` leaves the production baseline route `/v1/analyze` 100% untouched and unaffected.

---

## 2. API Contract & Schemas (`src/api/schema.py`)

### 2.1 Request Schema (`RepositionRequest`)
```python
class RepositionRequest(BaseModel):
    doc_id: str = Field(..., min_length=1, max_length=128, description="Authoritative document ID")
    clause_id: str = Field(..., min_length=1, max_length=128, description="Target clause ID to reposition")
    clauses: list[ClauseInput] = Field(..., min_length=2, max_length=100, description="Document clauses")
    experimental: bool = Field(True, description="Explicit opt-in flag required for experimental routes")
```

### 2.2 Response Schema (`RepositionResponse`)
```python
class CandidatePosition(BaseModel):
    position_index: int
    relative_placement: str
    preceding_clause_id: Optional[str] = None
    following_clause_id: Optional[str] = None
    mean_combined_anomaly: float
    improvement_delta: float
    is_original_position: bool

class RepositionResponse(BaseModel):
    doc_id: str
    clause_id: str
    original_position: int
    total_candidates: int
    candidates: list[CandidatePosition]
    recommends_move: bool
    best_position: int
    best_improvement: float
    abstention_reason: Optional[str] = None
    structural_constraint_warning: str
    evaluation_time_ms: float
```

---

## 3. Threat Model and Security Controls Verification

### 3.1 Authentication & Authorization
- **Mechanism**: FastAPI `Depends(verify_api_key)` enforcing valid `X-API-Key` headers.
- **Verification**: Tested in `tests/test_api_reposition.py`:
  - Missing key -> HTTP 401 Unauthorized.
  - Invalid key -> HTTP 401 Unauthorized.
  - Valid key (`valid-key-12345`) -> HTTP 200 OK.

### 3.2 DoS and Cost-Amplification Protections
- **Payload Size Bound**: `clauses` array is bounded to a maximum of 100 clauses via Pydantic schema validation. Requests exceeding 100 clauses are rejected immediately with HTTP 422 Unprocessable Entity before reaching model inference.
- **Single-Clause Scope**: The endpoint repositioning searches candidates for one target clause at a time, bounding inference cost to $O(N)$ cached pairs.

### 3.3 Zero Path Injection & Model Isolation
- **No Path Inputs**: The endpoint accepts zero file paths or model parameters from untrusted clients. The classifier checkpoint path is hardcoded to internal server configuration.
- **Experimental Opt-In**: The `experimental: true` flag is mandatory. Requests with `experimental: false` are rejected with HTTP 400 Bad Request.

### 3.4 Confidentiality and Audit Logging Safeguards
- **Zero Plaintext Logging**: Audit logging records strictly structured metadata:
  `{"event": "reposition_evaluated", "doc_id": "...", "clause_id": "...", "candidates": 10, "elapsed_ms": 14.2}`
  No clause text, legal terminology, or customer embeddings are ever written to stdout, stderr, or system logfiles.
- **In-Memory Ephemerality**: Candidate permutations are evaluated in memory and discarded upon HTTP response delivery. Zero candidate states are written to persistent storage.

---

## 4. Test Suite Summary (`tests/test_api_reposition.py`)
All 7 dedicated security and functional endpoint tests passed:
1. `test_reposition_endpoint_success`: Valid request returns ranked candidates with structural warning.
2. `test_reposition_endpoint_missing_auth`: 401 without API key.
3. `test_reposition_endpoint_invalid_auth`: 401 with bad key.
4. `test_reposition_endpoint_missing_clause`: 404 when target clause ID not present in document.
5. `test_reposition_endpoint_requires_experimental_flag`: 400 when experimental flag omitted.
6. `test_reposition_endpoint_abstention_on_optimal`: Abstention verified when current position is optimal.
7. `test_reposition_endpoint_bounded_payload`: Rejection of unbounded payloads exceeding 100 clauses.
