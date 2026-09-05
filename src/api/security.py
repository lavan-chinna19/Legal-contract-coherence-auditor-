"""
src/api/security.py — Authentication & Security Dependencies (Prompt 16 Work Package A)

Provides API-key authentication for protected endpoints:
- Supports X-API-Key header and Authorization: Bearer <token>
- Credentials sourced exclusively from environment / configuration
- Never leaks secrets in error messages or logs
- Transforms authenticated secrets into non-reversible client IDs for audit tracking
"""
import os
import hashlib
import secrets
from typing import Set, Optional
from fastapi import Request, HTTPException, Security, Header
from fastapi.security import APIKeyHeader

from src.api.audit import log_audit_event

API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)


def get_safe_client_id(raw_key: str) -> str:
    """Generates a non-reversible safe identifier for an API key."""
    digest = hashlib.sha256(raw_key.strip().encode("utf-8")).hexdigest()[:12]
    return f"key_{digest}"


def get_configured_api_keys() -> Set[str]:
    """
    Retrieves authorized API keys from environment configuration.
    Accepts comma-separated values in API_KEYS or a single API_KEY.
    """
    keys = set()
    raw_keys = os.environ.get("API_KEYS", "")
    if raw_keys:
        for k in raw_keys.split(","):
            k_clean = k.strip()
            if k_clean:
                keys.add(k_clean)
                
    single_key = os.environ.get("API_KEY", "").strip()
    if single_key:
        keys.add(single_key)
        
    return keys


async def verify_api_key(
    request: Request,
    api_key_header: Optional[str] = Security(API_KEY_HEADER),
    authorization: Optional[str] = Header(None)
) -> str:
    """
    Validates API key from X-API-Key header or Authorization: Bearer.
    Returns the non-reversible safe client identifier on success.
    Raises HTTP 401 on missing or invalid credentials.
    """
    token: Optional[str] = None
    
    if api_key_header:
        token = api_key_header.strip()
    elif authorization:
        parts = authorization.strip().split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            token = parts[1].strip()
            
    if not token:
        log_audit_event(
            event_type="AUTH_FAILURE",
            action=f"{request.method} {request.url.path}",
            client_id="anonymous",
            status="DENIED",
            http_status=401,
            details={"reason": "missing_credentials"}
        )
        raise HTTPException(
            status_code=401,
            detail="Authentication credentials were not provided."
        )

    valid_keys = get_configured_api_keys()
    if not valid_keys:
        # No keys configured on server -> reject
        log_audit_event(
            event_type="AUTH_FAILURE",
            action=f"{request.method} {request.url.path}",
            client_id="anonymous",
            status="DENIED",
            http_status=401,
            details={"reason": "no_server_keys_configured"}
        )
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials."
        )

    # Constant-time comparison against configured keys
    is_valid = any(secrets.compare_digest(token, valid_key) for valid_key in valid_keys)
    if not is_valid:
        log_audit_event(
            event_type="AUTH_FAILURE",
            action=f"{request.method} {request.url.path}",
            client_id="anonymous",
            status="DENIED",
            http_status=401,
            details={"reason": "invalid_credentials"}
        )
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials."
        )

    client_id = get_safe_client_id(token)
    return client_id
