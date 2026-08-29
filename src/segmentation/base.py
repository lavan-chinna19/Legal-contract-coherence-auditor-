from abc import ABC, abstractmethod
from typing import List
from src.config import ClauseRecord

class SegmenterInterface(ABC):
    """
    Shared interface for all clause segmenters (V1 rule-based, V2 learned).
    Both V1 and V2 MUST return the same schema.
    """
    
    @abstractmethod
    def segment(self, text: str, doc_id: str = "unknown") -> List[ClauseRecord]:
        """
        Segments a raw contract text into an ordered list of clause spans.
        
        Args:
            text: The raw contract text.
            doc_id: The document identifier (useful for ClauseRecord generation).
            
        Returns:
            An ordered list of ClauseRecord objects.
        """
        pass
