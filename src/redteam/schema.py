"""
src/redteam/schema.py — Data schemas and domain models for the Red-Team Laboratory.
"""
from enum import Enum
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from pydantic import BaseModel, Field


class PerturbationType(str, Enum):
    P1_DISPLACEMENT = "P1_DISPLACEMENT"
    P2_SWAP = "P2_SWAP"
    P3_EXACT_DUPLICATION = "P3_EXACT_DUPLICATION"
    P4_NEAR_DUPLICATION = "P4_NEAR_DUPLICATION"
    P5_BROKEN_REFERENCE = "P5_BROKEN_REFERENCE"
    P6_MISSING_EXHIBIT = "P6_MISSING_EXHIBIT"
    P7_DATE_INVERSION = "P7_DATE_INVERSION"
    P8_DELETION = "P8_DELETION"
    P9_NEGATIVE_CONTROL = "P9_NEGATIVE_CONTROL"
    P10_COMBINED = "P10_COMBINED"


class PerturbationDifficulty(str, Enum):
    LEVEL_1_STRAIGHTFORWARD = "LEVEL_1_STRAIGHTFORWARD"
    LEVEL_2_MODERATE = "LEVEL_2_MODERATE"
    LEVEL_3_DIFFICULT = "LEVEL_3_DIFFICULT"


class DetectionStatus(str, Enum):
    DETECTED = "DETECTED"
    NOT_DETECTED = "NOT_DETECTED"
    INCONCLUSIVE = "INCONCLUSIVE"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    INVALID_SCENARIO = "INVALID_SCENARIO"
    EXPERIMENT_FAILED = "EXPERIMENT_FAILED"


@dataclass
class OracleCondition:
    condition_name: str
    target_property: str
    expected_value: Any
    observed_value: Any
    is_satisfied: bool
    description: str


@dataclass
class OracleValidationResult:
    scenario_id: str
    valid_transformation: bool
    oracle_condition: str
    expected_detector: str
    ground_truth_supported: bool
    ground_truth_reason: str
    affected_clause_ids: List[str]
    eligible_for_strict_evaluation: bool
    conditions: List[OracleCondition] = field(default_factory=list)


@dataclass
class PerturbationScenario:
    scenario_id: str
    perturbation_type: PerturbationType
    difficulty: PerturbationDifficulty
    source_doc_id: str
    title: str
    description: str
    target_clause_ids: List[str]
    parameters: Dict[str, Any]
    expected_detector: str
    seed: int = 42
    reversibility_status: str = "REVERSIBLE"
    ground_truth_confidence: float = 1.0
    limitations: str = ""


@dataclass
class ChannelAblationScores:
    channel_a_only_anomaly_delta: float
    channel_b_only_anomaly_delta: float
    dual_channel_combined_delta: float
    rule_checker_flags_count: int
    integrated_pipeline_flags_count: int


@dataclass
class RedTeamCaseResult:
    scenario_id: str
    perturbation_type: PerturbationType
    difficulty: PerturbationDifficulty
    source_doc_id: str
    original_checksum: str
    perturbed_checksum: str
    oracle_result: OracleValidationResult
    detection_status: DetectionStatus
    attribution_valid: bool

    # Quantitative score deltas (original vs perturbed)
    original_mean_combined: float
    perturbed_mean_combined: float
    delta_mean_combined: float

    original_anomaly_count: int
    perturbed_anomaly_count: int
    delta_anomaly_count: int

    original_rule_flag_count: int
    perturbed_rule_flag_count: int
    new_rule_flags: List[Dict[str, Any]]

    # Specific Channel responses
    mean_channel_a_delta: float
    mean_channel_b_delta: float
    max_affected_clause_b_delta: float

    # Ablation metrics
    ablations: ChannelAblationScores

    # Evidence & failure diagnosis
    affected_clause_ids: List[str]
    failure_category: Optional[str] = None
    failure_explanation: Optional[str] = None
    execution_time_ms: float = 0.0


@dataclass
class RedTeamBatchReport:
    timestamp: str
    total_scenarios_attempted: int
    valid_transformations_count: int
    invalid_transformations_count: int
    strict_evaluation_eligible_count: int

    # Metric family summaries
    structural_scenarios_evaluated: int
    structural_detection_rate: float
    mean_structural_channel_b_delta: float

    rule_scenarios_evaluated: int
    rule_true_positives: int
    rule_false_negatives: int
    rule_false_positives: int
    rule_true_negatives: int
    rule_precision: float
    rule_recall: float
    rule_f1: float

    duplicate_scenarios_evaluated: int
    duplicate_detector_available: bool
    mean_duplicate_channel_b_delta: float

    deletion_scenarios_evaluated: int
    deletion_consequence_detection_rate: float

    negative_controls_evaluated: int
    clean_control_false_positive_rate: float
    clean_control_mean_anomaly: float

    combined_scenarios_evaluated: int
    combined_detection_rate: float

    case_results: List[RedTeamCaseResult] = field(default_factory=list)
