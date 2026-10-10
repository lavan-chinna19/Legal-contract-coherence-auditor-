"""
smoke_test_compose.py — Deterministic Local Stack Smoke Test (Prompt 18).

Usage:
    python smoke_test_compose.py [--backend-url URL] [--frontend-url URL] [--api-key KEY]
"""
import os
import sys
import time
import argparse
import requests
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
DEFAULT_BACKEND = os.environ.get("BACKEND_URL", "http://localhost:8000")
DEFAULT_FRONTEND = os.environ.get("FRONTEND_URL", "http://localhost:3000")
DEFAULT_API_KEY = os.environ.get("API_KEY", "dev_auditor_key_12345")


def wait_for_service(url: str, name: str, timeout_sec: int = 45) -> bool:
    print(f"[*] Waiting for {name} at {url}...")
    start = time.time()
    while time.time() - start < timeout_sec:
        try:
            res = requests.get(url, timeout=3)
            if res.status_code == 200:
                print(f"[OK] {name} is healthy! (status 200)")
                return True
        except Exception:
            pass
        time.sleep(2)
    print(f"[!] Warning: {name} did not respond within {timeout_sec}s.")
    return False


def run_smoke_test(backend_url: str, frontend_url: str, api_key: str) -> int:
    print("==================================================")
    print("LEGAL CONTRACT COHERENCE AUDITOR — SMOKE TEST")
    print("==================================================")
    print(f"Backend URL:  {backend_url}")
    print(f"Frontend URL: {frontend_url}")

    # 1. Check Backend Health
    backend_ok = wait_for_service(f"{backend_url}/health", "Backend API")
    if not backend_ok:
        print("[!] Backend is not reachable. Ensure service is started.")
        return 1

    # Optional check Frontend Health
    wait_for_service(frontend_url, "Frontend Service", timeout_sec=10)

    # 2. Upload Contract
    headers = {"X-API-Key": api_key}
    sample_dir = ROOT_DIR / "data" / "raw" / "sec_edgar"
    sample_files = list(sample_dir.glob("*.txt"))
    if not sample_files:
        print("[!] No sample contracts found in data/raw/sec_edgar")
        return 1

    test_file = sample_files[0]
    print(f"[*] Uploading contract: {test_file.name}...")
    with open(test_file, "rb") as f:
        res = requests.post(
            f"{backend_url}/v1/upload",
            files={"file": (test_file.name, f, "text/plain")},
            headers=headers,
            timeout=15
        )

    if res.status_code != 200:
        print(f"[!] Upload failed (HTTP {res.status_code}): {res.text}")
        return 1

    doc_id = res.json()["doc_id"]
    print(f"[OK] Uploaded successfully. Encrypted Doc ID: {doc_id}")

    # 3. Trigger Analysis
    print(f"[*] Dispatching analysis job for {doc_id}...")
    res = requests.post(
        f"{backend_url}/v1/analyze",
        json={"doc_id": doc_id},
        headers=headers,
        timeout=15
    )
    if res.status_code != 200:
        print(f"[!] Analyze trigger failed (HTTP {res.status_code}): {res.text}")
        return 1

    job_id = res.json()["job_id"]
    print(f"[OK] Job accepted: {job_id}")

    # 4. Poll Job
    print("[*] Polling job execution...")
    start_poll = time.time()
    status = "QUEUED"
    while time.time() - start_poll < 90:
        res = requests.get(f"{backend_url}/v1/jobs/{job_id}", headers=headers, timeout=5)
        if res.status_code == 200:
            status = res.json()["status"]
            if status == "COMPLETED":
                break
            elif status == "FAILED":
                print(f"[!] Job failed: {res.json().get('error')}")
                return 1
        time.sleep(2)

    if status != "COMPLETED":
        print(f"[!] Job timed out. Final status: {status}")
        return 1

    print(f"[OK] Analysis completed in {time.time() - start_poll:.2f}s")

    # 5. Fetch Results
    res = requests.get(f"{backend_url}/v1/jobs/{job_id}/results", headers=headers, timeout=10)
    if res.status_code != 200:
        print(f"[!] Failed to fetch results: {res.text}")
        return 1

    result_data = res.json()
    print(f"[OK] Audit Report Verified:")
    print(f"     Total Clauses:   {result_data['total_clauses']}")
    print(f"     Anomalies Found: {result_data['anomaly_count']}")
    print(f"     Mean Score:      {result_data['mean_combined_score']:.4f}")
    print(f"     Calibration:     {result_data['calibration_source']}")

    # 6. Submit Feedback
    target_clause = result_data["clauses"][0]
    feedback_payload = {
        "doc_id": doc_id,
        "clause_id": target_clause["clause_id"],
        "original_severity": target_clause["severity"],
        "reviewer_verdict": "CONFIRM_ANOMALY" if target_clause["severity"] in ("HIGH", "MEDIUM") else "REJECT_ANOMALY",
        "reviewer_id": "smoke_tester",
        "provenance": "SYNTHETIC_TEST",
        "corrected_severity": "HIGH",
        "model_version": "v1"
    }
    res = requests.post(f"{backend_url}/v1/feedback", json=feedback_payload, headers=headers, timeout=10)
    if res.status_code != 200:
        print(f"[!] Feedback submission failed: {res.text}")
        return 1

    print(f"[OK] Feedback stored: {res.json()['feedback_id']}")
    print("\n==================================================")
    print("ALL SMOKE TEST CHECKS PASSED SUCCESSFULLY!")
    print("==================================================")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run local stack smoke test")
    parser.add_argument("--backend-url", default=DEFAULT_BACKEND)
    parser.add_argument("--frontend-url", default=DEFAULT_FRONTEND)
    parser.add_argument("--api-key", default=DEFAULT_API_KEY)
    args = parser.parse_args()

    sys.exit(run_smoke_test(args.backend_url, args.frontend_url, args.api_key))
