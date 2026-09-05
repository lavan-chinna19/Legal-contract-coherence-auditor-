"""
src/api/audit.py — Security Audit Logging (Prompt 16 Work Package D)

Adheres strictly to the Global Execution Contract:
- NEVER logs contract plaintext or clause text
- NEVER logs request bodies
- NEVER logs raw filenames that could expose sensitive information
- NEVER logs API keys, tokens, or encryption keys
- Emits structured, distinct audit events tagged with [AUDIT]
"""
import logging
import json
from datetime import datetime, timezone
from typing import Optional, Dict, Any

# Dedicated audit logger
audit_logger = logging.getLogger("audit")
if not audit_logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s [AUDIT] %(message)s"))
    audit_logger.addHandler(handler)
audit_logger.setLevel(logging.INFO)
audit_logger.propagate = True


def log_audit_event(
    event_type: str,
    action: str,
    client_id: str = "anonymous",
    status: str = "SUCCESS",
    http_status: int = 200,
    resource_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Emits a structured audit record with safe metadata only.
    Returns the audit event dictionary.
    """
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": event_type,
        "action": action,
        "client_id": client_id,
        "resource_id": resource_id or "none",
        "status": status,
        "http_status": http_status,
        "details": details or {}
    }
    
    # Format as JSON string
    event_json = json.dumps(event, separators=(",", ":"))
    audit_logger.info(f"[AUDIT] {event_type} {event_json}")
    return event
