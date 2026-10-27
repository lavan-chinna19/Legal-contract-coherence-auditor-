"""Authenticated release workflows: history, exports and opt-in graph evidence."""
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, Field
from src.api.security import verify_api_key
from src.api.jobs import get_job, JobStatus
from src.api.storage import get_document_metadata, list_owned_documents, save_analysis_snapshot
from src.api.dependencies import get_segmenter_dep

router = APIRouter(prefix="/v1", tags=["Reports and history"])


def owned_job(job_id: str, client_id: str):
    job = get_job(job_id)
    if not job or not job.client_id or job.client_id != client_id:
        raise HTTPException(404, "Job not found.")
    meta = get_document_metadata(job.doc_id)
    if not meta or meta.get("client_id") != client_id:
        raise HTTPException(404, "Document not found.")
    if job.status != JobStatus.COMPLETED or not job.result:
        raise HTTPException(409, "Analysis is not completed. Retry after a successful analysis.")
    return job


@router.get("/session")
def session(client_id: str = Depends(verify_api_key)):
    return {"authenticated": True, "client_id": client_id}


@router.get("/documents")
def documents(client_id: str = Depends(verify_api_key)):
    return {"documents": list_owned_documents(client_id)}


@router.get("/documents/{doc_id}/clauses")
def parsed_clauses(doc_id: str, client_id: str = Depends(verify_api_key), segmenter=Depends(get_segmenter_dep)):
    meta = get_document_metadata(doc_id)
    if not meta or meta.get("client_id") != client_id:
        raise HTTPException(404, "Document not found.")
    from src.api.storage import load_and_decrypt_document
    try:
        source = load_and_decrypt_document(doc_id)
        clauses = segmenter.segment(source, doc_id)
    except Exception:
        raise HTTPException(503, "Could not parse the stored document. Verify storage configuration and retry.")
    if not clauses:
        raise HTTPException(400, "No readable clauses found.")
    if len(clauses) > 500:
        raise HTTPException(413, "Document exceeds the 500 clause analysis limit.")
    normalized = segmenter._clean_html(source) if hasattr(segmenter, "_clean_html") else source
    from src.structure import parse_contract, resolve_references
    structure = parse_contract(clauses, doc_id, source_text=source)
    return {"doc_id": doc_id, "source_text": normalized, "clauses": [c.to_dict() for c in clauses],
            "original_source_text": source, "structural_document": structure.to_dict(),
            "reference_resolutions": resolve_references(structure),
            "neural_input_coordinate_space": "legacy_normalized_extracted_text"}


@router.get("/jobs/{job_id}/report/{format}")
def export_report(job_id: str, format: Literal["pdf", "docx"], client_id: str = Depends(verify_api_key)):
    job = owned_job(job_id, client_id)
    from src.api.reports import render_report
    try:
        data = render_report(job.result, format)
    except (ImportError, RuntimeError):
        raise HTTPException(503, "Report renderer unavailable. Install requirements-release.txt and a Unicode font.")
    media = "application/pdf" if format == "pdf" else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    return Response(data, media_type=media, headers={"Content-Disposition": f'attachment; filename="LexAudit-{job.doc_id}.{format}"',
                                                   "Cache-Control": "no-store", "X-Content-Type-Options": "nosniff"})


class DependencyRequest(BaseModel):
    job_id: str
    experimental: bool = Field(strict=True)


@router.post("/experimental/dependencies")
def dependency_graph(request: DependencyRequest, client_id: str = Depends(verify_api_key)):
    if not request.experimental:
        raise HTTPException(400, "Explicit experimental opt-in is required.")
    job = owned_job(request.job_id, client_id)
    inventory = job.result.get("metadata", {}).get("clause_inventory")
    if inventory is None:
        raise HTTPException(409, "Reanalyze this legacy document to establish authoritative clause evidence.")
    from src.rules.dependency_graph import detect_dependencies
    source = job.result.get("metadata", {}).get("original_source_text")
    graph = detect_dependencies(inventory, source_text=source)
    if source is None:
        graph["evidence_limit"] = "Legacy saved analysis: only assembled scoring clauses are available; reanalyze for original extracted evidence."
    job.result["metadata"]["dependency_graph"] = graph
    save_analysis_snapshot(job.model_dump())
    return graph
