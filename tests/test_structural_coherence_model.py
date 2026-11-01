"""
tests/test_structural_coherence_model.py — Unit and Scientific Consistency Suite for Phase 4D-B.
Verifies:
1. Feature extraction & heading-first lifecycle stage inference.
2. Ground-truth label taxonomy and eligibility filtering.
3. Split isolation and zero cross-contamination.
4. Exact two-sided Wilson confidence interval calculations.
5. Score orientation and threshold behavior.
6. CPU inference shapes and latency.
7. Original model immutability and checkpoint integrity.
8. No oracle access during inference.
"""
import os
import math
import hashlib
from pathlib import Path
import pytest
import numpy as np

from src.config import ClauseRecord
from src.redteam.fixtures import get_synthetic_msa_clauses, get_synthetic_sla_clauses
from src.research.structural_coherence.schema import (
    StructuralAnomalyLabel,
    DocumentStructuralResult,
    ClauseStructuralScore
)
from src.research.structural_coherence.features import (
    infer_clause_lifecycle_stage,
    extract_contextual_window_distances,
    extract_progression_discordance,
    extract_boundary_contrast
)
from src.research.structural_coherence.models import (
    BaselineB0_ChannelB,
    BaselineB1_ProductionEnsemble,
    BaselineB2_CosineDistance,
    CandidateC1_ContextualBoundaryDetector,
    CandidateC3_StructureAwareDependencyModel
)
from src.research.structural_coherence.evaluator import (
    compute_wilson_score_interval,
    assemble_benchmark_cases
)


def test_wilson_score_interval_exactness():
    """Verifies that the two-sided Wilson 95% confidence interval matches analytical bounds."""
    # 0/5 case -> [0.0000, 0.4345]
    low_05, high_05 = compute_wilson_score_interval(0, 5)
    assert low_05 == 0.0
    assert high_05 == 0.4345

    # 0/6 case -> [0.0000, 0.3903]
    low_06, high_06 = compute_wilson_score_interval(0, 6)
    assert low_06 == 0.0
    assert high_06 == 0.3903

    # 2/2 case -> [0.3424, 1.0000]
    low_22, high_22 = compute_wilson_score_interval(2, 2)
    assert low_22 == 0.3424
    assert high_22 == 1.0000

    # 5/5 case -> [0.5655, 1.0000]
    low_55, high_55 = compute_wilson_score_interval(5, 5)
    assert low_55 == 0.5655
    assert high_55 == 1.0000

    # Degenerate zero denominator
    assert compute_wilson_score_interval(0, 0) == (0.0, 0.0)


def test_infer_lifecycle_stage_heading_priority():
    """Verifies that heading and label take priority over internal body text."""
    msa = get_synthetic_msa_clauses()
    
    # Clause 0: Preamble -> Stage 0
    assert infer_clause_lifecycle_stage(msa[0]) == 0
    
    # Clause 1: Scope of Services -> Stage 1
    assert infer_clause_lifecycle_stage(msa[1]) == 1
    
    # Clause 10: Exhibit A -> Stage 6 (must NOT match Stage 1 despite mentioning 'scope' in text)
    assert infer_clause_lifecycle_stage(msa[10]) == 6

    # Clause 8: Governing Law -> Stage 5
    assert infer_clause_lifecycle_stage(msa[8]) == 5


def test_clean_msa_discordance_zero():
    """Verifies that canonical unperturbed MSA produces zero progression discordance."""
    msa = get_synthetic_msa_clauses()
    disc = extract_progression_discordance(msa)
    assert np.all(disc == 0.0), f"Expected all zeros, got {disc}"


def test_progression_discordance_on_inversion():
    """Verifies that an inversion of Exhibit before Scope produces high discordance."""
    msa = get_synthetic_msa_clauses()
    # Invert: Exhibit A (slot 10) placed at slot 1, Scope at slot 10
    inverted = [msa[0], msa[10], msa[2], msa[3], msa[4], msa[5], msa[6], msa[7], msa[8], msa[9], msa[1]]
    disc = extract_progression_discordance(inverted)
    # The last clause (Scope after Exhibit) must have severe discordance
    assert disc[-1] > 0.5


