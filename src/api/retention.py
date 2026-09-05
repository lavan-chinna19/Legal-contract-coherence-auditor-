"""
src/api/retention.py — Enforced Data Retention & Automated Cleanup (Prompt 16 Work Package E)

Enforces data retention policies for contract uploads:
- Configurable retention period via DATA_RETENTION_SECONDS (default: 86400 seconds / 24 hours)
- Deletes expired encrypted uploads and associated metadata
- Purges corresponding in-memory job records
- Preserves audit logs for security accountability
- Provides accelerated interval support for testing
"""
import os
import time
import logging
from typing import Dict, Any, Optional, Set
from datetime import datetime, timezone

from src.api.storage import UPLOAD_DIR, delete_document_files, get_document_metadata
from src.api.jobs import delete_jobs_for_doc
from src.api.audit import log_audit_event

logger = logging.getLogger("api")

# Default retention window: 24 hours in seconds
DEFAULT_RETENTION_SECONDS = float(os.environ.get("DATA_RETENTION_SECONDS", "86400.0"))


def cleanup_expired_artifacts(max_age_seconds: Optional[float] = None) -> Dict[str, Any]:
    """
    Scans the uploads storage directory and deletes any artifacts that exceed the retention period.
    Also clears associated in-memory job records.
    Audit log records are deliberately preserved.
    """
    max_age = max_age_seconds if max_age_seconds is not None else DEFAULT_RETENTION_SECONDS
    now = time.time()
    
    deleted_docs: Set[str] = set()
    retained_docs: Set[str] = set()
    jobs_purged = 0

    if not UPLOAD_DIR.exists():
        return {
            "deleted_documents_count": 0,
            "retained_documents_count": 0,
            "jobs_purged_count": 0,
            "max_age_seconds": max_age
        }

    # Discover all document IDs present in UPLOAD_DIR
    all_doc_ids: Set[str] = set()
    for item in UPLOAD_DIR.iterdir():
        if item.is_file() and item.name.startswith("doc_"):
            # Extract doc_id (prefix before first dot or standard doc_{hex})
            doc_id = item.name.split(".")[0]
            all_doc_ids.add(doc_id)

    for doc_id in all_doc_ids:
        meta = get_document_metadata(doc_id)
        file_time: float
        if meta and "created_timestamp" in meta:
            file_time = float(meta["created_timestamp"])
        else:
            # Fall back to file modification time
            enc_file = UPLOAD_DIR / f"{doc_id}.enc"
            txt_file = UPLOAD_DIR / f"{doc_id}.txt"
            target = enc_file if enc_file.exists() else txt_file
            file_time = target.stat().st_mtime if target.exists() else now

        age = now - file_time
        if age >= max_age:
            delete_document_files(doc_id)
            purged = delete_jobs_for_doc(doc_id)
            jobs_purged += purged
            deleted_docs.add(doc_id)
        else:
            retained_docs.add(doc_id)

    result = {
        "deleted_documents_count": len(deleted_docs),
        "retained_documents_count": len(retained_docs),
        "jobs_purged_count": jobs_purged,
        "max_age_seconds": max_age,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    log_audit_event(
        event_type="RETENTION_CLEANUP",
        action="SYSTEM_RETENTION_CLEANUP",
        client_id="system",
        status="SUCCESS",
        http_status=200,
        details={
            "deleted_count": len(deleted_docs),
            "retained_count": len(retained_docs),
            "max_age_seconds": max_age
        }
    )

    logger.info(
        f"Retention cleanup complete: {len(deleted_docs)} documents deleted, "
        f"{len(retained_docs)} documents retained, {jobs_purged} jobs purged."
    )
    return result
