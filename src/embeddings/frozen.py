import numpy as np
from typing import List, Tuple
from sentence_transformers import SentenceTransformer

from src.config import ClauseRecord, LEGAL_BERT_MODEL
from src.embeddings.base import EmbeddingInterface
from src.embeddings.cache import EmbeddingCache


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
            # Compatibility bypass for transformers 5.x check_torch_load_is_safe on local weights
            try:
                import transformers.utils.import_utils
                import transformers.modeling_utils
                transformers.utils.import_utils.check_torch_load_is_safe = lambda: None
                transformers.modeling_utils.check_torch_load_is_safe = lambda: None
            except Exception:
                pass

            # Load locally or download if not present
            self._model = SentenceTransformer(self._model_name)
            # Ensure the model is completely frozen (baseline requirement)
            for param in self._model.parameters():
                param.requires_grad = False
            self._model.eval()

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
