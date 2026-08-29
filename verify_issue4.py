import sys
from src.segmentation.factory import get_segmenter

def verify_interface_guarantees(segmenter_id, text):
    print(f"\n--- Verifying Interface Guarantees for {segmenter_id.upper()} ---")
    seg = get_segmenter(segmenter_id)
    clauses = seg.segment(text, doc_id="test_doc")
    
    # Check 1: Valid offsets and stored text equals raw_text[start:end]
    valid_offsets = True
    for idx, c in enumerate(clauses):
        extracted = text[c.char_start:c.char_end].strip()
        if extracted != c.text.strip():
            print(f"ERROR: Offset mismatch for clause {idx}. Stored: {repr(c.text)}, Extracted: {repr(extracted)}")
            valid_offsets = False
            
    if valid_offsets:
        print("[OK] Offsets are valid and text perfectly matches raw_text[start:end].")
        
    # Check 2: Clause order is preserved
    order_preserved = all(clauses[i].char_start <= clauses[i+1].char_start for i in range(len(clauses)-1))
    if order_preserved:
        print("[OK] Clause order is preserved strictly.")
    else:
        print("ERROR: Clause order is NOT preserved.")
        
    # Check 3: Unexpected overlaps are absent
    no_overlaps = True
    for i in range(len(clauses)-1):
        if clauses[i].char_end > clauses[i+1].char_start:
            print(f"ERROR: Overlap between clause {i} and {i+1}")
            no_overlaps = False
            
    if no_overlaps:
        print("[OK] Unexpected overlaps are absent.")
        
def main():
    text = (
        "This Agreement is made on January 1, 2023.\n"
        "1. Definitions.\n"
        "In this agreement, 'Company' means XYZ.\n"
        "2. Payment.\n"
        "The client will pay within 30 days."
    )
    verify_interface_guarantees("v1", text)
    verify_interface_guarantees("v2", text)

if __name__ == "__main__":
    main()
