import sys
from src.segmentation.factory import get_segmenter
from src.config import ClauseRecord
from dataclasses import asdict

def main():
    text = (
        "This Agreement is made on January 1, 2023.\n"
        "1. Definitions.\n"
        "In this agreement, 'Company' means XYZ.\n"
        "2. Payment.\n"
        "The client will pay within 30 days."
    )
    
    print("--- RAW CONTRACT TEXT INPUT ---")
    print(text)
    print("-------------------------------\n")

    print("=== INSTANTIATING V1 VIA CONFIGURATION ===")
    seg_v1 = get_segmenter("v1")
    print(f"Segmenter Instance: {type(seg_v1).__name__}")
    
    print("\n=== INSTANTIATING V2 VIA CONFIGURATION ===")
    seg_v2 = get_segmenter("v2")
    print(f"Segmenter Instance: {type(seg_v2).__name__}")

    print("\n=== RUNNING V1 ===")
    clauses_v1 = seg_v1.segment(text, doc_id="test_doc")
    print(f"V1 Output count: {len(clauses_v1)}")
    for idx, c in enumerate(clauses_v1):
        print(f"Clause {idx + 1}:")
        print(asdict(c))
        assert isinstance(c, ClauseRecord)

    print("\n=== RUNNING V2 ===")
    clauses_v2 = seg_v2.segment(text, doc_id="test_doc")
    print(f"V2 Output count: {len(clauses_v2)}")
    for idx, c in enumerate(clauses_v2):
        print(f"Clause {idx + 1}:")
        print(asdict(c))
        assert isinstance(c, ClauseRecord)
        
    print("\n=== SCHEMA VERIFICATION ===")
    print("Both v1 and v2 successfully returned lists of ClauseRecord objects with identical schemas.")
    
if __name__ == "__main__":
    main()
