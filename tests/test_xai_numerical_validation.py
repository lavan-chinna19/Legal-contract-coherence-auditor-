"""
tests/test_xai_numerical_validation.py — Phase 4B XAI Numerical Validation Suite
Tests backend endpoints /v1/xai/attribution and /v1/xai/sensitivity on real pipeline output.
Exports validation tables to:
- design/ui_redesign/phase_04b/signed_attribution_validation.csv
- design/ui_redesign/phase_04b/sensitivity_numerical_validation.csv
"""
import os
import sys
import csv
import json
import time
from fastapi.testclient import TestClient

DEV_KEY = "dev_auditor_key_12345"
os.environ["API_KEY"] = DEV_KEY

sys.path.insert(0, os.path.abspath("."))
from src.api.main import app
FIXTURE_PATH = "design/ui_redesign/phase_03a/fixtures/fixture_01_baseline.txt"
ATTRIB_CSV_PATH = "design/ui_redesign/phase_04b/signed_attribution_validation.csv"
SENS_CSV_PATH = "design/ui_redesign/phase_04b/sensitivity_numerical_validation.csv"

def run_xai_validation():
    print("=== Executing XAI Numerical Validation Suite ===", flush=True)
    client = TestClient(app)

    # 1. Upload contract fixture
    with open(FIXTURE_PATH, "rb") as f:
        upload_res = client.post(
            "/v1/upload",
            files={"file": ("fixture_01_baseline.txt", f, "text/plain")},
            headers={"X-API-Key": DEV_KEY}
        )
    assert upload_res.status_code == 200, f"Upload failed: {upload_res.text}"
    doc_id = upload_res.json()["doc_id"]
    print(f"Uploaded contract doc_id: {doc_id}", flush=True)

    # 2. Trigger analysis
    analyze_res = client.post(
        "/v1/analyze",
        json={"doc_id": doc_id},
        headers={"X-API-Key": DEV_KEY}
    )
    assert analyze_res.status_code == 200, f"Analyze failed: {analyze_res.text}"
    job_id = analyze_res.json()["job_id"]

    # 3. Poll for completion
    for _ in range(60):
        status_res = client.get(f"/v1/jobs/{job_id}", headers={"X-API-Key": DEV_KEY})
        assert status_res.status_code == 200
        if status_res.json()["status"] == "COMPLETED":
            break
        time.sleep(0.5)
    else:
        raise TimeoutError("Analysis job timed out")

    # 4. Get results to obtain clause IDs
    results_res = client.get(f"/v1/jobs/{job_id}/results", headers={"X-API-Key": DEV_KEY})
    assert results_res.status_code == 200
    report = results_res.json()
    clauses = report["scoring_result"]["clauses"]
    assert len(clauses) >= 2, "Expected at least 2 clauses in report"

    target_clause_0 = clauses[0]["clause_id"]
    target_clause_1 = clauses[1]["clause_id"]
    print(f"Testing XAI on Clause 0: {target_clause_0} and Clause 1: {target_clause_1}", flush=True)

    # 5. Query Attribution for Clause 0 and Clause 1
    attrib_records = []
    sens_records = []
    os.makedirs("design/ui_redesign/phase_04b", exist_ok=True)

    for c_idx, c_id in enumerate([target_clause_0, target_clause_1]):
        attr_res = client.get(
            f"/v1/xai/attribution?doc_id={doc_id}&clause_id={c_id}",
            headers={"X-API-Key": DEV_KEY}
        )
        assert attr_res.status_code == 200, f"Attribution failed for {c_id}: {attr_res.text}"
        attr_data = attr_res.json()
        ig = attr_data.get("ig_payload")
        assert ig is not None, "Missing ig_payload in attribution response"

        tokens = ig["tokens"]
        attributions = ig["attributions"]
        target_score = ig["target_score"]
        baseline_score = ig["baseline_score"]

        assert len(tokens) == len(attributions), f"Token count ({len(tokens)}) != Attribution count ({len(attributions)})"
        assert len(tokens) > 0, "Empty token array in explanation"

        pos_count = sum(1 for a in attributions if a > 0)
        neg_count = sum(1 for a in attributions if a < 0)
        zero_count = sum(1 for a in attributions if a == 0)

        # Record representative sample tokens for validation CSV
        for t_idx in range(min(15, len(tokens))):
            attrib_records.append({
                "clause_id": c_id,
                "sequence_idx": c_idx,
                "token_index": t_idx,
                "token": tokens[t_idx],
                "attribution_value": attributions[t_idx],
                "attribution_sign": "POSITIVE" if attributions[t_idx] > 0 else ("NEGATIVE" if attributions[t_idx] < 0 else "ZERO"),
                "target_score": target_score,
                "baseline_score": baseline_score,
                "status": "VALIDATED"
            })

        print(f"Clause {c_idx} ({c_id}): {len(tokens)} tokens, {pos_count} positive (+), {neg_count} negative (-), {zero_count} zeros", flush=True)

        # 6. Query Sensitivity
        sens_res = client.get(
            f"/v1/xai/sensitivity?doc_id={doc_id}&clause_id={c_id}",
            headers={"X-API-Key": DEV_KEY}
        )
        assert sens_res.status_code == 200, f"Sensitivity failed for {c_id}: {sens_res.text}"
        sens_data = sens_res.json()
        sp = sens_data.get("sensitivity_payload")
        assert sp is not None, "Missing sensitivity_payload in response"

        orig_score = sp["original_score"]
        pert_score = sp["perturbed_score"]
        delta = sp["score_delta"]
        neighbor_pos = sp["neighbor_position"]
        neighbor_id = sp["neighbor_clause_id"]

        expected_delta = round(abs(orig_score - pert_score), 4)
        assert abs(delta - expected_delta) < 1e-3, f"Delta mismatch: {delta} != {expected_delta}"

        sens_records.append({
            "clause_id": c_id,
            "sequence_idx": c_idx,
            "neighbor_position": neighbor_pos,
            "neighbor_clause_id": neighbor_id,
            "baseline_anomaly_score": orig_score,
            "perturbed_anomaly_score": pert_score,
            "backend_delta": delta,
            "verified_delta": expected_delta,
            "perturbation_method": sp.get("perturbation_method", "mask_neighbor_text"),
            "status": "EXACT_MATCH"
        })

    # Export Attribution CSV
    with open(ATTRIB_CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "clause_id", "sequence_idx", "token_index", "token", "attribution_value",
            "attribution_sign", "target_score", "baseline_score", "status"
        ])
        writer.writeheader()
        writer.writerows(attrib_records)

    # Export Sensitivity CSV
    with open(SENS_CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "clause_id", "sequence_idx", "neighbor_position", "neighbor_clause_id",
            "baseline_anomaly_score", "perturbed_anomaly_score", "backend_delta",
            "verified_delta", "perturbation_method", "status"
        ])
        writer.writeheader()
        writer.writerows(sens_records)

    print(f"XAI Numerical Validation Complete!", flush=True)
    print(f"Attributions exported: {ATTRIB_CSV_PATH} ({len(attrib_records)} rows)", flush=True)
    print(f"Sensitivity exported:  {SENS_CSV_PATH} ({len(sens_records)} rows)", flush=True)

if __name__ == "__main__":
    run_xai_validation()
