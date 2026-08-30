"""
evaluate_ensemble.py - Prompt 8 Evaluation script.
Runs the SAME validation methodology as Prompt 6:
- Delta anomaly increase on shuffled vs clean clauses.
Evaluates:
- Fine-Tuned only (alpha = 1.0)
- Zero-Shot only (alpha = 0.0)
- Combined (alpha = 0.5)
- Combined (alpha = 0.25)
- Combined (alpha = 0.75)
"""
import sys
import numpy as np
from pathlib import Path

from src.config import EDGAR_RAW_DIR, ClauseRecord
from src.segmentation.factory import get_segmenter
from src.scoring.ensemble import ChannelBEnsembler

def evaluate():
    segmenter = get_segmenter("v1")
    txt_files = list(EDGAR_RAW_DIR.glob("*.txt"))
    if len(txt_files) < 2:
        print("FAIL: Insufficient EDGAR files found.")
        sys.exit(1)

    # 1. Prepare 3 documents (Same as Prompt 6)
    doc1_clauses = segmenter.segment(open(txt_files[0], encoding="utf-8").read(), doc_id=txt_files[0].stem)[:16]
    doc2_clauses = segmenter.segment(open(txt_files[1], encoding="utf-8").read(), doc_id=txt_files[1].stem)[:16]
    
    doc3_clauses = [
        ClauseRecord(
            clause_id=f"shuf_{c.sequence_idx}",
            doc_id="synthetic_shuffled_doc",
            text=c.text,
            label=c.label,
            sequence_idx=c.sequence_idx,
            char_start=c.char_start,
            char_end=c.char_end,
            source="synthetic"
        )
        for c in doc1_clauses
    ]
    import random
    rng = random.Random(123)
    shuffled_block = list(doc3_clauses[4:12])
    rng.shuffle(shuffled_block)
    doc3_clauses[4:12] = shuffled_block
    for i, c in enumerate(doc3_clauses):
        c.sequence_idx = i

    alphas_to_test = [1.0, 0.0, 0.5, 0.25, 0.75]
    modes = {
        1.0: "fine_tuned",
        0.0: "zero_shot",
        0.5: "combined",
        0.25: "combined",
        0.75: "combined"
    }
    
    # Pre-instantiate to reuse models (saves time)
    # The models themselves are stateless, so we can just create one Ensembler
    # and change its alpha/mode.
    ensembler = ChannelBEnsembler()

    results_table = []
    
    print(f"{'Variant (Mode)':<25} {'Alpha':<10} {'Delta Anomaly (Shuffled - Clean)':<35}")
    print("-" * 75)

    for alpha in alphas_to_test:
        mode = modes[alpha]
        ensembler.mode = mode
        ensembler.alpha = alpha
        
        # We only need doc1 and doc3 for the delta evaluation
        res1 = ensembler.score_document(doc1_clauses, "doc1_clean")
        res3 = ensembler.score_document(doc3_clauses, "doc3_shuffled")
        
        # Compare Channel B anomaly scores on the manipulated clauses (seq 4..11):
        shuffled_b_doc3 = [c.combined_score for c in res3.clauses if 4 <= c.sequence_idx <= 11]
        clean_b_doc1 = [c.combined_score for c in res1.clauses if 4 <= c.sequence_idx <= 11]
        
        mean_shuffled = float(np.mean(shuffled_b_doc3))
        mean_clean = float(np.mean(clean_b_doc1))
        delta = mean_shuffled - mean_clean
        
        variant_name = f"{mode} (a={alpha})"
        if alpha == 1.0: variant_name = "Fine-tuned only"
        if alpha == 0.0: variant_name = "Zero-shot only"
        if alpha == 0.5: variant_name = "Combined default"
        
        print(f"{variant_name:<25} {alpha:<10.2f} {delta:<35.4f}")
        results_table.append((variant_name, alpha, delta))

    print("\nIMPROVEMENT CHECK:")
    ft_delta = next(d for v, a, d in results_table if a == 1.0)
    zs_delta = next(d for v, a, d in results_table if a == 0.0)
    comb_delta = next(d for v, a, d in results_table if a == 0.5)
    
    print(f"Fine-tuned only delta: {ft_delta:+.4f}")
    print(f"Zero-shot only delta:  {zs_delta:+.4f}")
    print(f"Combined delta (a=0.5):{comb_delta:+.4f}")
    
    if comb_delta > ft_delta:
        print("\nCombined > Fine-tuned-only")
        print("YES, improvement was demonstrated.")
    else:
        print("\nCombined <= Fine-tuned-only")
        print("Combined ensemble did not improve over the stronger baseline.")

if __name__ == "__main__":
    evaluate()
