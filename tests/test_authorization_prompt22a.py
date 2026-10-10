"""
tests/test_authorization_prompt22a.py — Object-Level and Administrative Authorization Verification (Prompt 22A)

Tests:
Task B:
- Document and Job ownership enforcement between distinct authenticated clients
- Object-level authorization on /v1/analyze, /v1/jobs/{job_id}, /v1/jobs/{job_id}/results
- Object-level authorization on /v1/xai/attribution and /v1/xai/sensitivity
- Feedback authorization linking to protected documents
- Missing ownership metadata fails closed (no unauthorized access)
- Missing / invalid authentication rejection
- Rate limit headers preservation
- Ownership persistence in filesystem metadata

Task C:
- Administrative endpoint authorization on /v1/maintenance/cleanup
- Rejection of ordinary client keys (403 Forbidden)
- Rejection of missing/invalid keys (401 Unauthorized)
- Verified cleanup execution only upon authorized admin call
"""
import os
import time
import uuid
import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from cryptography.fernet import Fernet

from src.api.main import app
from src.api.storage import (
    save_encrypted_document,
    load_and_decrypt_document,
    document_exists,
    get_document_metadata,
    delete_document_files,
    UPLOAD_DIR
)
from src.api.jobs import create_job, get_job, JOB_STORE
from src.api.security import get_safe_client_id

# Fixed keys for isolated authorization testing
CLIENT_A_KEY = "test_auth_client_a_key_11111"
CLIENT_B_KEY = "test_auth_client_b_key_22222"
ADMIN_KEY = "test_auth_admin_key_99999"
INVALID_KEY = "invalid_nonexistent_key_00000"

HEADERS_A = {"X-API-Key": CLIENT_A_KEY}
HEADERS_B = {"X-API-Key": CLIENT_B_KEY}
HEADERS_ADMIN = {"X-API-Key": ADMIN_KEY}
HEADERS_INVALID = {"X-API-Key": INVALID_KEY}

SAMPLE_DOC = "1. Term. The agreement lasts for 12 months. 2. Governing Law. Delaware law applies."


@pytest.fixture(autouse=True)
def setup_auth_environment():
    """Configures isolated multi-key environment and ensures clean teardown."""
    old_api_keys = os.environ.get("API_KEYS")
    old_api_key = os.environ.get("API_KEY")
    old_admin_key = os.environ.get("ADMIN_API_KEY")

    # Set up both client keys and the admin key
    os.environ["API_KEYS"] = f"{CLIENT_A_KEY},{CLIENT_B_KEY}"
    os.environ["API_KEY"] = CLIENT_A_KEY
    os.environ["ADMIN_API_KEY"] = ADMIN_KEY

    yield

    # Restore environment
    if old_api_keys is not None:
        os.environ["API_KEYS"] = old_api_keys
    else:
        os.environ.pop("API_KEYS", None)

    if old_api_key is not None:
        os.environ["API_KEY"] = old_api_key
    else:
        os.environ.pop("API_KEY", None)

    if old_admin_key is not None:
        os.environ["ADMIN_API_KEY"] = old_admin_key
    else:
        os.environ.pop("ADMIN_API_KEY", None)


@pytest.fixture
def client():
    return TestClient(app)


# =============================================================================
# TASK B: DOCUMENT AND JOB OWNERSHIP AUTHORIZATION TESTS
# =============================================================================

def test_task_b_ownership_lifecycle_client_a_success(client):
    """Client A uploads, analyzes, retrieves job status and results successfully."""
    # 1. Client A uploads document
    resp_up = client.post(
        "/v1/upload",
        files={"file": ("contract_a.txt", SAMPLE_DOC.encode("utf-8"), "text/plain")},
        headers=HEADERS_A
    )
    assert resp_up.status_code == 200
    doc_id = resp_up.json()["doc_id"]

    # Verify metadata stores Client A's safe identity
    meta = get_document_metadata(doc_id)
    assert meta is not None
    assert meta["client_id"] == get_safe_client_id(CLIENT_A_KEY)

    # 2. Client A triggers analysis
    resp_an = client.post("/v1/analyze", json={"doc_id": doc_id}, headers=HEADERS_A)
    assert resp_an.status_code == 200
    job_id = resp_an.json()["job_id"]

    # 3. Client A checks job status
    resp_status = client.get(f"/v1/jobs/{job_id}", headers=HEADERS_A)
    assert resp_status.status_code == 200
    assert resp_status.json()["job_id"] == job_id

    # Wait for job completion
    for _ in range(60):
        r = client.get(f"/v1/jobs/{job_id}", headers=HEADERS_A)
        if r.json()["status"] == "COMPLETED":
            break
        time.sleep(0.5)

    # 4. Client A fetches results
    resp_res = client.get(f"/v1/jobs/{job_id}/results", headers=HEADERS_A)
    assert resp_res.status_code == 200
    assert resp_res.json()["doc_id"] == doc_id

    # Cleanup
    delete_document_files(doc_id)


