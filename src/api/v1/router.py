"""
src/api/v1/router.py — FastAPI endpoints with Security Hardening (Prompt 16)

Hardenings applied:
- Work Package A: Authentication via API keys (X-API-Key / Bearer)
- Work Package B: Process-local rate limiting on upload and analyze
- Work Package C: Encrypted storage at rest (Fernet authenticated encryption)
- Work Package D: Audit logging with safe metadata and zero plaintext/secret leakage
- Work Package E: Data retention cleanup
- Work Package F: Privacy and data retention policy exposure
"""
import uuid
import threading
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request

from src.api.schema import (
    JobStatusResponse, UploadResponse, AnalyzeRequest, AnalyzeResponse,
    DocumentScoringResultModel, FeedbackRequest, FeedbackResponse
)
from src.api.jobs import create_job, get_job, run_analysis_job_sync, JobStatus
from src.api.dependencies import get_segmenter_dep, get_scorer_dep
from src.api.security import verify_api_key
from src.api.rate_limiter import rate_limit_upload_and_analyze
from src.api.storage import (
    save_encrypted_document,
    load_and_decrypt_document,
    document_exists
)
from src.api.audit import log_audit_event
from src.api.retention import cleanup_expired_artifacts
from src.api.privacy import get_privacy_policy, PrivacyPolicyResponse
from src.feedback.storage import insert_feedback, init_db
from src.feedback.schema import FeedbackRecord

router = APIRouter(prefix="/v1", tags=["Analysis Pipeline"])

# Ensure DB is initialized
init_db()


@router.get("/privacy-policy", response_model=PrivacyPolicyResponse, tags=["Policy"])
async def privacy_policy():
    """
    Publicly accessible privacy and data retention policy.
    Must be surfaced by the frontend (Prompt 17) prior to file upload.
    """
    return get_privacy_policy()


@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    client_id: str = Depends(rate_limit_upload_and_analyze)
):
    """
    Accepts contract document, encrypts at rest using Fernet authenticated encryption.
    Rate limited and authenticated.
    """
    if not file.filename:
        log_audit_event(
            event_type="DOCUMENT_UPLOAD",
            action="POST /v1/upload",
            client_id=client_id,
            status="FAILED",
            http_status=400,
            details={"error": "missing_filename"}
        )
        raise HTTPException(status_code=400, detail="Filename missing.")
    
    doc_id = f"doc_{uuid.uuid4().hex[:8]}"
    
    try:
        content = await file.read()
        text_content = content.decode("utf-8")
        if not text_content.strip():
            log_audit_event(
                event_type="DOCUMENT_UPLOAD",
                action="POST /v1/upload",
                client_id=client_id,
                status="FAILED",
                http_status=400,
                details={"error": "empty_file"}
            )
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")

        # Save encrypted at rest — plaintext is never written to disk
        save_encrypted_document(doc_id=doc_id, document_text=text_content, client_id=client_id)
    except UnicodeDecodeError:
        log_audit_event(
            event_type="DOCUMENT_UPLOAD",
            action="POST /v1/upload",
            client_id=client_id,
            status="FAILED",
            http_status=400,
            details={"error": "unicode_decode_error"}
        )
        raise HTTPException(status_code=400, detail="Uploaded file must be valid UTF-8 text.")
    except HTTPException:
        raise
    except Exception as e:
        log_audit_event(
            event_type="DOCUMENT_UPLOAD",
            action="POST /v1/upload",
            client_id=client_id,
            status="FAILED",
            http_status=500,
            details={"error": "storage_encryption_error"}
        )
        raise HTTPException(status_code=500, detail=f"Failed to securely store file: {str(e)}")

    log_audit_event(
        event_type="DOCUMENT_UPLOAD",
        action="POST /v1/upload",
        client_id=client_id,
        status="SUCCESS",
        http_status=200,
        resource_id=doc_id,
        details={"bytes_received": len(content)}
    )
        
    return UploadResponse(doc_id=doc_id, message="Document uploaded and encrypted successfully.")


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_document(
    request: AnalyzeRequest,
    client_id: str = Depends(rate_limit_upload_and_analyze),
    segmenter=Depends(get_segmenter_dep),
    scorer=Depends(get_scorer_dep)
):
    """
    Triggers asynchronous analysis of an encrypted uploaded document.
    Decrypts document text strictly in memory for pipeline execution.
    """
    doc_id = request.doc_id
    if not document_exists(doc_id):
        log_audit_event(
            event_type="DOCUMENT_ANALYZE",
            action="POST /v1/analyze",
            client_id=client_id,
            status="FAILED",
            http_status=404,
            resource_id=doc_id,
            details={"error": "document_not_found"}
        )
        raise HTTPException(status_code=404, detail="Document not found. Please upload first.")
        
    try:
        # In-memory decryption — no plaintext temp files created on disk
        document_text = load_and_decrypt_document(doc_id)
    except Exception as e:
        log_audit_event(
            event_type="DOCUMENT_ANALYZE",
            action="POST /v1/analyze",
            client_id=client_id,
            status="FAILED",
            http_status=500,
            resource_id=doc_id,
            details={"error": "decryption_failed"}
        )
        raise HTTPException(status_code=500, detail="Failed to decrypt document for analysis.")

    job_id = create_job(doc_id)
    
    # Run in separate thread to prevent blocking the async event loop
    thread = threading.Thread(
        target=run_analysis_job_sync,
        args=(job_id, doc_id, document_text, segmenter, scorer),
        daemon=True
    )
    thread.start()

    log_audit_event(
        event_type="DOCUMENT_ANALYZE",
        action="POST /v1/analyze",
        client_id=client_id,
        status="SUCCESS",
        http_status=200,
        resource_id=doc_id,
        details={"job_id": job_id}
    )
    
    return AnalyzeResponse(job_id=job_id, message="Analysis job accepted and queued.")


