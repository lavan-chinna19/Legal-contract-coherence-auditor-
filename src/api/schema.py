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


class RuleFlagModel(BaseModel):
    flag_id: str
    doc_id: str
    flag_type: str
    category: str
    severity: str
    title: str
    description: str
    clause_id: Optional[str] = None
    involved_clause_ids: List[str] = Field(default_factory=list)
    evidence: Dict[str, Any] = Field(default_factory=dict)
    claim_scope: Optional[Dict[str, Any]] = None

class ReferenceTargetModel(BaseModel):
    target_type: str
    target_id: str
    raw_label: str
    clause_id: str
    char_start: int = 0
    char_end: int = 0

class DateEntityModel(BaseModel):
    role: str
    raw_text: str
    parsed_iso: str
    clause_id: str
    char_start: int = 0
    char_end: int = 0

class UnifiedAuditReportModel(BaseModel):
    doc_id: str
    total_clauses: int
    ml_anomaly_count: int
    rule_violation_count: int
    total_flags: int
    high_severity_count: int
    medium_severity_count: int
    low_severity_count: int
    scoring_result: DocumentScoringResultModel
    rule_flags: List[RuleFlagModel] = Field(default_factory=list)
    declared_targets: List[ReferenceTargetModel] = Field(default_factory=list)
    extracted_dates: List[DateEntityModel] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

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


# -----------------------------------------------------------------------------
# Phase 4C Counterfactual Repositioning Schemas (Experimental)
# -----------------------------------------------------------------------------

class RepositionRequest(BaseModel):
    doc_id: str
    clause_id: str
    experimental: bool = Field(..., strict=True, description="Explicit opt-in required for experimental repositioning evaluation; must be true.")
    min_delta_threshold: float = Field(0.005, ge=0.0, le=1.0, description="Minimum coherence improvement threshold for recommendation.")


class RepositionCandidateModel(BaseModel):
    position_idx: int
    rank: int
    relative_placement: str
    preceding_clause_id: Optional[str] = None
    succeeding_clause_id: Optional[str] = None
    mean_combined_score: float
    mean_channel_b_score: float
    clause_channel_b_score: float
    objective_delta: float
    is_current_position: bool
    is_recommended: bool


class RepositionResponse(BaseModel):
    doc_id: str
    target_clause_id: str
    target_clause_idx: int
    total_clauses: int
    original_mean_combined_score: float
    original_target_sb: float
    best_candidate_idx: Optional[int] = None
    best_objective_delta: float
    is_abstaining: bool
    abstention_reason: Optional[str] = None
    warning_notice: str
    model_provenance: str
    primary_objective_name: str
    candidates: List[RepositionCandidateModel] = Field(default_factory=list)
    optimization_verified: bool
    evaluation_time_ms: float


# -----------------------------------------------------------------------------
# Phase 4D Self Red-Team Robustness Laboratory Schemas (Experimental)
# -----------------------------------------------------------------------------

class RedTeamScenarioRequest(BaseModel):
    scenario_id: Optional[str] = None
    doc_id: Optional[str] = None
    fixture_id: Optional[str] = None
    perturbation_type: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    target_clause_ids: List[str] = Field(default_factory=list)
    experimental: bool = Field(..., strict=True, description="Explicit opt-in required for experimental red-team evaluation; must be true.")


class RedTeamConditionResult(BaseModel):
    condition_name: str
    target_property: str
    expected_value: Any
    observed_value: Any
    is_satisfied: bool
    description: str


class RedTeamOracleResponse(BaseModel):
    valid_transformation: bool
    oracle_condition: str
    expected_detector: str
    ground_truth_supported: bool
    ground_truth_reason: str
    affected_clause_ids: List[str]
    eligible_for_strict_evaluation: bool
    conditions: List[RedTeamConditionResult] = Field(default_factory=list)


class RedTeamCaseResponse(BaseModel):
    scenario_id: str
    perturbation_type: str
    difficulty: str
    source_doc_id: str
    original_checksum: str
    perturbed_checksum: str
    detection_status: str
    attribution_valid: bool
    original_mean_combined: float
    perturbed_mean_combined: float
    delta_mean_combined: float
    original_anomaly_count: int
    perturbed_anomaly_count: int
    delta_anomaly_count: int
    original_rule_flag_count: int
    perturbed_rule_flag_count: int
    new_rule_flags: List[Dict[str, Any]] = Field(default_factory=list)
    mean_channel_a_delta: float
    mean_channel_b_delta: float
    max_affected_clause_b_delta: float
    channel_a_only_delta: float
    channel_b_only_delta: float
    dual_channel_combined_delta: float
    affected_clause_ids: List[str]
    oracle_result: RedTeamOracleResponse
    failure_category: Optional[str] = None
    failure_explanation: Optional[str] = None
    execution_time_ms: float
    original_clauses_preview: List[Dict[str, Any]] = Field(default_factory=list)
    perturbed_clauses_preview: List[Dict[str, Any]] = Field(default_factory=list)