def test_task_b_cross_client_document_access_denied(client):
    """Client B cannot analyze or access Client A's uploaded document."""
    # Client A uploads document
    resp_up = client.post(
        "/v1/upload",
        files={"file": ("contract_a.txt", SAMPLE_DOC.encode("utf-8"), "text/plain")},
        headers=HEADERS_A
    )
    assert resp_up.status_code == 200
    doc_id = resp_up.json()["doc_id"]

    # Client B attempts to analyze Client A's document -> 404 Not Found
    resp_an = client.post("/v1/analyze", json={"doc_id": doc_id}, headers=HEADERS_B)
    assert resp_an.status_code == 404
    assert "Document not found" in resp_an.json()["detail"]

    # Cleanup
    delete_document_files(doc_id)


def test_task_b_cross_client_job_access_denied(client):
    """Client B cannot poll status or fetch results for Client A's job."""
    # Client A uploads and analyzes
    resp_up = client.post(
        "/v1/upload",
        files={"file": ("contract_a.txt", SAMPLE_DOC.encode("utf-8"), "text/plain")},
        headers=HEADERS_A
    )
    doc_id = resp_up.json()["doc_id"]

    resp_an = client.post("/v1/analyze", json={"doc_id": doc_id}, headers=HEADERS_A)
    job_id = resp_an.json()["job_id"]

    # Client B attempts to poll Client A's job status -> 404
    resp_b_status = client.get(f"/v1/jobs/{job_id}", headers=HEADERS_B)
    assert resp_b_status.status_code == 404
    assert resp_b_status.json()["detail"] == "Job not found."

    # Client B attempts to fetch Client A's job results -> 404
    resp_b_results = client.get(f"/v1/jobs/{job_id}/results", headers=HEADERS_B)
    assert resp_b_results.status_code == 404
    assert resp_b_results.json()["detail"] == "Job not found."

    # Cleanup
    delete_document_files(doc_id)


def test_task_b_xai_endpoints_cross_client_denied(client):
    """Client B cannot request XAI attribution or sensitivity on Client A's document."""
    # Client A uploads document
    resp_up = client.post(
        "/v1/upload",
        files={"file": ("contract_a.txt", SAMPLE_DOC.encode("utf-8"), "text/plain")},
        headers=HEADERS_A
    )
    doc_id = resp_up.json()["doc_id"]

    # Get clause ID
    from src.api.dependencies import get_segmenter_dep
    segmenter = get_segmenter_dep()
    clauses = segmenter.segment(SAMPLE_DOC, doc_id)
    clause_id = clauses[0].clause_id

    # Client B requests attribution on Client A's document -> 404
    resp_attr = client.get(
        f"/v1/xai/attribution?doc_id={doc_id}&clause_id={clause_id}",
        headers=HEADERS_B
    )
    assert resp_attr.status_code == 404
    assert resp_attr.json()["detail"] == "Document not found."

    # Client B requests sensitivity on Client A's document -> 404
    resp_sens = client.get(
        f"/v1/xai/sensitivity?doc_id={doc_id}&clause_id={clause_id}",
        headers=HEADERS_B
    )
    assert resp_sens.status_code == 404
    assert resp_sens.json()["detail"] == "Document not found."

    # Client A requests attribution on own document -> 200
    resp_a_attr = client.get(
        f"/v1/xai/attribution?doc_id={doc_id}&clause_id={clause_id}",
        headers=HEADERS_A
    )
    assert resp_a_attr.status_code == 200

    # Cleanup
    delete_document_files(doc_id)


