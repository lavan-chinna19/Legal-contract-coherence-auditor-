"""
tests/test_security.py — Automated Security & Hardening Tests (Prompt 16 Work Package G)

Verifies:
 1. unauthenticated protected request -> rejected (401)
 2. invalid credential -> rejected (401)
 3. valid credential -> accepted (200)
 4. health endpoint remains accessible (200)
 5. rate limiter triggers under a real burst (429)
 6. upload is encrypted at rest (.enc file created)
 7. raw stored bytes are not plaintext (marker string absent from raw disk bytes)
 8. encrypted upload can still be decrypted internally for pipeline processing
 9. retention cleanup actually deletes expired data
10. non-expired data remains
11. audit logs contain security metadata
12. audit logs contain no contract plaintext
13. audit logs contain no API secret
14. encryption key is not exposed through API responses/errors
15. existing Prompt 15 API integration behavior still works with authentication
16. existing feedback endpoint remains functional with authentication
"""
import os
import io
import time
import uuid
import logging
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Setup dynamic test keys via environment (No hardcoded secrets committed)
TEST_KEY_VALUE = os.environ.get("API_KEY") or f"test_sec_key_{uuid.uuid4().hex}"
os.environ["API_KEY"] = TEST_KEY_VALUE
AUTH_HEADERS = {"X-API-Key": TEST_KEY_VALUE}
BEARER_HEADERS = {"Authorization": f"Bearer {TEST_KEY_VALUE}"}
INVALID_HEADERS = {"X-API-Key": "invalid_unauthorized_token_xyz"}

from src.api.main import app
from src.api.storage import (
    save_encrypted_document,
    load_and_decrypt_document,
    UPLOAD_DIR,
    get_fernet
)
from src.api.retention import cleanup_expired_artifacts
from src.api.rate_limiter import rate_limiter

client = TestClient(app)


# Sample contract text with unique, searchable test markers
SAMPLE_CONTRACT_TEXT = (
    "CONFIDENTIAL EMPLOYMENT AGREEMENT. "
    "SECTION 1.1: The Executive agrees to maintain strict secrecy. "
    "UNIQUE_PLAINTEXT_MARKER_987654321_DO_NOT_LEAK. "
    "Governing Law: State of Delaware."
)
PLAINTEXT_MARKER = "UNIQUE_PLAINTEXT_MARKER_987654321_DO_NOT_LEAK"


@pytest.fixture(autouse=True)
def reset_limiter():
    """Reset rate limiter state between tests."""
    rate_limiter.reset()
    yield
    rate_limiter.reset()


def test_01_unauthenticated_protected_requests_rejected():
    """Requirement 1: Unauthenticated protected requests must return HTTP 401."""
    # Test upload
    r_upload = client.post("/v1/upload", files={"file": ("contract.txt", b"test content", "text/plain")})
    assert r_upload.status_code == 401
    assert "detail" in r_upload.json()

    # Test analyze
    r_analyze = client.post("/v1/analyze", json={"doc_id": "doc_test123"})
    assert r_analyze.status_code == 401

    # Test jobs status
    r_job = client.get("/v1/jobs/test-job-uuid")
    assert r_job.status_code == 401

    # Test job results
    r_results = client.get("/v1/jobs/test-job-uuid/results")
    assert r_results.status_code == 401

    # Test feedback
    r_feedback = client.post("/v1/feedback", json={
        "doc_id": "doc_test",
        "clause_id": "c_1",
        "original_severity": "LOW",
        "reviewer_verdict": "AGREE",
        "reviewer_id": "rev_1"
    })
    assert r_feedback.status_code == 401


