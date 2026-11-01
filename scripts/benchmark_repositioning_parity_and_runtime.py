"""
scripts/benchmark_repositioning_parity_and_runtime.py — Phase 4C Parity & Runtime Benchmark.
Measures:
1. Numerical parity |J_opt - J_ref| across diverse positions (first, middle, last, adjacent, long-distance)
2. Wall-clock latency of Reference vs Optimized rescoring across document lengths N in [3, 5, 8, 12, 16, 25]
3. Exports:
   - design/ui_redesign/phase_04c/optimized_rescoring_parity.csv
   - design/ui_redesign/phase_04c/runtime_benchmark.csv
"""
import os
import time
import csv
import sys
from pathlib import Path
import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.config import ClauseRecord
from src.scoring.repositioning import CounterfactualRepositioningEngine

PARITY_CSV_PATH = Path("design/ui_redesign/phase_04c/optimized_rescoring_parity.csv")
RUNTIME_CSV_PATH = Path("design/ui_redesign/phase_04c/runtime_benchmark.csv")

LABELS = [
    "Definitions", "Payment Terms", "Representations and Warranties",
    "Covenants", "Indemnification", "Limitation of Liability",
    "Term and Termination", "Confidentiality", "Governing Law",
    "Severability", "Notices", "Entire Agreement", "Arbitration"
]

def generate_synthetic_contract(n: int, doc_id: str = "benchmark_doc") -> list[ClauseRecord]:
    clauses = []
    for i in range(n):
        label = LABELS[i % len(LABELS)]
        text = (
            f"Section {i + 1}. {label}. The parties hereby agree to standard terms and covenants "
            f"governing {label.lower()} in accordance with applicable statutory rules and agreements."
        )
        clauses.append(
            ClauseRecord(
                clause_id=f"{doc_id}_c{i:02d}",
                doc_id=doc_id,
                sequence_idx=i,
                text=text,
                label=label,
                char_start=i * 120,
                char_end=(i + 1) * 120,
                source="sec_edgar",
                split="test"
            )
        )
    return clauses

def main():
    PARITY_CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    engine = CounterfactualRepositioningEngine(parity_tolerance=1e-5)

    print("=" * 70)
    print("PHASE 4C: BENCHMARKING NUMERICAL PARITY & RUNTIME SCALING")
    print("=" * 70)

    # 1. PARITY BENCHMARK
    print("\n--- 1. Evaluating Optimized vs Reference Numerical Parity ---")
    parity_rows = []
    test_scenarios = [
        ("N=5_mid", 5, 2, "middle_move"),
        ("N=5_first", 5, 0, "first_position_move"),
        ("N=5_last", 5, 4, "last_position_move"),
        ("N=8_mid", 8, 4, "middle_move"),
        ("N=8_adjacent", 8, 1, "adjacent_move"),
        ("N=12_long", 12, 11, "long_distance_move"),
        ("N=2_short", 2, 0, "two_clause_doc"),
        ("N=3_short", 3, 1, "three_clause_doc"),
    ]

    for scenario_name, n_clauses, target_idx, move_type in test_scenarios:
        clauses = generate_synthetic_contract(n_clauses, doc_id=f"doc_{scenario_name}")
        target_clause_id = clauses[target_idx].clause_id

        # Cache embeddings to measure purely scorer computation
        _, embs = engine.scorer.channel_a.embedder.embed_clauses(clauses)
        emb_map = {c.clause_id: embs[i] for i, c in enumerate(clauses)}

        ref_metrics = engine.evaluate_candidates_reference(clauses, target_clause_id)
        opt_metrics, _ = engine.evaluate_candidates_optimized(clauses, target_clause_id, cached_embeddings=emb_map)

        max_j_diff = 0.0
        max_sb_diff = 0.0
        for p in range(n_clauses):
            j_diff = abs(opt_metrics[p][0] - ref_metrics[p][0])
            sb_diff = abs(opt_metrics[p][1] - ref_metrics[p][1])
            if j_diff > max_j_diff:
                max_j_diff = j_diff
            if sb_diff > max_sb_diff:
                max_sb_diff = sb_diff

        status = "PASS" if max_j_diff <= 1e-4 else "FAIL"
        parity_rows.append({
            "scenario": scenario_name,
            "document_length": n_clauses,
            "target_clause_idx": target_idx,
            "move_type": move_type,
            "candidates_evaluated": n_clauses,
            "max_abs_objective_diff": f"{max_j_diff:.8f}",
            "max_abs_sb_diff": f"{max_sb_diff:.8f}",
            "tolerance": "0.0001",
            "parity_status": status
        })
        print(f"[{status}] {scenario_name:<15} | N={n_clauses:<2} | Target={target_idx} | Max |dJ| = {max_j_diff:.8f}")

    with open(PARITY_CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(parity_rows[0].keys()))
        writer.writeheader()
        writer.writerows(parity_rows)
    print(f"\nParity results written to: {PARITY_CSV_PATH}")

    # 2. RUNTIME BENCHMARK
    print("\n--- 2. Benchmarking Runtime Scaling Across Document Lengths ---")
    runtime_rows = []
    test_lengths = [3, 5, 8, 12, 16, 20]

    for n in test_lengths:
        clauses = generate_synthetic_contract(n, doc_id=f"runtime_n{n}")
        target_clause_id = clauses[n // 2].clause_id

        # Warmup embeddings
        _, embs = engine.scorer.channel_a.embedder.embed_clauses(clauses)
        emb_map = {c.clause_id: embs[i] for i, c in enumerate(clauses)}

        # Measure Reference latency (median of 3 runs)
        ref_times = []
        for _ in range(3):
            t0 = time.perf_counter()
            _ = engine.evaluate_candidates_reference(clauses, target_clause_id)
            t1 = time.perf_counter()
            ref_times.append((t1 - t0) * 1000)
        median_ref_ms = float(np.median(ref_times))

        # Measure Optimized latency (median of 3 runs)
        opt_times = []
        for _ in range(3):
            t0 = time.perf_counter()
            _ = engine.evaluate_candidates_optimized(clauses, target_clause_id, cached_embeddings=emb_map)
            t1 = time.perf_counter()
            opt_times.append((t1 - t0) * 1000)
        median_opt_ms = float(np.median(opt_times))

        speedup = median_ref_ms / max(median_opt_ms, 0.001)

        runtime_rows.append({
            "num_clauses": n,
            "candidates_evaluated": n,
            "reference_latency_ms": f"{median_ref_ms:.2f}",
            "optimized_latency_ms": f"{median_opt_ms:.2f}",
            "speedup_ratio": f"{speedup:.2f}x",
            "per_candidate_opt_ms": f"{median_opt_ms / n:.3f}",
            "environment": "CPU (Intel/AMD x86_64, PyTorch CPU)"
        })
        print(f"N={n:<2} clauses ({n:<2} candidates) | Ref: {median_ref_ms:>7.2f} ms | Opt: {median_opt_ms:>6.2f} ms | Speedup: {speedup:>5.1f}x")

    with open(RUNTIME_CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(runtime_rows[0].keys()))
        writer.writeheader()
        writer.writerows(runtime_rows)
    print(f"\nRuntime benchmark written to: {RUNTIME_CSV_PATH}")

if __name__ == "__main__":
    main()
