"""
src/coherence/base.py — Abstract Base Class for Clause Coherence Scoring Models.
"""
from abc import ABC, abstractmethod
from typing import List, Tuple
from src.config import ClauseRecord


class CoherenceModelInterface(ABC):
    """
    Unified abstract interface for discourse coherence models.
    Both fine-tuned neural heads and zero-shot LLM paths implement this interface.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Returns the human-readable model identifier."""
        pass

    @abstractmethod
    def score_pair(self, clause_a: ClauseRecord, clause_b: ClauseRecord) -> float:
        """
        Calculates a coherence probability score for transition from clause_a to clause_b.
        
        Args:
            clause_a: Antecedent ClauseRecord
            clause_b: Subsequent ClauseRecord
            
        Returns:
            float: Coherence likelihood score in the range [0.0, 1.0].
                   Higher values indicate stronger discourse coherence / legitimate consecutive flow.
        """
        pass

    @abstractmethod
    def score_pairs(self, pairs: List[Tuple[ClauseRecord, ClauseRecord]]) -> List[float]:
        """
        Calculates coherence probability scores for a batch of clause pairs.
        
        Args:
            pairs: List of tuples (clause_a, clause_b)
            
        Returns:
            List[float]: Coherence scores in [0.0, 1.0].
        """
        pass
