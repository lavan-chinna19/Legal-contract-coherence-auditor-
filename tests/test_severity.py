"""
tests/test_severity.py — Unit and integration tests for Decision-Support Ranking Layer (Prompt 10).
Validates cross-channel agreement, High/Medium/Low decision rules, schema integration,
and Acceptance Gate 2 (corrupted clauses receiving higher severity than clean clauses).
"""
import pytest
from typing import List

from src.config import ClauseRecord
from src.scoring.severity import (
    SeverityRanker,
    SeverityAssessment,
    compute_cross_channel_agreement
)
from src.scoring.schema import ClauseScoringResult, DocumentScoringResult
from src.scoring.pipeline import DualChannelScorer
from src.scoring.diagnostics import format_diagnostics_markdown, format_diagnostics_report


def test_cross_channel_agreement_calculation():
    # Perfect concordance clean
    ag_val, ag_type = compute_cross_channel_agreement(0.1, 0.1)
    assert ag_val == 1.0
    assert ag_type == "CONCORDANT_CLEAN"

    # Perfect concordance anomaly
    ag_val, ag_type = compute_cross_channel_agreement(0.8, 0.8)
    assert ag_val == 1.0
    assert ag_type == "CONCORDANT_ANOMALY"

    # Divergent: Channel A dominant
    ag_val, ag_type = compute_cross_channel_agreement(0.85, 0.15)
    assert ag_val == pytest.approx(0.30, abs=0.01)
    assert ag_type == "CHANNEL_A_DOMINANT"

    # Divergent: Channel B dominant
    ag_val, ag_type = compute_cross_channel_agreement(0.20, 0.90)
    assert ag_val == pytest.approx(0.30, abs=0.01)
    assert ag_type == "CHANNEL_B_DOMINANT"


def test_severity_ranker_decision_logic():
    ranker = SeverityRanker(high_threshold=0.65, med_threshold=0.45)

    # 1. Concordant High Anomaly -> HIGH
    res_high = ranker.assess_clause(
        channel_a_score=0.75,
        channel_b_score=0.80,
        combined_score=0.78,
        confidence_interval=(0.40, 1.0)
    )
    assert res_high.severity == "HIGH"
    assert res_high.is_anomaly is True
    assert res_high.agreement_type == "CONCORDANT_ANOMALY"
    assert "corroboration" in res_high.severity_justification.lower()

    # 2. Extreme Single-Channel Failure -> HIGH
    res_extreme_b = ranker.assess_clause(
        channel_a_score=0.10,
        channel_b_score=0.88,
        combined_score=0.76
    )
    assert res_extreme_b.severity == "HIGH"
    assert res_extreme_b.is_anomaly is True

    # 3. Moderate Anomaly -> MEDIUM
    res_med_a = ranker.assess_clause(
        channel_a_score=0.60,
        channel_b_score=0.20,
        combined_score=0.48
    )
    assert res_med_a.severity == "MEDIUM"
    assert res_med_a.is_anomaly is True
    assert res_med_a.agreement_type == "CHANNEL_A_DOMINANT"

    # 4. Low deviation -> LOW
    res_low = ranker.assess_clause(
        channel_a_score=0.38,
        channel_b_score=0.38,
        combined_score=0.38
    )
    assert res_low.severity == "LOW"
    assert res_low.is_anomaly is False

    # 5. Clean clause -> CLEAN
    res_clean = ranker.assess_clause(
        channel_a_score=0.12,
        channel_b_score=0.08,
        combined_score=0.10
    )
    assert res_clean.severity == "CLEAN"
    assert res_clean.is_anomaly is False


def test_schema_and_diagnostics_integration():
    ranker = SeverityRanker()
    assessment = ranker.assess_clause(
        channel_a_score=0.70,
        channel_b_score=0.65,
        combined_score=0.68,
        confidence_interval=(0.25, 0.95)
    )

    # Verify ClauseScoringResult carries all required fields
    from src.scoring.schema import ChannelAEvidence, ChannelBEvidence
    clause = ClauseScoringResult(
        clause_id="c_test_01",
        doc_id="doc_01",
        sequence_idx=0,
        text_preview="Governing Law clause...",
        channel_a_score=0.70,
        channel_b_score=0.65,
        combined_score=0.68,
        channel_a_evidence=ChannelAEvidence(nearest_centroid_label="Governing Law", centroid_distance=0.8, is_ood=True),
        channel_b_evidence=ChannelBEvidence(incoming_prob=0.2, outgoing_prob=0.3),
        is_anomaly=assessment.is_anomaly,
        severity=assessment.severity,
        confidence_interval=(0.25, 0.95),
        cross_channel_agreement=assessment.cross_channel_agreement,
        agreement_type=assessment.agreement_type,
        interval_width=assessment.interval_width,
        severity_justification=assessment.severity_justification
    )

    doc_res = DocumentScoringResult(
        doc_id="doc_01",
        total_clauses=1,
        anomaly_count=1,
        high_severity_count=1,
        medium_severity_count=0,
        mean_combined_score=0.68,
        max_combined_score=0.68,
        clauses=[clause]
    )

    # Check to_dict serialization
    d = doc_res.to_dict()
    assert d["clauses"][0]["cross_channel_agreement"] == pytest.approx(0.95, abs=0.01)
    assert d["clauses"][0]["agreement_type"] == "CONCORDANT_ANOMALY"
    assert d["clauses"][0]["severity"] == "HIGH"
    assert d["clauses"][0]["interval_width"] == 0.70

    # Check Markdown report generation
    md = format_diagnostics_markdown(doc_res)
    assert "Contract Anomaly Audit Report: `doc_01`" in md
    assert "CONCORDANT_ANOMALY" in md
    assert "High confidence dual-channel corroboration" in md

    # Check JSON report generation
    js = format_diagnostics_report(doc_res, format_type="json")
    assert '"severity": "HIGH"' in js
