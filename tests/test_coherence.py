"""
tests/test_coherence.py — Unit tests for Discourse Coherence modeling and registry.
"""
import pytest
import numpy as np
import torch
from unittest.mock import patch, MagicMock

from src.config import ClauseRecord
from src.coherence.pair_sampler import CoherencePairSampler, CoherencePair
from src.coherence.model import CoherenceScorerHead
from src.coherence.fine_tuned import FineTunedCoherenceModel
from src.coherence.zero_shot import ZeroShotCoherenceModel
from src.coherence.factory import get_coherence_model
from src.coherence.trainer import train_coherence_model


@pytest.fixture
def sample_doc_clauses():
    """Generates 5 sequential clauses for doc_A and 3 for doc_B."""
    doc_a = [
        ClauseRecord(
            clause_id=f"docA_{i}",
            doc_id="docA",
            text=f"Clause text {i} of document A regarding section {i}.",
            label="Terms",
            sequence_idx=i,
            char_start=i * 50,
            char_end=(i + 1) * 50,
            source="test"
        )
        for i in range(5)
    ]
    doc_b = [
        ClauseRecord(
            clause_id=f"docB_{j}",
            doc_id="docB",
            text=f"Clause text {j} of document B regarding topic {j}.",
            label="Payment",
            sequence_idx=j,
            char_start=j * 40,
            char_end=(j + 1) * 40,
            source="test"
        )
        for j in range(3)
    ]
    return doc_a, doc_b


def test_pair_sampler_document_pairs(sample_doc_clauses):
    doc_a, _ = sample_doc_clauses
    sampler = CoherencePairSampler(easy_neg_ratio=1.0, hard_neg_ratio=1.0, seed=42)
    
    # 5 clauses -> 4 positive consecutive pairs
    pairs = sampler.sample_document_pairs(doc_a)
    
    positives = [p for p in pairs if p.pair_type == "positive"]
    hard_negs = [p for p in pairs if p.pair_type == "hard_negative"]
    
    assert len(positives) == 4
    assert len(hard_negs) == 4
    
    # Check positive labels
    for p in positives:
        assert p.label == 1.0
        assert p.doc_id_a == "docA"
        assert p.doc_id_b == "docA"
        assert p.clause_b.sequence_idx == p.clause_a.sequence_idx + 1

    # Check hard negative labels
    for p in hard_negs:
        assert p.label == 0.0
        assert p.doc_id_a == "docA"
        assert p.doc_id_b == "docA"
        assert p.clause_b.sequence_idx != p.clause_a.sequence_idx + 1


def test_pair_sampler_cross_document_easy_negatives(sample_doc_clauses):
    doc_a, doc_b = sample_doc_clauses
    all_clauses = doc_a + doc_b
    sampler = CoherencePairSampler(easy_neg_ratio=1.0, hard_neg_ratio=1.0, seed=42)
    
    pairs = sampler.sample_dataset(all_clauses)
    
    positives = [p for p in pairs if p.pair_type == "positive"]
    easy_negs = [p for p in pairs if p.pair_type == "easy_negative"]
    hard_negs = [p for p in pairs if p.pair_type == "hard_negative"]
    
    # docA has 4 positives, docB has 2 positives -> 6 total positives
    assert len(positives) == 6
    assert len(easy_negs) == 6
    assert len(hard_negs) == 6
    
    for p in easy_negs:
        assert p.label == 0.0
        assert p.doc_id_a != p.doc_id_b


def test_coherence_scorer_head_forward():
    model = CoherenceScorerHead(embedding_dim=128, hidden_dim1=64, hidden_dim2=32)
    u = torch.randn(8, 128)
    v = torch.randn(8, 128)
    
    logits = model(u, v)
    assert logits.shape == (8, 1)
    
    probs = model.predict_proba(u.numpy(), v.numpy())
    assert probs.shape == (8,)
    assert np.all(probs >= 0.0) and np.all(probs <= 1.0)


def test_coherence_training_execution(sample_doc_clauses, tmp_path):
    doc_a, doc_b = sample_doc_clauses
    sampler = CoherencePairSampler(easy_neg_ratio=1.0, hard_neg_ratio=1.0, seed=42)
    pairs = sampler.sample_dataset(doc_a + doc_b)
    
    mock_embedder = MagicMock()
    mock_embedder.embedding_dim = 64
    
    def fake_embed(clauses):
        return [c.to_dict() for c in clauses], np.random.randn(len(clauses), 64).astype(np.float32)
        
    mock_embedder.embed_clauses.side_effect = fake_embed
    
    checkpoint_file = tmp_path / "test_model.pt"
    fixture_file = tmp_path / "test_curves.json"
    
    with patch("src.coherence.trainer.COHERENCE_CHECKPOINT_PATH", checkpoint_file), \
         patch("src.coherence.trainer.COHERENCE_TRAINING_CURVES_PATH", fixture_file):
        model, history = train_coherence_model(
            pairs=pairs,
            epochs=3,
            batch_size=4,
            embedder=mock_embedder,
            save_checkpoint=True,
            save_fixture=True
        )
        
        assert len(history["epochs"]) == 3
        assert "val_loss" in history["epochs"][0]
        assert "val_accuracy" in history["epochs"][0]
        assert checkpoint_file.exists()
        assert fixture_file.exists()


def test_coherence_factory():
    fine_tuned = get_coherence_model("fine_tuned")
    assert isinstance(fine_tuned, FineTunedCoherenceModel)
    
    zero_shot = get_coherence_model("zero_shot")
    assert isinstance(zero_shot, ZeroShotCoherenceModel)
    
    with pytest.raises(ValueError):
        get_coherence_model("invalid_model_type")
