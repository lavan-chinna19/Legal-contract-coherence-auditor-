"""
tests/test_ensemble.py - Prompt 8 Tests for Score Ensembling
"""
import pytest
from src.config import ClauseRecord
from src.scoring.ensemble import ChannelBEnsembler

@pytest.fixture
def sample_clauses():
    return [
        ClauseRecord(clause_id="c1", doc_id="d1", sequence_idx=0, text="Governing Law is Texas.", char_start=0, char_end=10, label="Governing Laws", source="demo"),
        ClauseRecord(clause_id="c2", doc_id="d1", sequence_idx=1, text="Confidentiality shall be maintained.", char_start=11, char_end=20, label="Confidentiality", source="demo"),
        ClauseRecord(clause_id="c3", doc_id="d1", sequence_idx=2, text="Random text here.", char_start=21, char_end=30, label="Other", source="demo")
    ]

def test_ensemble_modes(sample_clauses):
    # Test fine-tuned only
    ensembler_ft = ChannelBEnsembler(mode="fine_tuned")
    res_ft = ensembler_ft.score_document(sample_clauses, "d1", "NDA")
    assert res_ft.ensemble_mode == "fine_tuned"
    for c in res_ft.clauses:
        assert c.combined_score == c.fine_tuned_score
        
    # Test zero-shot only
    ensembler_zs = ChannelBEnsembler(mode="zero_shot")
    res_zs = ensembler_zs.score_document(sample_clauses, "d1", "NDA")
    assert res_zs.ensemble_mode == "zero_shot"
    for c in res_zs.clauses:
        assert c.combined_score == c.zero_shot_score
        
    # Test combined
    ensembler_comb = ChannelBEnsembler(mode="combined", alpha=0.5)
    res_comb = ensembler_comb.score_document(sample_clauses, "d1", "NDA")
    assert res_comb.ensemble_mode == "combined"
    for c in res_comb.clauses:
        expected = 0.5 * c.fine_tuned_score + 0.5 * c.zero_shot_score
        assert abs(c.combined_score - expected) < 1e-4

def test_ensemble_weights(sample_clauses):
    ensembler = ChannelBEnsembler(mode="combined", alpha=0.75)
    res = ensembler.score_document(sample_clauses, "d1", "NDA")
    for c in res.clauses:
        expected = 0.75 * c.fine_tuned_score + 0.25 * c.zero_shot_score
        assert abs(c.combined_score - expected) < 1e-4

def test_zero_shot_baseline(sample_clauses):
    # Test that a clause not in the checklist gets 0.5 anomaly
    ensembler = ChannelBEnsembler(mode="zero_shot")
    res = ensembler.score_document(sample_clauses, "d1", "NDA")
    # c3 is not on NDA checklist (Governing Laws, Confidentiality, Notices, Terminations)
    # It might get picked up if NLI is weird, but likely 0.5 or close to it if not matched.
    # Actually, c3 will not be matched as BEST evidence, so it should get exactly 0.5
    c3_res = next(c for c in res.clauses if c.clause_id == "c3")
    assert c3_res.zero_shot_score == 0.5
