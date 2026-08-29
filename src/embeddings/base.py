from abc import ABC, abstractmethod
from typing import List, Tuple
import numpy as np

from src.config import ClauseRecord


class EmbeddingInterface(ABC):
    """
    Standard interface for generating embeddings from ClauseRecords.
    """

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Return the name or identifier of the underlying model."""
        pass

    @property
    @abstractmethod
    def embedding_dim(self) -> int:
        """Return the dimensionality of the generated embeddings."""
        pass

    @abstractmethod
    def embed_clauses(self, clauses: List[ClauseRecord], batch_size: int = 32) -> Tuple[List[dict], np.ndarray]:
        """
        Generate embeddings for a list of ClauseRecords.

        Args:
            clauses: List of ClauseRecord objects to embed.
            batch_size: Batch size for processing.

        Returns:
            A tuple containing:
            1. A list of metadata dictionaries corresponding to each clause.
            2. A numpy array of shape (len(clauses), embedding_dim) containing the embeddings.
        """
        pass
