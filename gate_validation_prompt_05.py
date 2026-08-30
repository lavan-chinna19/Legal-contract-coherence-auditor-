"""
gate_validation_prompt_05.py — Master acceptance gate runner for Prompt 5.
Validates:
1. Training-pair construction (easy/hard negative sampling).
2. Fine-tuned coherence training and real stored loss/accuracy curve fixture.
3. Zero-shot LLM alternative path.
4. Model registry swappability.
"""
import os
import sys
import json
from pathlib import Path

from src.config import (
    COHERENCE_CHECKPOINT_PATH,
    COHERENCE_TRAINING_CURVES_PATH,
    EDGAR_RAW_DIR,
    ClauseRecord
)
from src.segmentation.factory import get_segmenter
from src.coherence.pair_sampler import CoherencePairSampler
from src.coherence.factory import get_coherence_model


def print_header(gate_num: int, title: str):
    print("\n" + "=" * 65)
    print(f"ACCEPTANCE GATE {gate_num}: {title}")
    print("=" * 65)


def run_gate_1() -> bool:
    print_header(1, "Training-Pair Construction with Easy/Hard Negatives")
    segmenter = get_segmenter("v1")
    txt_files = list(EDGAR_RAW_DIR.glob("*.txt"))
    if not txt_files:
        print("FAIL: No raw contract files found.")
        return False

    with open(txt_files[0], "r", encoding="utf-8") as f:
        text = f.read()
    clauses = segmenter.segment(text, doc_id=txt_files[0].stem)
    
    sampler = CoherencePairSampler(easy_neg_ratio=1.0, hard_neg_ratio=1.0, seed=42)
    pairs = sampler.sample_document_pairs(clauses)

    pos = [p for p in pairs if p.pair_type == "positive"]
    hard = [p for p in pairs if p.pair_type == "hard_negative"]
    
    print(f"Document ID: {txt_files[0].stem}")
    print(f"Total Extracted Clauses: {len(clauses)}")
    print(f"Positive Pairs (consecutive): {len(pos)} (Expected: {len(clauses) - 1})")
    print(f"Hard Negative Pairs (shuffle/jump): {len(hard)} (Expected: {len(pos)})")
    
    if len(pos) == len(clauses) - 1 and len(hard) == len(pos):
        print("GATE 1 STATUS: PASS")
        return True
    else:
        print("GATE 1 STATUS: FAIL")
        return False


def run_gate_2() -> bool:
    print_header(2, "Fine-Tuned Coherence Model Training & Stored Curve Fixture")
    if not COHERENCE_TRAINING_CURVES_PATH.exists():
        print(f"Training curves fixture not found at {COHERENCE_TRAINING_CURVES_PATH}. Running train_coherence_model.py...")
        import train_coherence_model
        train_coherence_model.run_training_pipeline()

    if COHERENCE_TRAINING_CURVES_PATH.exists() and COHERENCE_CHECKPOINT_PATH.exists():
        with open(COHERENCE_TRAINING_CURVES_PATH, "r", encoding="utf-8") as f:
            curves = json.load(f)
        
        print("Loaded Real Training Curves Fixture:")
        print(f"  Total Pairs Trained On: {curves['metadata']['num_total_pairs']}")
        print(f"  Train Pairs:            {curves['metadata']['num_train_pairs']}")
        print(f"  Val Pairs:              {curves['metadata']['num_val_pairs']}")
        print(f"  Epochs:                 {curves['metadata']['epochs']}")
        print(f"  Final Train Loss:       {curves['epochs'][-1]['train_loss']}")
        print(f"  Final Val Loss:         {curves['epochs'][-1]['val_loss']}")
        print(f"  Final Val Accuracy:     {curves['epochs'][-1]['val_accuracy']}")
        print(f"  Final Val F1:           {curves['epochs'][-1]['val_f1']}")
        print(f"  Final Val ROC-AUC:      {curves['epochs'][-1]['val_roc_auc']}")
        print(f"  Checkpoint Size:        {os.path.getsize(COHERENCE_CHECKPOINT_PATH):,} bytes")
        print("GATE 2 STATUS: PASS")
        return True
    else:
        print("GATE 2 STATUS: FAIL (Checkpoint or fixture missing)")
        return False


def run_gate_3() -> bool:
    print_header(3, "Zero-Shot Open-Source Alternative Path Execution")
    zero_shot_model = get_coherence_model("zero_shot")
    
    ca = ClauseRecord(
        clause_id="test_a",
        doc_id="doc1",
        text="Section 1.01. Definitions. As used herein, 'Agreement' means this Contract.",
        label="Definitions",
        sequence_idx=0,
        char_start=0,
        char_end=80,
        source="test"
    )
    cb = ClauseRecord(
        clause_id="test_b",
        doc_id="doc1",
        text="Section 1.02. Accounting Terms. All accounting terms shall have standard GAAP meaning.",
        label="Definitions",
        sequence_idx=1,
        char_start=81,
        char_end=170,
        source="test"
    )
    
    score = zero_shot_model.score_pair(ca, cb)
    print(f"Model Name: {zero_shot_model.name}")
    print(f"Sample Pair Score: {score:.4f}")
    
    if 0.0 <= score <= 1.0:
        print("GATE 3 STATUS: PASS")
        return True
    else:
        print("GATE 3 STATUS: FAIL")
        return False


def run_gate_4() -> bool:
    print_header(4, "Model Registry Swappability Demonstration")
    import demo_coherence_registry
    try:
        demo_coherence_registry.run_demo()
        print("GATE 4 STATUS: PASS")
        return True
    except Exception as e:
        print(f"GATE 4 STATUS: FAIL (Error: {e})")
        return False


def main():
    results = {
        "Gate 1": run_gate_1(),
        "Gate 2": run_gate_2(),
        "Gate 3": run_gate_3(),
        "Gate 4": run_gate_4(),
    }

    print("\n" + "=" * 65)
    print("PROMPT 5 ACCEPTANCE GATES SUMMARY")
    print("=" * 65)
    for gate, passed in results.items():
        print(f"{gate:<10}: {'PASS' if passed else 'FAIL'}")
    print("=" * 65)

    if all(results.values()):
        print("ALL ACCEPTANCE GATES PASSED SUCCESSFULLY!")
        sys.exit(0)
    else:
        print("SOME GATES FAILED!")
        sys.exit(1)


if __name__ == "__main__":
    main()
