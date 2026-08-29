import os
import json
import numpy as np
from typing import List, Tuple, Dict, Any, Optional
from src.config import EMBEDDINGS_CACHE_DIR, ClauseRecord

class EmbeddingCache:
    """
    Handles caching of embeddings to prevent unnecessary recomputation.
    Uses a simple file-based approach where each model has a directory,
    and embeddings can be stored individually or in chunks.
    For simplicity and compliance with the prompt (keyed by document_id + clause_id),
    we'll use a local mapping. To avoid millions of small files, we store them grouped
    by a hash or simply in a single large numpy archive per dataset/source if possible,
    but to be strictly keyed by doc_id+clause_id, we can store `.npy` files per document,
    containing a dict of clause_id -> vector.
    """

    def __init__(self, model_name: str):
        # Sanitize model name for filesystem
        safe_model_name = model_name.replace("/", "_").replace("\\", "_")
        self.cache_dir = EMBEDDINGS_CACHE_DIR / safe_model_name
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_doc_cache_path(self, doc_id: str) -> str:
        # Sanitize doc_id for filename
        safe_doc_id = "".join(c for c in doc_id if c.isalnum() or c in ('_', '-'))
        return str(self.cache_dir / f"{safe_doc_id}.npz")

    def get_cached_embeddings(self, clauses: List[ClauseRecord]) -> Tuple[List[ClauseRecord], Dict[str, np.ndarray]]:
        """
        Check the cache for the given clauses.
        Returns:
            missing_clauses: List of clauses that need to be computed.
            cached_vectors: Dictionary mapping clause_id to its embedding vector.
        """
        cached_vectors = {}
        missing_clauses = []

        # Group by doc_id to minimize file reads
        doc_id_to_clauses = {}
        for c in clauses:
            doc_id_to_clauses.setdefault(c.doc_id, []).append(c)

        for doc_id, doc_clauses in doc_id_to_clauses.items():
            cache_path = self._get_doc_cache_path(doc_id)
            if os.path.exists(cache_path):
                try:
                    with np.load(cache_path) as data:
                        for c in doc_clauses:
                            if c.clause_id in data:
                                cached_vectors[c.clause_id] = data[c.clause_id]
                            else:
                                missing_clauses.append(c)
                except Exception as e:
                    # If cache file is corrupted, treat all as missing
                    missing_clauses.extend(doc_clauses)
            else:
                missing_clauses.extend(doc_clauses)

        return missing_clauses, cached_vectors

    def save_embeddings(self, clauses: List[ClauseRecord], embeddings: np.ndarray):
        """
        Save computed embeddings to the cache.
        """
        if len(clauses) != len(embeddings):
            raise ValueError("Number of clauses must match number of embeddings.")

        # Group by doc_id
        doc_id_to_data = {}
        for i, c in enumerate(clauses):
            doc_id_to_data.setdefault(c.doc_id, {})[c.clause_id] = embeddings[i]

        for doc_id, new_data in doc_id_to_data.items():
            cache_path = self._get_doc_cache_path(doc_id)
            existing_data = {}
            if os.path.exists(cache_path):
                try:
                    with np.load(cache_path) as data:
                        existing_data = {k: data[k] for k in data.files}
                except Exception:
                    pass # Overwrite if corrupted
            
            # Update with new data
            existing_data.update(new_data)
            
            # Save back to disk
            np.savez_compressed(cache_path, **existing_data)
