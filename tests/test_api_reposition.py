"""
tests/test_api_reposition.py — Security & Integration Tests for POST /v1/experimental/reposition.
Phase 4C Verification.
"""
import io
import pytest
from fastapi.testclient import TestClient

import os

VALID_API_KEY = "test_key_phase4c"
OTHER_API_KEY = "other_client_key_phase4c"
os.environ["API_KEYS"] = f"{VALID_API_KEY},{OTHER_API_KEY}"

from src.api.main import app

client = TestClient(app)

SAMPLE_CONTRACT_TEXT = """1. Preamble. This Agreement is entered into between Party A and Party B.
2. Definitions. Certain terms used herein are defined in accordance with Section 2.
3. Payment Terms. All payments shall be made within thirty (30) days of invoice date.
4. Confidentiality. Each party agrees to protect the confidential information of the other.
5. Governing Law. This Agreement shall be governed by the laws of the State of Delaware."""
@pytest.fixture(autouse=True)
def setup_api_keys():
    current = os.environ.get("API_KEYS", "")
    keys = set(k.strip() for k in current.split(",") if k.strip())
    keys.add(VALID_API_KEY)
    keys.add(OTHER_API_KEY)
    os.environ["API_KEYS"] = ",".join(keys)
    yield


@pytest.fixture
def uploaded_doc_id():
    # Upload document as client_alpha
    res = client.post(
        "/v1/upload",
        headers={"X-API-Key": VALID_API_KEY},
        files={"file": ("contract.txt", io.BytesIO(SAMPLE_CONTRACT_TEXT.encode("utf-8")), "text/plain")}
    )
    assert res.status_code == 200
    doc_id = res.json()["doc_id"]
    return doc_id


def test_reposition_missing_auth():
    res = client.post(
        "/v1/experimental/reposition",
        json={"doc_id": "doc_dummy", "clause_id": "dummy_c0", "experimental": True}
    )
    assert res.status_code in [401, 403]


def test_reposition_invalid_api_key():
    res = client.post(
        "/v1/experimental/reposition",
        headers={"X-API-Key": "invalid_unregistered_key"},
        json={"doc_id": "doc_dummy", "clause_id": "dummy_c0", "experimental": True}
    )
    assert res.status_code == 401


def test_reposition_missing_experimental_opt_in(uploaded_doc_id):
    res = client.post(
        "/v1/experimental/reposition",
        headers={"X-API-Key": VALID_API_KEY},
        json={"doc_id": uploaded_doc_id, "clause_id": f"{uploaded_doc_id}_2", "experimental": False}
    )
    assert res.status_code == 400
    assert "experimental" in res.json()["detail"].lower()


def test_reposition_missing_document():
    res = client.post(
        "/v1/experimental/reposition",
        headers={"X-API-Key": VALID_API_KEY},
        json={"doc_id": "doc_nonexistent_999", "clause_id": "clause_00", "experimental": True}
    )
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()


def test_reposition_wrong_document_owner(uploaded_doc_id):
    # Attempting to access client_alpha's document using client_beta's key
    res = client.post(
        "/v1/experimental/reposition",
        headers={"X-API-Key": OTHER_API_KEY},
        json={"doc_id": uploaded_doc_id, "clause_id": f"{uploaded_doc_id}_1", "experimental": True}
    )
    assert res.status_code == 404  # Strict ownership isolation returns 404


def test_reposition_missing_clause_id(uploaded_doc_id):
    res = client.post(
        "/v1/experimental/reposition",
        headers={"X-API-Key": VALID_API_KEY},
        json={"doc_id": uploaded_doc_id, "clause_id": "nonexistent_clause_xyz", "experimental": True}
    )
    assert res.status_code == 404
    assert "not found in document" in res.json()["detail"].lower()