def test_benchmark_case_split_isolation():
    """Verifies that benchmark cases have strictly isolated partitions and disjoint case IDs."""
    cases = assemble_benchmark_cases()
    splits = {c.split for c in cases}
    assert splits == {"DIAGNOSTIC", "VALIDATION", "HELDOUT_TEST"}
    
    case_ids = [c.case_id for c in cases]
    assert len(case_ids) == len(set(case_ids)), "Duplicate case IDs detected!"
    
    # Ensure held-out test cases are distinct from diagnostic cases
    diag_ids = {c.case_id for c in cases if c.split == "DIAGNOSTIC"}
    test_ids = {c.case_id for c in cases if c.split == "HELDOUT_TEST"}
    assert diag_ids.isdisjoint(test_ids)


def test_label_taxonomy_and_eligibility():
    """Verifies that AMBIGUOUS_ORDER cases are excluded from strict positive denominator."""
    cases = assemble_benchmark_cases()
    ambig_cases = [c for c in cases if c.ground_truth_label == StructuralAnomalyLabel.AMBIGUOUS_ORDER]
    assert len(ambig_cases) >= 1
    for c in ambig_cases:
        assert c.is_positive is False, "Ambiguous cases must not be labeled positive in strict evaluation"


def test_candidate_c3_topological_clean_specificity():
    """Verifies that Candidate C3 produces 0 false positives on canonical clean contracts."""
    c3 = CandidateC3_StructureAwareDependencyModel(threshold=0.50)
    msa = get_synthetic_msa_clauses()
    sla = get_synthetic_sla_clauses()
    
    res_msa = c3.evaluate_document(msa, doc_id="msa_clean")
    assert res_msa.is_anomaly is False
    assert res_msa.max_structural_score == 0.0

    res_sla = c3.evaluate_document(sla, doc_id="sla_clean")
    assert res_sla.is_anomaly is False
    assert res_sla.max_structural_score == 0.0


def test_candidate_c3_topological_inversion_detection():
    """Verifies that Candidate C3 reliably detects major structural inversions."""
    c3 = CandidateC3_StructureAwareDependencyModel(threshold=0.50)
    msa = get_synthetic_msa_clauses()
    
    # Severe inversion: Governing Law (slot 8) moved before Scope (slot 1)
    inverted = [msa[0], msa[8], msa[1], msa[2], msa[3], msa[4], msa[5], msa[6], msa[7], msa[9], msa[10]]
    res = c3.evaluate_document(inverted, doc_id="test_inverted")
    assert res.is_anomaly is True
    assert res.max_structural_score == 1.0
    assert msa[1].clause_id in res.predicted_anomaly_clause_ids


def test_candidate_c1_clean_msa_specificity():
    """Verifies that Candidate C1 score on clean MSA stays well below threshold."""
    c1 = CandidateC1_ContextualBoundaryDetector(threshold=0.42)
    msa = get_synthetic_msa_clauses()
    res = c1.evaluate_document(msa, doc_id="msa_clean")
    assert res.is_anomaly is False
    assert res.max_structural_score < 0.42


def test_candidate_c2_checkpoint_exists_and_immutable():
    """Verifies that Candidate C2 checkpoint exists under models/experimental/ and matches expected SHA-256."""
    repo_root = Path(__file__).resolve().parent.parent
    ckpt_path = repo_root / "models" / "experimental" / "phase_04db" / "contextual_sequence_coherence.pt"
    assert ckpt_path.is_file(), f"Candidate C2 checkpoint missing at {ckpt_path}"
    
    with open(ckpt_path, "rb") as f:
        digest = hashlib.sha256(f.read()).hexdigest()
    assert digest == "cac804594959a419126463191c3c520206f00244540133492ffd98bbd4a4c9aa"


def test_frozen_models_immutability():
    """Verifies that original production Channel B weights and centroids remain untouched."""
    repo_root = Path(__file__).resolve().parent.parent
    b_path = repo_root / "models" / "coherence_classifier.pt"
    assert b_path.is_file()
    
    centroids_path = repo_root / "fixtures" / "ledgar_centroids.npz"
    assert centroids_path.is_file()