def test_task_b_feedback_cross_client_denied(client):
    """Client B cannot submit feedback modifying or targeting Client A's document."""
    # Client A uploads document
    resp_up = client.post(
        "/v1/upload",
        files={"file": ("contract_a.txt", SAMPLE_DOC.encode("utf-8"), "text/plain")},
        headers=HEADERS_A
    )
    doc_id = resp_up.json()["doc_id"]

    feedback_payload = {
        "doc_id": doc_id,
        "clause_id": "clause_1",
        "original_severity": "HIGH",
        "reviewer_verdict": "CONFIRM_ANOMALY",
        "reviewer_id": "reviewer_attacker",
        "provenance": "REAL"
    }

    # Client B attempts cross-client feedback injection -> 404
    resp_feed_b = client.post("/v1/feedback", json=feedback_payload, headers=HEADERS_B)
    assert resp_feed_b.status_code == 404
    assert resp_feed_b.json()["detail"] == "Document not found."

    # Client A submits feedback on own document -> 200
    feedback_payload["reviewer_id"] = "reviewer_owner"
    resp_feed_a = client.post("/v1/feedback", json=feedback_payload, headers=HEADERS_A)
    assert resp_feed_a.status_code == 200
    assert resp_feed_a.json()["message"] == "Feedback successfully recorded."

    # Cleanup
    delete_document_files(doc_id)


def test_task_b_missing_or_invalid_auth_rejected(client):
    """Missing or invalid API keys are rejected with HTTP 401."""
    # Missing authentication
    r1 = client.post("/v1/analyze", json={"doc_id": "doc_123"})
    assert r1.status_code == 401
    assert "not provided" in r1.json()["detail"]

    # Invalid authentication
    r2 = client.post("/v1/analyze", json={"doc_id": "doc_123"}, headers=HEADERS_INVALID)
    assert r2.status_code == 401
    assert "Invalid authentication credentials" in r2.json()["detail"]


def test_task_b_missing_ownership_metadata_fails_closed(client):
    """Documents without ownership metadata do not grant access."""
    # Manually create encrypted file without .meta.json
    doc_id = f"doc_legacy_{uuid.uuid4().hex[:6]}"
    enc_path = UPLOAD_DIR / f"{doc_id}.enc"
    fernet = Fernet(Fernet.generate_key())
    with open(enc_path, "wb") as f:
        f.write(fernet.encrypt(b"Plaintext content"))

    meta_path = UPLOAD_DIR / f"{doc_id}.meta.json"
    if meta_path.exists():
        meta_path.unlink()

    # Attempting to analyze without metadata must be rejected
    resp = client.post("/v1/analyze", json={"doc_id": doc_id}, headers=HEADERS_A)
    assert resp.status_code == 404

    # Cleanup
    if enc_path.exists():
        enc_path.unlink()


def test_task_b_ownership_survives_disk_persistence(client):
    """Document ownership metadata is persisted and reloaded from disk."""
    doc_id = f"doc_persist_{uuid.uuid4().hex[:6]}"
    save_encrypted_document(doc_id, "Sample contract", client_id=get_safe_client_id(CLIENT_A_KEY))

    # Read metadata directly from disk
    meta = get_document_metadata(doc_id)
    assert meta is not None
    assert meta["client_id"] == get_safe_client_id(CLIENT_A_KEY)

    # Verify authorization check succeeds with Client A
    resp_a = client.post("/v1/analyze", json={"doc_id": doc_id}, headers=HEADERS_A)
    assert resp_a.status_code == 200

    # Cleanup
    delete_document_files(doc_id)


def test_task_b_rate_limiting_functional_with_auth(client):
    """Rate limit headers are present on successful authenticated requests."""
    resp = client.post(
        "/v1/upload",
        files={"file": ("contract.txt", SAMPLE_DOC.encode("utf-8"), "text/plain")},
        headers=HEADERS_A
    )
    assert resp.status_code == 200
    assert "X-RateLimit-Limit" in resp.headers or "x-ratelimit-limit" in resp.headers
    assert "X-RateLimit-Remaining" in resp.headers or "x-ratelimit-remaining" in resp.headers

    doc_id = resp.json()["doc_id"]
    delete_document_files(doc_id)


