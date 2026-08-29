import json
from pathlib import Path
from typing import List, Dict, Tuple
from src.config import ClauseRecord

def evaluate_segmentation(
    predictions: List[ClauseRecord], 
    gold_standard: List[ClauseRecord],
    offset_tolerance: int = 10
) -> Dict[str, float]:
    """
    Evaluates segmentation predictions against gold standard labels.
    
    Args:
        predictions: List of predicted ClauseRecord objects.
        gold_standard: List of gold ClauseRecord objects.
        offset_tolerance: Number of characters by which a boundary can vary and still match.
        
    Returns:
        Dictionary containing Precision, Recall, and F1.
    """
    if not gold_standard:
        return {"precision": 0.0, "recall": 0.0, "f1": 0.0}
    if not predictions:
        return {"precision": 0.0, "recall": 0.0, "f1": 0.0}

    # Extract boundaries: (start, end)
    pred_boundaries = [(c.char_start, c.char_end) for c in predictions]
    gold_boundaries = [(c.char_start, c.char_end) for c in gold_standard]
    
    true_positives = 0
    
    # Simple matching with tolerance
    matched_gold = set()
    for p_start, p_end in pred_boundaries:
        for i, (g_start, g_end) in enumerate(gold_boundaries):
            if i in matched_gold:
                continue
            if (abs(p_start - g_start) <= offset_tolerance and 
                abs(p_end - g_end) <= offset_tolerance):
                true_positives += 1
                matched_gold.add(i)
                break
                
    precision = true_positives / len(pred_boundaries) if pred_boundaries else 0.0
    recall = true_positives / len(gold_boundaries) if gold_boundaries else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    
    return {
        "precision": precision,
        "recall": recall,
        "f1": f1
    }

def save_evaluation_fixture(results: dict, fixture_path: Path):
    """
    Saves the evaluation metrics as a reusable fixture.
    """
    fixture_path.parent.mkdir(parents=True, exist_ok=True)
    with open(fixture_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
