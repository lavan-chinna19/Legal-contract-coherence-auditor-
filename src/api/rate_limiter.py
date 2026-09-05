"""
src/api/rate_limiter.py — In-Process Rate Limiter (Prompt 16 Work Package B)

Implements thread-safe, sliding-window per-client rate limiting:
- No Redis / external infrastructure required
- Configurable requests limit and time window
- Returns HTTP 429 with standard Retry-After and X-RateLimit-* headers
- Emits audit log events on rate limit violations
- Safe identity tracking (never logs secrets)
"""
import os
import time
import math
import threading
from collections import defaultdict, deque
from typing import Dict, Deque, Optional
from fastapi import Request, HTTPException, Depends

from src.api.security import verify_api_key
from src.api.audit import log_audit_event

DEFAULT_RATE_LIMIT_REQUESTS = int(os.environ.get("RATE_LIMIT_REQUESTS", "10"))
DEFAULT_RATE_LIMIT_WINDOW_SECONDS = float(os.environ.get("RATE_LIMIT_WINDOW_SECONDS", "60.0"))


class SlidingWindowRateLimiter:
    """Thread-safe sliding-window rate limiter keyed by client identity."""
    
    def __init__(self, default_limit: int = DEFAULT_RATE_LIMIT_REQUESTS, default_window: float = DEFAULT_RATE_LIMIT_WINDOW_SECONDS):
        self.default_limit = default_limit
        self.default_window = default_window
        self._records: Dict[str, Deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def check(
        self,
        client_id: str,
        endpoint_action: str = "REQUEST",
        limit: Optional[int] = None,
        window: Optional[float] = None
    ) -> Dict[str, str]:
        max_req = limit or self.default_limit
        win_sec = window or self.default_window
        now = time.time()
        cutoff = now - win_sec

        with self._lock:
            timestamps = self._records[client_id]
            # Prune expired timestamps
            while timestamps and timestamps[0] <= cutoff:
                timestamps.popleft()

            if len(timestamps) >= max_req:
                oldest = timestamps[0]
                retry_after = max(1, math.ceil(oldest + win_sec - now))
                headers = {
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(max_req),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(retry_after),
                }
                log_audit_event(
                    event_type="RATE_LIMIT_EXCEEDED",
                    action=endpoint_action,
                    client_id=client_id,
                    status="RATE_LIMITED",
                    http_status=429,
                    details={"limit": max_req, "window_seconds": win_sec, "retry_after": retry_after}
                )
                raise HTTPException(
                    status_code=429,
                    detail="Rate limit exceeded. Please retry later.",
                    headers=headers
                )

            timestamps.append(now)
            remaining = max_req - len(timestamps)
            reset_in = max(1, math.ceil(timestamps[0] + win_sec - now))
            return {
                "X-RateLimit-Limit": str(max_req),
                "X-RateLimit-Remaining": str(remaining),
                "X-RateLimit-Reset": str(reset_in),
            }

    def reset(self):
        """Clears all rate limiting buckets (useful for tests)."""
        with self._lock:
            self._records.clear()


# Global in-process rate limiter instance
rate_limiter = SlidingWindowRateLimiter()


def rate_limit_upload_and_analyze(
    request: Request,
    client_id: str = Depends(verify_api_key)
) -> str:
    """FastAPI dependency enforcing rate limits on upload/analyze endpoints."""
    # Check rate limit using current configured limits
    rate_limiter.check(
        client_id=client_id,
        endpoint_action=f"{request.method} {request.url.path}"
    )
    return client_id
