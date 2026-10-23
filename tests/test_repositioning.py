"""
tests/test_repositioning.py — Unit & Numerical Parity Tests for Repositioning Engine.
Phase 4C Research Validation.
"""
import pytest
import numpy as np

from src.config import ClauseRecord
from src.scoring.repositioning import CounterfactualRepositioningEngine, RepositioningResult


def make_mock_clauses(n: int = 5) -> list[ClauseRecord]:
    labels = ["Governing Law", "Severability", "Term", "Confidentiality", "Notices", "Indemnification", "Arbitration"]
    return [
        ClauseRecord(
            clause_id=f"clause_{i:02d}",
            doc_id="test_doc_01",
            sequence_idx=i,
            text=f"Section {i}. This is standard test contract clause {i} concerning {labels[i % len(labels)]}.",
            label=labels[i % len(labels)],
            char_start=i * 100,
            char_end=(i + 1) * 100,
            source="sec_edgar",
            split="test"
        )
        for i in range(n)
    ]


def test_repositioning_engine_single_clause():
    engine = CounterfactualRepositioningEngine()
    clauses = make_mock_clauses(1)
    res = engine.evaluate(clauses, target_clause_id="clause_00")
    assert res.total_clauses == 1
    assert res.is_abstaining is True
    assert res.abstention_reason == "DOCUMENT_TOO_SHORT_FOR_REPOSITIONING"


def test_repositioning_engine_two_clauses():
    engine = CounterfactualRepositioningEngine()
    clauses = make_mock_clauses(2)
    res = engine.evaluate(clauses, target_clause_id="clause_01")
    assert res.total_clauses == 2
    assert len(res.candidates) == 2
    assert res.candidates[0].rank in [1, 2]
    assert res.candidates[1].rank in [1, 2]


def test_repositioning_numerical_parity_all_positions():
    """
    Validates that optimized rescoring yields exact parity with reference full rescoring
    for middle, first, and last clauses. Tolerance <= 1e-4.
    """
    engine = CounterfactualRepositioningEngine(parity_tolerance=1e-4)
    clauses = make_mock_clauses(5)

    # Test middle clause
    ref_mid = engine.evaluate_candidates_reference(clauses, target_clause_id="clause_02")
    opt_mid, _ = engine.evaluate_candidates_optimized(clauses, target_clause_id="clause_02")

    for p in range(len(clauses)):
        assert abs(opt_mid[p][0] - ref_mid[p][0]) <= 1e-4, f"Mismatch at pos {p}: opt={opt_mid[p][0]} vs ref={ref_mid[p][0]}"
        assert abs(opt_mid[p][1] - ref_mid[p][1]) <= 1e-4
        assert abs(opt_mid[p][2] - ref_mid[p][2]) <= 1e-4

    # Test first clause (boundary start)
    ref_first = engine.evaluate_candidates_reference(clauses, target_clause_id="clause_00")
    opt_first, _ = engine.evaluate_candidates_optimized(clauses, target_clause_id="clause_00")

    for p in range(len(clauses)):
        assert abs(opt_first[p][0] - ref_first[p][0]) <= 1e-4

    # Test last clause (boundary end)
    ref_last = engine.evaluate_candidates_reference(clauses, target_clause_id="clause_04")
    opt_last, _ = engine.evaluate_candidates_optimized(clauses, target_clause_id="clause_04")

    for p in range(len(clauses)):
        assert abs(opt_last[p][0] - ref_last[p][0]) <= 1e-4


def test_repositioning_abstention_when_optimal():
    """
    Verifies that when a clause is already in its optimal position (delta <= 0),
    the system abstains and does not recommend a spurious move.
    """
    engine = CounterfactualRepositioningEngine()
    clauses = make_mock_clauses(4)
    # Evaluate a clause
    res = engine.evaluate(clauses, target_clause_id="clause_01", min_delta_threshold=0.05)
    # If best delta is below threshold or current position is optimal, must abstain
    if res.best_candidate_idx == res.target_clause_idx or res.best_objective_delta <= 0.05:
        assert res.is_abstaining is True
        assert res.abstention_reason is not None
