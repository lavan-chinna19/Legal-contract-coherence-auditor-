import os
import glob
from src.segmentation.factory import get_segmenter
from src.segmentation.eval import evaluate_segmentation, save_evaluation_fixture
from src.config import EDGAR_RAW_DIR
from pathlib import Path

def main():
    print("--- GATE 1: Validating V1 on SEC EDGAR ---")
    files = glob.glob(str(EDGAR_RAW_DIR / "*.txt"))
    if not files:
        print("No SEC EDGAR files found. Run data ingestion first.")
        return
        
    print(f"Found {len(files)} EDGAR documents.")
    
    seg_v1 = get_segmenter("v1")
    
    processed = 0
    failed = 0
    total_clauses = 0
    
    for f in files:
        with open(f, "r", encoding="utf-8") as file:
            text = file.read()
        
        try:
            doc_id = Path(f).stem
            clauses = seg_v1.segment(text, doc_id=doc_id)
            processed += 1
            total_clauses += len(clauses)
        except Exception as e:
            failed += 1
            print(f"Failed to segment {f}: {e}")
            
    print(f"Documents processed: {processed}")
    print(f"Documents failed: {failed}")
    print(f"Total clauses identified: {total_clauses}")
    
    # Let's mock a gold standard for a single document to produce evaluation metrics (GATE 2)
    print("\n--- GATE 2: Evaluating V1 metrics ---")
    if processed > 0:
        print("STATUS: UNVERIFIED")
        print("REASON: A genuinely defensible held-out evaluation set using real available labels is not present. Rather than fabricating human labels, real segmentation evaluation is marked UNVERIFIED.")
        
        # We retain the synthetic fixture only as a unit test for the harness itself
        with open(files[0], "r", encoding="utf-8") as file:
            raw_text = file.read()
        
        doc_id = Path(files[0]).stem
        pred = seg_v1.segment(raw_text, doc_id=doc_id)
        
        import copy
        gold = copy.deepcopy(pred)
        if len(gold) > 1:
            gold.pop() # remove one to test recall
            
        metrics = evaluate_segmentation(pred, gold)
        
        fixture_path = Path("fixtures/segmentation_v1_metrics.json")
        fixture_data = {
            "dataset": "UNIT_TEST_SYNTHETIC_GOLD",
            "sample_size": 1,
            "model": "v1_rule_based",
            "evaluation_method": "offset_tolerance_10",
            "metrics": metrics,
            "status": "UNVERIFIED"
        }
        save_evaluation_fixture(fixture_data, fixture_path)
        print(f"Saved UNIT-TEST synthetic metrics fixture to {fixture_path}")
        
    print("\n--- GATE 3: Configuration Interchangeability ---")
    try:
        seg_v2 = get_segmenter("v2")
        print("V2 STATUS: NOT COMPLETED / PARTIAL")
        print("BLOCKER: Real BIO model (CRF/Transformer) was not trained. V2 is currently just heuristic sentence/line splitting for interface testing.")
        
        print("\nTesting Interchangeability Interface...")
        v2_pred = seg_v2.segment("This is a simple test.", doc_id="test2")
        print(f"V2 identified {len(v2_pred)} clauses in the simple test.")
    except Exception as e:
        print(f"Failed to run V2: {e}")

if __name__ == "__main__":
    main()
