# LexAudit Phase 4C-A — Experimental Opt-In Security & Validation Audit

## 1. Executive Summary & Problem Diagnosis
In the Phase 4C report, it was claimed that the counterfactual repositioning endpoint `POST /v1/experimental/reposition` was protected by an experimental opt-in requirement where omission of the flag causes HTTP 400.
However, an inspection of `src/api/schema.py` in Phase 4C revealed a critical security inconsistency:
```python
# Phase 4C implementation (vulnerable):
class RepositionRequest(BaseModel):
    document_id: str
    target_clause_id: str
    min_delta_threshold: float = 0.005
    experimental: bool = True  # <-- VULNERABILITY: defaulted to True!
```
Because `experimental` had a default value of `True`, any API client omitting `"experimental"` was silently treated as having opted in. Furthermore, standard Pydantic coercion would convert truthy strings (`"true"`, `"1"`) and integers (`1`) into `True`.
While the route implementation in `src/api/v1/router.py` correctly checked:
```python
if not request.experimental:
    raise HTTPException(status_code=400, detail="Explicit opt-in required: experimental must be True")
```
this check was only reached if the client explicitly sent `"experimental": false`. If the field was omitted entirely, the default `True` bypassed the check.

---

## 2. Minimal Security Correction (Phase 4C-A)
To fix this loophole without introducing architectural bloat, `src/api/schema.py` was minimally updated using Pydantic v2 strict typing:
```python
# Phase 4C-A corrected implementation:
class RepositionRequest(BaseModel):
    document_id: str = Field(..., description="Target document ID")
    target_clause_id: str = Field(..., description="ID of clause to reposition")
    min_delta_threshold: float = Field(
        0.005,
        ge=0.0,
        le=1.0,
        description="Minimum score delta required to recommend an alternative slot [0.0, 1.0]",
    )
    experimental: bool = Field(
        ...,
        strict=True,
        description="Explicit client opt-in required. Must be literal boolean true; omitted or false rejected.",
    )
```

### Validation Mechanics & HTTP Status Codes
1. **Pydantic Validation (HTTP 422 Unprocessable Entity)**:
   - **Omitted `experimental`**: Missing required field $\to$ HTTP 422.
   - **`null` value**: Cannot validate None as boolean $\to$ HTTP 422.
   - **Coercive strings (`"true"`, `"false"`)**: Under `strict=True`, Pydantic rejects non-boolean types $\to$ HTTP 422.
   - **Coercive numbers (`1`, `0`)**: Under `strict=True`, integers are rejected $\to$ HTTP 422.
   - **Out-of-bounds threshold (`min_delta_threshold < 0` or `> 1.0`)**: Rejected by `ge=0.0, le=1.0` $\to$ HTTP 422.
2. **Route-Level Logical Validation (HTTP 400 Bad Request)**:
   - **Explicit `"experimental": false`**: Passes schema validation as `bool`, but route logic rejects with `HTTPException(400, detail="Explicit opt-in required: experimental must be True")`.
   - **Document size $> 100$ clauses**: Rejected with `HTTPException(400, detail="Document exceeds maximum supported clause count for repositioning (100)")`.
   - **Unknown clause ID**: Rejected with `HTTPException(400, detail="Clause ... not found in document")`.
3. **Authentication & Ownership (HTTP 401 / 403 / 404)**:
   - **Missing / Invalid API Key**: Returns HTTP 401 / 403 before body inspection.
   - **Wrong Client Owner / Document Isolation**: If document was created by Client A, Client B receives HTTP 404 / 403.

---

## 3. Fail-Before-Inference Audit
Crucially, all schema and route-level rejections (400, 401, 403, 404, 422) occur **before** any neural embedding computation, Legal-BERT forward passes, or matrix candidate permutations are executed. 
This guarantees that unauthenticated, unauthorized, or malformed requests impose $O(1)$ zero-cost load on backend CPU/GPU resources.

---

## 4. Test Verification
The fix was formally verified by six new unit and integration tests added to `tests/test_api_reposition.py`:
- `test_reposition_omitted_opt_in_rejected_422`: Confirms HTTP 422 when `experimental` is absent.
- `test_reposition_null_opt_in_rejected_422`: Confirms HTTP 422 on `experimental: null`.
- `test_reposition_coercive_string_opt_in_rejected_422`: Confirms HTTP 422 on `experimental: "true"`.
- `test_reposition_negative_threshold_rejected_422`: Confirms HTTP 422 on `min_delta_threshold: -0.01`.
- `test_reposition_threshold_above_one_rejected_422`: Confirms HTTP 422 on `min_delta_threshold: 1.5`.
- `test_reposition_clauses_exceeding_100_rejected_400`: Confirms HTTP 400 before inference on 101 clauses.

All 13 tests in `tests/test_api_reposition.py` passed with zero errors.
