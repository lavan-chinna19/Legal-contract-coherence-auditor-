"""
src/coherence/factory.py — Factory registry for Discourse Coherence Models.
Allows seamless switching between fine-tuned neural scoring and zero-shot LLM paths.
"""
from typing import Optional
from src.config import ACTIVE_COHERENCE_MODEL
from src.coherence.base import CoherenceModelInterface
from src.coherence.fine_tuned import FineTunedCoherenceModel
from src.coherence.zero_shot import ZeroShotCoherenceModel


def get_coherence_model(model_type: Optional[str] = None) -> CoherenceModelInterface:
    """
    Retrieves the requested coherence scoring model.
    
    Args:
        model_type: "fine_tuned" | "zero_shot" (defaults to config.ACTIVE_COHERENCE_MODEL)
        
    Returns:
        CoherenceModelInterface
    """
    active = model_type or ACTIVE_COHERENCE_MODEL

    if active == "fine_tuned":
        return FineTunedCoherenceModel()
    elif active == "zero_shot":
        return ZeroShotCoherenceModel()
    else:
        raise ValueError(f"Unknown coherence model type: '{active}'. Supported: ['fine_tuned', 'zero_shot']")
