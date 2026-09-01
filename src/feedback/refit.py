"""
src/feedback/refit.py — Refit job to recalculate thresholds based on feedback.
"""
import json
import numpy as np
from pathlib import Path
from typing import Tuple, Dict

from src.feedback.storage import get_all_feedback
from src.config import (
    THRESHOLDS_PATH, 
    SEVERITY_HIGH_THRESHOLD, 
    SEVERITY_MED_THRESHOLD
)

def run_refit(provenance: str = "SYNTHETIC_TEST") -> Tuple[Dict[str, float], Dict[str, float], int]:
    """
    Recalculates thresholds based on accumulated feedback of the given provenance.
    For this demo, if reviewers mark HIGH anomalies as OVERKILL, we raise the threshold slightly.
    If they mark CLEAN as MISSED, we lower the MEDIUM threshold.
    
    Returns:
        (old_thresholds, new_thresholds, feedback_count)
    """
    records = get_all_feedback(provenance_filter=provenance)
    
    old_high = SEVERITY_HIGH_THRESHOLD
    old_med = SEVERITY_MED_THRESHOLD
    
    if not records:
        return (
            {"SEVERITY_HIGH_THRESHOLD": old_high, "SEVERITY_MED_THRESHOLD": old_med},
            {"SEVERITY_HIGH_THRESHOLD": old_high, "SEVERITY_MED_THRESHOLD": old_med},
            0
        )
        
    # A highly simplistic and transparent heuristic for recalibration:
    high_overkill_count = sum(1 for r in records if r.original_severity == 'HIGH' and r.reviewer_verdict == 'OVERKILL')
    high_valid_count = sum(1 for r in records if r.original_severity == 'HIGH' and r.reviewer_verdict == 'VALID')
    
    med_missed_count = sum(1 for r in records if r.original_severity in ['CLEAN', 'LOW'] and r.reviewer_verdict == 'MISSED')
    med_valid_count = sum(1 for r in records if r.original_severity == 'MEDIUM' and r.reviewer_verdict == 'VALID')
    
    new_high = old_high
    new_med = old_med
    
    # Adjust HIGH threshold
    if high_overkill_count > high_valid_count:
        # Too many false positives; tighten threshold
        new_high = min(0.95, round(old_high + 0.05, 3))
    elif high_valid_count > high_overkill_count * 2:
        # Mostly valid, we could maybe relax it to catch more
        new_high = max(0.60, round(old_high - 0.02, 3))
        
    # Adjust MED threshold
    if med_missed_count > med_valid_count:
        # We are missing things, lower the threshold
        new_med = max(0.35, round(old_med - 0.05, 3))
    
    # Ensure logical consistency
    if new_med >= new_high:
        new_med = new_high - 0.1
        
    new_thresholds = {
        "SEVERITY_HIGH_THRESHOLD": new_high,
        "SEVERITY_MED_THRESHOLD": new_med
    }
    
    old_thresholds = {
        "SEVERITY_HIGH_THRESHOLD": old_high,
        "SEVERITY_MED_THRESHOLD": old_med
    }
    
    # Save the recalibrated configuration
    THRESHOLDS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(THRESHOLDS_PATH, "w") as f:
        json.dump(new_thresholds, f, indent=4)
        
    return old_thresholds, new_thresholds, len(records)