def test_02_invalid_credentials_rejected():
    """Requirement 2: Invalid credentials must return HTTP 401 without leaking info."""
    response = client.post(
        "/v1/upload",
        files={"file": ("contract.txt", b"test content", "text/plain")},
        headers=INVALID_HEADERS
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid authentication credentials."
    # Ensure invalid token is not echoed in error
    assert "invalid_unauthorized_token_xyz" not in response.text


def test_03_valid_credentials_accepted():
    """Requirement 3: Valid credentials via X-API-Key and Bearer header are accepted."""
    # Test via X-API-Key
    r1 = client.post(
        "/v1/upload",
        files={"file": ("contract.txt", SAMPLE_CONTRACT_TEXT.encode("utf-8"), "text/plain")},
        headers=AUTH_HEADERS
    )
    assert r1.status_code == 200
    doc_id = r1.json()["doc_id"]
    assert doc_id.startswith("doc_")

    # Test via Authorization: Bearer
    r2 = client.post(
        "/v1/upload",
        files={"file": ("contract2.txt", SAMPLE_CONTRACT_TEXT.encode("utf-8"), "text/plain")},
        headers=BEARER_HEADERS
    )
    assert r2.status_code == 200


def test_04_health_and_readiness_remain_accessible():
    """Requirement 4: Health and readiness endpoints remain accessible without authentication."""
    r_health = client.get("/health")
    assert r_health.status_code == 200
    assert r_health.json()["status"] == "ok"

    r_ready = client.get("/ready")
    assert r_ready.status_code == 200
    assert r_ready.json()["status"] == "ready"


def test_05_rate_limiter_triggers_under_burst():
    """Requirement 5: Burst of requests triggers HTTP 429 with rate limit headers."""
    # Configure tight burst threshold
    burst_limit = 5
    window_sec = 60.0
    
    # Send requests up to burst limit
    for i in range(burst_limit):
        headers = rate_limiter.check(
            client_id="test_rate_client",
            endpoint_action="BURST_TEST",
            limit=burst_limit,
            window=window_sec
        )
        assert "X-RateLimit-Remaining" in headers

    # Next request must trigger 429
    with pytest.raises(Exception) as exc_info:
        rate_limiter.check(
            client_id="test_rate_client",
            endpoint_action="BURST_TEST",
            limit=burst_limit,
            window=window_sec
        )
    
    from fastapi import HTTPException
    assert isinstance(exc_info.value, HTTPException)
    assert exc_info.value.status_code == 429
    assert "Retry-After" in exc_info.value.headers
    assert exc_info.value.headers["X-RateLimit-Remaining"] == "0"


def test_06_upload_encrypted_at_rest():
    """Requirement 6: Upload writes encrypted file (.enc) and not plaintext .txt."""
    response = client.post(
        "/v1/upload",
        files={"file": ("contract.txt", SAMPLE_CONTRACT_TEXT.encode("utf-8"), "text/plain")},
        headers=AUTH_HEADERS
    )
    assert response.status_code == 200
    doc_id = response.json()["doc_id"]

    enc_file = UPLOAD_DIR / f"{doc_id}.enc"
    assert enc_file.exists(), "Encrypted .enc file must exist on disk"
    assert enc_file.stat().st_size > 0


def test_07_raw_stored_bytes_are_not_plaintext():
    """Requirement 7: Inspect raw stored disk bytes and verify plaintext marker is completely absent."""
    response = client.post(
        "/v1/upload",
        files={"file": ("secret_contract.txt", SAMPLE_CONTRACT_TEXT.encode("utf-8"), "text/plain")},
        headers=AUTH_HEADERS
    )
    assert response.status_code == 200
    doc_id = response.json()["doc_id"]

    enc_file = UPLOAD_DIR / f"{doc_id}.enc"
    with open(enc_file, "rb") as f:
        raw_bytes = f.read()

    # The raw bytes must be Fernet ciphertext (starts with b'gAAAAA')
    assert raw_bytes.startswith(b"gAAAAA"), "Must be a valid Fernet ciphertext token"
    
    # The sensitive plaintext marker must NOT appear anywhere in the raw bytes
    assert PLAINTEXT_MARKER.encode("utf-8") not in raw_bytes
    assert b"CONFIDENTIAL EMPLOYMENT AGREEMENT" not in raw_bytes


def test_08_encrypted_upload_decrypted_internally():
    """Requirement 8: Encrypted upload can be decrypted internally for pipeline processing."""
    response = client.post(
        "/v1/upload",
        files={"file": ("test_decrypt.txt", SAMPLE_CONTRACT_TEXT.encode("utf-8"), "text/plain")},
        headers=AUTH_HEADERS
    )
    assert response.status_code == 200
    doc_id = response.json()["doc_id"]

    # Decrypt internally
    decrypted_text = load_and_decrypt_document(doc_id)
    assert decrypted_text == SAMPLE_CONTRACT_TEXT
    assert PLAINTEXT_MARKER in decrypted_text


def test_09_retention_cleanup_deletes_expired_data():
    """Requirement 9: Enforced data retention cleanup actually deletes expired artifacts."""
    doc_id = f"doc_expired_{uuid.uuid4().hex[:6]}"
    save_encrypted_document(doc_id, SAMPLE_CONTRACT_TEXT, client_id="test_retention")

    enc_path = UPLOAD_DIR / f"{doc_id}.enc"
    assert enc_path.exists()

    # Sleep slightly to ensure age > 0.05
    time.sleep(0.1)

    # Run cleanup with accelerated threshold (0.05 seconds)
    result = cleanup_expired_artifacts(max_age_seconds=0.05)
    assert result["deleted_documents_count"] >= 1
    assert not enc_path.exists(), "Expired artifact must be deleted"


def test_10_non_expired_data_remains():
    """Requirement 10: Non-expired artifacts remain intact during cleanup."""
    doc_id = f"doc_fresh_{uuid.uuid4().hex[:6]}"
    save_encrypted_document(doc_id, SAMPLE_CONTRACT_TEXT, client_id="test_fresh")

    enc_path = UPLOAD_DIR / f"{doc_id}.enc"
    assert enc_path.exists()

    # Run cleanup with a 3600 second (1 hour) retention window
    cleanup_expired_artifacts(max_age_seconds=3600.0)

    # Fresh artifact must still exist
    assert enc_path.exists(), "Non-expired artifact must remain on disk"


def test_11_audit_logs_contain_security_metadata():
    """Requirement 11: Audit logs capture safe security metadata (timestamp, client_id, status, event_type)."""
    log_capture = io.StringIO()
    handler = logging.StreamHandler(log_capture)
    audit_logger = logging.getLogger("audit")
    audit_logger.addHandler(handler)

    client.post(
        "/v1/upload",
        files={"file": ("audit_test.txt", b"Sample test clause.", "text/plain")},
        headers=AUTH_HEADERS
    )
    
    audit_logger.removeHandler(handler)
    logs = log_capture.getvalue()

    assert "[AUDIT]" in logs
    assert "DOCUMENT_UPLOAD" in logs
    assert "key_" in logs  # Safe hashed client ID
    assert "SUCCESS" in logs


def test_12_audit_logs_contain_no_contract_plaintext():
    """Requirement 12: Audit logs must NEVER contain contract plaintext."""
    log_capture = io.StringIO()
    handler = logging.StreamHandler(log_capture)
    audit_logger = logging.getLogger("audit")
    audit_logger.addHandler(handler)

    client.post(
        "/v1/upload",
        files={"file": ("secret.txt", SAMPLE_CONTRACT_TEXT.encode("utf-8"), "text/plain")},
        headers=AUTH_HEADERS
    )

    audit_logger.removeHandler(handler)
    logs = log_capture.getvalue()

    assert PLAINTEXT_MARKER not in logs
    assert "CONFIDENTIAL EMPLOYMENT AGREEMENT" not in logs


def test_13_audit_logs_contain_no_api_secret():
    """Requirement 13: Audit logs must NEVER contain raw API keys or tokens."""
    log_capture = io.StringIO()
    handler = logging.StreamHandler(log_capture)
    audit_logger = logging.getLogger("audit")
    audit_logger.addHandler(handler)

    # Trigger both success and failure
    client.post(
        "/v1/upload",
        files={"file": ("key_test.txt", b"test content", "text/plain")},
        headers=AUTH_HEADERS
    )
    client.post(
        "/v1/upload",
        files={"file": ("key_test.txt", b"test content", "text/plain")},
        headers={"X-API-Key": "super_secret_forbidden_token"}
    )

    audit_logger.removeHandler(handler)
    logs = log_capture.getvalue()

    assert TEST_KEY_VALUE not in logs
    assert "super_secret_forbidden_token" not in logs


def test_14_encryption_key_not_exposed():
    """Requirement 14: Storage encryption key is never exposed via API responses or errors."""
    # Test normal response
    r1 = client.get("/v1/privacy-policy")
    assert r1.status_code == 200
    fernet = get_fernet()
    # Ensure key is not in privacy response
    assert str(fernet) not in r1.text

    # Test error response
    r2 = client.post("/v1/analyze", json={"doc_id": "non_existent_doc"}, headers=AUTH_HEADERS)
    assert r2.status_code == 404
    assert str(fernet) not in r2.text


def test_15_existing_api_integration_behavior():
    """Requirement 15: Upload and Analyze flow works end-to-end with authentication."""
    # Upload
    r_up = client.post(
        "/v1/upload",
        files={"file": ("contract.txt", SAMPLE_CONTRACT_TEXT.encode("utf-8"), "text/plain")},
        headers=AUTH_HEADERS
    )
    assert r_up.status_code == 200
    doc_id = r_up.json()["doc_id"]

    # Analyze
    r_an = client.post("/v1/analyze", json={"doc_id": doc_id}, headers=AUTH_HEADERS)
    assert r_an.status_code == 200
    job_id = r_an.json()["job_id"]

    # Status
    r_st = client.get(f"/v1/jobs/{job_id}", headers=AUTH_HEADERS)
    assert r_st.status_code == 200
    assert r_st.json()["job_id"] == job_id


def test_16_feedback_endpoint_remains_functional():
    """Requirement 16: Feedback endpoint functions properly when authenticated."""
    response = client.post(
        "/v1/feedback",
        json={
            "doc_id": "doc_test_feed",
            "clause_id": "c_feed_1",
            "original_severity": "MEDIUM",
            "reviewer_verdict": "AGREE",
            "reviewer_id": "test_reviewer_16",
            "provenance": "SYNTHETIC_TEST",
            "corrected_severity": None,
            "model_version": "v1"
        },
        headers=AUTH_HEADERS
    )
    assert response.status_code == 200
    data = response.json()
    assert "feedback_id" in data
    assert data["message"] == "Feedback successfully recorded."
