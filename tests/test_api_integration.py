"""
tests/test_api_integration.py — Local API Integration Test (Prompt 15)
"""
import time
import pytest
from fastapi.testclient import TestClient

from src.api.main import app
from src.config import EDGAR_RAW_DIR
from src.api.dependencies import get_ml_segmenter, get_dual_channel_scorer

client = TestClient(app)

def test_health_and_readiness():
    """GATE 1: API starts locally and /health succeeds."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json()["status"] == "ready"


def test_end_to_end_analysis_flow():
    """
    GATE 2 & 3: End-to-end integration and programmatic comparison.
    Uploads a real document, polls job, and compares API result to direct invocation.
    """
    # Find a real document
    txt_files = list(EDGAR_RAW_DIR.glob("*.txt"))
    if not txt_files:
        pytest.skip("No EDGAR sample documents found.")
        
    test_file_path = txt_files[0]
    
    # 1. Upload
    with open(test_file_path, "rb") as f:
        # FastAPI's UploadFile via TestClient needs a file-like object or bytes
        response = client.post(
            "/v1/upload",
            files={"file": (test_file_path.name, f, "text/plain")}
        )
    assert response.status_code == 200, f"Upload failed: {response.text}"
    upload_data = response.json()
    doc_id = upload_data["doc_id"]
    
    # 2. Analyze
    response = client.post("/v1/analyze", json={"doc_id": doc_id})
    assert response.status_code == 200, f"Analyze failed: {response.text}"
    analyze_data = response.json()
    job_id = analyze_data["job_id"]
    
    # 3. Poll Status
    max_retries = 120
    delay = 1.0
    for _ in range(max_retries):
        response = client.get(f"/v1/jobs/{job_id}")
        assert response.status_code == 200
        status_data = response.json()
        if status_data["status"] == "COMPLETED":
            break
        elif status_data["status"] == "FAILED":
            pytest.fail(f"Job failed: {status_data.get('error')}")
        time.sleep(delay)
    else:
        pytest.fail("Job timed out.")
        
    # 4. Get Results
    response = client.get(f"/v1/jobs/{job_id}/results")
    assert response.status_code == 200, f"Results fetch failed: {response.text}"
    api_result = response.json()
    
    # 5. Direct Pipeline Invocation for Comparison (GATE 3)
    segmenter = get_ml_segmenter()
    scorer = get_dual_channel_scorer()
    
    with open(test_file_path, "r", encoding="utf-8") as f:
        doc_text = f.read()
        
    clauses = segmenter.segment(doc_text, doc_id)
    direct_result = scorer.score_document(clauses, doc_id)
    
    # Compare
    assert api_result["doc_id"] == direct_result.doc_id
    assert api_result["total_clauses"] == direct_result.total_clauses
    assert api_result["anomaly_count"] == direct_result.anomaly_count
    assert api_result["high_severity_count"] == direct_result.high_severity_count
    assert api_result["medium_severity_count"] == direct_result.medium_severity_count
    assert abs(api_result["mean_combined_score"] - direct_result.mean_combined_score) < 1e-4
    assert abs(api_result["max_combined_score"] - direct_result.max_combined_score) < 1e-4
    
    # Check that clauses match exactly in number
    assert len(api_result["clauses"]) == len(direct_result.clauses)
    if len(api_result["clauses"]) > 0:
        api_c0 = api_result["clauses"][0]
        dir_c0 = direct_result.clauses[0]
        assert api_c0["clause_id"] == dir_c0.clause_id
        assert abs(api_c0["combined_score"] - dir_c0.combined_score) < 1e-4
        assert api_c0["severity"] == dir_c0.severity

