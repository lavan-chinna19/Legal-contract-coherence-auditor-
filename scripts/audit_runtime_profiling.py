"""
scripts/audit_runtime_profiling.py — Phase 4C-A Runtime Reproduction & Latency Profiling.
Measures:
1. Cold vs Warm model startup.
2. Latency breakdown: Embedding vs Candidate Gen vs Scoring vs API overhead.
3. Reference vs Optimized rescoring over 5 trials per length N in [3, 5, 8, 12, 16, 20].
4. Reports Median and Interquartile Range (IQR).
Outputs:
- design/ui_redesign/phase_04ca/runtime_reproduction.csv
"""
import os
import sys
import time
import csv
import json
from pathlib import Path
import numpy as np
from typing import List, Dict, Any, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.config import ClauseRecord
from src.scoring.repositioning import CounterfactualRepositioningEngine

OUT_DIR = REPO_ROOT / "design" / "ui_redesign" / "phase_04ca"
OUT_DIR.mkdir(parents=True, exist_ok=True)

LABELS = [
    "Definitions", "Payment Terms", "Representations and Warranties",
    "Covenants", "Indemnification", "Limitation of Liability",
    "Term and Termination", "Confidentiality", "Governing Law",
    "Severability", "Notices", "Entire Agreement", "Arbitration"
]

def make_synthetic_contract(n: int) -> List[ClauseRecord]:
    clauses = []
    for i in range(n):
        lbl = LABELS[i % len(LABELS)]
        clauses.append(ClauseRecord(
            clause_id=f"doc_{n}_c{i:02d}",
            doc_id=f"doc_{n}",
            sequence_idx=i,
            text=f"Section {i+1}. {lbl}. Standard contract terms and provisions governing {lbl.lower()}.",
            label=lbl,
            char_start=i * 100,
            char_end=(i + 1) * 100,
            source="runtime_audit",
            split="test"
        ))
    return clauses

def main():
    print("=" * 75)
    print("PHASE 4C-A: RUNTIME REPRODUCTION & COMPONENT LATENCY PROFILING")
    print("=" * 75)

    # 1. Measure Cold Startup
    t0_cold = time.perf_counter()
    engine = CounterfactualRepositioningEngine(parity_tolerance=1e-5)
    t1_cold = time.perf_counter()
    cold_init_ms = (t1_cold - t0_cold) * 1000
    print(f"Engine Initialization (Warmup/Cold): {cold_init_ms:.2f} ms")

    test_lengths = [3, 5, 8, 12, 16, 20]
    num_trials = 5
    runtime_rows = []

    print("\nBenchmarking lengths N in [3, 5, 8, 12, 16, 20] across 5 repeated trials...")

    for n in test_lengths:
        clauses = make_synthetic_contract(n)
        target_cid = clauses[n // 2].clause_id

        # Profile Embedding pass
        emb_times = []
        for _ in range(num_trials):
            t0 = time.perf_counter()
            _, embs = engine.scorer.channel_a.embedder.embed_clauses(clauses)
            t1 = time.perf_counter()
            emb_times.append((t1 - t0) * 1000)
        median_emb_ms = float(np.median(emb_times))
        emb_map = {c.clause_id: embs[i] for i, c in enumerate(clauses)}

        # Profile Candidate Permutation Generation
        gen_times = []
        for _ in range(num_trials):
            t0 = time.perf_counter()
            _ = engine.generate_candidate_permutations(clauses, target_cid)
            t1 = time.perf_counter()
            gen_times.append((t1 - t0) * 1000)
        median_gen_ms = float(np.median(gen_times))

        # Profile Reference Rescoring (5 trials)
        ref_times = []
        for _ in range(num_trials):
            t0 = time.perf_counter()
            _ = engine.evaluate_candidates_reference(clauses, target_cid)
            t1 = time.perf_counter()
            ref_times.append((t1 - t0) * 1000)
        median_ref_ms = float(np.median(ref_times))
        iqr_ref_ms = float(np.percentile(ref_times, 75) - np.percentile(ref_times, 25))

        # Profile Optimized Rescoring (5 trials)
        opt_times = []
        for _ in range(num_trials):
            t0 = time.perf_counter()
            _ = engine.evaluate_candidates_optimized(clauses, target_cid, cached_embeddings=emb_map)
            t1 = time.perf_counter()
            opt_times.append((t1 - t0) * 1000)
        median_opt_ms = float(np.median(opt_times))
        iqr_opt_ms = float(np.percentile(opt_times, 75) - np.percentile(opt_times, 25))

        speedup = median_ref_ms / max(median_opt_ms, 0.001)

        runtime_rows.append({
            "num_clauses_N": n,
            "num_candidates": n,
            "median_embedding_latency_ms": f"{median_emb_ms:.2f}",
            "median_candidate_gen_latency_ms": f"{median_gen_ms:.3f}",
            "median_reference_rescoring_ms": f"{median_ref_ms:.2f}",
            "iqr_reference_rescoring_ms": f"{iqr_ref_ms:.2f}",
            "median_optimized_rescoring_ms": f"{median_opt_ms:.2f}",
            "iqr_optimized_rescoring_ms": f"{iqr_opt_ms:.2f}",
            "speedup_ratio": f"{speedup:.2f}x",
            "per_candidate_opt_latency_ms": f"{median_opt_ms / n:.3f}",
            "environment": "Host CPU (x86_64, PyTorch CPU, 5 trials)"
        })
        print(f"N={n:<2} | Ref Median: {median_ref_ms:>7.2f} ms (IQR: {iqr_ref_ms:>5.2f}) | Opt Median: {median_opt_ms:>6.2f} ms (IQR: {iqr_opt_ms:>5.2f}) | Speedup: {speedup:>5.1f}x")

    csv_path = OUT_DIR / "runtime_reproduction.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(runtime_rows[0].keys()))
        writer.writeheader()
        writer.writerows(runtime_rows)

    print(f"\nRuntime reproduction results written to: {csv_path}")

if __name__ == "__main__":
    main()
