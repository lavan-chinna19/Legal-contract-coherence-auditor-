from src.embeddings.base import EmbeddingInterface
from src.embeddings.frozen import FrozenLegalBERTEmbedder
# from src.embeddings.fine_tune import FineTunedEmbedder  # To be implemented

def get_embedder(source: str) -> EmbeddingInterface:
    """
    Factory to retrieve the appropriate embedding interface based on configuration.
    
    Args:
        source: "frozen" or "fine_tuned"
    
    Returns:
        Instance of an EmbeddingInterface.
    """
    if source == "frozen":
        return FrozenLegalBERTEmbedder()
    elif source == "fine_tuned":
        # Placeholder for stretch goal implementation
        try:
            from src.embeddings.fine_tune import FineTunedEmbedder
            return FineTunedEmbedder()
        except ImportError:
            raise NotImplementedError("Fine-tuned embedder is not fully implemented or could not be loaded.")
    else:
        raise ValueError(f"Unknown embedding source: {source}")
