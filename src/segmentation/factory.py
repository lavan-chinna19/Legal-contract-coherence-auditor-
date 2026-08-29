from .base import SegmenterInterface
from .rule_based import RuleBasedSegmenter
from .bio_tagger import BIOTaggerSegmenter

def get_segmenter(segmenter_type: str) -> SegmenterInterface:
    """
    Factory method to instantiate the requested segmenter.
    
    Args:
        segmenter_type: "v1" for Rule-Based, "v2" for BIO Tagger.
        
    Returns:
        An instance of SegmenterInterface.
    """
    if segmenter_type.lower() == "v1":
        return RuleBasedSegmenter()
    elif segmenter_type.lower() == "v2":
        return BIOTaggerSegmenter()
    else:
        raise ValueError(f"Unknown segmenter_type: {segmenter_type}. Must be 'v1' or 'v2'.")
