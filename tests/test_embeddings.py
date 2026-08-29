import pytest
import numpy as np
from unittest.mock import patch, MagicMock

from src.config import ClauseRecord, EMBEDDINGS_CACHE_DIR
from src.embeddings.cache import EmbeddingCache
from src.embeddings.frozen import FrozenLegalBERTEmbedder
from src.embeddings.factory import get_embedder

@pytest.fixture
def sample_clauses():
    return [
        ClauseRecord(
            clause_id="doc1_0",
            doc_id="doc1",
            text="This is the first test clause.",
            label="General",
            sequence_idx=0,
            char_start=0,
            char_end=30,
            source="test"
        ),
        ClauseRecord(
            clause_id="doc1_1",
            doc_id="doc1",
            text="This is the second test clause.",
            label="General",
            sequence_idx=1,
            char_start=31,
            char_end=62,
            source="test"
        )
    ]

def test_cache_miss_and_hit(sample_clauses, tmp_path):
    # Override cache dir for test
    with patch('src.embeddings.cache.EMBEDDINGS_CACHE_DIR', tmp_path):
        cache = EmbeddingCache("test_model")
        
        # Initial check (Miss)
        missing, cached = cache.get_cached_embeddings(sample_clauses)
        assert len(missing) == 2
        assert len(cached) == 0
        
        # Save mock embeddings
        mock_embeddings = np.array([[1.0, 2.0], [3.0, 4.0]])
        cache.save_embeddings(sample_clauses, mock_embeddings)
        
        # Second check (Hit)
        missing, cached = cache.get_cached_embeddings(sample_clauses)
        assert len(missing) == 0
        assert len(cached) == 2
        np.testing.assert_array_equal(cached["doc1_0"], mock_embeddings[0])
        np.testing.assert_array_equal(cached["doc1_1"], mock_embeddings[1])

def test_frozen_embedder_metadata_and_shape(sample_clauses, tmp_path):
    with patch('src.embeddings.cache.EMBEDDINGS_CACHE_DIR', tmp_path):
        embedder = FrozenLegalBERTEmbedder("nlpaueb/legal-bert-base-uncased")
        
        # We don't want to actually load the real model in a unit test if possible,
        # but since we need shape, we'll mock the `encode` and `embedding_dim`.
        with patch.object(embedder, '_load_model', return_value=None):
            with patch('src.embeddings.frozen.FrozenLegalBERTEmbedder.embedding_dim', new_callable=pytest.MonkeyPatch) as mock_dim:
                # Actually, MonkeyPatch on a property via patch is tricky. Let's just mock the property itself:
                pass
                
        # Better yet, let's just patch PropertyMock:
        from unittest.mock import PropertyMock
        with patch.object(embedder, '_load_model', return_value=None):
            with patch('src.embeddings.frozen.FrozenLegalBERTEmbedder.embedding_dim', new_callable=PropertyMock, return_value=768):
                embedder._model = MagicMock()
                embedder._model.encode.return_value = np.zeros((2, 768))
                
                meta, embs = embedder.embed_clauses(sample_clauses)
                
                assert len(meta) == 2
                assert embs.shape == (2, 768)
                assert meta[0]["clause_id"] == "doc1_0"
                assert meta[0]["doc_id"] == "doc1"
                assert meta[0]["label"] == "General"

def test_factory_frozen():
    embedder = get_embedder("frozen")
    assert isinstance(embedder, FrozenLegalBERTEmbedder)

def test_factory_unknown():
    with pytest.raises(ValueError):
        get_embedder("unknown_source")
