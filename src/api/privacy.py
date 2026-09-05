"""
src/api/privacy.py — Privacy & Confidentiality Policy (Prompt 16 Work Package F)

Provides policy text and metadata suitable for client applications and future frontend (Prompt 17):
- Explicit data handling guarantees
- Transparent disclosure of encryption at rest (Fernet AES-128-CBC + HMAC-SHA256)
- Explicit data retention schedule (24h default TTL)
- Zero external LLM or third-party cloud data transmission
- Forward requirement documentation for Prompt 17 UI notice
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Any

from src.api.retention import DEFAULT_RETENTION_SECONDS


class PrivacyPolicyResponse(BaseModel):
    version: str = "1.0.0"
    retention_period_seconds: float
    retention_period_hours: float
    encryption_at_rest: str
    confidentiality_guarantees: List[str]
    frontend_notice_requirement: str


PRIVACY_GUARANTEES = [
    "Contracts are encrypted at rest using authenticated symmetric encryption (Fernet AES-128-CBC + HMAC-SHA256).",
    "Plaintext contract content is NEVER written to server logs, stdout, or audit records.",
    "Plaintext contract text exists exclusively in volatile memory buffers during active ML pipeline analysis.",
    "No uploaded contract text is transmitted to external paid APIs, third-party LLMs, or unauthorized third parties.",
    "Uploaded documents and associated temporary artifacts are automatically purged upon expiration of the retention window.",
    "Security audit logs capture non-reversible identity hashes and event metadata, never contract contents or credentials."
]

FRONTEND_REQUIREMENT = (
    "Prompt 17 UI must visibly display this privacy and retention notice to users "
    "prior to accepting any contract file upload."
)


def get_privacy_policy() -> PrivacyPolicyResponse:
    """Returns structured privacy and data retention policy."""
    return PrivacyPolicyResponse(
        version="1.0.0",
        retention_period_seconds=DEFAULT_RETENTION_SECONDS,
        retention_period_hours=round(DEFAULT_RETENTION_SECONDS / 3600.0, 2),
        encryption_at_rest="Fernet (AES-128-CBC with HMAC-SHA256 authenticated encryption)",
        confidentiality_guarantees=PRIVACY_GUARANTEES,
        frontend_notice_requirement=FRONTEND_REQUIREMENT
    )
