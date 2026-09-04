"""
src/api/schema.py — Pydantic schemas for the FastAPI backend.
Mirrors internal schemas in src.scoring.schema and src.feedback.schema.
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any


# -----------------------------------------------------------------------------
# Scoring Schemas (Mirrors src.scoring.schema)
# -----------------------------------------------------------------------------

class ChannelAEvidenceModel(BaseModel):
    nearest_centroid_label: str
    centroid_distance: float
    is_ood: bool
    top_k_distances: Dict[str, float] = Field(default_factory=dict)


class ChannelBEvidenceModel(BaseModel):
    incoming_prob: Optional[float] = None
    outgoing_prob: Optional[float] = None
    incoming_anomaly: Optional[float] = None
    outgoing_anomaly: Optional[float] = None
    prev_clause_id: Optional[str] = None
    next_clause_id: Optional[str] = None


class ClauseScoringResultModel(BaseModel):
    clause_id: str
    doc_id: str
    sequence_idx: int
    text_preview: str
    channel_a_score: float
    channel_b_score: float
    combined_score: float
    channel_a_evidence: ChannelAEvidenceModel
    channel_b_evidence: ChannelBEvidenceModel
    is_anomaly: bool
    severity: str
    source_label: Optional[str] = None
    confidence_interval: Optional[List[float]] = None
    calibration_source: str
    cross_channel_agreement: float
    agreement_type: str
    interval_width: Optional[float] = None
    severity_justification: Optional[str] = None


class DocumentScoringResultModel(BaseModel):
    doc_id: str
    total_clauses: int
    anomaly_count: int
    high_severity_count: int
    medium_severity_count: int
    mean_combined_score: float
    max_combined_score: float
    clauses: List[ClauseScoringResultModel]
    metadata: Dict[str, Any] = Field(default_factory=dict)
    calibration_source: str


# -----------------------------------------------------------------------------
# Job & API Schemas
# -----------------------------------------------------------------------------

class JobStatusResponse(BaseModel):
    job_id: str
    status: str  # QUEUED, RUNNING, COMPLETED, FAILED
    error: Optional[str] = None


class UploadResponse(BaseModel):
    doc_id: str
    message: str


class AnalyzeRequest(BaseModel):
    doc_id: str


class AnalyzeResponse(BaseModel):
    job_id: str
    message: str


# -----------------------------------------------------------------------------
# Feedback Schemas
# -----------------------------------------------------------------------------

class FeedbackRequest(BaseModel):
    doc_id: str
    clause_id: str
    original_severity: str
    reviewer_verdict: str
    reviewer_id: str
    provenance: str = "REAL"
    corrected_severity: Optional[str] = None
    model_version: str = "v1"
    anomaly_id: Optional[str] = None


class FeedbackResponse(BaseModel):
    feedback_id: str
    message: str

