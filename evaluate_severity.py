"""
evaluate_severity.py — End-to-End Decision-Support Severity Ranking Evaluation (Prompt 10).

Work Package C & Acceptance Gates 1 & 2:
- Runs DualChannelScorer end-to-end across SEC EDGAR sample documents.
- Evaluates a deliberately corrupted document (shuffled transitions & OOD insertions).
- Demonstrates Acceptance Gate 2: Corrupted clauses receive High/Medium severity at a strictly higher rate than clean clauses.
- Persists summary metrics to fixtures/severity_metrics.json.
"""
import os
import sys
import json
import time
from pathlib import Path
from typing import List, Dict, Any

from src.config import EDGAR_RAW_DIR, ClauseRecord
from src.segmentation.factory import get_segmenter
from src.calibration.conformal import ConformalCalibrator
from src.scoring.pipeline import DualChannelScorer
from src.scoring.diagnostics import format_diagnostics_markdown


def run_severity_evaluation():
    print("=" * 80, flush=True)
    print("  PROMPT 10: DECISION-SUPPORT SEVERITY RANKING EVALUATION", flush=True)
    print("=" * 80, flush=True)

    # 1. Discover all SEC EDGAR sample documents
    segmenter = get_segmenter("v1")
    txt_files = sorted(list(EDGAR_RAW_DIR.glob("*.txt")))
    if not txt_files:
        print("FAIL: No EDGAR sample documents found in data/raw/edgar_samples/", flush=True)
        sys.exit(1)

    print(f"\n[1/4] Discovered {len(txt_files)} SEC EDGAR sample documents in {EDGAR_RAW_DIR}:", flush=True)
    eval_files = txt_files[:10]
    for f in eval_files:
        print(f"  - {f.name}", flush=True)

    # 2. Load Conformal Calibrator state if available
    calibrator = None
    state_path = Path("fixtures/conformal_calibration_fixture.json")
    if state_path.exists():
        try:
            calibrator = ConformalCalibrator.from_state_file(state_path)
            print(f"\n[2/4] Loaded ConformalCalibrator state from {state_path} (Target: {calibrator.target_coverage*100:.1f}%)", flush=True)
        except Exception as e:
            print(f"Warning: Could not load calibrator ({e}), proceeding without CI.", flush=True)
    else:
        print("\n[2/4] No calibrator fixture found; proceeding with uncalibrated bounds.", flush=True)

    scorer = DualChannelScorer(calibrator=calibrator)

    # 3. Process clean SEC EDGAR sample documents (Acceptance Gate 1)
    print("\n[3/4] Running DualChannelScorer end-to-end on clean EDGAR sample documents (Gate 1)...", flush=True)
    clean_results: List[Dict[str, Any]] = []
    total_clean_clauses = 0
    clean_high = 0
    clean_med = 0
    clean_low = 0
    clean_clean = 0

    for f in eval_files:
        text = open(f, encoding="utf-8").read()
        clauses = segmenter.segment(text, doc_id=f.stem)[:12]  # First 12 clauses per document
        if not clauses:
            continue
        doc_res = scorer.score_document(clauses, doc_id=f.stem)
        total_clean_clauses += doc_res.total_clauses
        clean_high += doc_res.high_severity_count
        clean_med += doc_res.medium_severity_count
        for c in doc_res.clauses:
            if c.severity == "LOW":
                clean_low += 1
            elif c.severity == "CLEAN":
                clean_clean += 1
        clean_results.append({
            "doc_id": doc_res.doc_id,
            "clauses": doc_res.total_clauses,
            "anomalies": doc_res.anomaly_count,
            "high": doc_res.high_severity_count,
            "med": doc_res.medium_severity_count,
            "mean_score": doc_res.mean_combined_score
        })
        print(f"  - {f.stem}: {doc_res.total_clauses} clauses -> High={doc_res.high_severity_count}, Med={doc_res.medium_severity_count}, Low={sum(1 for c in doc_res.clauses if c.severity=='LOW')}, Clean={sum(1 for c in doc_res.clauses if c.severity=='CLEAN')}, Mean={doc_res.mean_combined_score:.3f}", flush=True)

    print(f"\n  [PASS] Acceptance Gate 1: Successfully processed {len(clean_results)} clean documents ({total_clean_clauses} total clauses) without crashes.")
    print(f"  Clean Dataset Summary: High={clean_high}, Med={clean_med}, Low={clean_low}, Clean={clean_clean} (Overall Clean Flag Rate: {(clean_high+clean_med)/max(1, total_clean_clauses)*100:.1f}%)")

    # 4. Construct and Score Deliberately Corrupted Document (Acceptance Gate 2)
    print("\n[4/4] Evaluating Deliberately Corrupted Contract (Acceptance Gate 2)...", flush=True)
    base_file = txt_files[0]
    base_text = open(base_file, encoding="utf-8").read()
    base_clauses = segmenter.segment(base_text, doc_id="corrupted_doc")[:8]

    # Create corrupted document:
    # - Clause 0: Clean original
    # - Clause 1 & 2: Swapped / reversed order (transition corruption)
    # - Clause 3: Injected Out-of-Distribution non-legal recipe text (semantic OOD corruption)
    # - Clause 4 & 5: Reversed order (transition corruption)
    # - Clause 6 & 7: Clean original
    corrupted_clauses: List[ClauseRecord] = []
    known_bad_indices = {1, 2, 3, 4, 5}

    corrupted_clauses.append(ClauseRecord(
        clause_id="corrupt_c00", doc_id="corrupted_contract", sequence_idx=0,
        text=base_clauses[0].text, label="Clean_Base",
        char_start=0, char_end=len(base_clauses[0].text), source="sec_edgar"
    ))
    # Inverted transition
    corrupted_clauses.append(ClauseRecord(
        clause_id="corrupt_c01_shuffled", doc_id="corrupted_contract", sequence_idx=1,
        text=base_clauses[2].text, label="Shuffled_Transition",
        char_start=0, char_end=len(base_clauses[2].text), source="synthetic_shuffle"
    ))
    corrupted_clauses.append(ClauseRecord(
        clause_id="corrupt_c02_shuffled", doc_id="corrupted_contract", sequence_idx=2,
        text=base_clauses[1].text, label="Shuffled_Transition",
        char_start=0, char_end=len(base_clauses[1].text), source="synthetic_shuffle"
    ))
    # Injected OOD recipe
    ood_text = "Preheat the oven to 375 degrees Fahrenheit. Mix two cups of flour, one cup of sugar, and one teaspoon of baking soda in a large mixing bowl."
    corrupted_clauses.append(ClauseRecord(
        clause_id="corrupt_c03_ood", doc_id="corrupted_contract", sequence_idx=3,
        text=ood_text, label="Injected_OOD",
        char_start=0, char_end=len(ood_text), source="synthetic_ood"
    ))
    # Inverted transition
    corrupted_clauses.append(ClauseRecord(
        clause_id="corrupt_c04_shuffled", doc_id="corrupted_contract", sequence_idx=4,
        text=base_clauses[5].text, label="Shuffled_Transition",
        char_start=0, char_end=len(base_clauses[5].text), source="synthetic_shuffle"
    ))
    corrupted_clauses.append(ClauseRecord(
        clause_id="corrupt_c05_shuffled", doc_id="corrupted_contract", sequence_idx=5,
        text=base_clauses[4].text, label="Shuffled_Transition",
        char_start=0, char_end=len(base_clauses[4].text), source="synthetic_shuffle"
    ))
    # Clean tail
    corrupted_clauses.append(ClauseRecord(
        clause_id="corrupt_c06_clean", doc_id="corrupted_contract", sequence_idx=6,
        text=base_clauses[6].text, label="Clean_Base",
        char_start=0, char_end=len(base_clauses[6].text), source="sec_edgar"
    ))
    corrupted_clauses.append(ClauseRecord(
        clause_id="corrupt_c07_clean", doc_id="corrupted_contract", sequence_idx=7,
        text=base_clauses[7].text, label="Clean_Base",
        char_start=0, char_end=len(base_clauses[7].text), source="sec_edgar"
    ))

    corrupt_res = scorer.score_document(corrupted_clauses, doc_id="corrupted_contract_demo")

    # Tally metrics for Acceptance Gate 2
    corrupt_bad_high_med = 0
    corrupt_bad_total = len(known_bad_indices)
    corrupt_clean_high_med = 0
    corrupt_clean_total = len(corrupted_clauses) - len(known_bad_indices)

    print("\n  Per-Clause Audit for Corrupted Document:")
    print("  " + "-" * 76)
    print(f"  {'Idx':<4} {'Clause ID':<22} {'Type':<18} {'Combined':<9} {'Agreement':<12} {'Severity':<10}")
    print("  " + "-" * 76)
    for c in corrupt_res.clauses:
        is_bad = c.sequence_idx in known_bad_indices
        type_str = "KNOWN-CORRUPT" if is_bad else "CLEAN-BASE"
        if is_bad and c.severity in ("HIGH", "MEDIUM"):
            corrupt_bad_high_med += 1
        elif (not is_bad) and c.severity in ("HIGH", "MEDIUM"):
            corrupt_clean_high_med += 1

        print(f"  {c.sequence_idx:<4} {c.clause_id:<22} {type_str:<18} {c.combined_score:<9.3f} {c.cross_channel_agreement:<12.2f} {c.severity:<10}")

    bad_rate = corrupt_bad_high_med / corrupt_bad_total if corrupt_bad_total else 0.0
    clean_rate = corrupt_clean_high_med / corrupt_clean_total if corrupt_clean_total else 0.0

    print("  " + "-" * 76)
    print(f"  Known-Bad Clauses High/Med Severity Rate: {bad_rate*100:.1f}% ({corrupt_bad_high_med}/{corrupt_bad_total})")
    print(f"  Clean-Base Clauses High/Med Severity Rate: {clean_rate*100:.1f}% ({corrupt_clean_high_med}/{corrupt_clean_total})")
    print(f"  Delta (Bad Rate - Clean Rate):              {bad_rate*100 - clean_rate*100:+.1f}%")

    if bad_rate > clean_rate:
        print("  [PASS] Acceptance Gate 2: Known-bad clauses received High/Medium severity strictly more often than clean clauses.", flush=True)
    else:
        print("  [FAIL] Acceptance Gate 2: Known-bad clauses did NOT receive higher severity rate.", flush=True)
        sys.exit(1)

    # Save metrics fixture
    fixtures_dir = Path("fixtures")
    fixtures_dir.mkdir(parents=True, exist_ok=True)
    metrics_path = fixtures_dir / "severity_metrics.json"

    metrics_data = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "clean_documents_evaluated": len(clean_results),
        "total_clean_clauses": total_clean_clauses,
        "clean_high_severity_count": clean_high,
        "clean_medium_severity_count": clean_med,
        "clean_low_severity_count": clean_low,
        "clean_clean_severity_count": clean_clean,
        "clean_overall_anomaly_rate": round(float((clean_high + clean_med) / max(1, total_clean_clauses)), 4),
        "corrupted_document": {
            "doc_id": "corrupted_contract_demo",
            "total_clauses": len(corrupted_clauses),
            "known_bad_count": corrupt_bad_total,
            "known_clean_count": corrupt_clean_total,
            "bad_clauses_high_or_med_rate": round(float(bad_rate), 4),
            "clean_clauses_high_or_med_rate": round(float(clean_rate), 4),
            "rate_delta": round(float(bad_rate - clean_rate), 4)
        },
        "severity_thresholds": {
            "high_combined": 0.65,
            "high_single_channel": 0.85,
            "med_combined": 0.50,
            "med_single_channel": 0.70,
            "low_combined": 0.35,
            "threshold_justification": "Reasoned defaults based on multi-channel corroboration and single-channel sensitivity envelopes."
        },
        "acceptance_gate_1": "PASSED - End-to-end execution on clean EDGAR samples without crashing",
        "acceptance_gate_2": f"PASSED - Known-bad anomaly rate ({bad_rate*100:.1f}%) > Clean anomaly rate ({clean_rate*100:.1f}%)"
    }

    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics_data, f, indent=2)

    print(f"\nSaved severity metrics fixture to: {metrics_path}", flush=True)
    print("=" * 80, flush=True)


if __name__ == "__main__":
    run_severity_evaluation()
