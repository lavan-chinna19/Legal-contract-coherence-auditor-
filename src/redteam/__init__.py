"""
src/redteam/ — LexAudit Self Red-Team Robustness Laboratory & Perturbation Benchmark.
Phase 4D Research Extension Program.
"""
from src.redteam.schema import (
    PerturbationType,
    PerturbationDifficulty,
    DetectionStatus,
    PerturbationScenario,
    OracleCondition,
    OracleValidationResult,
    RedTeamCaseResult,
    RedTeamBatchReport
)
from src.redteam.transformations import (
    apply_clause_displacement,
    apply_clause_swap,
    apply_exact_duplication,
    apply_near_duplication,
    apply_broken_reference,
    apply_missing_exhibit,
    apply_date_inversion,
    apply_clause_deletion,
    apply_negative_control,
    apply_combined_perturbation
)
from src.redteam.oracle import IndependentGroundTruthOracle
from src.redteam.runner import RedTeamExperimentRunner

__all__ = [
    "PerturbationType",
    "PerturbationDifficulty",
    "DetectionStatus",
    "PerturbationScenario",
    "OracleCondition",
    "OracleValidationResult",
    "RedTeamCaseResult",
    "RedTeamBatchReport",
    "apply_clause_displacement",
    "apply_clause_swap",
    "apply_exact_duplication",
    "apply_near_duplication",
    "apply_broken_reference",
    "apply_missing_exhibit",
    "apply_date_inversion",
    "apply_clause_deletion",
    "apply_negative_control",
    "apply_combined_perturbation",
    "IndependentGroundTruthOracle",
    "RedTeamExperimentRunner",
]