def test_reposition_successful_evaluation(uploaded_doc_id):
    target_clause = f"{uploaded_doc_id}_2"
    res = client.post(
        "/v1/experimental/reposition",
        headers={"X-API-Key": VALID_API_KEY},
        json={"doc_id": uploaded_doc_id, "clause_id": target_clause, "experimental": True}
    )
    assert res.status_code == 200
    data = res.json()

    assert data["doc_id"] == uploaded_doc_id
    assert data["target_clause_id"] == target_clause
    assert data["total_clauses"] >= 3
    assert len(data["candidates"]) == data["total_clauses"]
    assert "warning_notice" in data
    assert "Experimental" in data["warning_notice"]
    assert "primary_objective_name" in data
    assert data["optimization_verified"] is True
    assert data["evaluation_time_ms"] > 0

    # Verify candidate ranks and fields
    for c in data["candidates"]:
        assert "position_idx" in c
        assert "rank" in c
        assert "relative_placement" in c
        assert "mean_combined_score" in c
        assert "objective_delta" in c
        assert 0.0 <= c["mean_combined_score"] <= 1.0

    # Verify best candidate has rank 1
    best_candidate = next(c for c in data["candidates"] if c["position_idx"] == data["best_candidate_idx"])
    assert best_candidate["rank"] == 1


def test_reposition_omitted_experimental_flag(uploaded_doc_id):
    """GATE 4 & 6: Omitted experimental flag must fail closed with HTTP 422 (not default to true)."""
    res = client.post(
        "/v1/experimental/reposition",
        headers={"X-API-Key": VALID_API_KEY},
        json={"doc_id": uploaded_doc_id, "clause_id": f"{uploaded_doc_id}_2"}
    )
    assert res.status_code == 422


def test_reposition_null_experimental_flag(uploaded_doc_id):
    """Null experimental flag must be rejected with HTTP 422."""
    res = client.post(
        "/v1/experimental/reposition",
        headers={"X-API-Key": VALID_API_KEY},
        json={"doc_id": uploaded_doc_id, "clause_id": f"{uploaded_doc_id}_2", "experimental": None}
    )
    assert res.status_code == 422


def test_reposition_coercive_or_invalid_experimental_flag(uploaded_doc_id):
    """Coercive string or integer types for boolean flag must be rejected with HTTP 422 under strict mode."""
    res = client.post(
        "/v1/experimental/reposition",
        headers={"X-API-Key": VALID_API_KEY},
        json={"doc_id": uploaded_doc_id, "clause_id": f"{uploaded_doc_id}_2", "experimental": "true"}
    )
    assert res.status_code == 422

    res_int = client.post(
        "/v1/experimental/reposition",
        headers={"X-API-Key": VALID_API_KEY},
        json={"doc_id": uploaded_doc_id, "clause_id": f"{uploaded_doc_id}_2", "experimental": 1}
    )
    assert res_int.status_code == 422


def test_reposition_negative_threshold_rejected(uploaded_doc_id):
    """Negative threshold must be rejected with HTTP 422."""
    res = client.post(
        "/v1/experimental/reposition",
        headers={"X-API-Key": VALID_API_KEY},
        json={"doc_id": uploaded_doc_id, "clause_id": f"{uploaded_doc_id}_2", "experimental": True, "min_delta_threshold": -0.05}
    )
    assert res.status_code == 422


def test_reposition_excessive_threshold_rejected(uploaded_doc_id):
    """Out-of-bounds threshold (> 1.0) must be rejected with HTTP 422."""
    res = client.post(
        "/v1/experimental/reposition",
        headers={"X-API-Key": VALID_API_KEY},
        json={"doc_id": uploaded_doc_id, "clause_id": f"{uploaded_doc_id}_2", "experimental": True, "min_delta_threshold": 1.5}
    )
    assert res.status_code == 422


def test_reposition_document_size_limit_exceeded():
    """Documents exceeding MAX_REPOSITION_CLAUSES (100) must be rejected with HTTP 400 before scoring."""
    long_doc_text = "\n".join([f"{i}. Clause {i}. Standard boilerplate text." for i in range(105)])
    res = client.post(
        "/v1/upload",
        headers={"X-API-Key": VALID_API_KEY},
        files={"file": ("long_contract.txt", io.BytesIO(long_doc_text.encode("utf-8")), "text/plain")}
    )
    assert res.status_code == 200
    doc_id = res.json()["doc_id"]

    res_eval = client.post(
        "/v1/experimental/reposition",
        headers={"X-API-Key": VALID_API_KEY},
        json={"doc_id": doc_id, "clause_id": f"{doc_id}_5", "experimental": True}
    )
    assert res_eval.status_code == 400
    assert "exceeds maximum supported size" in res_eval.json()["detail"].lower()
