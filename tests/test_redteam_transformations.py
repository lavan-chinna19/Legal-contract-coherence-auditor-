"""
tests/test_redteam_transformations.py — Unit tests for deterministic pure contract transformations.
Verifies copy-on-write invariants, sequence monotonic re-indexing, checksum changes, and immutability.
"""
import pytest
from src.redteam.fixtures import get_synthetic_msa_clauses, get_synthetic_sla_clauses
from src.redteam.transformations import (
    compute_clauses_checksum,
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


def test_compute_clauses_checksum_deterministic():
    clauses1 = get_synthetic_msa_clauses()
    clauses2 = get_synthetic_msa_clauses()
    cs1 = compute_clauses_checksum(clauses1)
    cs2 = compute_clauses_checksum(clauses2)
    assert cs1 == cs2
    assert len(cs1) == 64


def test_apply_clause_displacement_invariants():
    orig = get_synthetic_msa_clauses()
    orig_cs = compute_clauses_checksum(orig)
    orig_len = len(orig)

    pert, meta = apply_clause_displacement(orig, source_slot=1, target_slot=8)
    pert_cs = compute_clauses_checksum(pert)

    # 1. Total length preserved
    assert len(pert) == orig_len
    # 2. Checksum differs
    assert orig_cs != pert_cs
    # 3. Target clause moved to slot 8
    assert pert[8].clause_id == orig[1].clause_id
    # 4. Monotonic sequence_idx
    for i, c in enumerate(pert):
        assert c.sequence_idx == i
    # 5. Original clauses immutable
    assert compute_clauses_checksum(orig) == orig_cs


def test_apply_clause_displacement_noop_rejected():
    orig = get_synthetic_msa_clauses()
    with pytest.raises(ValueError, match="no-op prohibited"):
        apply_clause_displacement(orig, source_slot=2, target_slot=2)


def test_apply_clause_swap_invariants():
    orig = get_synthetic_msa_clauses()
    orig_cs = compute_clauses_checksum(orig)

    pert, meta = apply_clause_swap(orig, slot_a=0, slot_b=1)
    assert len(pert) == len(orig)
    assert pert[0].clause_id == orig[1].clause_id
    assert pert[1].clause_id == orig[0].clause_id
    assert compute_clauses_checksum(pert) != orig_cs
    # Non-swapped slots untouched
    for i in range(2, len(orig)):
        assert pert[i].clause_id == orig[i].clause_id


def test_apply_exact_duplication():
    orig = get_synthetic_msa_clauses()
    pert, meta = apply_exact_duplication(orig, source_slot=4, insert_slot=8)
    assert len(pert) == len(orig) + 1
    dup_id = meta["duplicate_clause_id"]
    dup_clause = next(c for c in pert if c.clause_id == dup_id)
    assert dup_clause.text == orig[4].text
    assert dup_clause.sequence_idx == 8


def test_apply_near_duplication():
    orig = get_synthetic_msa_clauses()
    pert, meta = apply_near_duplication(orig, source_slot=4, insert_slot=8)
    assert len(pert) == len(orig) + 1
    var_id = meta["variant_clause_id"]
    var_clause = next(c for c in pert if c.clause_id == var_id)
    assert var_clause.text != orig[4].text
    assert len(var_clause.text) > 10


def test_apply_broken_reference():
    orig = get_synthetic_msa_clauses()
    target_id = "SYNTH_DOC_01_MSA_c03"
    pert, meta = apply_broken_reference(orig, target_clause_id=target_id, old_target_sec="2", new_nonexistent_sec="Section 99")
    pert_clause = next(c for c in pert if c.clause_id == target_id)
    assert "Section 99" in pert_clause.text
    assert "Section 2" not in pert_clause.text


def test_apply_missing_exhibit():
    orig = get_synthetic_msa_clauses()
    target_id = "SYNTH_DOC_01_MSA_c01"
    pert, meta = apply_missing_exhibit(orig, target_clause_id=target_id, new_nonexistent_exhibit="Exhibit Z")
    pert_clause = next(c for c in pert if c.clause_id == target_id)
    assert "Exhibit Z" in pert_clause.text


def test_apply_date_inversion():
    orig = get_synthetic_msa_clauses()
    target_id = "SYNTH_DOC_01_MSA_c05"
    pert, meta = apply_date_inversion(orig, target_clause_id=target_id, inversion_type="INVERTED_CONTRACT_TERM", new_date_str="December 31, 2020")
    pert_clause = next(c for c in pert if c.clause_id == target_id)
    assert "December 31, 2020" in pert_clause.text


def test_apply_clause_deletion():
    orig = get_synthetic_msa_clauses()
    orig_len = len(orig)
    deleted_id = orig[1].clause_id
    pert, meta = apply_clause_deletion(orig, target_slot=1)
    assert len(pert) == orig_len - 1
    assert all(c.clause_id != deleted_id for c in pert)


def test_apply_negative_control():
    orig = get_synthetic_msa_clauses()
    pert, meta = apply_negative_control(orig)
    assert len(pert) == len(orig)
    assert compute_clauses_checksum(pert) == compute_clauses_checksum(orig)


def test_apply_combined_perturbation():
    orig = get_synthetic_msa_clauses()
    steps = [
        {"type": "P1_DISPLACEMENT", "source_slot": 1, "target_slot": 5},
        {"type": "P5_BROKEN_REFERENCE", "target_clause_id": "SYNTH_DOC_01_MSA_c06", "old_target_sec": "5", "new_sec": "Section 99"}
    ]
    pert, meta = apply_combined_perturbation(orig, steps)
    assert meta["step_count"] == 2
    assert compute_clauses_checksum(pert) != compute_clauses_checksum(orig)
