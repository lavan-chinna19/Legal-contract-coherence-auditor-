"""
tests/test_conformal.py — Unit and integration tests for Conformal Calibration (Prompt 9).

Validates Acceptance Gates:
1. Calibration set is provably synthetic-only (assert_is_synthetic_only).
2. Empirical coverage is computed and reported against target coverage level with delta.
3. calibration_source == 'synthetic_shuffle_only' is present on every scoring result.
"""
import pytest
import numpy as np
from pathlib import Path
from unittest.mock import MagicMock

from src.config import ClauseRecord
from src.calibration.synthetic_generator import (
    SyntheticCalibrationItem,
    SyntheticShuffleDatasetGenerator,
    assert_is_synthetic_only
)
from src.calibration.conformal import ConformalCalibrator, ConformalInterval
from src.scoring.schema import (
    ClauseScoringResult,
    DocumentScoringResult,
    ChannelAEvidence,
    ChannelBEvidence
)
from src.scoring.ensemble import (
    EnsembleClauseResult,
    EnsembleDocumentResult,
    ChannelBEnsembler
)
from src.scoring.pipeline import DualChannelScorer


@pytest.fixture
def mock_clauses():
    return [
        ClauseRecord(
            clause_id="c0",
            doc_id="doc1",
            text="Section 1. Definitions.",
            label="Definitions",
            sequence_idx=0,
            char_start=0,
            char_end=23,
            source="synthetic"
        ),
        ClauseRecord(
            clause_id="c1",
            doc_id="doc1",
            text="Section 2. Confidentiality.",
            label="Confidentiality",
            sequence_idx=1,
            char_start=24,
            char_end=51,
            source="synthetic"
        ),
        ClauseRecord(
            clause_id="c2",
            doc_id="doc1",
            text="Section 3. Governing Law.",
            label="Governing Law",
            sequence_idx=2,
            char_start=52,
            char_end=77,
            source="synthetic"
        ),
        ClauseRecord(
            clause_id="c3",
            doc_id="doc1",
            text="Section 4. Termination.",
            label="Termination",
            sequence_idx=3,
            char_start=78,
            char_end=101,
            source="synthetic"
        )
    ]


# =========================================================================
# Acceptance Gate 1: Provably Synthetic-Only Calibration Dataset
# =========================================================================

def test_acceptance_gate_1_synthetic_only_assertion(mock_clauses):
    """
    Asserts that calibration datasets generated via shuffle tests pass
    synthetic provenance verification, and that any non-synthetic data is rejected.
    """
    gen = SyntheticShuffleDatasetGenerator(seed=42)
    doc_sources = [("doc1", mock_clauses), ("doc2", mock_clauses)]
    cal_set, test_set = gen.generate_calibration_and_test_splits(doc_sources, cal_fraction=0.5)

    assert len(cal_set) > 0
    assert len(test_set) > 0

    # Must pass synthetic validation
    assert assert_is_synthetic_only(cal_set) is True
    assert assert_is_synthetic_only(test_set) is True

    # Every item must have synthetic flag and synthetic source prefix
    for item in cal_set:
        assert item.is_synthetic is True
        assert item.source.startswith("synthetic")
        for c in item.clauses:
            assert c.source.startswith("synthetic")


def test_acceptance_gate_1_rejects_non_synthetic_data(mock_clauses):
    """
    Asserts that assert_is_synthetic_only raises AssertionError if real/external labels are introduced.
    """
    # 1. Non-synthetic source on item
    with pytest.raises(ValueError):
        SyntheticCalibrationItem(
            item_id="invalid_1",
            doc_id="doc_x",
            clauses=mock_clauses,
            manipulation_type="clean",
            ground_truth_anomaly=[0.0] * 4,
            perturbed_indices=[],
            source="production_human_dispute_label",
            is_synthetic=False
        )

    # 2. Non-synthetic clause inside item
    tainted_clauses = list(mock_clauses)
    tainted_clauses[0] = ClauseRecord(
        clause_id="tainted_0",
        doc_id="doc_x",
        text="Tainted clause",
        label="Unknown",
        sequence_idx=0,
        char_start=0,
        char_end=14,
        source="real_human_annotation"
    )

    tainted_item = SyntheticCalibrationItem(
        item_id="tainted_item",
        doc_id="doc_x",
        clauses=tainted_clauses,
        manipulation_type="clean",
        ground_truth_anomaly=[0.0] * 4,
        perturbed_indices=[],
        source="synthetic_clean",
        is_synthetic=True
    )

    with pytest.raises(AssertionError, match="invalid source 'real_human_annotation'"):
        assert_is_synthetic_only([tainted_item])


# =========================================================================
# Acceptance Gate 2: Empirical Coverage vs Target Coverage
# =========================================================================

def test_acceptance_gate_2_empirical_coverage():
    """
    Validates that ConformalCalibrator produces valid intervals,
    computes empirical coverage on held-out data, and reports the delta.
    """
    rng = np.random.RandomState(42)
    
    # Simulate calibration set (synthetic shuffle test residuals)
    n_cal = 200
    y_true_cal = rng.choice([0.0, 1.0], size=n_cal, p=[0.5, 0.5])
    # Predictions with noise
    y_pred_cal = np.clip(y_true_cal + rng.normal(0.0, 0.15, size=n_cal), 0.0, 1.0)

    calibrator = ConformalCalibrator(target_coverage=0.90)
    calibrator.fit(y_true_cal, y_pred_cal, calibration_source="synthetic_shuffle_only")

    assert calibrator.is_fitted
    assert calibrator.n_calibration_samples == n_cal

    # Simulate held-out synthetic test set
    n_test = 200
    y_true_test = rng.choice([0.0, 1.0], size=n_test, p=[0.5, 0.5])
    y_pred_test = np.clip(y_true_test + rng.normal(0.0, 0.15, size=n_test), 0.0, 1.0)

    eval_results = calibrator.evaluate_coverage(y_true_test, y_pred_test, confidence_level=0.90)

    assert eval_results["target_coverage"] == 0.90
    assert 0.0 <= eval_results["empirical_coverage"] <= 1.0
    # On exchangeable synthetic data, coverage should be close to 0.90 (within statistical tolerance)
    assert abs(eval_results["coverage_delta"]) < 0.10
    assert eval_results["calibration_source"] == "synthetic_shuffle_only"

    # Verify interval bounds
    intervals = calibrator.predict_interval(y_pred_test[:10])
    for low, high in intervals:
        assert 0.0 <= low <= high <= 1.0


