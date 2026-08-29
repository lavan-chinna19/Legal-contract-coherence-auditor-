import glob
import sys
from pathlib import Path
from src.config import EDGAR_RAW_DIR
from src.segmentation.factory import get_segmenter

def main():
    print("--- SEC EDGAR V1 VALIDATION SCRIPT (WITH HTML CLEANING) ---")
    
    files = glob.glob(str(EDGAR_RAW_DIR / "*.txt"))
    if not files:
        print("No SEC EDGAR files found. Ensure data has been ingested.")
        sys.exit(1)
        
    print(f"1. Number of SEC documents discovered: {len(files)}")
    
    seg = get_segmenter("v1")
    
    processed = 0
    failed = 0
    total_clauses = 0
    representative_outputs = []
    
    for idx, f in enumerate(files):
        try:
            with open(f, "r", encoding="utf-8") as file:
                raw_text = file.read()
                
            doc_id = Path(f).stem
            clauses = seg.segment(raw_text, doc_id=doc_id)
            
            processed += 1
            clause_count = len(clauses)
            total_clauses += clause_count
            
            if idx == 0:
                print("\n--- DATA FLOW TRACE ---")
                print("RAW TEXT BEFORE PREPROCESSING (First 200 chars):")
                print(repr(raw_text[:200]))
                print("\nCLEANED TEXT ACTUALLY PASSED TO SEGMENTER (First 200 chars):")
                print(repr(seg._clean_html(raw_text)[:200]))
                print(f"\nEXACT CLAUSE COUNT FOR THIS DOCUMENT: {clause_count}")
                print("-----------------------")
            
            # Keep a couple of documents for manual inspection
            if len(representative_outputs) < 3 and clause_count > 0:
                representative_outputs.append((doc_id, clauses[:5])) # First 5 clauses
                
        except Exception as e:
            failed += 1
            print(f"Failed on {f}: {str(e)}")
            
    print(f"\n2. Number successfully processed: {processed}")
    print(f"3. Number failed: {failed}")
    
    print(f"\n4. Clause count summary:")
    print(f"   Total clauses extracted: {total_clauses}")
    print(f"   Average clauses per document: {total_clauses / processed if processed else 0:.1f}")
    
    print("\n7. Representative segmentation outputs for manual inspection:")
    for doc_id, clauses in representative_outputs:
        print(f"\nDocument ID: {doc_id}")
        for i, c in enumerate(clauses):
            text_preview = c.text[:150].replace('\n', ' ') + ('...' if len(c.text) > 150 else '')
            print(f"  Clause {i+1} [{c.label}]: {text_preview}")

if __name__ == "__main__":
    main()
