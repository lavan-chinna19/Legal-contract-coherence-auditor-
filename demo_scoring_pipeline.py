"""
demo_scoring_pipeline.py — Demonstration and sanity check for Dual-Channel Scoring.
Runs on 3 real documents (2 clean SEC EDGAR contracts + 1 synthetically shuffled contract)
to verify non-degenerate score distributions and Channel B sensitivity to structural shuffling.
"""
import random
from pathlib import Path
import numpy as np

from src.config import EDGAR_RAW_DIR, ClauseRecord
from src.segmentation.factory import get_segmenter
from src.scoring.pipeline import DualChannelScorer
from src.scoring.diagnostics import format_diagnostics_report


def run_demo():
    print("=" * 68)
    print("DEMO: Dual-Channel Scoring Pipeline & Diagnostics (Prompt 6)")
    print("=" * 68)

    segmenter = get_segmenter("v1")
    txt_files = list(EDGAR_RAW_DIR.glob("*.txt"))
    if len(txt_files) < 2:
        print("ERROR: Not enough SEC EDGAR contracts found.")
        return

    # Document 1: Clean contract
    doc1_path = txt_files[0]
    with open(doc1_path, "r", encoding="utf-8") as f:
        doc1_clauses = segmenter.segment(f.read(), doc_id=doc1_path.stem)[:15]

    # Document 2: Clean contract
    doc2_path = txt_files[1]
    with open(doc2_path, "r", encoding="utf-8") as f:
        doc2_clauses = segmenter.segment(f.read(), doc_id=doc2_path.stem)[:15]

    # Document 3: Synthetically shuffled document
    # Take clean doc1 clauses and shuffle indices 4..10
    doc3_clauses = []
    for c in doc1_clauses:
        # Clone clause
        doc3_clauses.append(ClauseRecord(
            clause_id=f"shuffled_{c.sequence_idx}",
            doc_id="synthetic_shuffled_doc",
            text=c.text,
            label=c.label,
            sequence_idx=c.sequence_idx,
            char_start=c.char_start,
            char_end=c.char_end,
            source="synthetic_shuffled"
        ))

    # Inject shuffle anomaly between indices 4 and 10
    rng = random.Random(42)
    shuffled_segment = doc3_clauses[4:11]
    rng.shuffle(shuffled_segment)
    # Reassign sequence indices to reflect new unnatural order
    for idx, clause in enumerate(shuffled_segment, start=4):
        clause.sequence_idx = idx
    doc3_clauses[4:11] = shuffled_segment

    scorer = DualChannelScorer()

    documents = [
        ("Clean Contract 1", doc1_clauses),
        ("Clean Contract 2", doc2_clauses),
        ("Synthetic Shuffled Contract", doc3_clauses),
    ]

    all_results = []

    for name, clauses in documents:
        print(f"\n" + "-" * 68)
        print(f"Scoring: {name} ({len(clauses)} clauses)")
        print("-" * 68)

        res = scorer.score_document(clauses, doc_id=clauses[0].doc_id)
        all_results.append((name, res))

        print(f"  Total Clauses:        {res.total_clauses}")
        print(f"  Anomalies Detected:   {res.anomaly_count}")
        print(f"  High Severity:        {res.high_severity_count}")
        print(f"  Medium Severity:      {res.medium_severity_count}")
        print(f"  Mean Combined Score:  {res.mean_combined_score:.4f}")
        print(f"  Max Combined Score:   {res.max_combined_score:.4f}")

        # Non-degenerate check
        scores_a = [c.channel_a_score for c in res.clauses]
        scores_b = [c.channel_b_score for c in res.clauses]
        comb = [c.combined_score for c in res.clauses]

        print(f"  Channel A range:      [{min(scores_a):.4f}, {max(scores_a):.4f}] (std: {np.std(scores_a):.4f})")
        print(f"  Channel B range:      [{min(scores_b):.4f}, {max(scores_b):.4f}] (std: {np.std(scores_b):.4f})")
        print(f"  Combined range:       [{min(comb):.4f}, {max(comb):.4f}] (std: {np.std(comb):.4f})")

    # Sanity Check Comparison on Document 3 (Shuffled in Doc 3 vs Clean in Doc 1)
    clean_res = all_results[0][1]
    shuffled_res = all_results[2][1]
    shuffled_clause_scores = [c.channel_b_score for c in shuffled_res.clauses if 4 <= c.sequence_idx <= 10]
    clean_clause_scores = [c.channel_b_score for c in clean_res.clauses if 4 <= c.sequence_idx <= 10]

    mean_shuffled_b = float(np.mean(shuffled_clause_scores))
    mean_clean_b = float(np.mean(clean_clause_scores))

    print("\n" + "=" * 68)
    print("GATE 2 SANITY CHECK: Channel B Sensitivity on Shuffled Clauses")
    print("=" * 68)
    print(f"Mean Channel B Anomaly on Shuffled Clauses (in Doc 3):   {mean_shuffled_b:.4f}")
    print(f"Mean Channel B Anomaly on Clean Clauses    (in Doc 1):   {mean_clean_b:.4f}")
    print(f"Difference (Shuffled - Clean):                            {mean_shuffled_b - mean_clean_b:+.4f}")

    # Display Diagnostics Report for Document 3
    print("\n" + "=" * 68)
    print("GATE 3 DIAGNOSTICS REPORT SAMPLE")
    print("=" * 68)
    md_report = format_diagnostics_report(shuffled_res, format_type="markdown")
    print(md_report[:1200] + "\n... [Report truncated for display] ...")

    return all_results


if __name__ == "__main__":
    run_demo()