# =============================================================================
# TASK C: ADMINISTRATIVE ENDPOINT AUTHORIZATION TESTS
# =============================================================================

def test_task_c_admin_key_authorizes_cleanup(client):
    """Admin key can successfully invoke administrative cleanup."""
    resp = client.post("/v1/maintenance/cleanup", headers=HEADERS_ADMIN)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "cleanup_complete"
    assert "deleted_documents_count" in data["result"]
    assert "retained_documents_count" in data["result"]


def test_task_c_ordinary_user_key_forbidden_from_cleanup(client):
    """Ordinary client key (Client A or Client B) receives 403 Forbidden."""
    resp_a = client.post("/v1/maintenance/cleanup", headers=HEADERS_A)
    assert resp_a.status_code == 403
    assert "Administrative privileges required" in resp_a.json()["detail"]

    resp_b = client.post("/v1/maintenance/cleanup", headers=HEADERS_B)
    assert resp_b.status_code == 403
    assert "Administrative privileges required" in resp_b.json()["detail"]


def test_task_c_missing_or_invalid_key_rejected_from_cleanup(client):
    """Missing key gives 401, invalid key gives 401."""
    # Missing key
    resp_missing = client.post("/v1/maintenance/cleanup")
    assert resp_missing.status_code == 401
    assert "not provided" in resp_missing.json()["detail"]

    # Invalid key
    resp_invalid = client.post("/v1/maintenance/cleanup", headers=HEADERS_INVALID)
    assert resp_invalid.status_code == 401
    assert "Invalid authentication credentials" in resp_invalid.json()["detail"]


def test_task_c_unauthorized_call_does_not_trigger_cleanup(client):
    """An unauthorized call does not prune expired test artifacts."""
    doc_id = f"doc_expired_test_{uuid.uuid4().hex[:6]}"
    save_encrypted_document(doc_id, "Expired document", client_id="test_owner")

    # Manually backdate the metadata to make it expired
    meta_path = UPLOAD_DIR / f"{doc_id}.meta.json"
    import json
    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)
    meta["created_timestamp"] = time.time() - 999999
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f)

    # Attempt cleanup with regular user key (should be denied)
    resp = client.post("/v1/maintenance/cleanup", headers=HEADERS_A)
    assert resp.status_code == 403

    # File should STILL exist because cleanup was not run
    assert document_exists(doc_id)

    # Now run authorized cleanup
    resp_admin = client.post("/v1/maintenance/cleanup", headers=HEADERS_ADMIN)
    assert resp_admin.status_code == 200

    # Cleanup any residual
    delete_document_files(doc_id)


def test_task_b_job_pruning_boundary_cases():
    """Verify BUG-010: Expired completed jobs are pruned; actively running jobs are not discarded."""
    from src.api.jobs import JOB_STORE, Job, JobStatus, _prune_jobs

    # 1. Old completed job (older than TTL)
    j_old_done = Job(job_id="j_old_done", doc_id="d1", status=JobStatus.COMPLETED, created_at=time.time() - 4000)
    JOB_STORE["j_old_done"] = j_old_done

    # 2. Old running job (older than TTL, but actively running)
    j_old_running = Job(job_id="j_old_running", doc_id="d2", status=JobStatus.RUNNING, created_at=time.time() - 4000)
    JOB_STORE["j_old_running"] = j_old_running

    # 3. Fresh completed job
    j_fresh_done = Job(job_id="j_fresh_done", doc_id="d3", status=JobStatus.COMPLETED, created_at=time.time())
    JOB_STORE["j_fresh_done"] = j_fresh_done

    # Run pruning
    _prune_jobs()

    assert "j_old_done" not in JOB_STORE, "Old completed job must be pruned"
    assert "j_old_running" in JOB_STORE, "Old actively running job must NOT be pruned"
    assert "j_fresh_done" in JOB_STORE, "Fresh completed job must NOT be pruned"

    # Cleanup test jobs
    JOB_STORE.pop("j_old_done", None)
    JOB_STORE.pop("j_old_running", None)
    JOB_STORE.pop("j_fresh_done", None)
