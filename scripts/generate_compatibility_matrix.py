"""
scripts/generate_compatibility_matrix.py — LexAudit Phase 4B
Generates the learned clause-pair compatibility matrix from frozen model artifacts.
"""
import os
import sys
import json
import time
import hashlib
from datetime import datetime, timezone
import torch
import numpy as np

# Add repo root to path
sys.path.insert(0, os.path.abspath("."))
from src.coherence.model import CoherenceScorerHead

LEDGAR_LABEL_NAMES = [
    "Adjustments", "Agreements", "Amendments", "Anti-Corruption Laws", "Applicable Laws",
    "Approvals", "Arbitration", "Assignments", "Assigns", "Authority",
    "Availability Of Funds", "Base Salary", "Benefits", "Binding Effect", "Books And Records",
    "Capitalization", "Change In Control", "Closing", "Closing Conditions", "Collateral",
    "Commissions", "Compliance With Laws", "Condition", "Conduct Of Business", "Confidentiality",
    "Consent", "Counterparts", "Death", "Disability", "Disclosure",
    "Enforceability", "Entire Agreement", "Erisa", "Events Of Default", "Expenses",
    "Fees", "Financial Statements", "Forbearances", "Further Assurances", "Governing Laws",
    "Headings", "Indemnifications", "Indemnity", "Injunctions", "Insurance",
    "Integration", "Interest", "Interim Operations", "Jurisdictions", "Labels",
    "Liabilities", "Litigations", "Miscellaneous", "Modifications", "No Conflicts",
    "No Defaults", "No Material Adverse Effect", "Non-Competition", "Non-Disparagement", "Notices",
    "Payments", "Permitted Encumbrances", "Preamble", "Public Announcements", "Record Dates",
    "Records", "Remedies", "Representations", "Representations And Warranties", "Severability",
    "Shareholders", "Solvency", "Specific Performance", "Standard Of Care", "Submissions",
    "Subsidiaries", "Successors", "Survival", "Taxes", "Term",
    "Terminations", "Titles", "Transactions", "Transactions With Affiliates", "Transfers",
    "Types", "Use Of Proceeds", "Vacation", "Valuation", "Vesting",
    "Voluntary Prepayments", "Voting", "Waiver Of Jury Trial", "Waivers", "Warranties",
    "Warranty", "Withholdings", "Witnesseth"
]

