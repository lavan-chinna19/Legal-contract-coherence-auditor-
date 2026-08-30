"""
tests/test_scoring.py — Unit tests for Channel A, Channel B, Dual-Channel Pipeline, and Diagnostics.
"""
import pytest
import numpy as np
from unittest.mock import patch, MagicMock

from src.config import ClauseRecord
from src.scoring.schema import (
    ChannelAEvidence,
    ChannelBEvidence,
    ClauseScoringResult,
    DocumentScoringResult
)
from src.scoring.channel_a import ChannelAScorer
from src.scoring.channel_b import ChannelBScorer
from src.scoring.pipeline import DualChannelScorer
from src.scoring.diagnostics import format_diagnostics_report


@pytest.fixture
def sample_clauses():
    return [
        ClauseRecord(
            clause_id="doc1_0",
            doc_id="doc1",
            text="Section 1.01. Definitions. Capitalized terms shall have the meanings set forth herein.",
            label="Definitions",
            sequence_idx=0,
            char_start=0,
            char_end=85,
            source="test"
        ),
        ClauseRecord(
            clause_id="doc1_1",
            doc_id="doc1",
            text="Section 1.02. Payment. The buyer shall wire funds within 30 days of closing date.",
            label="Payment",
            sequence_idx=1,
            char_start=86,
            char_end=170,
            source="test"
        ),
        ClauseRecord(
            clause_id="doc1_2",
            doc_id="doc1",
            text="Section 1.03. Governing Law. This agreement is governed by the laws of Delaware.",
            label="Governing Law",
            sequence_idx=2,
            char_start=171,
            char_end=250,
            source="test"
        )
    ]


def test_channel_a_scoring(sample_clauses, tmp_path):
    # Create synthetic centroids
    centroids_file = tmp_path / "test_centroids.npz"
    c_def = np.ones(64, dtype=np.float32)
    c_def /= np.linalg.norm(c_def)
    c_pay = np.zeros(64, dtype=np.float32)
    c_pay[0] = 1.0
    np.savez(centroids_file, type_Definitions=c_def, type_Payment=c_pay)

    mock_embedder = MagicMock()
    # Return embedding aligned with Definitions for clause 0
    e0 = c_def.copy()
    e1 = c_pay.copy()
    e2 = np.zeros(64, dtype=np.float32)
    e2[10] = 1.0  # Orthogonal to both -> OOD
    mock_embedder.embed_clauses.return_value = ([], np.vstack([e0, e1, e2]))

    scorer = ChannelAScorer(centroids_path=centroids_file, embedder=mock_embedder)
    results = scorer.score_clauses(sample_clauses)

    assert len(results) == 3
    # Clause 0 should be close to Definitions
    score0, ev0 = results[0]
    assert ev0.nearest_centroid_label == "type_Definitions"
    assert ev0.centroid_distance < 0.05
    assert not ev0.is_ood

    # Clause 2 should be far (OOD)
    score2, ev2 = results[2]
    assert ev2.centroid_distance > 0.5
    assert ev2.is_ood


def test_channel_b_scoring(sample_clauses):
    mock_model = MagicMock()
    # Transition (c0 -> c1) is coherent (prob 0.9), (c1 -> c2) is incoherent (prob 0.1)
    mock_model.score_pairs.return_value = [0.90, 0.10]

    scorer = ChannelBScorer(coherence_model=mock_model)
    results = scorer.score_document_clauses(sample_clauses)

    assert len(results) == 3
    # c0: outgoing anomaly = 1 - 0.9 = 0.10
    score0, ev0 = results[0]
    assert ev0.incoming_prob is None
    assert ev0.outgoing_prob == 0.90
    assert abs(score0 - 0.10) < 1e-3

    # c1: incoming = 0.90 (anom 0.10), outgoing = 0.10 (anom 0.90) -> max is 0.90
    score1, ev1 = results[1]
    assert ev1.incoming_prob == 0.90
    assert ev1.outgoing_prob == 0.10
    assert abs(score1 - 0.90) < 1e-3

    # c2: incoming = 0.10 (anom 0.90) -> score is 0.90
    score2, ev2 = results[2]
    assert ev2.incoming_prob == 0.10
    assert ev2.outgoing_prob is None
    assert abs(score2 - 0.90) < 1e-3


def test_dual_channel_pipeline_and_diagnostics(sample_clauses, tmp_path):
    mock_a = MagicMock()
    mock_a.score_clauses.return_value = [
        (0.1, ChannelAEvidence("type_Def", 0.1, False, {"type_Def": 0.1})),
        (0.2, ChannelAEvidence("type_Pay", 0.2, False, {"type_Pay": 0.2})),
        (0.8, ChannelAEvidence("type_Law", 0.8, True, {"type_Law": 0.8}))
    ]

    mock_b = MagicMock()
    mock_b.score_document_clauses.return_value = [
        (0.1, ChannelBEvidence(incoming_prob=None, outgoing_prob=0.9)),
        (0.9, ChannelBEvidence(incoming_prob=0.9, outgoing_prob=0.1)),
        (0.9, ChannelBEvidence(incoming_prob=0.1, outgoing_prob=None))
    ]

    pipeline = DualChannelScorer(
        channel_a=mock_a,
        channel_b=mock_b,
        alpha=0.5,
        high_threshold=0.75,
        med_threshold=0.50
    )

    doc_result = pipeline.score_document(sample_clauses, doc_id="doc1")

    assert doc_result.doc_id == "doc1"
    assert doc_result.total_clauses == 3
    # Clause 0: 0.5*0.1 + 0.5*0.1 = 0.10 (CLEAN)
    # Clause 1: 0.5*0.2 + 0.5*0.9 = 0.55 (MEDIUM)
    # Clause 2: 0.5*0.8 + 0.5*0.9 = 0.85 (HIGH)
    assert doc_result.clauses[0].severity == "CLEAN"
    assert doc_result.clauses[1].severity == "MEDIUM"
    assert doc_result.clauses[2].severity == "HIGH"
    assert doc_result.anomaly_count == 2
    assert doc_result.high_severity_count == 1
    assert doc_result.medium_severity_count == 1

    # Diagnostics generation test
    report_md = format_diagnostics_report(doc_result, format_type="markdown")
    assert "Contract Anomaly Audit Report: `doc1`" in report_md
    assert "High Severity Anomalies" in report_md
    assert "HIGH" in report_md

    report_json = format_diagnostics_report(doc_result, format_type="json")
    assert '"doc_id": "doc1"' in report_json
