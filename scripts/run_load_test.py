"""
scripts/run_load_test.py — Realistic Multi-Tier Contract Load Test (Prompt 20).

Executes realistic workloads against the FastAPI backend across three document sizes:
- Small (Short NDA snippet, ~3 clauses)
- Medium (Standard commercial agreement, ~15 clauses)
- Large (Full multi-clause SEC EDGAR filing, ~26+ clauses)

Records real measured latency, throughput, and HTTP status distribution.
"""
import os
import sys
import time
import json
import statistics
from pathlib import Path
from typing import Dict, Any, List

from fastapi.testclient import TestClient

# Configure authentication
TEST_KEY = os.environ.get("API_KEY", "load_test_key_secret_123")
os.environ["API_KEY"] = TEST_KEY
AUTH_HEADERS = {"X-API-Key": TEST_KEY}

from src.api.main import app
from src.config import EDGAR_RAW_DIR, REPO_ROOT

client = TestClient(app)

OUTPUT_FILE = REPO_ROOT / "fixtures" / "load_test_results.json"


def prepare_documents() -> Dict[str, str]:
    """Prepares small, medium, and large document payloads."""
    # Find real EDGAR contract
    candidates = list(EDGAR_RAW_DIR.glob("*.txt"))
    if candidates:
        with open(candidates[0], "r", encoding="utf-8") as f:
            full_text = f.read()
    else:
        full_text = (
            "SECTION 1: Definitions and Interpretation.\n"
            "SECTION 2: Term and Termination.\n"
            "SECTION 3: Confidentiality Obligations.\n"
            "SECTION 4: Governing Law and Jurisdiction.\n"
        ) * 10

    lines = [line.strip() for line in full_text.split("\n") if line.strip()]
    
    small_doc = "\n\n".join(lines[:6]) if len(lines) >= 6 else full_text[:400]
    med_doc = "\n\n".join(lines[:20]) if len(lines) >= 20 else full_text[:1500]
    large_doc = full_text

    return {
        "SMALL_NDA": small_doc,
        "MEDIUM_AGREEMENT": med_doc,
        "LARGE_EDGAR_CONTRACT": large_doc
    }


def execute_pipeline_cycle(doc_name: str, doc_text: str) -> Dict[str, Any]:
    t0 = time.time()
    
    # 1. Upload
    up_res = client.post(
        "/v1/upload",
        files={"file": (f"{doc_name}.txt", doc_text.encode("utf-8"), "text/plain")},
        headers=AUTH_HEADERS
    )
    if up_res.status_code != 200:
        return {"status": "FAILED", "stage": "upload", "status_code": up_res.status_code}
    doc_id = up_res.json()["doc_id"]
    t_upload = time.time() - t0

    # 2. Analyze
    t1 = time.time()
    an_res = client.post("/v1/analyze", json={"doc_id": doc_id}, headers=AUTH_HEADERS)
    if an_res.status_code != 200:
        return {"status": "FAILED", "stage": "analyze", "status_code": an_res.status_code}
    job_id = an_res.json()["job_id"]

    # 3. Poll
    poll_start = time.time()
    completed = False
    while time.time() - poll_start < 60:
        st_res = client.get(f"/v1/jobs/{job_id}", headers=AUTH_HEADERS)
        if st_res.status_code == 200 and st_res.json()["status"] == "COMPLETED":
            completed = True
            break
        time.sleep(0.5)

    if not completed:
        return {"status": "TIMEOUT", "stage": "polling"}
    t_pipeline = time.time() - t1

    # 4. Results
    res_res = client.get(f"/v1/jobs/{job_id}/results", headers=AUTH_HEADERS)
    total_latency = time.time() - t0
    
    result_data = res_res.json() if res_res.status_code == 200 else {}
    return {
        "status": "SUCCESS",
        "doc_name": doc_name,
        "bytes": len(doc_text),
        "total_clauses": result_data.get("total_clauses", 0),
        "anomaly_count": result_data.get("anomaly_count", 0),
        "upload_sec": round(t_upload, 3),
        "pipeline_sec": round(t_pipeline, 3),
        "total_latency_sec": round(total_latency, 3)
    }


def run_load_test(iterations_per_tier: int = 3) -> Dict[str, Any]:
    print("==================================================")
    print("STARTING REALISTIC CONTRACT LOAD TEST (PROMPT 20)")
    print("==================================================")
    docs = prepare_documents()
    
    all_runs: List[Dict[str, Any]] = []
    overall_start = time.time()

    for tier, text in docs.items():
        print(f"\n[*] Benchmarking Tier: {tier} ({len(text):,} bytes)...")
        for i in range(iterations_per_tier):
            run_res = execute_pipeline_cycle(f"{tier}_{i+1}", text)
            all_runs.append(run_res)
            print(f"    Run {i+1}/{iterations_per_tier}: {run_res['status']} in {run_res.get('total_latency_sec', 0)}s "
                  f"({run_res.get('total_clauses', 0)} clauses, {run_res.get('anomaly_count', 0)} anomalies)")

    overall_duration = time.time() - overall_start
    successful = [r for r in all_runs if r["status"] == "SUCCESS"]
    latencies = [r["total_latency_sec"] for r in successful]

    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "total_requests": len(all_runs),
        "successful_requests": len(successful),
        "failed_requests": len(all_runs) - len(successful),
        "total_duration_sec": round(overall_duration, 2),
        "mean_latency_sec": round(statistics.mean(latencies), 3) if latencies else 0.0,
        "p50_latency_sec": round(statistics.median(latencies), 3) if latencies else 0.0,
        "max_latency_sec": round(max(latencies), 3) if latencies else 0.0,
        "min_latency_sec": round(min(latencies), 3) if latencies else 0.0,
        "throughput_req_per_min": round((len(successful) / overall_duration) * 60, 2) if overall_duration > 0 else 0.0,
        "runs": all_runs
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print("\n==================================================")
    print("LOAD TEST SUMMARY RESULTS:")
    print(f"  Total Requests:     {report['total_requests']}")
    print(f"  Success Rate:       {len(successful)}/{len(all_runs)} (100%)" if len(successful) == len(all_runs) else f"  Success Rate: {len(successful)}/{len(all_runs)}")
    print(f"  Mean Latency:       {report['mean_latency_sec']}s")
    print(f"  Median (P50):       {report['p50_latency_sec']}s")
    print(f"  Min / Max Latency:  {report['min_latency_sec']}s / {report['max_latency_sec']}s")
    print(f"  Throughput:         {report['throughput_req_per_min']} req/min")
    print(f"  Results saved to:   {OUTPUT_FILE}")
    print("==================================================")
    return report


if __name__ == "__main__":
    run_load_test()
