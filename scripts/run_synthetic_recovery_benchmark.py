"""
scripts/run_synthetic_recovery_benchmark.py — Phase 4C Synthetic Displacement Recovery Benchmark.
Evaluates held-out SEC EDGAR contract sequences under a reproducible perturbation protocol.
"""
import os
import sys
import time
import json
import csv
import random
from pathlib import Path
from typing import List, Dict, Any, Tuple
import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.config import EDGAR_RAW_DIR, ClauseRecord
from src.segmentation.factory import get_segmenter
from src.scoring.repositioning import CounterfactualRepositioningEngine

# Artifact output paths
PHASE4C_DIR = REPO_ROOT / "design" / "ui_redesign" / "phase_04c"
RESEARCH_DIR = REPO_ROOT / "research" / "counterfactual_repositioning"

SEED = 42
MIN_CLAUSES = 5
MAX_CLAUSES = 30


def run_benchmark():
    random.seed(SEED)
    np.random.seed(SEED)

    PHASE4C_DIR.mkdir(parents=True, exist_ok=True)
    RESEARCH_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("PHASE 4C: SYNTHETIC DISPLACEMENT RECOVERY BENCHMARK")
    print(f"Random Seed: {SEED} | Min Clauses: {MIN_CLAUSES} | Max Clauses: {MAX_CLAUSES}")
    print("=" * 70)

    # 1. Inspect EDGAR Contracts & Split Separation
    segmenter = get_segmenter("v1")
    txt_files = sorted(list(EDGAR_RAW_DIR.glob("*.txt")))

    # Identify training documents (first contracts reaching >= 300 clauses in train_coherence_model.py)
    train_docs = set()
    total_train_clauses = 0
    all_doc_clauses: Dict[str, List[ClauseRecord]] = {}

    for p in txt_files:
        doc_id = p.stem
        with open(p, "r", encoding="utf-8") as f:
            text = f.read()
        clauses = segmenter.segment(text, doc_id=doc_id)
        all_doc_clauses[doc_id] = clauses
        if 5 <= len(clauses) <= 50 and total_train_clauses < 300:
            train_docs.add(doc_id)
            total_train_clauses += len(clauses)

    print(f"Total raw files: {len(txt_files)}")
    print(f"Training split documents: {len(train_docs)} ({total_train_clauses} clauses)")
    held_out_docs = [doc_id for doc_id in all_doc_clauses if doc_id not in train_docs]
    print(f"Held-out test candidate documents: {len(held_out_docs)}")

    # 2. Export Dataset & Split Manifests
    dataset_manifest_rows = []
    split_manifest_rows = []

    for p in txt_files:
        doc_id = p.stem
        clauses = all_doc_clauses[doc_id]
        split = "train_seen" if doc_id in train_docs else "held_out_test"
        eligible = (split == "held_out_test" and MIN_CLAUSES <= len(clauses) <= MAX_CLAUSES)
        
        dataset_manifest_rows.append({
            "doc_id": doc_id,
            "filename": p.name,
            "total_clauses": len(clauses),
            "file_size_bytes": os.path.getsize(p),
            "split": split,
            "is_benchmark_eligible": eligible,
            "exclusion_reason": "none" if eligible else ("train_split_contamination_prevention" if split == "train_seen" else f"length_out_of_bounds_{len(clauses)}")
        })

        split_manifest_rows.append({
            "doc_id": doc_id,
            "split": split,
            "provenance": "SEC_EDGAR_EX10_PUBLIC",
            "license": "Public Domain (US SEC EDGAR)",
            "num_clauses": len(clauses)
        })

    for out_dir in [PHASE4C_DIR, RESEARCH_DIR]:
        with open(out_dir / "benchmark_dataset_manifest.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(dataset_manifest_rows[0].keys()))
            w.writeheader()
            w.writerows(dataset_manifest_rows)

        with open(out_dir / "benchmark_split_manifest.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(split_manifest_rows[0].keys()))
            w.writeheader()
            w.writerows(split_manifest_rows)

    print("Dataset & split manifests generated.")

    # 3. Filter Eligible Held-out Test Contracts
    eligible_test_docs = [
        doc_id for doc_id in held_out_docs
        if MIN_CLAUSES <= len(all_doc_clauses[doc_id]) <= MAX_CLAUSES
    ]
    print(f"Eligible held-out test contracts ({MIN_CLAUSES} <= N <= {MAX_CLAUSES}): {len(eligible_test_docs)}")

    # Initialize Engine
    engine = CounterfactualRepositioningEngine(parity_tolerance=1e-5)

    # 4. Run Perturbation Protocol
    # For each eligible test contract, we test:
    # A) Negative Control (Unperturbed original): verify false repair / abstention
    # B) Deliberate displacement of an interior clause to a non-adjacent slot
    trials = []
    neg_control_trials = []

    print("\nExecuting Synthetic Displacement & Recovery Protocol...")
    t_start = time.perf_counter()

    for doc_idx, doc_id in enumerate(eligible_test_docs):
        clean_clauses = all_doc_clauses[doc_id]
        n = len(clean_clauses)
        if n < 4:
            continue

        # Embed once for speed & fairness
        _, embs = engine.scorer.channel_a.embedder.embed_clauses(clean_clauses)
        emb_map = {c.clause_id: embs[i] for i, c in enumerate(clean_clauses)}

        # --- A. NEGATIVE CONTROL ---
        # Select an interior clause and evaluate repositioning without displacing it
        control_target_idx = n // 2
        control_target_id = clean_clauses[control_target_idx].clause_id
        control_res = engine.evaluate(
            clean_clauses,
            target_clause_id=control_target_id,
            use_optimization=True,
            min_delta_threshold=0.005,
            verify_parity=False
        )
        neg_control_trials.append({
            "doc_id": doc_id,
            "num_clauses": n,
            "target_clause_id": control_target_id,
            "is_abstaining": control_res.is_abstaining,
            "abstention_reason": control_res.abstention_reason,
            "best_candidate_idx": control_res.best_candidate_idx,
            "recommended_move": not control_res.is_abstaining
        })

        # --- B. SYNTHETIC DISPLACEMENT PERTURBATION ---
        # Choose a target clause at original position s
        # Displace to position d such that |d - s| >= 2 (or opposite side)
        s = random.randint(1, n - 2)
        possible_d = [pos for pos in range(n) if abs(pos - s) >= 2]
        if not possible_d:
            possible_d = [0 if s > n // 2 else n - 1]
        d = random.choice(possible_d)

        target_clause = clean_clauses[s]
        remaining = [c for i, c in enumerate(clean_clauses) if i != s]

        # Construct perturbed sequence D_tilde
        perturbed_perm = remaining[:d] + [target_clause] + remaining[d:]
        perturbed_clauses = [
            ClauseRecord(
                clause_id=c.clause_id,
                doc_id=c.doc_id,
                sequence_idx=idx,
                text=c.text,
                label=c.label,
                char_start=c.char_start,
                char_end=c.char_end,
                source=c.source,
                split=c.split
            )
            for idx, c in enumerate(perturbed_perm)
        ]

        # Ground truth slot in perturbed sequence is position s!
        # When evaluating perturbed sequence, target clause is currently at position d.
        # Its candidate positions are p in 0..n-1.
        # Insertion at position p = s recovers the exact original pre-perturbation ordering!
        truth_slot = s

        # Evaluate candidate positions using Counterfactual Engine
        t0_trial = time.perf_counter()
        opt_metrics, _ = engine.evaluate_candidates_optimized(
            perturbed_clauses,
            target_clause_id=target_clause.clause_id,
            cached_embeddings=emb_map
        )
        t1_trial = time.perf_counter()
        trial_latency_ms = (t1_trial - t0_trial) * 1000

        # Extract objective values
        # Sort candidates to determine ranks
        cand_list = []
        for p in range(n):
            mean_comb, mean_sb, target_sb = opt_metrics[p]
            cand_list.append({
                "pos": p,
                "mean_combined": mean_comb,
                "target_sb": target_sb
            })

        # Rank: lowest mean_combined first, tie-break by target_sb
        cand_list_sorted = sorted(cand_list, key=lambda x: (x["mean_combined"], x["target_sb"]))
        for r_idx, c in enumerate(cand_list_sorted):
            c["rank"] = r_idx + 1

        # Locate rank of truth slot s
        truth_cand = next(c for c in cand_list_sorted if c["pos"] == truth_slot)
        truth_rank = truth_cand["rank"]
        top1_cand = cand_list_sorted[0]

        is_top1 = (truth_rank == 1)
        is_top3 = (truth_rank <= 3)
        rr = 1.0 / truth_rank

        # --- Baseline 1: Pairwise Embedding Cosine Similarity Heuristic ---
        # Heuristic score for slot p: sum of adjacent cosine similarities
        heuristic_scores = []
        for p in range(n):
            perm = remaining[:p] + [target_clause] + remaining[p:]
            sim_sum = 0.0
            if p > 0:
                sim_sum += float(np.dot(emb_map[perm[p - 1].clause_id], emb_map[target_clause.clause_id]))
            if p < n - 1:
                sim_sum += float(np.dot(emb_map[target_clause.clause_id], emb_map[perm[p + 1].clause_id]))
            heuristic_scores.append((p, sim_sum))
        heuristic_sorted = sorted(heuristic_scores, key=lambda x: x[1], reverse=True)
        heuristic_ranks = {item[0]: r_idx + 1 for r_idx, item in enumerate(heuristic_sorted)}
        heuristic_truth_rank = heuristic_ranks[truth_slot]
        heuristic_is_top1 = (heuristic_truth_rank == 1)
        heuristic_is_top3 = (heuristic_truth_rank <= 3)
        heuristic_rr = 1.0 / heuristic_truth_rank

        # --- Baseline 2: Current Displaced Position Baseline ---
        # Predicts that clause stays at d (rank of truth_slot under identity is 0 if d!=s)
        current_pos_is_top1 = (d == truth_slot)  # 0 by construction

        # --- Baseline 3: Random Guess Baseline ---
        random_prob_top1 = 1.0 / n
        random_prob_top3 = min(3.0, n) / n
        random_expected_rr = sum(1.0 / r for r in range(1, n + 1)) / n

        trials.append({
            "doc_id": doc_id,
            "document_length": n,
            "target_clause_id": target_clause.clause_id,
            "original_slot_s": s,
            "displaced_slot_d": d,
            "displacement_distance": abs(d - s),
            "truth_rank": truth_rank,
            "is_top1": is_top1,
            "is_top3": is_top3,
            "reciprocal_rank": rr,
            "best_predicted_slot": top1_cand["pos"],
            "heuristic_truth_rank": heuristic_truth_rank,
            "heuristic_is_top1": heuristic_is_top1,
            "heuristic_is_top3": heuristic_is_top3,
            "heuristic_rr": heuristic_rr,
            "random_expected_top1": random_prob_top1,
            "random_expected_top3": random_prob_top3,
            "random_expected_rr": random_expected_rr,
            "latency_ms": trial_latency_ms
        })
        print(f"[{doc_idx+1:02d}/{len(eligible_test_docs):02d}] {doc_id:<32} | N={n:<2} | Slot {s}->{d} | Truth Rank: {truth_rank}/{n} | Top-1: {is_top1} | MRR: {rr:.3f}")

    t_end = time.perf_counter()
    total_eval_time = t_end - t_start

    # 5. Compute Aggregate Benchmark Statistics
    num_trials = len(trials)
    top1_count = sum(1 for t in trials if t["is_top1"])
    top3_count = sum(1 for t in trials if t["is_top3"])
    top1_rate = top1_count / num_trials if num_trials else 0.0
    top3_rate = top3_count / num_trials if num_trials else 0.0
    mrr = float(np.mean([t["reciprocal_rank"] for t in trials])) if num_trials else 0.0
    mean_rank = float(np.mean([t["truth_rank"] for t in trials])) if num_trials else 0.0
    median_rank = float(np.median([t["truth_rank"] for t in trials])) if num_trials else 0.0

    # Heuristic baseline aggregates
    h_top1_rate = sum(1 for t in trials if t["heuristic_is_top1"]) / num_trials if num_trials else 0.0
    h_top3_rate = sum(1 for t in trials if t["heuristic_is_top3"]) / num_trials if num_trials else 0.0
    h_mrr = float(np.mean([t["heuristic_rr"] for t in trials])) if num_trials else 0.0

    # Random baseline aggregates
    r_top1_rate = float(np.mean([t["random_expected_top1"] for t in trials])) if num_trials else 0.0
    r_top3_rate = float(np.mean([t["random_expected_top3"] for t in trials])) if num_trials else 0.0
    r_mrr = float(np.mean([t["random_expected_rr"] for t in trials])) if num_trials else 0.0

    # Negative control aggregates
    neg_control_count = len(neg_control_trials)
    neg_abstention_count = sum(1 for t in neg_control_trials if t["is_abstaining"])
    neg_abstention_rate = neg_abstention_count / neg_control_count if neg_control_count else 0.0
    false_repair_rate = 1.0 - neg_abstention_rate

    # Latency aggregates
    mean_latency_ms = float(np.mean([t["latency_ms"] for t in trials])) if num_trials else 0.0

    # Grouped bootstrap 95% Confidence Interval for MRR and Top-1
    bootstrap_mrr = []
    bootstrap_top1 = []
    for _ in range(1000):
        sample = [random.choice(trials) for _ in range(num_trials)]
        bootstrap_mrr.append(np.mean([s["reciprocal_rank"] for s in sample]))
        bootstrap_top1.append(np.mean([1.0 if s["is_top1"] else 0.0 for s in sample]))
    ci95_mrr = [round(float(np.percentile(bootstrap_mrr, 2.5)), 4), round(float(np.percentile(bootstrap_mrr, 97.5)), 4)]
    ci95_top1 = [round(float(np.percentile(bootstrap_top1, 2.5)), 4), round(float(np.percentile(bootstrap_top1, 97.5)), 4)]

    # 6. Export Results JSON & Markdown
    benchmark_results = {
        "metadata": {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            "benchmark_name": "Synthetic Displacement Recovery Benchmark",
            "seed": SEED,
            "dataset": "SEC EDGAR Clean Exhibit 10 Held-out Contracts",
            "total_contracts_evaluated": num_trials,
            "train_contracts_excluded": len(train_docs),
            "scoring_pipeline": "Frozen Legal-BERT + PyTorch CoherenceScorerHead",
            "primary_objective": "Whole-Document Mean Combined Anomaly J(D^(p))",
            "total_benchmark_time_seconds": round(total_eval_time, 2)
        },
        "metrics": {
            "top1_recovery_rate": round(top1_rate, 4),
            "top1_ci95": ci95_top1,
            "top3_recovery_rate": round(top3_rate, 4),
            "mean_reciprocal_rank": round(mrr, 4),
            "mrr_ci95": ci95_mrr,
            "mean_rank": round(mean_rank, 2),
            "median_rank": round(median_rank, 1),
            "negative_control_abstention_rate": round(neg_abstention_rate, 4),
            "false_repair_rate": round(false_repair_rate, 4),
            "mean_per_contract_latency_ms": round(mean_latency_ms, 2)
        },
        "baseline_comparison": {
            "counterfactual_frozen_model": {
                "top1_recovery": round(top1_rate, 4),
                "top3_recovery": round(top3_rate, 4),
                "mrr": round(mrr, 4)
            },
            "pairwise_embedding_cosine_heuristic": {
                "top1_recovery": round(h_top1_rate, 4),
                "top3_recovery": round(h_top3_rate, 4),
                "mrr": round(h_mrr, 4)
            },
            "random_eligible_insertion": {
                "top1_recovery": round(r_top1_rate, 4),
                "top3_recovery": round(r_top3_rate, 4),
                "mrr": round(r_mrr, 4)
            },
            "current_position_identity": {
                "top1_recovery": 0.0,
                "top3_recovery": 0.0,
                "mrr": 0.0
            }
        },
        "trials": trials,
        "negative_controls": neg_control_trials
    }

    # Baseline comparison CSV rows
    baseline_rows = [
        {
            "method": "Counterfactual Scorer (Primary Frozen Head)",
            "top1_recovery": f"{top1_rate:.4f}",
            "top3_recovery": f"{top3_rate:.4f}",
            "mrr": f"{mrr:.4f}",
            "top1_ci95": f"[{ci95_top1[0]:.4f}, {ci95_top1[1]:.4f}]",
            "mrr_ci95": f"[{ci95_mrr[0]:.4f}, {ci95_mrr[1]:.4f}]"
        },
        {
            "method": "Pairwise Cosine Similarity Heuristic",
            "top1_recovery": f"{h_top1_rate:.4f}",
            "top3_recovery": f"{h_top3_rate:.4f}",
            "mrr": f"{h_mrr:.4f}",
            "top1_ci95": "N/A",
            "mrr_ci95": "N/A"
        },
        {
            "method": "Random Eligible Insertion Baseline",
            "top1_recovery": f"{r_top1_rate:.4f}",
            "top3_recovery": f"{r_top3_rate:.4f}",
            "mrr": f"{r_mrr:.4f}",
            "top1_ci95": "N/A",
            "mrr_ci95": "N/A"
        },
        {
            "method": "Current Displaced Position (Identity)",
            "top1_recovery": "0.0000",
            "top3_recovery": "0.0000",
            "mrr": "0.0000",
            "top1_ci95": "N/A",
            "mrr_ci95": "N/A"
        }
    ]

    for out_dir in [PHASE4C_DIR, RESEARCH_DIR]:
        with open(out_dir / "position_recovery_results.json", "w", encoding="utf-8") as f:
            json.dump(benchmark_results, f, indent=2)

        with open(out_dir / "baseline_comparison.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(baseline_rows[0].keys()))
            w.writeheader()
            w.writerows(baseline_rows)

    print("\n" + "=" * 70)
    print("BENCHMARK SUMMARY RESULTS:")
    print(f"Top-1 Recovery Rate:               {top1_rate:.4f} (95% CI: [{ci95_top1[0]:.4f}, {ci95_top1[1]:.4f}])")
    print(f"Top-3 Recovery Rate:               {top3_rate:.4f}")
    print(f"Mean Reciprocal Rank (MRR):        {mrr:.4f} (95% CI: [{ci95_mrr[0]:.4f}, {ci95_mrr[1]:.4f}])")
    print(f"Random Baseline Top-1:             {r_top1_rate:.4f} | MRR: {r_mrr:.4f}")
    print(f"Cosine Heuristic Top-1:            {h_top1_rate:.4f} | MRR: {h_mrr:.4f}")
    print(f"Negative Control Abstention Rate:  {neg_abstention_rate:.4f} (False repair: {false_repair_rate:.4f})")
    print(f"Mean Latency per Contract:         {mean_latency_ms:.2f} ms")
    print("=" * 70)

if __name__ == "__main__":
    run_benchmark()
