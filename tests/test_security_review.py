"""
tests/test_security_review.py — Production Security Review Test Suite (Prompt 20).

Validates the security checklist items with real tests:
1. Server-side upload validation (file type, empty files, binary corruption rejection)
2. SSRF vulnerability review (no unvalidated outbound URL calls)
3. Path-traversal attack resistance on doc_id and upload endpoints
4. Error payload hygiene (no raw encryption keys or passwords returned)
"""
import os
import io
import uuid
import pytest
from pathlib import Path
from fastapi.testclient import TestClient

TEST_KEY = os.environ.get("API_KEY") or f"test_key_{uuid.uuid4().hex[:8]}"
os.environ["API_KEY"] = TEST_KEY
AUTH_HEADERS = {"X-API-Key": TEST_KEY}

from src.api.main import app
from src.api.storage import UPLOAD_DIR, load_and_decrypt_document, document_exists

client = TestClient(app)


def test_upload_validation_rejects_empty_file():
    """Security Checklist 1A: Empty file upload must return HTTP 400."""
    res = client.post(
        "/v1/upload",
        files={"file": ("empty.txt", b"", "text/plain")},
        headers=AUTH_HEADERS
    )
    assert res.status_code == 400
    assert "empty" in res.text.lower()


def test_upload_validation_rejects_corrupted_binary():
    """Security Checklist 1B: Non-UTF8 binary upload must return HTTP 400."""
    corrupted_bytes = b"\xff\xfe\x00\x00\xff\xff\x80\xbf"
    res = client.post(
        "/v1/upload",
        files={"file": ("corrupted.bin", corrupted_bytes, "application/octet-stream")},
        headers=AUTH_HEADERS
    )
    assert res.status_code == 400
    assert "utf-8" in res.text.lower()


def test_path_traversal_on_analyze():
    """Security Checklist 2A: Path traversal attempt on analyze endpoint must be rejected."""
    traversal_doc_ids = [
        "../../etc/passwd",
        "..\\..\\windows\\win.ini",
        "....//....//etc/shadow",
        "/etc/passwd",
        "C:\\Windows\\System32\\drivers\\etc\\hosts"
    ]
    for bad_id in traversal_doc_ids:
        res = client.post(
            "/v1/analyze",
            json={"doc_id": bad_id},
            headers=AUTH_HEADERS
        )
        assert res.status_code in (400, 404), f"Path traversal not blocked for {bad_id}"


def test_path_traversal_direct_storage():
    """Security Checklist 2B: Direct storage helper must not access paths outside UPLOAD_DIR."""
    bad_id = "../../etc/passwd"
    assert not document_exists(bad_id), "document_exists should return False for traversal ID"
    with pytest.raises(Exception):
        load_and_decrypt_document(bad_id)


def test_ssrf_codebase_audit():
    """Security Checklist 3: Verify no arbitrary user-supplied URL fetching in API routers."""
    import src.api.v1.router as router_mod
    import inspect
    
    # Inspect router source
    source = inspect.getsource(router_mod)
    # Check that requests/urllib/httpx are not used with request parameters for outbound calls
    assert "requests.get(request." not in source
    assert "urllib.request" not in source
    assert "httpx.get(request." not in source


def test_error_payload_hygiene():
    """Security Checklist 4: Error responses must not echo server secrets."""
    res = client.get("/v1/jobs/nonexistent_job_12345", headers=AUTH_HEADERS)
    assert res.status_code == 404
    error_text = res.text
    
    # Secrets check
    assert TEST_KEY not in error_text
    assert "fernet" not in error_text.lower()
    assert "password" not in error_text.lower()
