import pytest
from fastapi.testclient import TestClient
import os
from src.api.main import app
from src.api.storage import document_exists, save_encrypted_document
from cryptography.fernet import Fernet
import uuid

# Remove API Key logic from environment to avoid issues
os.environ.setdefault("API_KEY", "test-api-key")
os.environ["STORAGE_ENCRYPTION_KEY"] = Fernet.generate_key().decode("utf-8")

client = TestClient(app)

def test_xai_endpoints():
    doc_id = f"doc_{uuid.uuid4().hex[:8]}"
    doc_text = "This is a test document. It contains multiple clauses. We will test XAI on it."
    
    # Store document using the storage module with the owner client_id
    from src.api.security import get_safe_client_id
    owner_client_id = get_safe_client_id(os.environ["API_KEY"])
    save_encrypted_document(doc_id, doc_text, owner_client_id)
    assert document_exists(doc_id)
    
    headers = {"X-API-Key": os.environ["API_KEY"]}
    
    # Get clause dynamically
    from src.api.dependencies import get_segmenter_dep
    segmenter = get_segmenter_dep()
    clauses = segmenter.segment(doc_text, doc_id)
    clause_id = clauses[0].clause_id
    
    # Test attribution
    res = client.get(f"/v1/xai/attribution?doc_id={doc_id}&clause_id={clause_id}", headers=headers)
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["explanation_type"] == "INTEGRATED_GRADIENTS"
    assert "ig_payload" in data
    assert "tokens" in data["ig_payload"]
    assert "attributions" in data["ig_payload"]
    
    # Test sensitivity
    res = client.get(f"/v1/xai/sensitivity?doc_id={doc_id}&clause_id={clause_id}", headers=headers)
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["explanation_type"] == "SENSITIVITY"
    assert "sensitivity_payload" in data
    assert "score_delta" in data["sensitivity_payload"]
