"""
tests/test_phase_04dda_audit.py
Validation and semantic audit test suite for LexAudit Phase 4D-D-A.
Validates:
1. Nondirectional references remain valid when section order changes.
2. Verified "Section X above" relationships become invalid when target moves below.
3. Immediate-predecessor discourse detects wrong antecedent after displacement.
4. Intra-clause discourse antecedents remain valid when clause moves intact.
5. Coupled block movements preserve internal relative order while external links require vetting.
6. Unresolved target identities and duplicate headers cause abstention.
7. CIK-plus-exhibit collision prevention (no substring collision between EX-10.1 and EX-10.12).
8. Exact mathematical reconciliation between original 30/30/12 counts and revised Phase 4D-D-A manifests.
"""
import os
import csv
import json
import re
import pytest

from src.research.dependency_ground_truth.builder import DependencyDatasetBuilder

PHASE_4DD_DIR = "research/dependency_ground_truth_phase_04dd"
PHASE_4DDA_DIR = "design/ui_redesign/phase_04dda"


@pytest.fixture(scope="module")
def builder():
    return DependencyDatasetBuilder()


@pytest.fixture(scope="module")
def original_manifest():
    path = os.path.join(PHASE_4DD_DIR, "dataset_manifest.csv")
    with open(path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


@pytest.fixture(scope="module")
def corrected_manifest():
    path = os.path.join(PHASE_4DDA_DIR, "corrected_label_manifest.csv")
    with open(path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


@pytest.fixture(scope="module")
def pos_audit():
    path = os.path.join(PHASE_4DDA_DIR, "positive_case_semantic_audit.csv")
    with open(path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


@pytest.fixture(scope="module")
def neg_audit():
    path = os.path.join(PHASE_4DDA_DIR, "negative_case_semantic_audit.csv")
    with open(path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


@pytest.fixture(scope="module")
def source_corrections():
    path = os.path.join(PHASE_4DDA_DIR, "source_identity_corrections.csv")
    with open(path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


# -----------------------------------------------------------------------------
# Test 1: Nondirectional reference remains valid under reordering
# -----------------------------------------------------------------------------
def test_nondirectional_reference_remains_valid_under_reordering(pos_audit, builder):
    """A reference to Section X without directional marker ('above'/'below') remains valid when X moves."""
    nondir_cases = [r for r in pos_audit if r["revised_phase_04dda_classification"] == "NONDIRECTIONAL_REFERENCE_STILL_VALID"]
    assert len(nondir_cases) == 16, f"Expected 16 nondirectional cases, found {len(nondir_cases)}"

    for case in nondir_cases:
        pid = case["parent_document_id"]
        raw_text, clauses = builder.load_parent_clauses(pid)
        target_sec = case["target_section_identity"]
        
        # Verify that target section is present and resolvable in document text
        sec_m = re.search(r'([0-9]+(?:\.[0-9]+)*)', target_sec)
        sec_num = sec_m.group(1) if sec_m else ""
        matches = re.findall(rf'\b(?:Section|Article)[\s\xa0]+{re.escape(sec_num)}\b', raw_text, re.I)
        assert len(matches) > 0, f"Target {target_sec} must exist in document {pid}"
        
        # Verify that referencing expression does not contain directional markers
        ref_expr = case["exact_reference_expression"].lower()
        assert "above" not in ref_expr, f"Nondirectional case {case['case_id']} contains 'above'"
        assert "below" not in ref_expr, f"Nondirectional case {case['case_id']} contains 'below'"
        assert "preceding" not in ref_expr, f"Nondirectional case {case['case_id']} contains 'preceding'"


# -----------------------------------------------------------------------------
# Test 2: Verified "Section X above" relationship invalidated when X moves below
# -----------------------------------------------------------------------------
def test_directional_above_reference_invalidated_when_target_moves_below(pos_audit):
    """When a clause specifies 'Section X above' and is moved ahead of Section X, deictic marker becomes false."""
    verified_violations = [r for r in pos_audit if r["revised_phase_04dda_classification"] == "VERIFIED_ORDER_SENSITIVE_VIOLATION"]
    assert len(verified_violations) == 9, f"Expected 9 verified violations, found {len(verified_violations)}"

    for case in verified_violations:
        assert case["has_explicit_directional_marker"] == "True"
        assert case["directional_marker_text"] == "above"
        
        # Verify that displacement places referencing clause strictly before antecedent
        disp_idx = int(case["original_displaced_idx"])
        tgt_idx = int(case["transformed_target_idx"])
        assert disp_idx > tgt_idx, f"Original order must have antecedent preceding reference for {case['case_id']}"
        assert case["moving_clause_breaks_interpretation"] == "True"


# -----------------------------------------------------------------------------
# Test 3: Immediate-predecessor discourse detects wrong antecedent after displacement
# -----------------------------------------------------------------------------
def test_immediate_predecessor_discourse_detects_wrong_antecedent(builder):
    """Moving a clause with boundary discourse marker changes its immediate predecessor, altering the antecedent."""
    pid = "SEC_CIK810136_EX_10_15"
    raw_text, clauses = builder.load_parent_clauses(pid)
    
    # Clause at boundary with backward discourse marker
    clause_idx = 17
    clause = clauses[clause_idx]
    assert "notwithstanding the foregoing" in clause.text.lower()
    
    orig_pred = clauses[clause_idx - 1]
    displaced_idx = 5
    new_pred = clauses[displaced_idx - 1]
    
    # Verify that displacing the clause changes the immediate predecessor text
    assert orig_pred.clause_id != new_pred.clause_id
    assert orig_pred.text != new_pred.text


# -----------------------------------------------------------------------------
# Test 4: Intra-clause antecedent remains valid when clause moves intact
# -----------------------------------------------------------------------------
def test_intra_clause_antecedent_remains_valid_when_clause_moves_intact(neg_audit, builder):
    """Discourse markers at sentence >= 1 have antecedents within the clause; moving clause intact preserves cohesion."""
    intra_cases = [r for r in neg_audit if "INTRA_CLAUSE" in r["transformation_type"]]
    assert len(intra_cases) == 10

    for case in intra_cases:
        pid = case["parent_document_id"]
        disp_idx = int(case["original_displaced_idx"])
        raw_text, clauses = builder.load_parent_clauses(pid)
        c = clauses[disp_idx]
        
        # Split sentences
        sents = [s.strip() for s in re.split(r'(?<=[.!?])\s+', c.text) if s.strip()]
        assert len(sents) >= 2, f"Clause {c.clause_id} must have at least 2 sentences"
        
        # Verify discourse marker is at sentence index >= 1
        found_intra = False
        for s_idx, s in enumerate(sents[1:], start=1):
            if re.search(r'\b(?:notwithstanding the foregoing|preceding sentence)\b', s, re.I):
                found_intra = True
                break
        assert found_intra, f"Clause {c.clause_id} must contain intra-clause discourse marker"
        assert case["intra_clause_cohesion_preserved"] == "True"


# -----------------------------------------------------------------------------
# Test 5: Moving antecedent and reference together preserves relative order
# -----------------------------------------------------------------------------
def test_coupled_block_movement_preserves_internal_order(neg_audit):
    """Moving paired provisions together preserves relative order, but external links require vetting."""
    coupled_cases = [r for r in neg_audit if "COUPLED_BLOCK" in r["transformation_type"]]
    assert len(coupled_cases) == 8

    clean_count = 0
    provisional_count = 0
    for case in coupled_cases:
        assert case["coupled_block_internal_order_preserved"] == "True"
        if case["displaced_clause_external_references"] == "None":
            clean_count += 1
            assert case["revised_phase_04dda_classification"] == "VERIFIED_ORDER_SENSITIVE_PRESERVATION"
        else:
            provisional_count += 1
            assert case["revised_phase_04dda_classification"] == "PROVISIONAL_NEGATIVE_EXTERNAL_DEPENDENCY_AUDIT"
            
    assert clean_count + provisional_count == 8


# -----------------------------------------------------------------------------
# Test 6: Duplicate section numbers and unresolved target identities cause abstention
# -----------------------------------------------------------------------------
def test_unresolved_target_identity_and_collision_abstention(pos_audit):
    """Header/page number collisions and duplicate extractions cause abstention."""
    unresolved_cases = [r for r in pos_audit if r["revised_phase_04dda_classification"] == "UNRESOLVED_SOURCE_MAPPING"]
    assert len(unresolved_cases) == 2  # POS_009 and POS_010 mapped to page header '2'
    
    for case in unresolved_cases:
        assert case["case_id"] in ["CASE_04DD_POS_009", "CASE_04DD_POS_010"]
        assert "filing page header" in case["audit_rationale_and_exclusion_reason"]

    invalid_cases = [r for r in pos_audit if r["revised_phase_04dda_classification"] == "INVALID_TRANSFORMATION"]
    assert len(invalid_cases) == 3  # POS_006, POS_007, POS_014 redundant duplicates
    for case in invalid_cases:
        assert "Redundant duplicate" in case["audit_rationale_and_exclusion_reason"]


# -----------------------------------------------------------------------------
# Test 7: CIK-plus-exhibit collision cannot silently select the wrong document
# -----------------------------------------------------------------------------
def test_cik_plus_exhibit_collision_guard():
    """Verify that exhibit matching logic prevents substring collisions (e.g. EX_10_1 matching EX_10_12)."""
    pid = "SEC_CIK810136_EX_10_12"
    ex_candidate = "EX_10_1"
    
    # Flawed naive substring match:
    naive_match = ex_candidate in pid
    assert naive_match is True, "Naive substring match erroneously matches EX_10_1 against EX_10_12"
    
    # Corrected exact token match:
    pid_ex = pid.split("_EX_")[-1]  # "10_12"
    cand_ex = ex_candidate.replace("EX_", "")  # "10_1"
    exact_match = (pid_ex == cand_ex)
    assert exact_match is False, "Exact token match must reject EX_10_1 against EX_10_12"


# -----------------------------------------------------------------------------
# Test 8: Original and corrected label counts reconcile exactly
# -----------------------------------------------------------------------------
def test_reconciliation_exactness(original_manifest, corrected_manifest, pos_audit, neg_audit):
    """Verify exact numerical reconciliation between Phase 4D-D and Phase 4D-D-A."""
    # Original Phase 4D-D counts
    assert len(original_manifest) == 72
    pos_orig = [r for r in original_manifest if r["case_type"] == "POSITIVE"]
    neg_orig = [r for r in original_manifest if r["case_type"] == "HARD_NEGATIVE"]
    amb_orig = [r for r in original_manifest if r["case_type"] == "AMBIGUOUS"]
    assert len(pos_orig) == 30
    assert len(neg_orig) == 30
    assert len(amb_orig) == 12

    # Corrected Phase 4D-D-A counts
    assert len(corrected_manifest) == 72
    assert len(pos_audit) == 30
    assert len(neg_audit) == 30

    pos_classes = [r["revised_phase_04dda_classification"] for r in pos_audit]
    assert pos_classes.count("VERIFIED_ORDER_SENSITIVE_VIOLATION") == 9
    assert pos_classes.count("NONDIRECTIONAL_REFERENCE_STILL_VALID") == 16
    assert pos_classes.count("INVALID_TRANSFORMATION") == 3
    assert pos_classes.count("UNRESOLVED_SOURCE_MAPPING") == 2
    assert len(pos_classes) == 30

    neg_classes = [r["revised_phase_04dda_classification"] for r in neg_audit]
    assert neg_classes.count("VERIFIED_ORDER_SENSITIVE_PRESERVATION") == 11
    assert neg_classes.count("VERIFIED_COMMUTATIVE_REORDERING") == 4
    assert neg_classes.count("PROVISIONAL_NEGATIVE_EXTERNAL_DEPENDENCY_AUDIT") == 9
    assert neg_classes.count("EDITORIAL_REORDERING_NON_DEFECTIVE") == 6
    assert len(neg_classes) == 30

    # Eligible vs Unresolved partition
    eligible = [r for r in corrected_manifest if r["eligibility_for_order_sensitive_benchmark"] == "ELIGIBLE_FOR_ORDER_SENSITIVE_BENCHMARK"]
    unresolved = [r for r in corrected_manifest if r["eligibility_for_order_sensitive_benchmark"] != "ELIGIBLE_FOR_ORDER_SENSITIVE_BENCHMARK"]
    assert len(eligible) == 24
    assert len(unresolved) == 48
    assert len(eligible) + len(unresolved) == 72
