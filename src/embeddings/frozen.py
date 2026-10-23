import numpy as np
import os
import threading
from typing import List, Tuple
from sentence_transformers import SentenceTransformer

from src.config import ClauseRecord, LEGAL_BERT_MODEL
from src.embeddings.base import EmbeddingInterface
from src.embeddings.cache import EmbeddingCache

_MODEL_LOAD_LOCK = threading.Lock()


class FrozenLegalBERTEmbedder(EmbeddingInterface):
    """
    Produces clause-level embeddings using a frozen Legal-BERT model.
    Implements caching to avoid recomputing vectors for identical clauses.
    """

    def __init__(self, model_name: str = LEGAL_BERT_MODEL):
        self._model_name = model_name
        # Lazy loading to avoid overhead if not used
        self._model = None
        self._cache = EmbeddingCache(model_name)
        # SentenceTransformer default pooling is MEAN, which is appropriate.
        # Max sequence length is typically 512 for BERT.
    
    def _load_model(self):
        if self._model is None:
            with _MODEL_LOAD_LOCK:
                if self._model is None:
                    model = SentenceTransformer(self._model_name, device="cpu",
                        local_files_only=os.environ.get("LEXAUDIT_ALLOW_MODEL_DOWNLOAD", "0") != "1")
                    for param in model.parameters():
                        param.requires_grad = False
                    model.eval()
                    # Publish only a completely initialized frozen model.
                    self._model = model

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def embedding_dim(self) -> int:
        if self._model is not None:
            return self._model.get_embedding_dimension()
        return 768  # Standard Legal-BERT base uncased hidden dimension

    def embed_clauses(self, clauses: List[ClauseRecord], batch_size: int = 32) -> Tuple[List[dict], np.ndarray]:
        if not clauses:
            return [], np.array([])

        missing_clauses, cached_vectors = self._cache.get_cached_embeddings(clauses)
        
        # Compute embeddings for missing clauses
        if missing_clauses:
            self._load_model()
            texts = [c.text for c in missing_clauses]
            
            # encode() handles truncation to model max_length (512 usually) and batching
            computed_embeddings = self._model.encode(
                texts,
                batch_size=batch_size,
                show_progress_bar=False,
                convert_to_numpy=True,
                normalize_embeddings=True # Normalizing to use cosine similarity
            )
            
            # Save newly computed embeddings to cache
            self._cache.save_embeddings(missing_clauses, computed_embeddings)
            
            # Update cached_vectors dict so we can build the final aligned array
            for i, c in enumerate(missing_clauses):
                cached_vectors[c.clause_id] = computed_embeddings[i]

        # Reconstruct output in the exact order requested
        final_embeddings = []
        final_metadata = []
        
        for c in clauses:
            emb = cached_vectors[c.clause_id]
            final_embeddings.append(emb)
            # Preserve metadata
            meta = {
                "clause_id": c.clause_id,
                "doc_id": c.doc_id,
                "label": c.label,
                "model": self.model_name
            }
            final_metadata.append(meta)

        return final_metadata, np.vstack(final_embeddings)
