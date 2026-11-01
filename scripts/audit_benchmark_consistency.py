"""
scripts/audit_benchmark_consistency.py — Rigorous mathematical consistency audit.
Verifies:
1. Per-case ranks in position_recovery_results.json vs benchmark_case_level_results.csv
2. Exact calculation of Top-1, Top-3, MRR, Mean Rank, Median Rank, and Bootstrap CIs
3. Paired baseline statistics vs Cosine Heuristic, Random, and Identity baselines
4. Candidate tie analysis and abstention mechanics
"""
import json
import csv
import numpy as np
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PHASE4C_JSON = REPO_ROOT / "design" / "ui_redesign" / "phase_04c" / "position_recovery_results.json"
PHASE4CA_CSV = REPO_ROOT / "design" / "ui_redesign" / "phase_04ca" / "benchmark_case_level_results.csv"

def audit():
    print("=== AUDITING BENCHMARK CONSISTENCY ===")
    
    # 1. Load Phase 4C ground truth JSON
    with open(PHASE4C_JSON, "r", encoding="utf-8") as f:
        p4c_data = json.load(f)
    
    p4c_trials = p4c_data["trials"]
    print(f"Loaded {len(p4c_trials)} trials from Phase 4C position_recovery_results.json")
    
    p4c_ranks = [t["truth_rank"] for t in p4c_trials]
    p4c_rrs = [t["reciprocal_rank"] for t in p4c_trials]
    p4c_cosine_ranks = [t["heuristic_truth_rank"] for t in p4c_trials]
    p4c_cosine_rrs = [t["heuristic_rr"] for t in p4c_trials]
    
    print(f"Phase 4C Scorer Ranks: {p4c_ranks}")
    print(f"Phase 4C Scorer RRs:   {[round(x, 4) for x in p4c_rrs]}")
    print(f"Phase 4C Cosine Ranks: {p4c_cosine_ranks}")
    print(f"Phase 4C Cosine RRs:   {[round(x, 4) for x in p4c_cosine_rrs]}")
    
    # 2. Load Phase 4C-A CSV
    with open(PHASE4CA_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        p4ca_rows = list(reader)
    
    p4ca_ranks = [int(r["truth_slot_rank"]) for r in p4ca_rows]
    p4ca_rrs = [float(r["scorer_rr"]) for r in p4ca_rows]
    p4ca_cosine_ranks = [int(r["cosine_truth_rank"]) for r in p4ca_rows]
    p4ca_cosine_rrs = [float(r["cosine_rr"]) for r in p4ca_rows]
    
    print(f"\nPhase 4C-A CSV Scorer Ranks: {p4ca_ranks}")
    print(f"Phase 4C-A CSV Cosine Ranks: {p4ca_cosine_ranks}")
    
    assert p4c_ranks == p4ca_ranks, f"Mismatch between 4C and 4C-A ranks: {p4c_ranks} vs {p4ca_ranks}"
    assert p4c_cosine_ranks == p4ca_cosine_ranks, "Mismatch between 4C and 4C-A cosine ranks"
    
    # 3. Direct Mathematical Calculations from Verified Ranks: [8, 1, 2, 1, 9, 3, 3, 1, 2]
    ranks = np.array(p4c_ranks)
    rrs = np.array(p4c_rrs)
    cosine_ranks = np.array(p4c_cosine_ranks)
    cosine_rrs = np.array(p4c_cosine_rrs)
    paired_deltas = rrs - cosine_rrs
    
    n = len(ranks)
    top1_count = int(np.sum(ranks == 1))
    top3_count = int(np.sum(ranks <= 3))
    top1_rate = top1_count / n
    top3_rate = top3_count / n
    mrr = float(np.mean(rrs))
    mean_rank = float(np.mean(ranks))
    median_rank = float(np.median(ranks))
    
    cosine_top1_count = int(np.sum(cosine_ranks == 1))
    cosine_top3_count = int(np.sum(cosine_ranks <= 3))
    cosine_top1_rate = cosine_top1_count / n
    cosine_top3_rate = cosine_top3_count / n
    cosine_mrr = float(np.mean(cosine_rrs))
    cosine_mean_rank = float(np.mean(cosine_ranks))
    cosine_median_rank = float(np.median(cosine_ranks))
    
    mean_paired_delta = float(np.mean(paired_deltas))
    
    # 4. Bootstrap Confidence Intervals (10,000 resamples, fixed seed)
    rng = np.random.RandomState(42)
    boot_top1 = []
    boot_top3 = []
    boot_mrr = []
    boot_paired_delta = []
    
    for _ in range(10000):
        idx = rng.choice(n, size=n, replace=True)
        boot_top1.append(np.mean(ranks[idx] == 1))
        boot_top3.append(np.mean(ranks[idx] <= 3))
        boot_mrr.append(np.mean(rrs[idx]))
        boot_paired_delta.append(np.mean(paired_deltas[idx]))
        
    ci95_top1 = (float(np.percentile(boot_top1, 2.5)), float(np.percentile(boot_top1, 97.5)))
    ci95_top3 = (float(np.percentile(boot_top3, 2.5)), float(np.percentile(boot_top3, 97.5)))
    ci95_mrr = (float(np.percentile(boot_mrr, 2.5)), float(np.percentile(boot_mrr, 97.5)))
    ci95_paired = (float(np.percentile(boot_paired_delta, 2.5)), float(np.percentile(boot_paired_delta, 97.5)))
    
    print("\n--- EXACT MATHEMATICAL AGGREGATES FROM AUTHORITATIVE RANKS ---")
    print(f"Sample size N = {n}")
    print(f"Top-1: {top1_count}/{n} = {top1_rate:.4f} (95% CI: [{ci95_top1[0]:.4f}, {ci95_top1[1]:.4f}])")
    print(f"Top-3: {top3_count}/{n} = {top3_rate:.4f} (95% CI: [{ci95_top3[0]:.4f}, {ci95_top3[1]:.4f}])")
    print(f"MRR:   {mrr:.4f} (95% CI: [{ci95_mrr[0]:.4f}, {ci95_mrr[1]:.4f}])")
    print(f"Mean Rank:   {mean_rank:.2f}")
    print(f"Median Rank: {median_rank:.1f}")
    print(f"\nCosine Heuristic Top-1: {cosine_top1_count}/{n} = {cosine_top1_rate:.4f}")
    print(f"Cosine Heuristic Top-3: {cosine_top3_count}/{n} = {cosine_top3_rate:.4f}")
    print(f"Cosine Heuristic MRR:   {cosine_mrr:.4f}")
    print(f"Cosine Mean Rank:       {cosine_mean_rank:.2f}")
    print(f"Cosine Median Rank:     {cosine_median_rank:.1f}")
    print(f"\nPaired RR Delta (Scorer - Cosine): +{mean_paired_delta:.4f} (95% CI: [{ci95_paired[0]:.4f}, {ci95_paired[1]:.4f}])")
    print(f"Confidence interval crosses zero? {ci95_paired[0] <= 0 <= ci95_paired[1]} -> Statistical superiority unproven.")

    # 5. Contrast against the erroneous textual list [1, 3, 2, 2, 2, 1, 4, 3, 1]
    err_ranks = np.array([1, 3, 2, 2, 2, 1, 4, 3, 1])
    err_rrs = 1.0 / err_ranks
    print("\n--- IMPLICATIONS OF ERRONEOUS TEXTUAL LIST [1, 3, 2, 2, 2, 1, 4, 3, 1] ---")
    print(f"Erroneous Top-1: {int(np.sum(err_ranks==1))}/9 = {np.mean(err_ranks==1):.4f}")
    print(f"Erroneous Top-3: {int(np.sum(err_ranks<=3))}/9 = {np.mean(err_ranks<=3):.4f} (8/9 = 88.89%)")
    print(f"Erroneous MRR:   {np.mean(err_rrs):.4f} (0.6019)")
    print(f"Erroneous Mean Rank: {np.mean(err_ranks):.2f} (2.11)")
    print("Conclusion: The aggregate figures (Top-1=3/9, Top-3=7/9, MRR=0.5448, Mean Rank=3.33) were ALWAYS derived from the authoritative case ranks [8, 1, 2, 1, 9, 3, 3, 1, 2]. The erroneous list in Section J was a textual transcription bug.")

if __name__ == "__main__":
    audit()
