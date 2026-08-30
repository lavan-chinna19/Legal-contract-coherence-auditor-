"""
verify_pair_sampling.py — Verification script for Acceptance Gate 1:
Demonstrates training-pair construction on full SEC EDGAR documents with exact sampling counts.
"""
import os
import json
from pathlib import Path
from src.config import EDGAR_RAW_DIR, ClauseRecord
from src.segmentation.factory import get_segmenter
from src.coherence.pair_sampler import CoherencePairSampler


def run_verification():
    print("=" * 60)
    print("GATE 1 VERIFICATION: Training-Pair Construction & Negative Sampling")
    print("=" * 60)

    # 1. Segment at least 2 full SEC EDGAR documents
    segmenter = get_segmenter("v1")
    txt_files = list(EDGAR_RAW_DIR.glob("*.txt"))
    if not txt_files:
        print("ERROR: No EDGAR contracts found in data/raw/sec_edgar/")
        return

    doc_clauses_map = {}
    total_clauses = 0

    print("\n--- 1. Ingesting & Segmenting Sample Contracts ---")
    for txt_path in txt_files[:3]:
        doc_id = txt_path.stem
        with open(txt_path, "r", encoding="utf-8") as f:
            text = f.read()
        clauses = segmenter.segment(text, doc_id=doc_id)
        doc_clauses_map[doc_id] = clauses
        total_clauses += len(clauses)
        print(f"Document: {doc_id} | Character Length: {len(text):,} | Clauses Extracted: {len(clauses)}")

    # 2. Sample Pairs on First Document
    doc_1_id = list(doc_clauses_map.keys())[0]
    doc_1_clauses = doc_clauses_map[doc_1_id]

    sampler = CoherencePairSampler(easy_neg_ratio=1.0, hard_neg_ratio=1.0, seed=42)
    single_doc_pairs = sampler.sample_document_pairs(doc_1_clauses, all_docs_clauses=doc_clauses_map)

    pos_single = [p for p in single_doc_pairs if p.pair_type == "positive"]
    hard_single = [p for p in single_doc_pairs if p.pair_type == "hard_negative"]
    easy_single = [p for p in single_doc_pairs if p.pair_type == "easy_negative"]

    print(f"\n--- 2. Single Document Sampling Verification ({doc_1_id}) ---")
    print(f"Total Clauses in Document: {len(doc_1_clauses)}")
    print(f"Consecutive Positive Pairs (c_i, c_{{i+1}}): {len(pos_single)} (Expected: {len(doc_1_clauses) - 1})")
    print(f"Hard Negative Pairs (Shuffle/Jump/Reverse): {len(hard_single)} (Ratio: 1.0 -> {len(hard_single)} / {len(pos_single)})")
    print(f"Easy Negative Pairs (Cross-Document):      {len(easy_single)} (Ratio: 1.0 -> {len(easy_single)} / {len(pos_single)})")
    print(f"Total Pairs Generated for Document:        {len(single_doc_pairs)}")

    assert len(pos_single) == len(doc_1_clauses) - 1, "Positive count mismatch!"
    assert len(hard_single) == len(pos_single), "Hard negative count mismatch!"
    assert len(easy_single) == len(pos_single), "Easy negative count mismatch!"

    # 3. Sample Dataset Across All 3 Documents
    all_clauses = []
    for clist in doc_clauses_map.values():
        all_clauses.extend(clist)

    dataset_pairs = sampler.sample_dataset(all_clauses)
    total_pos = [p for p in dataset_pairs if p.pair_type == "positive"]
    total_hard = [p for p in dataset_pairs if p.pair_type == "hard_negative"]
    total_easy = [p for p in dataset_pairs if p.pair_type == "easy_negative"]

    print("\n--- 3. Multi-Document Dataset Aggregate Counts ---")
    print(f"Total Combined Clauses: {len(all_clauses)}")
    print(f"Total Positive Pairs:   {len(total_pos)}")
    print(f"Total Hard Negatives:   {len(total_hard)}")
    print(f"Total Easy Negatives:   {len(total_easy)}")
    print(f"Total Dataset Size:     {len(dataset_pairs)}")

    # 4. Display Sample Formats
    print("\n--- 4. Sample Pair Inspections ---")
    for ptype, pair_list in [("POSITIVE", total_pos), ("HARD NEGATIVE", total_hard), ("EASY NEGATIVE", total_easy)]:
        p = pair_list[0]
        print(f"\n[{ptype}]")
        print(f"  Clause A ({p.doc_id_a}, seq={p.clause_a.sequence_idx}): {p.clause_a.text[:80]}...")
        print(f"  Clause B ({p.doc_id_b}, seq={p.clause_b.sequence_idx}): {p.clause_b.text[:80]}...")
        print(f"  Target Label: {p.label}")

    print("\n" + "=" * 60)
    print("STATUS: PASS (Acceptance Gate 1 Verified)")
    print("=" * 60)


if __name__ == "__main__":
    run_verification()
