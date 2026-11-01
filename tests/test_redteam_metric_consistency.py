"""
tests/test_redteam_metric_consistency.py
Automated test suite verifying red-team metric consistency, denominator calculation,
score orientations, and production detection predicate integrity for Phase 4D-A.
"""
import pytest
import csv
import json
from pathlib import Path

from src.config import REPO_ROOT, ClauseRecord
from src.scoring.pipeline import DualChannelScorer
from src.scoring.severity import SeverityRanker, compute_cross_channel_agreement
from src.redteam.fixtures import get_synthetic_msa_clauses, get_synthetic_sla_clauses
from src.redteam.scenarios import get_canonical_benchmark_scenarios
from src.redteam.runner import RedTeamExperimentRunner
from scripts.audit_phase4d_metrics import audit_metrics_consistency, compute_wilson_score_interval


def test_metric_consistency_audit_passes():
    """Verify that all 8 automated consistency checks pass on stored experiment data."""
    case_path = REPO_ROOT / "research" / "redteam_robustness" / "experiment_case_results.csv"
    recalc_path = REPO_ROOT / "design" / "ui_redesign" / "phase_04da" / "structural_detection_recalculation.json"
    
    report = audit_metrics_consistency(case_path, recalc_path)
    assert report["status"] == "AUDIT_PASSED"
    assert report["failed_checks"] == 0
    assert report["total_checks"] == 8


def test_production_detection_predicate_on_fixtures():
    """
    Unit test verifying the actual production detection predicate:
    Clauses are anomalies iff combined >= 0.50 or max(A, B) >= 0.70.
    Sub-threshold scores (< 0.35) must be CLEAN and is_anomaly=False.
    """
    ranker = SeverityRanker(high_threshold=0.65, med_threshold=0.50, low_threshold=0.35)
    
    # 1. Clean synthetic score (~0.34)
    assessment = ranker.assess_clause(channel_a_score=0.0, channel_b_score=0.68, combined_score=0.34)
    assert assessment.severity == "CLEAN"
    assert assessment.is_anomaly is False

    # 2. Medium single-channel anomaly
    assessment_med = ranker.assess_clause(channel_a_score=0.0, channel_b_score=0.72, combined_score=0.36)
    assert assessment_med.severity == "MEDIUM"
    assert assessment_med.is_anomaly is True

    # 3. High concordant anomaly
    assessment_high = ranker.assess_clause(channel_a_score=0.70, channel_b_score=0.70, combined_score=0.70)
    assert assessment_high.severity == "HIGH"
    assert assessment_high.is_anomaly is True


def test_channel_a_strict_permutation_invariance():
    """
    Verifies that Channel A is mathematically invariant under clause permutations.
    For identical clause text, score A(c_i | D) == A(c_i | pi(D)).
    """
    clauses = get_synthetic_msa_clauses()
    scorer = DualChannelScorer()
    
    res_orig = scorer.score_document(clauses)
    orig_a = {c.clause_id: c.channel_a_score for c in res_orig.clauses}
    
    # Permute clauses (reverse order)
    rev_clauses = list(reversed(clauses))
    res_perm = scorer.score_document(rev_clauses)
    perm_a = {c.clause_id: c.channel_a_score for c in res_perm.clauses}
    
    for cid in orig_a:
        assert abs(orig_a[cid] - perm_a[cid]) < 1e-6, f"Channel A not invariant for clause {cid}"