@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(
    job_id: str,
    client_id: str = Depends(verify_api_key)
):
    """
    Retrieves the status of an analysis job. Authenticated endpoint.
    """
    job = get_job(job_id)
    if not job:
        log_audit_event(
            event_type="JOB_STATUS_CHECK",
            action=f"GET /v1/jobs/{job_id}",
            client_id=client_id,
            status="FAILED",
            http_status=404,
            resource_id=job_id
        )
        raise HTTPException(status_code=404, detail="Job not found.")
        
    log_audit_event(
        event_type="JOB_STATUS_CHECK",
        action=f"GET /v1/jobs/{job_id}",
        client_id=client_id,
        status="SUCCESS",
        http_status=200,
        resource_id=job_id,
        details={"job_status": job.status}
    )

    return JobStatusResponse(
        job_id=job.job_id,
        status=job.status,
        error=job.error
    )


@router.get("/jobs/{job_id}/results", response_model=DocumentScoringResultModel)
async def get_job_results(
    job_id: str,
    client_id: str = Depends(verify_api_key)
):
    """
    Retrieves the full typed result of a completed analysis job. Authenticated endpoint.
    """
    job = get_job(job_id)
    if not job:
        log_audit_event(
            event_type="JOB_RESULTS_FETCH",
            action=f"GET /v1/jobs/{job_id}/results",
            client_id=client_id,
            status="FAILED",
            http_status=404,
            resource_id=job_id
        )
        raise HTTPException(status_code=404, detail="Job not found.")
        
    if job.status != JobStatus.COMPLETED:
        log_audit_event(
            event_type="JOB_RESULTS_FETCH",
            action=f"GET /v1/jobs/{job_id}/results",
            client_id=client_id,
            status="FAILED",
            http_status=400,
            resource_id=job_id,
            details={"current_status": job.status}
        )
        raise HTTPException(
            status_code=400, 
            detail=f"Job is not completed. Current status: {job.status}"
        )
        
    if not job.result:
        raise HTTPException(status_code=500, detail="Job completed but result is missing.")

    log_audit_event(
        event_type="JOB_RESULTS_FETCH",
        action=f"GET /v1/jobs/{job_id}/results",
        client_id=client_id,
        status="SUCCESS",
        http_status=200,
        resource_id=job_id
    )
        
    return job.result


@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(
    request: FeedbackRequest,
    client_id: str = Depends(verify_api_key)
):
    """
    Submit reviewer feedback (Prompt 11 integration). Authenticated endpoint.
    """
    record = FeedbackRecord.create(
        doc_id=request.doc_id,
        clause_id=request.clause_id,
        original_severity=request.original_severity,
        reviewer_verdict=request.reviewer_verdict,
        reviewer_id=request.reviewer_id,
        provenance=request.provenance,
        corrected_severity=request.corrected_severity,
        model_version=request.model_version,
        anomaly_id=request.anomaly_id
    )
    
    init_db()
    insert_feedback(record)

    log_audit_event(
        event_type="FEEDBACK_SUBMIT",
        action="POST /v1/feedback",
        client_id=client_id,
        status="SUCCESS",
        http_status=200,
        resource_id=request.doc_id,
        details={"feedback_id": record.feedback_id, "clause_id": request.clause_id}
    )
    
    return FeedbackResponse(
        feedback_id=record.feedback_id,
        message="Feedback successfully recorded."
    )


@router.post("/maintenance/cleanup", tags=["Maintenance"])
async def trigger_retention_cleanup(
    client_id: str = Depends(verify_api_key)
):
    """
    Authenticated administrative maintenance endpoint to enforce data retention cleanup.
    """
    result = cleanup_expired_artifacts()
    return {"status": "cleanup_complete", "result": result}
