"""
tests/test_redteam_oracle.py — Unit tests for the independent ground-truth oracle.
Verifies that the oracle checks semantic conditions strictly without invoking target detectors.
"""
import pytest
from src.redteam.fixtures import get_synthetic_msa_clauses
from src.redteam.schema import (
    PerturbationType,
    PerturbationDifficulty,
    PerturbationScenario
)
from src.redteam.transformations import (
    apply_clause_displacement,
    apply_clause_swap,
    apply_exact_duplication,
    apply_broken_reference,
    apply_missing_exhibit,
    apply_date_inversion,
    apply_clause_deletion,
    apply_negative_control
)
from src.redteam.oracle import IndependentGroundTruthOracle


def test_oracle_validates_displacement():
    oracle = IndependentGroundTruthOracle()
    orig = get_synthetic_msa_clauses()
    pert, meta = apply_clause_displacement(orig, source_slot=1, target_slot=8)

    scen = PerturbationScenario(
        scenario_id="SCEN_DISP_TEST",
        perturbation_type=PerturbationType.P1_DISPLACEMENT,
        difficulty=PerturbationDifficulty.LEVEL_1_STRAIGHTFORWARD,
        source_doc_id="SYNTH_DOC_01_MSA",
        title="Displacement Test",
        description="Test",
        target_clause_ids=["SYNTH_DOC_01_MSA_c01"],
        parameters={"source_slot": 1, "target_slot": 8},
        expected_detector="CHANNEL_B_DISCOURSE_MODEL"
    )

    res = oracle.validate_scenario(scen, orig, pert, meta)
    assert res.valid_transformation is True
    assert res.oracle_condition == "SYNTHETIC_DISPLACEMENT"
    assert res.eligible_for_strict_evaluation is True
    assert all(c.is_satisfied for c in res.conditions)


def test_oracle_validates_broken_reference():
    oracle = IndependentGroundTruthOracle()
    orig = get_synthetic_msa_clauses()
    target_id = "SYNTH_DOC_01_MSA_c03"
    pert, meta = apply_broken_reference(orig, target_clause_id=target_id, old_target_sec="2", new_nonexistent_sec="Section 99")

    scen = PerturbationScenario(
        scenario_id="SCEN_REF_TEST",
        perturbation_type=PerturbationType.P5_BROKEN_REFERENCE,
        difficulty=PerturbationDifficulty.LEVEL_1_STRAIGHTFORWARD,
        source_doc_id="SYNTH_DOC_01_MSA",
        title="Reference Test",
        description="Test",
        target_clause_ids=[target_id],
        parameters={"old_target_sec": "2", "new_nonexistent_sec": "Section 99"},
        expected_detector="CROSS_REFERENCE_CHECKER"
    )

    res = oracle.validate_scenario(scen, orig, pert, meta)
    assert res.valid_transformation is True
    assert res.oracle_condition == "DANGLING_INTERNAL_REFERENCE"
    assert res.eligible_for_strict_evaluation is True


def test_oracle_validates_exact_duplication_descriptive_only():
    oracle = IndependentGroundTruthOracle()
    orig = get_synthetic_msa_clauses()
    pert, meta = apply_exact_duplication(orig, source_slot=4, insert_slot=8)

    scen = PerturbationScenario(
        scenario_id="SCEN_DUP_TEST",
        perturbation_type=PerturbationType.P3_EXACT_DUPLICATION,
        difficulty=PerturbationDifficulty.LEVEL_2_MODERATE,
        source_doc_id="SYNTH_DOC_01_MSA",
        title="Duplication Test",
        description="Test",
        target_clause_ids=["SYNTH_DOC_01_MSA_c04"],
        parameters={"source_slot": 4, "insert_slot": 8},
        expected_detector="NONE"
    )

    res = oracle.validate_scenario(scen, orig, pert, meta)
    assert res.valid_transformation is True
    assert res.oracle_condition == "EXACT_DUPLICATION"
    # Strict evaluation must be false because LexAudit lacks a dedicated duplicate detector
    assert res.eligible_for_strict_evaluation is False
    assert res.ground_truth_supported is False


def test_oracle_validates_negative_control():
    oracle = IndependentGroundTruthOracle()
    orig = get_synthetic_msa_clauses()
    pert, meta = apply_negative_control(orig)

    scen = PerturbationScenario(
        scenario_id="SCEN_CONTROL_TEST",
        perturbation_type=PerturbationType.P9_NEGATIVE_CONTROL,
        difficulty=PerturbationDifficulty.LEVEL_1_STRAIGHTFORWARD,
        source_doc_id="SYNTH_DOC_01_MSA",
        title="Control Test",
        description="Test",
        target_clause_ids=[],
        parameters={},
        expected_detector="NONE"
    )

    res = oracle.validate_scenario(scen, orig, pert, meta)
    assert res.valid_transformation is True
    assert res.oracle_condition == "CLEAN_NEGATIVE_CONTROL"
    assert res.eligible_for_strict_evaluation is True