def test_dynamic_denominators_and_eligibility():
    """
    Validates that denominators derive strictly from scenario eligibility,
    without hardcoded magic constants.
    """
    case_path = REPO_ROOT / "research" / "redteam_robustness" / "experiment_case_results.csv"
    with open(case_path, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    
    # Derive structural denominator dynamically
    struct_rows = [r for r in rows if r["perturbation_type"] in ("P1_DISPLACEMENT", "P2_SWAP")]
    assert len(struct_rows) == 6
    
    # Derive reference denominator dynamically
    ref_rows = [r for r in rows if r["perturbation_type"] in ("P5_BROKEN_REFERENCE", "P6_MISSING_EXHIBIT")]
    assert len(ref_rows) == 3
    
    # Derive date denominator dynamically
    date_rows = [r for r in rows if r["perturbation_type"] == "P7_DATE_INVERSION"]
    assert len(date_rows) == 2


def test_negative_controls_have_zero_baseline_findings():
    """
    Validates that clean negative control documents have zero baseline anomalies
    and zero rule flags prior to transformation.
    """
    msa = get_synthetic_msa_clauses()
    sla = get_synthetic_sla_clauses()
    scorer = DualChannelScorer()
    
    res_msa = scorer.score_document(msa)
    assert res_msa.anomaly_count == 0
    assert all(not c.is_anomaly for c in res_msa.clauses)
    
    res_sla = scorer.score_document(sla)
    assert res_sla.anomaly_count == 0
    assert all(not c.is_anomaly for c in res_sla.clauses)


def test_wilson_confidence_interval_bounds():
    """
    Regression test verifying exact two-sided Wilson 95% confidence intervals
    for structural recall and rule-based benchmark detectors:
    - 0/5 strictly eligible structural cases: [0.0000, 0.4345]
    - 0/6 original structural transformations: [0.0000, 0.3903]
    - 3/3 broken reference detections: [0.4385, 1.0000]
    - 2/2 date chronology detections: [0.3424, 1.0000]
    Also validates that the upper bound decreases monotonically as sample size increases from 5 to 6.
    """
    # 0/5 strictly eligible structural recall: [0.0000, 0.4345]
    low_5, high_5 = compute_wilson_score_interval(0, 5)
    assert low_5 == 0.0
    assert abs(high_5 - 0.4345) < 1e-4

    # 0/6 broad structural recall: [0.0000, 0.3903]
    low_6, high_6 = compute_wilson_score_interval(0, 6)
    assert low_6 == 0.0
    assert abs(high_6 - 0.3903) < 1e-4

    # Monotonicity with sample size (larger n contracts the null upper bound)
    assert high_5 > high_6

    # 3/3 reference rule detections: [0.4385, 1.0000]
    low_ref, high_ref = compute_wilson_score_interval(3, 3)
    assert abs(low_ref - 0.4385) < 1e-4
    assert high_ref == 1.0

    # 2/2 date rule detections: [0.3424, 1.0000]
    low_date, high_date = compute_wilson_score_interval(2, 2)
    assert abs(low_date - 0.3424) < 1e-4
    assert high_date == 1.0


def test_per_clause_detection_aggregation_on_all_structural_cases():
    """
    Regression test verifying that structural anomaly conclusions use actual
    per-clause production decisions, not document-level mean scores or heuristics.
    For each of the six original P1/P2 cases:
    - Verifies maximum combined score before and after (all <= 0.3449, well below 0.35 LOW tier)
    - Verifies maximum Channel A score before and after (all 0.0000)
    - Verifies maximum Channel B score before and after (all <= 0.6898, below 0.70 threshold)
    - Verifies severity classifications (100% CLEAN before and after across all 66 clauses)
    - Verifies is_anomaly flags (100% False before and after across all 66 clauses)
    - Verifies document-level anomaly count is 0 before and after
    - Verifies that production detection recall is 0/6 across all structural transformations
      and 0/5 across strictly eligible structural scenarios.
    """
    scorer = DualChannelScorer()
    msa_clauses = get_synthetic_msa_clauses()
    scenarios = get_canonical_benchmark_scenarios()
    runner = RedTeamExperimentRunner()

    structural_ids = [
        "SCEN_P1_01_DISP_DISTANT",
        "SCEN_P1_02_DISP_MODERATE",
        "SCEN_P1_03_DISP_SUBTLE",
        "SCEN_P2_01_SWAP_ADJACENT",
        "SCEN_P2_02_SWAP_DISTANT",
        "SCEN_P2_03_SWAP_SUBTLE"
    ]
    struct_scenarios = [s for s in scenarios if s.scenario_id in structural_ids]
    assert len(struct_scenarios) == 6

    total_clauses_evaluated = 0
    total_anomalies_observed = 0

    for scen in struct_scenarios:
        pert_clauses, _ = runner._apply_transformation(scen, msa_clauses)
        orig_doc_res = scorer.score_document(msa_clauses, doc_id="SYNTH_DOC_01_MSA")
        pert_doc_res = scorer.score_document(pert_clauses, doc_id="SYNTH_DOC_01_MSA")

        assert len(orig_doc_res.clauses) == 11
        assert len(pert_doc_res.clauses) == 11

        # Check maximum scores before and after
        orig_max_c = max(c.combined_score for c in orig_doc_res.clauses)
        pert_max_c = max(c.combined_score for c in pert_doc_res.clauses)
        orig_max_a = max(c.channel_a_score for c in orig_doc_res.clauses)
        pert_max_a = max(c.channel_a_score for c in pert_doc_res.clauses)
        orig_max_b = max(c.channel_b_score for c in orig_doc_res.clauses)
        pert_max_b = max(c.channel_b_score for c in pert_doc_res.clauses)

        assert orig_max_c <= 0.3449 + 1e-4
        assert pert_max_c <= 0.3449 + 1e-4
        assert orig_max_a == 0.0
        assert pert_max_a == 0.0
        assert orig_max_b <= 0.6898 + 1e-4
        assert pert_max_b <= 0.6898 + 1e-4

        # Check per-clause severities and is_anomaly flags
        for c in pert_doc_res.clauses:
            total_clauses_evaluated += 1
            assert c.severity == "CLEAN", f"Clause {c.clause_id} in {scen.scenario_id} had severity {c.severity}"
            assert c.is_anomaly is False, f"Clause {c.clause_id} in {scen.scenario_id} flagged as anomaly"
            if c.is_anomaly:
                total_anomalies_observed += 1

        assert orig_doc_res.anomaly_count == 0
        assert pert_doc_res.anomaly_count == 0

    assert total_clauses_evaluated == 66  # 6 cases * 11 clauses
    assert total_anomalies_observed == 0

