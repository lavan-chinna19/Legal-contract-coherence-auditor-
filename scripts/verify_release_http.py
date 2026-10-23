"""Live HTTP acceptance against a running loopback API; synthetic fixtures only."""
import argparse
import json
import time
from pathlib import Path
import httpx

parser = argparse.ArgumentParser()
parser.add_argument("--url", default="http://127.0.0.1:8010")
args = parser.parse_args()
root = Path(__file__).resolve().parents[1] / "tmp" / "final-release"
root.mkdir(parents=True, exist_ok=True)
checks = []
client = httpx.Client(base_url=args.url, headers={"X-API-Key": "dev_auditor_key_12345"}, timeout=180)


def checked(name, method, route, **kwargs):
    started = time.perf_counter()
    response = client.request(method, route, **kwargs)
    checks.append({"name": name, "status": response.status_code, "seconds": round(time.perf_counter() - started, 3)})
    response.raise_for_status()
    print(name, response.status_code, flush=True)
    return response


for suffix in ["txt", "pdf", "docx"]:
    path = root / f"synthetic-contract.{suffix}"
    uploaded = checked(f"{suffix} upload", "POST", "/v1/upload", files={"file": (path.name, path.read_bytes())}).json()
    doc_id = uploaded["doc_id"]
    parsed = checked(f"{suffix} clause preview", "GET", f"/v1/documents/{doc_id}/clauses").json()
    assert parsed["clauses"] and parsed["doc_id"] == doc_id
    job_id = checked(f"{suffix} analyze", "POST", "/v1/analyze", json={"doc_id": doc_id}).json()["job_id"]
    for attempt in range(180):
        state = client.get(f"/v1/jobs/{job_id}").json()
        if state["status"] == "COMPLETED":
            break
        if state["status"] == "FAILED":
            raise RuntimeError(state["error"])
        time.sleep(1)
    else:
        raise RuntimeError("Bounded analysis polling timed out")
    result = checked(f"{suffix} results", "GET", f"/v1/jobs/{job_id}/results").json()
    assert result["total_clauses"] >= 4
    assert parsed["clauses"] == result["metadata"]["clause_inventory"]
    for clause in result["metadata"]["clause_inventory"]:
        assert result["metadata"]["source_text"][clause["char_start"]:clause["char_end"]] == clause["text"]
    target = result["scoring_result"]["clauses"][0]["clause_id"]
    graph = checked(f"{suffix} graph", "POST", "/v1/experimental/dependencies", json={"job_id": job_id, "experimental": True}).json()
    assert graph["findings"]
    for format in ["pdf", "docx"]:
        response = checked(f"{suffix} export {format}", "GET", f"/v1/jobs/{job_id}/report/{format}")
        assert len(response.content) > 1000
        (root / f"{suffix}-analysis-report.{format}").write_bytes(response.content)
    if suffix == "txt":
        params = {"doc_id": doc_id, "clause_id": target}
        attribution = checked("attribution", "GET", "/v1/xai/attribution", params=params).json()
        assert attribution["clause_id"] == target and attribution["ig_payload"]["tokens"]
        sensitivity = checked("sensitivity", "GET", "/v1/xai/sensitivity", params=params).json()
        assert sensitivity["clause_id"] == target
        repair = checked("counterfactual", "POST", "/v1/experimental/reposition",
                         json={**params, "experimental": True}).json()
        assert "is_abstaining" in repair and repair["target_clause_id"] == target
        robust = checked("robustness negative control", "POST", "/v1/experimental/redteam",
                         json={"doc_id": doc_id, "perturbation_type": "P9_NEGATIVE_CONTROL", "experimental": True}).json()
        assert robust["original_checksum"] == robust["perturbed_checksum"]
        other = client.get(f"/v1/jobs/{job_id}/report/pdf", headers={"X-API-Key": "client_b_key_67890"})
        assert other.status_code == 404
        checks.append({"name": "other-client export denied", "status": other.status_code})
        (root / "live-analysis.json").write_text(json.dumps({"job_id": job_id, "doc_id": doc_id, "target": target}), encoding="utf-8")
        result = checked("saved analysis with experiments", "GET", f"/v1/jobs/{job_id}/results").json()
        assert result["metadata"]["counterfactual"]["target_clause_id"] == target

checked("saved documents", "GET", "/v1/documents")
(root / "http-acceptance.json").write_text(json.dumps({"status": "PASS", "checks": checks}, indent=2), encoding="utf-8")
print(f"PASS: {len(checks)} live HTTP checks")
