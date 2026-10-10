import json
import logging
from pathlib import Path
from src.evaluation.completeness import CompletenessChecker
from src.segmentation.factory import get_segmenter
from src.config import EDGAR_RAW_DIR

logging.basicConfig(level=logging.ERROR)

def main():
    segmenter = get_segmenter("v1")
    checker = CompletenessChecker(threshold=0.5)
    
    sec_files = list(EDGAR_RAW_DIR.glob("*.txt"))
    if not sec_files:
        return
        
    test_file = sec_files[0]
    with open(test_file, "r", encoding="utf-8") as f:
        text = f.read()
    
    # Just segment a small portion to make it fast
    clauses = segmenter.segment(text[:10000], doc_id=test_file.stem)
    
    # Original
    res_orig = checker.check_document(test_file.stem, clauses, category="Default")
    present_reports = [r for r in res_orig.reports if r.is_present]
    
    if present_reports:
        target_report = present_reports[0]
        target_type = target_report.expected_type
        target_clause_id = target_report.evidence_clause_id
        
        synthetic_clauses = [c for c in clauses if c.clause_id != target_clause_id]
        synth_doc_id = f"SYNTHETIC DELIBERATE-REMOVAL TEST ({test_file.stem})"
        
        res_synth = checker.check_document(synth_doc_id, synthetic_clauses, category="Default")
        synth_target_report = next(r for r in res_synth.reports if r.expected_type == target_type)
        
        print(f"DELIBERATE REMOVAL TEST:")
        print(f"Clause: {target_type}")
        print(f"Original: PRESENT (Score: {target_report.nli_score:.2f})")
        print(f"Synthetic: {'PRESENT' if synth_target_report.is_present else 'MISSING'} (Score: {synth_target_report.nli_score:.2f})")
    else:
        print("No clauses present in the first 10000 chars.")

if __name__ == "__main__":
    main()
