"""
gate_validation_prompt_06.py — Master acceptance gate runner for Prompt 6.
Validates:
1. Dual channels end-to-end execution on 3 documents with non-degenerate distributions.
2. Channel B sensitivity on synthetically shuffled document (higher anomaly on shuffled clauses).
3. Human-readable diagnostics reporting traceable to raw scores.
"""
import sys
import numpy as np
from pathlib import Path

from src.config import EDGAR_RAW_DIR, ClauseRecord
from src.segmentation.factory import get_segmenter
from src.scoring.pipeline import DualChannelScorer
from src.scoring.diagnostics import format_diagnostics_report


def print_gate(gate_num: int, title: str):
    print("\n" + "=" * 65)
    print(f"ACCEPTANCE GATE {gate_num}: {title}")
    print("=" * 65)


def run_all_gates():
    segmenter = get_segmenter("v1")
    txt_files = list(EDGAR_RAW_DIR.glob("*.txt"))
    if len(txt_files) < 2:
        print("FAIL: Insufficient EDGAR files found.")
        sys.exit(1)

    # Prepare 3 documents
    doc1_clauses = segmenter.segment(open(txt_files[0], encoding="utf-8").read(), doc_id=txt_files[0].stem)[:16]
    doc2_clauses = segmenter.segment(open(txt_files[1], encoding="utf-8").read(), doc_id=txt_files[1].stem)[:16]
    
    # Synthetically shuffled document:
    # First 4 clauses remain strictly consecutive (unshuffled control group)
    # Next 8 clauses are completely scrambled/shuffled (anomalous test group)
    # Remaining clauses remain intact
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

    scorer = DualChannelScorer()

    # --- GATE 1: End-to-end execution & Non-degenerate distributions ---
    print_gate(1, "End-to-End Execution on 3 Documents & Non-Degenerate Distributions")
    res1 = scorer.score_document(doc1_clauses, doc_id="doc1_clean")
    res2 = scorer.score_document(doc2_clauses, doc_id="doc2_clean")
    res3 = scorer.score_document(doc3_clauses, doc_id="doc3_shuffled")

    gate1_passed = True
    for name, r in [("Doc 1 Clean", res1), ("Doc 2 Clean", res2), ("Doc 3 Shuffled", res3)]:
        sc_a = [c.channel_a_score for c in r.clauses]
        sc_b = [c.channel_b_score for c in r.clauses]
        std_a = np.std(sc_a)
        std_b = np.std(sc_b)
        print(f"{name}: Total Clauses={r.total_clauses} | Mean Combined={r.mean_combined_score:.4f} | Std A={std_a:.4f} | Std B={std_b:.4f}")
        # Ensure variance exists (not all-identical or degenerate)
        if std_a < 1e-4 or std_b < 1e-4:
            gate1_passed = False

    if gate1_passed:
        print("GATE 1 STATUS: PASS (Distributions are non-degenerate and varied)")
    else:
        print("GATE 1 STATUS: FAIL (Scores are degenerate)")

    # --- GATE 2: Sanity Check on Shuffled Clauses ---
    print_gate(2, "Channel B Sensitivity Sanity Check on Shuffled vs Unshuffled Clauses")
    # Compare Channel B anomaly scores on the manipulated clauses (seq 4..11):
    # Shuffled version (in doc3) vs Clean Unshuffled version (in doc1)
    shuffled_b_doc3 = [c.channel_b_score for c in res3.clauses if 4 <= c.sequence_idx <= 11]
    clean_b_doc1 = [c.channel_b_score for c in res1.clauses if 4 <= c.sequence_idx <= 11]

    mean_shuffled = float(np.mean(shuffled_b_doc3))
    mean_clean = float(np.mean(clean_b_doc1))

    print(f"Mean Channel B Anomaly on Shuffled Clauses (in Doc 3): {mean_shuffled:.4f}")
    print(f"Mean Channel B Anomaly on Clean Clauses    (in Doc 1): {mean_clean:.4f}")
    print(f"Delta Anomaly Increase (Shuffled - Clean):             {mean_shuffled - mean_clean:+.4f}")

    gate2_passed = mean_shuffled > mean_clean
    if gate2_passed:
        print("GATE 2 STATUS: PASS (Channel B is visibly higher on shuffled clauses than clean ones)")
    else:
        print("GATE 2 STATUS: FAIL")

    # --- GATE 3: Diagnostics Report Traceability ---
    print_gate(3, "Diagnostics Report Traceability & Human-Readability")
    report_md = format_diagnostics_report(res3, format_type="markdown")
    has_header = "# Contract Anomaly Audit Report" in report_md
    has_table = "| Seq | Clause ID | Score A (OOD) |" in report_md
    has_evidence = "Nearest Centroid" in report_md and "Trans Probs" in report_md

    print("Diagnostics Markdown Report Sample:")
    print("-" * 50)
    print("\n".join(report_md.split("\n")[:18]))
    print("-" * 50)

    gate3_passed = has_header and has_table and has_evidence
    if gate3_passed:
        print("GATE 3 STATUS: PASS (Report is well-structured and fully traceable)")
    else:
        print("GATE 3 STATUS: FAIL")

    # Summary
    print("\n" + "=" * 65)
    print("PROMPT 6 ACCEPTANCE GATES SUMMARY")
    print("=" * 65)
    print(f"Gate 1 (End-to-End Distributions):  {'PASS' if gate1_passed else 'FAIL'}")
    print(f"Gate 2 (Shuffled Sensitivity):      {'PASS' if gate2_passed else 'FAIL'}")
    print(f"Gate 3 (Diagnostics Report):        {'PASS' if gate3_passed else 'FAIL'}")
    print("=" * 65)

    if gate1_passed and gate2_passed and gate3_passed:
        print("ALL ACCEPTANCE GATES PASSED SUCCESSFULLY!")
        sys.exit(0)
    else:
        print("SOME GATES FAILED!")
        sys.exit(1)


if __name__ == "__main__":
    run_all_gates()
