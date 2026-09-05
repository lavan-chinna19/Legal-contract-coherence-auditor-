"""
src/api/jobs.py — In-memory job queue for async contract analysis.
Allows immediate HTTP return while processing long documents.
"""
import asyncio
import uuid
from typing import Dict, Optional, Any
from pydantic import BaseModel

from src.scoring.pipeline import DualChannelScorer

class JobStatus:
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class Job(BaseModel):
    job_id: str
    doc_id: str
    status: str = JobStatus.QUEUED
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# Simple in-memory store for jobs
JOB_STORE: Dict[str, Job] = {}


def create_job(doc_id: str) -> str:
    job_id = str(uuid.uuid4())
    JOB_STORE[job_id] = Job(job_id=job_id, doc_id=doc_id)
    return job_id


def get_job(job_id: str) -> Optional[Job]:
    return JOB_STORE.get(job_id)


def delete_jobs_for_doc(doc_id: str) -> int:
    """Removes in-memory jobs associated with a purged document."""
    to_delete = [jid for jid, j in JOB_STORE.items() if j.doc_id == doc_id]
    for jid in to_delete:
        del JOB_STORE[jid]
    return len(to_delete)


def run_analysis_job_sync(job_id: str, doc_id: str, document_text: str, segmenter: Any, scorer: DualChannelScorer):
    """
    Background worker to process the contract using synchronous execution in a separate thread.
    """
    job = JOB_STORE.get(job_id)
    if not job:
        return

    job.status = JobStatus.RUNNING
    try:
        # Segment the document
        clauses = segmenter.segment(document_text, doc_id)
        
        # Run scoring pipeline
        result = scorer.score_document(clauses, doc_id)
        
        # Store result as dict matching schema
        job.result = result.to_dict()
        job.status = JobStatus.COMPLETED
    except Exception as e:
        job.error = f"Analysis failed: {str(e)}"
        job.status = JobStatus.FAILED

