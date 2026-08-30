"""
build_centroids.py — Computes reference clause-type centroids from LEDGAR dataset
and preserves them into fixtures/ledgar_centroids.npz for Channel A semantic OOD scoring.
"""
import os
import json
from pathlib import Path
from typing import List
from collections import Counter

from src.config import LEDGAR_PROCESSED, LEDGAR_CENTROIDS_PATH, ClauseRecord
from src.embeddings.factory import get_embedder
from src.scoring.channel_a import ChannelAScorer


def build_ledgar_centroids(sample_limit: int = 500):
    print("=" * 60)
    print("Building LEDGAR Reference Clause-Type Centroids for Channel A")
    print("=" * 60)

    train_path = LEDGAR_PROCESSED / "train.jsonl"
    if not train_path.exists():
        print(f"ERROR: {train_path} not found.")
        return

    print(f"Loading sample of {sample_limit} clauses from {train_path}...")
    clauses: List[ClauseRecord] = []
    
    # Read balanced sample across labels
    label_counts = Counter()
    with open(train_path, "r", encoding="utf-8") as f:
        for line in f:
            data = json.loads(line)
            lbl = str(data.get("label", "unknown"))
            if label_counts[lbl] < 20:  # Cap per label for balance
                clauses.append(ClauseRecord(**data))
                label_counts[lbl] += 1
            if len(clauses) >= sample_limit:
                break

    print(f"Selected {len(clauses)} clauses across {len(label_counts)} distinct clause types.")
    
    embedder = get_embedder("frozen")
    print("\nComputing embeddings and unit-normalized centroids...")
    scorer = ChannelAScorer.compute_and_save_centroids(
        labeled_clauses=clauses,
        embedder=embedder,
        output_path=LEDGAR_CENTROIDS_PATH
    )

    print(f"Saved {len(scorer.centroid_names)} reference centroids to: {LEDGAR_CENTROIDS_PATH}")
    print("STATUS: SUCCESS")


if __name__ == "__main__":
    build_ledgar_centroids()
