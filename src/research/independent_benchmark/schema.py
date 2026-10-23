"""
src/research/independent_benchmark/schema.py
Phase 4D-C — Schema and Data Definitions for Independent Contract Benchmark.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Any


class SplitPartition(str, Enum):
    DEVELOPMENT = "development"
    VALIDATION = "validation"
    SEALED_TEST = "sealed_test"


class TaskCategory(str, Enum):
    TASK_A_DISCOURSE_COHERENCE = "TASK_A_DISCOURSE_COHERENCE"
    TASK_B_STRUCTURAL_DEPENDENCY = "TASK_B_STRUCTURAL_DEPENDENCY"
    TASK_C_CONTENT_LOGIC = "TASK_C_CONTENT_LOGIC"
    TASK_D_CONVENTIONAL_ORGANIZATION = "TASK_D_CONVENTIONAL_ORGANIZATION"
    TASK_E_POSITION_RECOVERY = "TASK_E_POSITION_RECOVERY"


class GroundTruthLabel(str, Enum):
    VERIFIED_DISCOURSE_DEPENDENCY_VIOLATION = "VERIFIED_DISCOURSE_DEPENDENCY_VIOLATION"
    VERIFIED_EXPLICIT_STRUCTURAL_VIOLATION = "VERIFIED_EXPLICIT_STRUCTURAL_VIOLATION"
    VERIFIED_CONTENT_LOGIC_VIOLATION = "VERIFIED_CONTENT_LOGIC_VIOLATION"
    VALID_NONCANONICAL_ORDER = "VALID_NONCANONICAL_ORDER"
    VALID_CANONICAL_ORDER = "VALID_CANONICAL_ORDER"
    SYNTHETIC_REORDERING_ONLY = "SYNTHETIC_REORDERING_ONLY"
    AMBIGUOUS = "AMBIGUOUS"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    INVALID_TRANSFORMATION = "INVALID_TRANSFORMATION"
    ANNOTATION_PENDING = "ANNOTATION_PENDING"


@dataclass
class SourceDocumentRecord:
    parent_document_id: str
    document_family_id: str
    source_uri_or_reference: str
    source_type: str
    contract_type: str
    source_organization: str
    acquisition_date: str
    license_status: str
    raw_sha256: str
    normalized_text_sha256: str
    content_fingerprint: str
    parser_version: str
    clause_segmentation_version: str
    split_assignment: str
    provenance_confidence: str
    clause_count: int = 0
    char_length: int = 0
    file_path: str = ""


@dataclass
class DuplicateAuditRecord:
    doc_id_a: str
    doc_id_b: str
    family_id_a: str
    family_id_b: str
    is_exact_byte_duplicate: bool
    is_normalized_duplicate: bool
    jaccard_similarity: float
    audit_verdict: str  # DISTINCT_INDEPENDENT, NEAR_DUPLICATE_SAME_FAMILY, CROSS_FAMILY_COLLISION
    notes: str = ""


@dataclass
class SplitAssignmentRecord:
    document_family_id: str
    source_organization: str
    split_assignment: SplitPartition
    parent_contract_count: int
    parent_document_ids: List[str] = field(default_factory=list)


@dataclass
class AnnotationRecord:
    case_id: str
    parent_document_id: str
    document_family_id: str
    split: str
    original_source_identity: str
    source_text_hash: str
    perturbed_text_hash: str
    ground_truth_label: GroundTruthLabel
    task_category: TaskCategory
    transformation_type: str
    affected_clause_ids: List[str] = field(default_factory=list)
    supporting_source_spans: List[str] = field(default_factory=list)
    exact_reason_for_label: str = ""
    independently_checkable_condition: str = ""
    labeling_method: str = "DETERMINISTIC_ORACLE_LCC"
    label_author: str = "PHASE_4DC_INDEPENDENT_RESEARCH_TEAM"
    label_confidence: str = "HIGH"
    reviewer_disagreement_status: str = "NO_EXPERT_ADJUDICATION"
    eligible_benchmark_task: str = "STRUCTURAL_ANOMALY_DETECTION"
    eligibility_decision: str = "ELIGIBLE"  # ELIGIBLE or EXCLUDED
    exclusion_reason: Optional[str] = None


@dataclass
class PerturbationRecord:
    case_id: str
    parent_document_id: str
    document_family_id: str
    split: str
    category_code: str  # P1, P2, P3, N1, N2, N3, N4, A1
    transformation_name: str
    is_positive: bool
    is_hard_negative: bool
    is_ambiguous: bool
    source_clause_count: int
    perturbed_clause_count: int
    displaced_clause_indices: List[int]
    target_clause_indices: List[int]
    transformation_valid: bool
    deterministic_seed: int
    description: str


@dataclass
class BenchmarkCase:
    annotation: AnnotationRecord
    perturbation: PerturbationRecord
    original_clauses: List[Any]
    perturbed_clauses: List[Any]


@dataclass
class LatencyBreakdown:
    text_preparation_ms: float = 0.0
    clause_segmentation_ms: float = 0.0
    embedding_computation_ms: float = 0.0
    feature_extraction_ms: float = 0.0
    model_inference_ms: float = 0.0
    decision_calculation_ms: float = 0.0
    total_end_to_end_ms: float = 0.0


@dataclass
class EvaluationPrediction:
    case_id: str
    model_name: str
    model_version: str
    ground_truth_label: GroundTruthLabel
    is_ground_truth_anomaly: bool
    predicted_anomaly: bool
    anomaly_score: float
    threshold_used: float
    predicted_clause_ids: List[str] = field(default_factory=list)
    latency: LatencyBreakdown = field(default_factory=LatencyBreakdown)
    document_family_id: str = ""
    split: str = ""
    task_category: str = ""


@dataclass
class WilsonInterval:
    point_estimate: float
    lower_bound: float
    upper_bound: float
    confidence_level: float = 0.95


@dataclass
class MetricBundle:
    total_cases: int
    tp: int
    fp: int
    fn: int
    tn: int
    precision: float
    recall: float
    specificity: float
    f1: float
    false_positive_rate: float
    balanced_accuracy: float
    recall_ci: WilsonInterval
    precision_ci: WilsonInterval
    specificity_ci: WilsonInterval
    family_count: int = 0
    family_level_results: Dict[str, Dict[str, Any]] = field(default_factory=dict)
