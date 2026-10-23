"""
tests/test_matrix_numerical_validation.py — Phase 4B Numerical Validation Suite
Compares matrix artifact values against direct frozen model inference.
Exports comparison table to ignored tmp/final-release/matrix_numerical_validation.csv.
"""
import os
import sys
import json
import csv
import torch
import numpy as np
import pytest

sys.path.insert(0, os.path.abspath("."))
from src.coherence.model import CoherenceScorerHead

ARTIFACT_PATH = "frontend/public/research/learned_clause_pair_compatibility.json"
CHECKPOINT_PATH = "models/coherence_classifier.pt"
CENTROIDS_PATH = "fixtures/ledgar_centroids.npz"
CSV_OUT_PATH = "tmp/final-release/matrix_numerical_validation.csv"

def test_matrix_artifact_structure():
    assert os.path.exists(ARTIFACT_PATH), f"Matrix artifact {ARTIFACT_PATH} does not exist"
    with open(ARTIFACT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["schema_version"] == "1.0.0"
    assert data["milestone"] == "PHASE_4B"
    assert data["dimensions"]["num_clause_types"] == 66
    assert data["dimensions"]["num_ordered_pairs"] == 4356
    assert len(data["clause_types"]) == 66
    assert len(data["compatibility_matrix"]) == 66
    for row in data["compatibility_matrix"]:
        assert len(row) == 66

def test_matrix_values_bounded_and_finite():
    with open(ARTIFACT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    matrix = np.array(data["compatibility_matrix"])
    assert np.all(np.isfinite(matrix))
    assert np.all((matrix >= 0.0) & (matrix <= 1.0))
    assert matrix.min() >= 0.30
    assert matrix.max() <= 0.50

def test_matrix_not_row_normalized():
    with open(ARTIFACT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    matrix = np.array(data["compatibility_matrix"])
    row_sums = matrix.sum(axis=1)
    # If row normalized, row sums would equal 1.0. Here row sums are ~ 66 * 0.348 ~ 23.0
    assert not np.allclose(row_sums, 1.0), "Matrix should not be row-normalized!"
    assert np.all(row_sums > 15.0)

def test_direct_inference_cell_comparison():
    with open(ARTIFACT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    matrix = data["compatibility_matrix"]
    clause_types = data["clause_types"]

    # Load frozen model and centroids
    sd = torch.load(CHECKPOINT_PATH, weights_only=True)
    model = CoherenceScorerHead(embedding_dim=768)
    model.load_state_dict(sd)
    model.eval()

    npz_data = np.load(CENTROIDS_PATH)
    raw_keys = list(npz_data.files)
    centroids = np.vstack([npz_data[k] for k in raw_keys])
    norms = np.linalg.norm(centroids, axis=1, keepdims=True)
    centroids = centroids / (norms + 1e-9)

    # Test 12 specific pairs across different regions
    test_pairs = [
        (0, 0), (0, 1), (1, 0), (0, 65), (65, 0),
        (5, 12), (12, 5), (20, 20), (33, 44), (44, 33),
        (50, 60), (65, 65)
    ]

    os.makedirs(os.path.dirname(CSV_OUT_PATH), exist_ok=True)
    records = []

    for i, j in test_pairs:
        u = torch.from_numpy(centroids[i]).float().unsqueeze(0)
        v = torch.from_numpy(centroids[j]).float().unsqueeze(0)
        with torch.no_grad():
            direct_prob = float(torch.sigmoid(model(u, v)).squeeze().item())

        matrix_prob = float(matrix[i][j])
        delta = abs(direct_prob - matrix_prob)

        # Accuracy within 6 decimal precision
        assert delta < 1e-5, f"Cell ({i}, {j}) delta {delta} exceeds tolerance!"

        records.append({
            "antecedent_index": i,
            "antecedent_name": clause_types[i]["name"],
            "successor_index": j,
            "successor_name": clause_types[j]["name"],
            "artifact_score": round(matrix_prob, 6),
            "direct_inference_score": round(direct_prob, 6),
            "absolute_delta": f"{delta:.2e}",
            "status": "EXACT_MATCH" if delta < 1e-5 else "MISMATCH"
        })

    with open(CSV_OUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "antecedent_index", "antecedent_name", "successor_index", "successor_name",
            "artifact_score", "direct_inference_score", "absolute_delta", "status"
        ])
        writer.writeheader()
        writer.writerows(records)

    print(f"Validated {len(records)} cells. Comparison exported to {CSV_OUT_PATH}")

if __name__ == "__main__":
    test_matrix_artifact_structure()
    test_matrix_values_bounded_and_finite()
    test_matrix_not_row_normalized()
    test_direct_inference_cell_comparison()
    print("All matrix numerical validation tests passed!")
