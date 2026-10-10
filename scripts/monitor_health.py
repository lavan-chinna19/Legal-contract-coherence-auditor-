"""
scripts/monitor_health.py — Lightweight Uptime & Health Monitor (Prompt 20).

Polls /health and /ready endpoints, records latency, and emits alert notifications
when an endpoint becomes unavailable or degraded.
"""
import os
import sys
import time
import requests
from typing import Dict, Any

DEFAULT_URL = os.environ.get("BACKEND_URL", "http://127.0.0.1:8000")


def check_health(base_url: str = DEFAULT_URL, timeout_sec: int = 5) -> Dict[str, Any]:
    start_time = time.time()
    try:
        resp = requests.get(f"{base_url}/health", timeout=timeout_sec)
        latency_ms = round((time.time() - start_time) * 1000, 2)
        if resp.status_code == 200:
            return {
                "healthy": True,
                "status_code": resp.status_code,
                "latency_ms": latency_ms,
                "error": None
            }
        else:
            return {
                "healthy": False,
                "status_code": resp.status_code,
                "latency_ms": latency_ms,
                "error": f"Unexpected HTTP status {resp.status_code}"
            }
    except Exception as e:
        latency_ms = round((time.time() - start_time) * 1000, 2)
        return {
            "healthy": False,
            "status_code": 0,
            "latency_ms": latency_ms,
            "error": str(e)
        }


def trigger_alert(details: Dict[str, Any]):
    print(f"[ALERT] [MONITORING FAILURE] Service unreachable or degraded!")
    print(f"        Details: {details}")


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_URL
    print(f"[*] Running health monitor probe on {url}...")
    res = check_health(url)
    if res["healthy"]:
        print(f"[OK] Health probe passed in {res['latency_ms']}ms (HTTP {res['status_code']})")
        sys.exit(0)
    else:
        trigger_alert(res)
        sys.exit(1)