# =========================================================================
# Acceptance Gate 3: calibration_source Field Presence & Check
# =========================================================================

def test_acceptance_gate_3_calibration_source_on_schemas():
    """
    Asserts that calibration_source == 'synthetic_shuffle_only' is present on all
    scoring schemas across clause-level and document-level results.
    """
    # 1. ClauseScoringResult
    ev_a = ChannelAEvidence("type_Def", 0.1, False, {})
    ev_b = ChannelBEvidence(incoming_prob=0.9, outgoing_prob=0.8)
    clause_res = ClauseScoringResult(
        clause_id="c0",
        doc_id="d1",
        sequence_idx=0,
        text_preview="Preview text...",
        channel_a_score=0.1,
        channel_b_score=0.2,
        combined_score=0.15,
        channel_a_evidence=ev_a,
        channel_b_evidence=ev_b,
        is_anomaly=False,
        severity="CLEAN",
        confidence_interval=(0.05, 0.25)
    )
    assert clause_res.calibration_source == "synthetic_shuffle_only"
    assert clause_res.confidence_interval == (0.05, 0.25)
    d_dict = clause_res.to_dict()
    assert d_dict["calibration_source"] == "synthetic_shuffle_only"

    # 2. DocumentScoringResult
    doc_res = DocumentScoringResult(
        doc_id="d1",
        total_clauses=1,
        anomaly_count=0,
        high_severity_count=0,
        medium_severity_count=0,
        mean_combined_score=0.15,
        max_combined_score=0.15,
        clauses=[clause_res]
    )
    assert doc_res.calibration_source == "synthetic_shuffle_only"
    doc_dict = doc_res.to_dict()
    assert doc_dict["calibration_source"] == "synthetic_shuffle_only"

    # 3. EnsembleClauseResult & EnsembleDocumentResult
    ens_clause = EnsembleClauseResult(
        clause_id="c0",
        sequence_idx=0,
        fine_tuned_score=0.1,
        zero_shot_score=0.2,
        combined_score=0.15,
        confidence_interval=(0.05, 0.25)
    )
    assert ens_clause.calibration_source == "synthetic_shuffle_only"

    ens_doc = EnsembleDocumentResult(
        doc_id="d1",
        ensemble_mode="combined",
        ensemble_weight=0.5,
        clauses=[ens_clause]
    )
    assert ens_doc.calibration_source == "synthetic_shuffle_only"


def test_pipeline_integration_with_calibrator(mock_clauses):
    """
    Tests DualChannelScorer with an attached ConformalCalibrator.
    """
    calibrator = ConformalCalibrator(target_coverage=0.90)
    # Fit calibrator on synthetic data
    calibrator.fit([0.0, 1.0, 0.0, 1.0], [0.1, 0.9, 0.2, 0.8], calibration_source="synthetic_shuffle_only")

    mock_a = MagicMock()
    mock_a.score_clauses.return_value = [
        (0.1, ChannelAEvidence("type_Def", 0.1, False, {})),
        (0.2, ChannelAEvidence("type_Conf", 0.2, False, {})),
        (0.3, ChannelAEvidence("type_Law", 0.3, False, {})),
        (0.4, ChannelAEvidence("type_Term", 0.4, False, {}))
    ]

    mock_b = MagicMock()
    mock_b.score_document_clauses.return_value = [
        (0.1, ChannelBEvidence()),
        (0.2, ChannelBEvidence()),
        (0.3, ChannelBEvidence()),
        (0.4, ChannelBEvidence())
    ]

    pipeline = DualChannelScorer(
        channel_a=mock_a,
        channel_b=mock_b,
        calibrator=calibrator
    )

    doc_result = pipeline.score_document(mock_clauses, doc_id="test_doc")
    assert doc_result.calibration_source == "synthetic_shuffle_only"

    for c in doc_result.clauses:
        assert c.calibration_source == "synthetic_shuffle_only"
        assert c.confidence_interval is not None
        low, high = c.confidence_interval
        assert 0.0 <= low <= c.combined_score <= high <= 1.0


def test_calibrator_serialization(tmp_path):
    """
    Tests saving and loading calibration state to/from JSON fixture.
    """
    fixture_path = tmp_path / "test_conformal_fixture.json"
    calibrator = ConformalCalibrator(target_coverage=0.90)
    calibrator.fit([0.0, 1.0, 0.0, 1.0], [0.1, 0.85, 0.15, 0.9], calibration_source="synthetic_shuffle_only")

    calibrator.save_state(fixture_path)
    assert fixture_path.exists()

    loaded = ConformalCalibrator()
    loaded.load_state(fixture_path)

    assert loaded.is_fitted
    assert loaded.target_coverage == 0.90
    assert loaded.calibration_source == "synthetic_shuffle_only"

    int1 = calibrator.predict_interval(0.5)
    int2 = loaded.predict_interval(0.5)
    assert int1 == int2
