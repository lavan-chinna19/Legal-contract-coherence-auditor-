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
from starlette.concurrency import run_in_threadpool
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request

from src.api.schema import (
    JobStatusResponse, UploadResponse, AnalyzeRequest, AnalyzeResponse,
    DocumentScoringResultModel, UnifiedAuditReportModel, FeedbackRequest, FeedbackResponse,
    RepositionRequest, RepositionResponse, RepositionCandidateModel,
    RedTeamScenarioRequest, RedTeamCaseResponse, RedTeamOracleResponse, RedTeamConditionResult
)
from src.config import ClauseRecord
from src.redteam.schema import PerturbationType, PerturbationDifficulty, PerturbationScenario
from src.redteam.fixtures import SYNTHETIC_FIXTURE_REGISTRY
from src.redteam.runner import RedTeamExperimentRunner
from src.api.jobs import create_job, get_job, run_analysis_job_sync, JobStatus, run_model_operation, ANALYSIS_LOCK
from src.api.dependencies import get_segmenter_dep, get_auditor_dep, get_scorer_dep
from src.api.security import verify_api_key, verify_admin_api_key
from src.api.rate_limiter import rate_limit_upload_and_analyze
from src.api.storage import (
    save_encrypted_document,
    load_and_decrypt_document,
    document_exists,
    get_document_metadata
)
from src.api.audit import log_audit_event
from src.api.retention import cleanup_expired_artifacts
from src.api.privacy import get_privacy_policy, PrivacyPolicyResponse
from src.api.ingestion import parse_document, MAX_UPLOAD_BYTES
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
    
    doc_id = f"doc_{uuid.uuid4().hex}"
    
    try:
        content = await file.read(MAX_UPLOAD_BYTES + 1)
        text_content = await run_in_threadpool(parse_document, content, file.filename)
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
        safe_name = file.filename.replace("\\", "/").rsplit("/", 1)[-1]
        safe_name = "".join(c for c in safe_name if c.isprintable())[:180]
        save_encrypted_document(doc_id=doc_id, document_text=text_content, client_id=client_id, filename=safe_name)
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
        raise HTTPException(status_code=500, detail="Failed to securely store file. Check server storage configuration.")

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
    auditor=Depends(get_auditor_dep)
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
        
    meta = get_document_metadata(doc_id)
    if not meta or not meta.get("client_id") or meta.get("client_id") != client_id:
        log_audit_event(
            event_type="DOCUMENT_ANALYZE",
            action="POST /v1/analyze",
            client_id=client_id,
            status="FAILED",
            http_status=404,
            resource_id=doc_id,
            details={"error": "unauthorized_document_access"}
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

    if ANALYSIS_LOCK.locked():
        raise HTTPException(429, "Another model operation is running. Retry when it finishes.")
    job_id = create_job(doc_id, client_id=client_id)
    
    # Run in separate thread to prevent blocking the async event loop
    thread = threading.Thread(
        target=run_analysis_job_sync,
        args=(job_id, doc_id, document_text, segmenter, auditor),
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
    if not job or not job.client_id or job.client_id != client_id:
        log_audit_event(
            event_type="JOB_STATUS_CHECK",
            action=f"GET /v1/jobs/{job_id}",
            client_id=client_id,
            status="FAILED",
            http_status=404,
            resource_id=job_id,
            details={"error": "unauthorized_or_missing_job"}
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


@router.get("/jobs/{job_id}/results", response_model=UnifiedAuditReportModel)
async def get_job_results(
    job_id: str,
    client_id: str = Depends(verify_api_key)
):
    """
    Retrieves the full typed result of a completed analysis job. Authenticated endpoint.
    """
    job = get_job(job_id)
    if not job or not job.client_id or job.client_id != client_id:
        log_audit_event(
            event_type="JOB_RESULTS_FETCH",
            action=f"GET /v1/jobs/{job_id}/results",
            client_id=client_id,
            status="FAILED",
            http_status=404,
            resource_id=job_id,
            details={"error": "unauthorized_or_missing_job"}
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
    if document_exists(request.doc_id):
        meta = get_document_metadata(request.doc_id)
        if not meta or not meta.get("client_id") or meta.get("client_id") != client_id:
            log_audit_event(
                event_type="FEEDBACK_SUBMIT",
                action="POST /v1/feedback",
                client_id=client_id,
                status="FAILED",
                http_status=404,
                resource_id=request.doc_id,
                details={"error": "unauthorized_document_feedback"}
            )
            raise HTTPException(status_code=404, detail="Document not found.")

    valid_verdicts = {"CONFIRM_ANOMALY", "REJECT_ANOMALY"}
    if request.reviewer_verdict not in valid_verdicts:
        log_audit_event(
            event_type="FEEDBACK_SUBMIT",
            action="POST /v1/feedback",
            client_id=client_id,
            status="FAILED",
            http_status=422,
            resource_id=request.doc_id,
            details={"error": "invalid_verdict"}
        )
        raise HTTPException(status_code=422, detail=f"Invalid reviewer_verdict. Must be one of: {valid_verdicts}")

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


@router.get("/xai/attribution", tags=["Explainability"])
async def get_attribution(
    doc_id: str,
    clause_id: str,
    client_id: str = Depends(verify_api_key),
    segmenter=Depends(get_segmenter_dep),
    scorer=Depends(get_scorer_dep)
):
    """
    Get token-level Integrated Gradients attribution for a clause (Channel A).
    """
    from src.xai.ig import IntegratedGradientsExplainer
    
    if not document_exists(doc_id):
        raise HTTPException(status_code=404, detail="Document not found.")

    meta = get_document_metadata(doc_id)
    if not meta or not meta.get("client_id") or meta.get("client_id") != client_id:
        raise HTTPException(status_code=404, detail="Document not found.")
        
    try:
        doc_text = load_and_decrypt_document(doc_id)
        clauses = segmenter.segment(doc_text, doc_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to load document for explanation.")
        
    clause = next((c for c in clauses if c.clause_id == clause_id), None)
    if not clause:
        raise HTTPException(status_code=404, detail="Clause not found.")
        
    def explain():
        return IntegratedGradientsExplainer(scorer.channel_a).explain(clause)
    result = await run_in_threadpool(run_model_operation, explain)
    
    return result.to_dict()


@router.get("/xai/sensitivity", tags=["Explainability"])
async def get_sensitivity(
    doc_id: str,
    clause_id: str,
    client_id: str = Depends(verify_api_key),
    segmenter=Depends(get_segmenter_dep),
    scorer=Depends(get_scorer_dep)
):
    """
    Get neighborhood perturbation sensitivity for a clause (Channel B).
    """
    from src.xai.sensitivity import ChannelBSensitivityAnalyzer
    
    if not document_exists(doc_id):
        raise HTTPException(status_code=404, detail="Document not found.")

    meta = get_document_metadata(doc_id)
    if not meta or not meta.get("client_id") or meta.get("client_id") != client_id:
        raise HTTPException(status_code=404, detail="Document not found.")
        
    try:
        doc_text = load_and_decrypt_document(doc_id)
        clauses = segmenter.segment(doc_text, doc_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to load document for explanation.")
        
    clause = next((c for c in clauses if c.clause_id == clause_id), None)
    if not clause:
        raise HTTPException(status_code=404, detail="Clause not found.")
        
    def explain():
        return ChannelBSensitivityAnalyzer(scorer.channel_b).explain(clause, clauses)
    result = await run_in_threadpool(run_model_operation, explain)
    
    return result.to_dict()


@router.post("/maintenance/cleanup", tags=["Maintenance"])
async def trigger_retention_cleanup(
    client_id: str = Depends(verify_admin_api_key)
):
    """
    Authenticated administrative maintenance endpoint to enforce data retention cleanup.
    Requires validated administrative privileges (ADMIN_API_KEY).
    """
    result = cleanup_expired_artifacts()
    log_audit_event(
        event_type="ADMIN_CLEANUP",
        action="POST /v1/maintenance/cleanup",
        client_id=client_id,
        status="SUCCESS",
        http_status=200,
        details={"purged_count": result.get("deleted_documents_count", 0)}
    )
    return {"status": "cleanup_complete", "result": result}


@router.post("/experimental/reposition", response_model=RepositionResponse, tags=["Experimental"])
async def evaluate_repositioning(
    request: RepositionRequest,
    client_id: str = Depends(verify_api_key),
    segmenter=Depends(get_segmenter_dep),
    scorer=Depends(get_scorer_dep)
):
    """
    Experimental Counterfactual Clause Repositioning endpoint (Phase 4C).
    Evaluates alternative insertion positions for an authoritative clause ID using the frozen coherence scorer.
    Enforces authentication, document ownership, bounds checking, and strict zero-mutation guarantees.
    """
    from src.scoring.repositioning import CounterfactualRepositioningEngine

    if not request.experimental:
        log_audit_event(
            event_type="EXPERIMENTAL_REPOSITION",
            action="POST /v1/experimental/reposition",
            client_id=client_id,
            status="FAILED",
            http_status=400,
            resource_id=request.doc_id,
            details={"error": "missing_experimental_opt_in"}
        )
        raise HTTPException(
            status_code=400,
            detail="Counterfactual repositioning is an experimental capability. Parameter 'experimental' must be true."
        )

    if not document_exists(request.doc_id):
        log_audit_event(
            event_type="EXPERIMENTAL_REPOSITION",
            action="POST /v1/experimental/reposition",
            client_id=client_id,
            status="FAILED",
            http_status=404,
            resource_id=request.doc_id,
            details={"error": "document_not_found"}
        )
        raise HTTPException(status_code=404, detail="Document not found.")

    meta = get_document_metadata(request.doc_id)
    if not meta or not meta.get("client_id") or meta.get("client_id") != client_id:
        log_audit_event(
            event_type="EXPERIMENTAL_REPOSITION",
            action="POST /v1/experimental/reposition",
            client_id=client_id,
            status="FAILED",
            http_status=404,
            resource_id=request.doc_id,
            details={"error": "unauthorized_document_access"}
        )
        raise HTTPException(status_code=404, detail="Document not found.")

    try:
        doc_text = load_and_decrypt_document(request.doc_id)
        clauses = segmenter.segment(doc_text, request.doc_id)
    except Exception as e:
        log_audit_event(
            event_type="EXPERIMENTAL_REPOSITION",
            action="POST /v1/experimental/reposition",
            client_id=client_id,
            status="FAILED",
            http_status=500,
            resource_id=request.doc_id,
            details={"error": "document_load_or_segment_error"}
        )
        raise HTTPException(status_code=500, detail="Failed to load document for repositioning evaluation.")

    # Bound document size to mitigate cost-amplification attacks
    MAX_REPOSITION_CLAUSES = 100
    if len(clauses) > MAX_REPOSITION_CLAUSES:
        log_audit_event(
            event_type="EXPERIMENTAL_REPOSITION",
            action="POST /v1/experimental/reposition",
            client_id=client_id,
            status="FAILED",
            http_status=400,
            resource_id=request.doc_id,
            details={"error": "document_size_exceeded", "clause_count": len(clauses)}
        )
        raise HTTPException(
            status_code=400,
            detail=f"Document exceeds maximum supported size for experimental repositioning ({len(clauses)} > {MAX_REPOSITION_CLAUSES} clauses)."
        )

    target_clause = next((c for c in clauses if c.clause_id == request.clause_id), None)
    if not target_clause:
        log_audit_event(
            event_type="EXPERIMENTAL_REPOSITION",
            action="POST /v1/experimental/reposition",
            client_id=client_id,
            status="FAILED",
            http_status=404,
            resource_id=request.doc_id,
            details={"error": "clause_not_found", "clause_id": request.clause_id}
        )
        raise HTTPException(status_code=404, detail=f"Clause '{request.clause_id}' not found in document.")

    engine = CounterfactualRepositioningEngine(scorer=scorer)
    result = await run_in_threadpool(run_model_operation, engine.evaluate,
        clauses=clauses,
        target_clause_id=request.clause_id,
        use_optimization=True,
        min_delta_threshold=request.min_delta_threshold,
        verify_parity=True
    )

    log_audit_event(
        event_type="EXPERIMENTAL_REPOSITION",
        action="POST /v1/experimental/reposition",
        client_id=client_id,
        status="SUCCESS",
        http_status=200,
        resource_id=request.doc_id,
        details={
            "clause_id": request.clause_id,
            "is_abstaining": result.is_abstaining,
            "abstention_reason": result.abstention_reason,
            "best_candidate_idx": result.best_candidate_idx,
            "best_objective_delta": result.best_objective_delta,
            "evaluation_time_ms": round(result.evaluation_time_ms, 2)
        }
    )

    candidate_models = [
        RepositionCandidateModel(
            position_idx=c.position_idx,
            rank=c.rank,
            relative_placement=c.relative_placement,
            preceding_clause_id=c.preceding_clause_id,
            succeeding_clause_id=c.succeeding_clause_id,
            mean_combined_score=c.mean_combined_score,
            mean_channel_b_score=c.mean_channel_b_score,
            clause_channel_b_score=c.clause_channel_b_score,
            objective_delta=c.objective_delta,
            is_current_position=c.is_current_position,
            is_recommended=c.is_recommended
        )
        for c in result.candidates
    ]

    response = RepositionResponse(
        doc_id=result.doc_id,
        target_clause_id=result.target_clause_id,
        target_clause_idx=result.target_clause_idx,
        total_clauses=result.total_clauses,
        original_mean_combined_score=result.original_mean_combined_score,
        original_target_sb=result.original_target_sb,
        best_candidate_idx=result.best_candidate_idx,
        best_objective_delta=result.best_objective_delta,
        is_abstaining=result.is_abstaining,
        abstention_reason=result.abstention_reason,
        warning_notice=result.warning_notice,
        model_provenance=result.model_provenance,
        primary_objective_name=result.primary_objective_name,
        candidates=candidate_models,
        optimization_verified=result.optimization_verified,
        evaluation_time_ms=result.evaluation_time_ms
    )
    if meta.get("latest_job_id"):
        saved_job = get_job(meta["latest_job_id"])
        if saved_job and saved_job.result and saved_job.client_id == client_id:
            from src.api.storage import save_analysis_snapshot
            saved_job.result.setdefault("metadata", {})["counterfactual"] = response.model_dump()
            save_analysis_snapshot(saved_job.model_dump())
    return response


# -----------------------------------------------------------------------------
# Phase 4D Self Red-Team Robustness Laboratory Endpoint (Experimental)
# -----------------------------------------------------------------------------

@router.post("/experimental/redteam", response_model=RedTeamCaseResponse, tags=["Experimental Red-Team"])
async def evaluate_redteam_scenario(
    request: RedTeamScenarioRequest,
    client_id: str = Depends(verify_api_key),
    segmenter=Depends(get_segmenter_dep),
    auditor=Depends(get_auditor_dep)
):
    """
    Experimental Self Red-Team Robustness Laboratory endpoint (Phase 4D).
    Generates controlled, reversible perturbations and measures existing detector sensitivity in memory.
    Enforces authentication, document ownership, strict experimental opt-in, bounds checking, and zero document mutation.
    """
    if not request.experimental:
        log_audit_event(
            event_type="EXPERIMENTAL_REDTEAM",
            action="POST /v1/experimental/redteam",
            client_id=client_id,
            status="FAILED",
            http_status=400,
            resource_id=request.doc_id or request.fixture_id or "unknown",
            details={"error": "missing_experimental_opt_in"}
        )
        raise HTTPException(
            status_code=400,
            detail="Red-team robustness evaluation is an experimental capability. Parameter 'experimental' must be true."
        )

    # Validate perturbation type
    valid_types = {pt.value for pt in PerturbationType}
    if request.perturbation_type not in valid_types:
        log_audit_event(
            event_type="EXPERIMENTAL_REDTEAM",
            action="POST /v1/experimental/redteam",
            client_id=client_id,
            status="FAILED",
            http_status=400,
            resource_id=request.doc_id or request.fixture_id or "unknown",
            details={"error": "unsupported_perturbation_type", "type": request.perturbation_type}
        )
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported perturbation type: '{request.perturbation_type}'. Valid types: {sorted(list(valid_types))}"
        )

    # Load clauses: either from synthetic fixture or authenticated client document
    clauses: List[ClauseRecord] = []
    source_doc_id = ""

    if request.fixture_id:
        if request.fixture_id not in SYNTHETIC_FIXTURE_REGISTRY:
            log_audit_event(
                event_type="EXPERIMENTAL_REDTEAM",
                action="POST /v1/experimental/redteam",
                client_id=client_id,
                status="FAILED",
                http_status=404,
                resource_id=request.fixture_id,
                details={"error": "fixture_not_found"}
            )
            raise HTTPException(status_code=404, detail=f"Synthetic fixture '{request.fixture_id}' not found.")
        clauses = SYNTHETIC_FIXTURE_REGISTRY[request.fixture_id]()
        source_doc_id = request.fixture_id
    elif request.doc_id:
        if not document_exists(request.doc_id):
            log_audit_event(
                event_type="EXPERIMENTAL_REDTEAM",
                action="POST /v1/experimental/redteam",
                client_id=client_id,
                status="FAILED",
                http_status=404,
                resource_id=request.doc_id,
                details={"error": "document_not_found"}
            )
            raise HTTPException(status_code=404, detail="Document not found.")

        meta = get_document_metadata(request.doc_id)
        if not meta or not meta.get("client_id") or meta.get("client_id") != client_id:
            log_audit_event(
                event_type="EXPERIMENTAL_REDTEAM",
                action="POST /v1/experimental/redteam",
                client_id=client_id,
                status="FAILED",
                http_status=404,
                resource_id=request.doc_id,
                details={"error": "unauthorized_document_access"}
            )
            raise HTTPException(status_code=404, detail="Document not found.")

        try:
            doc_text = load_and_decrypt_document(request.doc_id)
            clauses = segmenter.segment(doc_text, request.doc_id)
            source_doc_id = request.doc_id
        except Exception as e:
            log_audit_event(
                event_type="EXPERIMENTAL_REDTEAM",
                action="POST /v1/experimental/redteam",
                client_id=client_id,
                status="FAILED",
                http_status=500,
                resource_id=request.doc_id,
                details={"error": "document_load_or_segment_error"}
            )
            raise HTTPException(status_code=500, detail="Failed to load document for red-team evaluation.")
    else:
        raise HTTPException(status_code=400, detail="Either 'fixture_id' or 'doc_id' must be provided.")

    # Bound document size to mitigate resource exhaustion
    MAX_REDTEAM_CLAUSES = 100
    if len(clauses) > MAX_REDTEAM_CLAUSES:
        log_audit_event(
            event_type="EXPERIMENTAL_REDTEAM",
            action="POST /v1/experimental/redteam",
            client_id=client_id,
            status="FAILED",
            http_status=400,
            resource_id=source_doc_id,
            details={"error": "document_size_exceeded", "clause_count": len(clauses)}
        )
        raise HTTPException(
            status_code=400,
            detail=f"Document exceeds maximum supported size for experimental red-team ({len(clauses)} > {MAX_REDTEAM_CLAUSES} clauses)."
        )

    # Validate target clause IDs if supplied
    all_clause_ids = {c.clause_id for c in clauses}
    for cid in request.target_clause_ids:
        if cid not in all_clause_ids:
            log_audit_event(
                event_type="EXPERIMENTAL_REDTEAM",
                action="POST /v1/experimental/redteam",
                client_id=client_id,
                status="FAILED",
                http_status=404,
                resource_id=source_doc_id,
                details={"error": "target_clause_not_found", "clause_id": cid}
            )
            raise HTTPException(status_code=404, detail=f"Target clause '{cid}' not found in document.")

    # Build scenario and run pure in-memory experiment
    scenario_id = request.scenario_id or f"SCEN_{request.perturbation_type}_{uuid.uuid4().hex[:6]}"
    scenario = PerturbationScenario(
        scenario_id=scenario_id,
        perturbation_type=PerturbationType(request.perturbation_type),
        difficulty=PerturbationDifficulty.LEVEL_2_MODERATE,
        source_doc_id=source_doc_id,
        title=f"Ad-hoc {request.perturbation_type} Evaluation",
        description=f"Interactive red-team test for {request.perturbation_type}",
        target_clause_ids=request.target_clause_ids,
        parameters=request.parameters,
        expected_detector="UNIFIED_AUDITOR"
    )

    runner = RedTeamExperimentRunner(auditor=auditor)
    case_res = await run_in_threadpool(run_model_operation, runner.run_scenario, scenario, clauses)

    # Re-apply pure transformation to capture previews
    try:
        pert_clauses, _ = runner._apply_transformation(scenario, clauses) if case_res.oracle_result.valid_transformation else (clauses, {})
    except Exception:
        pert_clauses = clauses

    log_audit_event(
        event_type="EXPERIMENTAL_REDTEAM",
        action="POST /v1/experimental/redteam",
        client_id=client_id,
        status="SUCCESS",
        http_status=200,
        resource_id=source_doc_id,
        details={
            "scenario_id": case_res.scenario_id,
            "perturbation_type": case_res.perturbation_type.value,
            "detection_status": case_res.detection_status.value,
            "execution_time_ms": case_res.execution_time_ms
        }
    )

    oracle_conditions = [
        RedTeamConditionResult(
            condition_name=c.condition_name,
            target_property=c.target_property,
            expected_value=c.expected_value,
            observed_value=c.observed_value,
            is_satisfied=c.is_satisfied,
            description=c.description
        )
        for c in case_res.oracle_result.conditions
    ]

    oracle_model = RedTeamOracleResponse(
        valid_transformation=case_res.oracle_result.valid_transformation,
        oracle_condition=case_res.oracle_result.oracle_condition,
        expected_detector=case_res.oracle_result.expected_detector,
        ground_truth_supported=case_res.oracle_result.ground_truth_supported,
        ground_truth_reason=case_res.oracle_result.ground_truth_reason,
        affected_clause_ids=case_res.oracle_result.affected_clause_ids,
        eligible_for_strict_evaluation=case_res.oracle_result.eligible_for_strict_evaluation,
        conditions=oracle_conditions
    )

    orig_preview = [{"clause_id": c.clause_id, "sequence_idx": c.sequence_idx, "text": c.text[:140], "label": c.label} for c in clauses]
    pert_preview = [{"clause_id": c.clause_id, "sequence_idx": c.sequence_idx, "text": c.text[:140], "label": c.label} for c in pert_clauses]

    return RedTeamCaseResponse(
        scenario_id=case_res.scenario_id,
        perturbation_type=case_res.perturbation_type.value,
        difficulty=case_res.difficulty.value,
        source_doc_id=case_res.source_doc_id,
        original_checksum=case_res.original_checksum,
        perturbed_checksum=case_res.perturbed_checksum,
        detection_status=case_res.detection_status.value,
        attribution_valid=case_res.attribution_valid,
        original_mean_combined=case_res.original_mean_combined,
        perturbed_mean_combined=case_res.perturbed_mean_combined,
        delta_mean_combined=case_res.delta_mean_combined,
        original_anomaly_count=case_res.original_anomaly_count,
        perturbed_anomaly_count=case_res.perturbed_anomaly_count,
        delta_anomaly_count=case_res.delta_anomaly_count,
        original_rule_flag_count=case_res.original_rule_flag_count,
        perturbed_rule_flag_count=case_res.perturbed_rule_flag_count,
        new_rule_flags=case_res.new_rule_flags,
        mean_channel_a_delta=case_res.mean_channel_a_delta,
        mean_channel_b_delta=case_res.mean_channel_b_delta,
        max_affected_clause_b_delta=case_res.max_affected_clause_b_delta,
        channel_a_only_delta=case_res.ablations.channel_a_only_anomaly_delta,
        channel_b_only_delta=case_res.ablations.channel_b_only_anomaly_delta,
        dual_channel_combined_delta=case_res.ablations.dual_channel_combined_delta,
        affected_clause_ids=case_res.affected_clause_ids,
        oracle_result=oracle_model,
        failure_category=case_res.failure_category,
        failure_explanation=case_res.failure_explanation,
        execution_time_ms=case_res.execution_time_ms,
        original_clauses_preview=orig_preview,
        perturbed_clauses_preview=pert_preview
    )
