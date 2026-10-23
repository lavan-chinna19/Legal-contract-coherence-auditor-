"""
tests/test_api_redteam.py — Security & Integration Tests for POST /v1/experimental/redteam.
Phase 4D Verification.
"""
import io
import os
import pytest
from fastapi.testclient import TestClient

VALID_API_KEY = "test_key_phase4d"
OTHER_API_KEY = "other_client_key_phase4d"
os.environ["API_KEYS"] = f"{VALID_API_KEY},{OTHER_API_KEY}"

@pytest.fixture(autouse=True)
def setup_api_keys():
    current = os.environ.get("API_KEYS", "")
    keys = set(k.strip() for k in current.split(",") if k.strip())
    keys.add(VALID_API_KEY)
    keys.add(OTHER_API_KEY)
    keys.add("test_key_phase4c")
    keys.add("other_client_key_phase4c")
    os.environ["API_KEYS"] = ",".join(keys)
    yield

from src.api.main import app
client = TestClient(app)

SAMPLE_CONTRACT_TEXT = """1. Preamble. This Agreement is entered into between Party A and Party B.
2. Definitions. Certain terms used herein are defined in accordance with Section 2.
3. Payment Terms. All payments shall be made within thirty (30) days of invoice date.
4. Confidentiality. Each party agrees to protect the confidential information of the other.
5. Governing Law. This Agreement shall be governed by the laws of the State of Delaware."""


@pytest.fixture
def uploaded_doc_id():
    res = client.post(
        "/v1/upload",
        headers={"X-API-Key": VALID_API_KEY},
        files={"file": ("contract.txt", io.BytesIO(SAMPLE_CONTRACT_TEXT.encode("utf-8")), "text/plain")}
    )
    assert res.status_code == 200
    return res.json()["doc_id"]


def test_redteam_missing_auth():
    res = client.post(
        "/v1/experimental/redteam",
        json={"fixture_id": "SYNTH_DOC_01_MSA", "perturbation_type": "P1_DISPLACEMENT", "experimental": True}
    )
    assert res.status_code in [401, 403]


def test_redteam_invalid_api_key():
    res = client.post(
        "/v1/experimental/redteam",
        headers={"X-API-Key": "invalid_unregistered_key"},
        json={"fixture_id": "SYNTH_DOC_01_MSA", "perturbation_type": "P1_DISPLACEMENT", "experimental": True}
    )
    assert res.status_code == 401


def test_redteam_missing_opt_in():
    res = client.post(
        "/v1/experimental/redteam",
        headers={"X-API-Key": VALID_API_KEY},
        json={"fixture_id": "SYNTH_DOC_01_MSA", "perturbation_type": "P1_DISPLACEMENT", "experimental": False}
    )
    assert res.status_code == 400
    assert "experimental capability" in res.json()["detail"].lower()


def test_redteam_unsupported_perturbation_type():
    res = client.post(
        "/v1/experimental/redteam",
        headers={"X-API-Key": VALID_API_KEY},
        json={"fixture_id": "SYNTH_DOC_01_MSA", "perturbation_type": "P99_UNSUPPORTED", "experimental": True}
    )
    assert res.status_code == 400
    assert "Unsupported perturbation type" in res.json()["detail"]


def test_redteam_invalid_fixture():
    res = client.post(
        "/v1/experimental/redteam",
        headers={"X-API-Key": VALID_API_KEY},
        json={"fixture_id": "NONEXISTENT_FIXTURE", "perturbation_type": "P1_DISPLACEMENT", "experimental": True}
    )
    assert res.status_code == 404


def test_redteam_cross_tenant_document_access(uploaded_doc_id):
    # Other client attempts to access uploaded document
    res = client.post(
        "/v1/experimental/redteam",
        headers={"X-API-Key": OTHER_API_KEY},
        json={"doc_id": uploaded_doc_id, "perturbation_type": "P1_DISPLACEMENT", "experimental": True}
    )
    assert res.status_code == 404


def test_redteam_invalid_target_clause(uploaded_doc_id):
    res = client.post(
        "/v1/experimental/redteam",
        headers={"X-API-Key": VALID_API_KEY},
        json={
            "doc_id": uploaded_doc_id,
            "perturbation_type": "P5_BROKEN_REFERENCE",
            "target_clause_ids": ["nonexistent_clause_id"],
            "experimental": True
        }
    )
    assert res.status_code == 404
    assert "Target clause" in res.json()["detail"]


def test_redteam_successful_synthetic_evaluation():
    res = client.post(
        "/v1/experimental/redteam",
        headers={"X-API-Key": VALID_API_KEY},
        json={
            "fixture_id": "SYNTH_DOC_01_MSA",
            "perturbation_type": "P5_BROKEN_REFERENCE",
            "target_clause_ids": ["SYNTH_DOC_01_MSA_c03"],
            "parameters": {"old_target_sec": "2", "new_nonexistent_sec": "Section 99"},
            "experimental": True
        }
    )
    assert res.status_code == 200
    data = res.json()
    assert data["perturbation_type"] == "P5_BROKEN_REFERENCE"
    assert data["detection_status"] == "DETECTED"
    assert data["attribution_valid"] is True
    assert data["oracle_result"]["valid_transformation"] is True
    assert len(data["new_rule_flags"]) >= 1
    assert len(data["original_clauses_preview"]) > 0
    assert len(data["perturbed_clauses_preview"]) > 0
