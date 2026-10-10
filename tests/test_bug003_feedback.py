import pytest
import os
os.environ["API_KEY"] = "dev_auditor_key_12345"

from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_feedback_vocabulary_validation():
    test_key = os.environ.get("API_KEY", "dev_auditor_key_12345")
    headers = {"X-API-Key": test_key}
    
    # Valid verdict
    valid_payload = {
        "doc_id": "test_doc_1",
        "clause_id": "clause_1",
        "original_severity": "HIGH",
        "reviewer_verdict": "CONFIRM_ANOMALY",
        "reviewer_id": "rev1",
        "provenance": "REAL"
    }
    resp = client.post("/v1/feedback", json=valid_payload, headers=headers)
    assert resp.status_code == 200
    
    # Invalid verdict
    invalid_payload = dict(valid_payload)
    invalid_payload["reviewer_verdict"] = "OVERKILL"
    resp = client.post("/v1/feedback", json=invalid_payload, headers=headers)
    assert resp.status_code == 422
    assert "Invalid reviewer_verdict" in resp.text