def compute_sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def generate_compatibility_matrix():
    print("=== Generating Frozen Clause-Pair Compatibility Matrix ===", flush=True)
    pt_path = os.path.abspath("models/coherence_classifier.pt")
    npz_path = os.path.abspath("fixtures/ledgar_centroids.npz")
    out_dir = os.path.abspath("frontend/public/research")
    out_path = os.path.join(out_dir, "learned_clause_pair_compatibility.json")
    os.makedirs(out_dir, exist_ok=True)

    checkpoint_sha256 = compute_sha256(pt_path)
    centroid_sha256 = compute_sha256(npz_path)

    print(f"Checkpoint SHA-256: {checkpoint_sha256}", flush=True)
    print(f"Centroids SHA-256:  {centroid_sha256}", flush=True)

    # Load centroids in deterministic order
    npz_data = np.load(npz_path)
    raw_keys = list(npz_data.files)
    K = len(raw_keys)
    print(f"Loaded {K} centroid vectors.", flush=True)

    centroid_vectors = np.vstack([npz_data[k] for k in raw_keys])  # (K, 768)
    # Unit normalization check
    norms = np.linalg.norm(centroid_vectors, axis=1, keepdims=True)
    centroid_vectors = centroid_vectors / (norms + 1e-9)

    # Map labels
    clause_types = []
    for idx, key in enumerate(raw_keys):
        numeric_id = int(key.replace("type_", ""))
        human_name = LEDGAR_LABEL_NAMES[numeric_id] if numeric_id < len(LEDGAR_LABEL_NAMES) else f"Clause Category {numeric_id}"
        clause_types.append({
            "id": key,
            "numeric_id": numeric_id,
            "name": human_name,
            "matrix_index": idx
        })

    # Load frozen model
    state_dict = torch.load(pt_path, weights_only=True)
    model = CoherenceScorerHead(embedding_dim=768)
    model.load_state_dict(state_dict)
    model.eval()

    # Form all K x K ordered pairs (i = antecedent, j = successor)
    # Row i represents antecedent c_i
    # Column j represents successor c_j
    centroids_t = torch.from_numpy(centroid_vectors).float()

    # Vectorized computation for all K*K pairs
    u = centroids_t.unsqueeze(1).expand(K, K, -1).reshape(-1, 768)  # (K*K, 768)
    v = centroids_t.unsqueeze(0).expand(K, K, -1).reshape(-1, 768)  # (K*K, 768)

    print(f"Evaluating {u.shape[0]} ordered pairs through CoherenceScorerHead...", flush=True)
    with torch.no_grad():
        logits = model(u, v)
        probs = torch.sigmoid(logits).squeeze(-1).reshape(K, K).numpy()

    # Numerical verification
    assert probs.shape == (K, K), f"Expected shape ({K}, {K}), got {probs.shape}"
    assert np.all(np.isfinite(probs)), "Matrix contains NaN or Inf values!"
    assert np.all((probs >= 0.0) & (probs <= 1.0)), "Values outside [0, 1]!"

    min_val = float(probs.min())
    max_val = float(probs.max())
    mean_val = float(probs.mean())
    diag_mean = float(np.diag(probs).mean())
    asymmetry = float(np.abs(probs - probs.T).mean())

    print(f"Matrix Statistics: Min={min_val:.4f}, Max={max_val:.4f}, Mean={mean_val:.4f}", flush=True)
    print(f"Diagonal (Self-Transition) Mean: {diag_mean:.4f}", flush=True)
    print(f"Mean Pairwise Directional Asymmetry: {asymmetry:.4f}", flush=True)

    # Convert to standard Python lists for JSON serialization (preserve 6 decimal places)
    matrix_list = [[round(float(val), 6) for val in row] for row in probs]

    artifact = {
        "schema_version": "1.0.0",
        "milestone": "PHASE_4B",
        "title": "LexAudit Learned Clause-Pair Compatibility Matrix",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "script_version": "scripts/generate_compatibility_matrix.py@v1.0",
        "provenance": {
            "model_architecture": "CoherenceScorerHead(input_dim=3072, hidden=[256, 64], output=1)",
            "checkpoint_path": "models/coherence_classifier.pt",
            "checkpoint_sha256": checkpoint_sha256,
            "checkpoint_size_bytes": os.path.getsize(pt_path),
            "centroids_path": "fixtures/ledgar_centroids.npz",
            "centroids_sha256": centroid_sha256,
            "centroids_size_bytes": os.path.getsize(npz_path),
            "reference_corpus": "LEDGAR (SEC EDGAR Filings via LexGLUE)",
            "embedding_model": "nlpaueb/legal-bert-base-uncased (frozen, 768-dim)"
        },
        "score_semantics": {
            "quantity": "Learned Pairwise Discourse Compatibility P(Antecedent -> Successor)",
            "mathematical_formula": "P(c_i -> c_j) = sigmoid(MLP([c_i, c_j, |c_i - c_j|, c_i * c_j]))",
            "domain": "[0.0, 1.0]",
            "orientation": "HIGH_COMPATIBILITY_AT_1",
            "interpretation": "Values close to 1.0 represent high model transition compatibility (normal sequential ordering); values close to 0.0 represent structural discontinuity / anomalous flow.",
            "anomaly_relation": "Channel B Anomaly Score = 1.0 - Compatibility",
            "directional": True,
            "row_stochastic_normalized": False,
            "normalization_disclosure": "Scores are independent pairwise binary classification likelihoods, not row-stochastic Markov transition probabilities. Row sums do NOT sum to 1.0."
        },
        "dimensions": {
            "num_clause_types": K,
            "num_ordered_pairs": K * K,
            "rows_meaning": "Antecedent Clause Type (c_i)",
            "columns_meaning": "Successor Clause Type (c_j)"
        },
        "summary_statistics": {
            "min_score": round(min_val, 6),
            "max_score": round(max_val, 6),
            "mean_score": round(mean_val, 6),
            "diagonal_self_mean": round(diag_mean, 6),
            "mean_directional_asymmetry": round(asymmetry, 6)
        },
        "clause_types": clause_types,
        "compatibility_matrix": matrix_list
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(artifact, f, indent=2)

    print(f"Artifact successfully exported to: {out_path}", flush=True)
    print(f"Artifact size: {os.path.getsize(out_path):,} bytes", flush=True)
    return out_path

if __name__ == "__main__":
    generate_compatibility_matrix()
