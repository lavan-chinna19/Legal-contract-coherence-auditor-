"""
src/api/jobs.py — In-memory job queue for async contract analysis.
Allows immediate HTTP return while processing long documents.
"""
import asyncio
import uuid
import time
import threading
from typing import Dict, Optional, Any
from pydantic import BaseModel, Field

from src.scoring.pipeline import DualChannelScorer
from src.rules.unified_pipeline import UnifiedAuditor

class JobStatus:
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class Job(BaseModel):
    job_id: str
    doc_id: str
    client_id: Optional[str] = None
    status: str = JobStatus.QUEUED
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: float = Field(default_factory=time.time)


# Simple in-memory store for jobs
JOB_STORE: Dict[str, Job] = {}
JOB_TTL_SECONDS = 3600  # 1 hour TTL
ANALYSIS_LOCK = threading.Lock()
MODEL_QUEUE = threading.BoundedSemaphore(3)
MODEL_WAIT_SECONDS = 60
JOB_TIMEOUT_SECONDS = 900


def run_model_operation(function, *args, **kwargs):
    """One CPU model operation at a time; keep the HTTP event loop responsive."""
    from fastapi import HTTPException
    if not MODEL_QUEUE.acquire(blocking=False):
        raise HTTPException(429, "Another model operation is running. Retry when it finishes.")
    try:
        if not ANALYSIS_LOCK.acquire(timeout=MODEL_WAIT_SECONDS):
            raise HTTPException(429, "Model operation wait timed out. Retry when it finishes.")
        try:
            return function(*args, **kwargs)
        finally:
            ANALYSIS_LOCK.release()
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(503, "Local model operation unavailable. Verify checkpoints and dependencies, then retry.")
    finally:
        MODEL_QUEUE.release()


def _prune_jobs():
    now = time.time()
    to_delete = [
        jid for jid, j in list(JOB_STORE.items())
        if (now - j.created_at) > JOB_TTL_SECONDS and j.status in (JobStatus.COMPLETED, JobStatus.FAILED)
    ]
    for jid in to_delete:
        JOB_STORE.pop(jid, None)


def create_job(doc_id: str, client_id: Optional[str] = None) -> str:
    _prune_jobs()
    job_id = str(uuid.uuid4())
    JOB_STORE[job_id] = Job(job_id=job_id, doc_id=doc_id, client_id=client_id)
    return job_id


def get_job(job_id: str) -> Optional[Job]:
    if job_id in JOB_STORE:
        job = JOB_STORE[job_id]
        if job.status in (JobStatus.QUEUED, JobStatus.RUNNING) and time.time() - job.created_at > JOB_TIMEOUT_SECONDS:
            job.status = JobStatus.FAILED
            job.error = "Analysis exceeded the 15 minute limit. Retry; restart the API if its model worker remains busy."
            job.result = None
        return job
    from src.api.storage import UPLOAD_DIR, load_analysis_snapshot
    import json
    for path in UPLOAD_DIR.glob("doc_*.meta.json"):
        try:
            meta = json.loads(path.read_text(encoding="utf-8"))
            if meta.get("latest_job_id") == job_id:
                snapshot = load_analysis_snapshot(meta["doc_id"])
                if snapshot:
                    return JOB_STORE.setdefault(job_id, Job(**snapshot))
        except Exception:
            continue
    return None


def delete_jobs_for_doc(doc_id: str) -> int:
    """Removes in-memory jobs associated with a purged document."""
    to_delete = [jid for jid, j in JOB_STORE.items() if j.doc_id == doc_id]
    for jid in to_delete:
        del JOB_STORE[jid]
    return len(to_delete)


def run_analysis_job_sync(job_id: str, doc_id: str, document_text: str, segmenter: Any, auditor: UnifiedAuditor):
    """
    Background worker to process the contract using synchronous execution in a separate thread.
    """
    job = JOB_STORE.get(job_id)
    if not job:
        return

    if not ANALYSIS_LOCK.acquire(blocking=False):
        job.status = JobStatus.FAILED
        job.error = "Another analysis is running. Retry when it finishes."
        return
    job.status = JobStatus.RUNNING
    try:
        # Segment the document
        clauses = segmenter.segment(document_text, doc_id)
        if not clauses:
            raise ValueError("No clauses could be parsed")
        if len(clauses) > 500:
            raise ValueError("Document exceeds the 500 clause analysis limit")
        
        # Run unified scoring pipeline
        result = auditor.audit_document(clauses, doc_id)
        if job.status == JobStatus.FAILED:
            return
        
        # Store result as dict matching schema
        job.result = result.to_dict()
        from src.api.storage import document_name, save_analysis_snapshot
        from src.config import LEGAL_BERT_MODEL, COHERENCE_CHECKPOINT_PATH
        import hashlib
        job.result.setdefault("metadata", {}).update({
            "document_name": document_name(doc_id),
            "model_version": f"{LEGAL_BERT_MODEL}; coherence_classifier.pt",
            "checkpoint_sha256": hashlib.sha256(COHERENCE_CHECKPOINT_PATH.read_bytes()).hexdigest(),
            "clause_inventory": [c.to_dict() for c in clauses],
            "source_text": segmenter._clean_html(document_text) if hasattr(segmenter, "_clean_html") else document_text,
            "analysis_state": "REVIEW_REQUIRED" if job.result.get("total_flags") else "NO_FINDINGS",
        })
        job.status = JobStatus.COMPLETED
        save_analysis_snapshot(job.model_dump())
    except Exception:
        job.error = "Analysis failed. Check local model availability, storage configuration and the 500 clause limit; retry the document."
        job.status = JobStatus.FAILED
        job.result = None
        from src.api.storage import document_exists, delete_document_files
        if not document_exists(doc_id):
            # Retention may have expired this document while the model was running.
            delete_document_files(doc_id)
    finally:
        ANALYSIS_LOCK.release()

