"""
src/api/v1/router.py — FastAPI endpoints for the ML Pipeline (Prompt 15)
"""
import uuid
import asyncio
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, UploadFile, File

from src.api.schema import (
    JobStatusResponse, UploadResponse, AnalyzeRequest, AnalyzeResponse,
    DocumentScoringResultModel, FeedbackRequest, FeedbackResponse
)
from src.api.jobs import create_job, get_job, run_analysis_job_sync, JobStatus
from src.api.dependencies import get_segmenter_dep, get_scorer_dep, UPLOAD_DIR
from src.feedback.storage import insert_feedback, init_db
from src.feedback.schema import FeedbackRecord

router = APIRouter(prefix="/v1", tags=["Analysis Pipeline"])

# Ensure DB is initialized
init_db()


@router.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Accepts a contract document (plaintext), stores it temporarily, and returns a doc_id.
    Ensures confidentiality (Rule 4) by never logging the contract content.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename missing.")
    
    doc_id = f"doc_{uuid.uuid4().hex[:8]}"
    file_path = UPLOAD_DIR / f"{doc_id}.txt"
    
    try:
        content = await file.read()
        text_content = content.decode("utf-8")
        # Save to disk instead of logging
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(text_content)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read file: {e}")
        
    return UploadResponse(doc_id=doc_id, message="Document uploaded successfully.")


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_document(
    request: AnalyzeRequest,
    segmenter=Depends(get_segmenter_dep),
    scorer=Depends(get_scorer_dep)
):
    """
    Triggers asynchronous analysis of an uploaded document.
    """
    doc_id = request.doc_id
    file_path = UPLOAD_DIR / f"{doc_id}.txt"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Document not found. Please upload first.")
        
    with open(file_path, "r", encoding="utf-8") as f:
        document_text = f.read()

    job_id = create_job(doc_id)
    
    # Use threading.Thread instead of BackgroundTasks/asyncio.create_task for TestClient compatibility
    import threading
    thread = threading.Thread(
        target=run_analysis_job_sync,
        args=(job_id, doc_id, document_text, segmenter, scorer),
        daemon=True
    )
    thread.start()
    
    return AnalyzeResponse(job_id=job_id, message="Analysis job accepted and queued.")


@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """
    Retrieves the status of an analysis job.
    """
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
        
    return JobStatusResponse(
        job_id=job.job_id,
        status=job.status,
        error=job.error
    )


@router.get("/jobs/{job_id}/results", response_model=DocumentScoringResultModel)
async def get_job_results(job_id: str):
    """
    Retrieves the full typed result of a completed analysis job.
    """
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
        
    if job.status != JobStatus.COMPLETED:
        raise HTTPException(
            status_code=400, 
            detail=f"Job is not completed. Current status: {job.status}"
        )
        
    if not job.result:
        raise HTTPException(status_code=500, detail="Job completed but result is missing.")
        
    # Return as dictated by DocumentScoringResultModel schema
    return job.result


@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(request: FeedbackRequest):
    """
    Submit reviewer feedback (Prompt 11 integration).
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
    
    insert_feedback(record)
    
    return FeedbackResponse(
        feedback_id=record.feedback_id,
        message="Feedback successfully recorded."
    )
