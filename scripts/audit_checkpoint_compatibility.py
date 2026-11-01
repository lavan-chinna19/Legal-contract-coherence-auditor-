import os
import sys
import hashlib
import json
import torch
import numpy as np

# Add repo root to sys.path
sys.path.insert(0, os.path.abspath("."))
from src.coherence.model import CoherenceScorerHead

def compute_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def get_ledgar_label_names():
    try:
        from datasets import load_dataset_builder
        builder = load_dataset_builder("lex_glue", "ledgar")
        return builder.info.features["label"].names
    except Exception as e:
        print(f"Warning: could not load HF dataset builder: {e}", flush=True)
        return None

def main():
    print("=== CHECKPOINT & CENTROIDS AUDIT ===", flush=True)
    pt_path = os.path.abspath("models/coherence_classifier.pt")
    npz_path = os.path.abspath("fixtures/ledgar_centroids.npz")

    pt_hash = compute_sha256(pt_path)
    pt_size = os.path.getsize(pt_path)
    print(f"Model Checkpoint Path: {pt_path}", flush=True)
    print(f"Model Checkpoint SHA-256: {pt_hash}", flush=True)
    print(f"Model Checkpoint Size: {pt_size} bytes", flush=True)

    npz_hash = compute_sha256(npz_path)
    npz_size = os.path.getsize(npz_path)
    print(f"Centroids Path: {npz_path}", flush=True)
    print(f"Centroids SHA-256: {npz_hash}", flush=True)
    print(f"Centroids Size: {npz_size} bytes", flush=True)

    sd = torch.load(pt_path, weights_only=True)
    print("\nCheckpoint State Dict Keys & Shapes:", flush=True)
    for k, v in sd.items():
        print(f"  {k}: shape {tuple(v.shape)}, dtype {v.dtype}", flush=True)

    npz_data = np.load(npz_path)
    raw_keys = list(npz_data.files)
    K = len(raw_keys)
    print(f"\nCentroid Keys Count (K): {K}", flush=True)

    # Reconstruct matrix of centroids in order of npz.files
    centroid_matrix = np.vstack([npz_data[k] for k in raw_keys])
    print(f"Centroid Matrix Shape: {centroid_matrix.shape}, dtype: {centroid_matrix.dtype}", flush=True)

    # Norm analysis
    norms = np.linalg.norm(centroid_matrix, axis=1)
    print(f"Centroid L2 Norms - Min: {norms.min():.4f}, Max: {norms.max():.4f}, Mean: {norms.mean():.4f}", flush=True)

    # Label resolution
    hf_names = get_ledgar_label_names()
    label_descriptors = []
    for k in raw_keys:
        idx = int(k.replace("type_", ""))
        human_name = hf_names[idx] if hf_names and idx < len(hf_names) else f"Clause Category {idx}"
        label_descriptors.append({"key": k, "index": idx, "name": human_name})

    print(f"\nFirst 5 Centroid Descriptors:", flush=True)
    for d in label_descriptors[:5]:
        print(f"  {d['key']} -> {d['name']} (index {d['index']})", flush=True)

    # Model instantiation
    model = CoherenceScorerHead(embedding_dim=768)
    model.load_state_dict(sd)
    model.eval()

    print("\n=== INFERENCE STABILITY & ORIENTATION TEST ===", flush=True)
    u = centroid_matrix[0]
    v = centroid_matrix[1]

    # Predict u -> v multiple times to test determinism
    p1 = model.predict_proba(u, v)
    p2 = model.predict_proba(u, v)
    print(f"P({label_descriptors[0]['name']} -> {label_descriptors[1]['name']}) Run 1: {float(p1):.6f}", flush=True)
    print(f"P({label_descriptors[0]['name']} -> {label_descriptors[1]['name']}) Run 2: {float(p2):.6f}", flush=True)
    assert abs(p1 - p2) < 1e-9, "Repeated inference non-deterministic!"

    # Predict v -> u to test directionality
    p_rev = model.predict_proba(v, u)
    print(f"P({label_descriptors[1]['name']} -> {label_descriptors[0]['name']}) [Reverse]: {float(p_rev):.6f}", flush=True)
    print(f"Directional Asymmetry: {abs(float(p1) - float(p_rev)):.6f}", flush=True)

    # Self-compatibility
    p_self0 = model.predict_proba(u, u)
    print(f"P(Self 0 -> 0): {float(p_self0):.6f}", flush=True)

    # Verify vectorized forward pass
    with torch.no_grad():
        u_t = torch.from_numpy(centroid_matrix[:5]).float()
        v_t = torch.from_numpy(centroid_matrix[5:10]).float()
        batch_out = torch.sigmoid(model(u_t, v_t)).squeeze(-1).numpy()
    print(f"Batch Vectorized 5-pair Output: {batch_out.round(4)}", flush=True)

    print("\n=== AUDIT COMPLETE: ALL PRECONDITIONS PASS ===", flush=True)

if __name__ == "__main__":
    main()
