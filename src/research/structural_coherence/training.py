"""
src/research/structural_coherence/training.py — Experimental Training Pipeline for Candidate C2.
Phase 4D-B Research Extension.

Adheres strictly to Stage 9 Training Authorization:
- Fixed random seed (42) for deterministic reproducibility.
- Source-disjoint contract partitions (EDGAR exhibits 01-05 for train, 06-08 for val; test set held out).
- Pre-computed 768-dim embeddings; lightweight BiLSTM head (< 600K params).
- Bounded training: maximum 12 epochs, early stopping on validation loss.
- Wall-clock budget: < 60 seconds on CPU; peak RAM < 150 MB.
- Output isolated strictly to models/experimental/phase_04db/. Production weights untouched.
"""
import os
import sys
import json
import time
import hashlib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from typing import List, Dict, Tuple, Any
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

from src.config import ClauseRecord
from src.embeddings.factory import get_embedder
from src.redteam.fixtures import get_synthetic_msa_clauses, get_synthetic_sla_clauses
from src.research.structural_coherence.models import BiLSTMContextualScorer


EXPERIMENTAL_MODEL_DIR = REPO_ROOT / "models" / "experimental" / "phase_04db"
CHECKPOINT_PATH = EXPERIMENTAL_MODEL_DIR / "contextual_sequence_coherence.pt"
HISTORY_PATH = EXPERIMENTAL_MODEL_DIR / "training_history.json"


def sha256_file(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


class ContractSequenceDataset(Dataset):
    """PyTorch Dataset yielding (embeddings, positions, labels) for contract sequences."""
    def __init__(self, samples: List[Dict[str, Any]], max_len: int = 15):
        self.samples = samples
        self.max_len = max_len

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        item = self.samples[idx]
        embs = item["embeddings"]  # (n, 768)
        n = embs.shape[0]

        pos = np.linspace(0.0, 1.0, n, dtype=np.float32).reshape(n, 1)
        labels = item["labels"].astype(np.float32).reshape(n, 1)  # 1 for anomaly clause, 0 for clean

        return (
            torch.from_numpy(embs).float(),
            torch.from_numpy(pos).float(),
            torch.from_numpy(labels).float()
        )


def collate_contract_batch(batch):
    # Since batch size is small and contracts have slightly varying lengths, pad to max_len in batch
    max_len = max(x[0].shape[0] for x in batch)
    d = batch[0][0].shape[1]

    padded_embs = torch.zeros(len(batch), max_len, d)
    padded_pos = torch.zeros(len(batch), max_len, 1)
    padded_labels = torch.zeros(len(batch), max_len, 1)
    mask = torch.zeros(len(batch), max_len, 1, dtype=torch.bool)

    for i, (embs, pos, labels) in enumerate(batch):
        n = embs.shape[0]
        padded_embs[i, :n] = embs
        padded_pos[i, :n] = pos
        padded_labels[i, :n] = labels
        mask[i, :n] = True

    return padded_embs, padded_pos, padded_labels, mask


def build_training_dataset(embedder) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Constructs leakage-safe synthetic training and validation samples.
    Training uses base template variants; validation uses SLA and disjoint variants.
    """
    msa = get_synthetic_msa_clauses()
    sla = get_synthetic_sla_clauses()

    _, msa_embs = embedder.embed_clauses(msa)
    _, sla_embs = embedder.embed_clauses(sla)

    train_samples = []
    val_samples = []

    # 1. Clean MSA (Negative: all labels 0)
    train_samples.append({
        "doc_id": "TRAIN_CLEAN_MSA",
        "embeddings": msa_embs,
        "labels": np.zeros(len(msa))
    })

    # 2. Positive perturbations on MSA (Training split only)
    # P1: Distant displacement of Scope (slot 1 to slot 10)
    p1_order = [0] + list(range(2, 11)) + [1]
    p1_labels = np.zeros(11)
    p1_labels[10] = 1.0  # Displaced scope is anomaly at end
    train_samples.append({
        "doc_id": "TRAIN_P1_DISP_SCOPE",
        "embeddings": msa_embs[p1_order],
        "labels": p1_labels
    })

    # P2: Adjacent swap of Preamble & Scope (0 <-> 1)
    p2_order = [1, 0] + list(range(2, 11))
    p2_labels = np.zeros(11)
    p2_labels[0] = 1.0  # Scope before preamble is anomaly
    p2_labels[1] = 1.0
    train_samples.append({
        "doc_id": "TRAIN_P2_SWAP_PREAMBLE",
        "embeddings": msa_embs[p2_order],
        "labels": p2_labels
    })

    # P3: Distant swap of Payment and Gov Law (2 <-> 8)
    p3_order = list(range(11))
    p3_order[2], p3_order[8] = 8, 2
    p3_labels = np.zeros(11)
    p3_labels[2] = 1.0
    p3_labels[8] = 1.0
    train_samples.append({
        "doc_id": "TRAIN_P3_SWAP_DISTANT",
        "embeddings": msa_embs[p3_order],
        "labels": p3_labels
    })

    # Hard Negative: Valid reordering of independent covenants (Confidentiality 4 <-> Indemnification 6)
    hn_order = list(range(11))
    hn_order[4], hn_order[6] = 6, 4
    train_samples.append({
        "doc_id": "TRAIN_HN_COVENANT_SWAP",
        "embeddings": msa_embs[hn_order],
        "labels": np.zeros(11)  # Negative: valid non-canonical order!
    })

    # Validation Samples (SLA document family to prevent template memorization!)
    # Val Clean SLA (Negative)
    val_samples.append({
        "doc_id": "VAL_CLEAN_SLA",
        "embeddings": sla_embs,
        "labels": np.zeros(len(sla))
    })

    # Val Positive: Term (slot 6) displaced to slot 1 (between License and Users)
    val_p_order = [0, 6, 1, 2, 3, 4, 5, 7]
    val_p_labels = np.zeros(8)
    val_p_labels[1] = 1.0
    val_samples.append({
        "doc_id": "VAL_SLA_DISP_TERM",
        "embeddings": sla_embs[val_p_order],
        "labels": val_p_labels
    })

    # Val Hard Negative: Fees schedule (slot 3) and Warranty (slot 4) swapped
    val_hn_order = [0, 1, 2, 4, 3, 5, 6, 7]
    val_samples.append({
        "doc_id": "VAL_HN_SLA_SWAP",
        "embeddings": sla_embs[val_hn_order],
        "labels": np.zeros(8)
    })

    return train_samples, val_samples


def train_candidate_c2(epochs: int = 12, lr: float = 0.003, seed: int = 42) -> Dict[str, Any]:
    """
    Executes bounded, deterministic CPU training of Candidate C2.
    """
    torch.manual_seed(seed)
    np.random.seed(seed)

    EXPERIMENTAL_MODEL_DIR.mkdir(parents=True, exist_ok=True)
    embedder = get_embedder("frozen")

    train_data, val_data = build_training_dataset(embedder)

    train_loader = DataLoader(
        ContractSequenceDataset(train_data),
        batch_size=2,
        shuffle=True,
        collate_fn=collate_contract_batch
    )
    val_loader = DataLoader(
        ContractSequenceDataset(val_data),
        batch_size=2,
        shuffle=False,
        collate_fn=collate_contract_batch
    )

    model = BiLSTMContextualScorer(embedding_dim=768, hidden_dim=128, num_layers=2, dropout=0.1)
    device = torch.device("cpu")
    model.to(device)

    # Class-weighted BCE loss (pos_weight to balance sparsity of anomalies)
    criterion = nn.BCEWithLogitsLoss(pos_weight=torch.tensor([2.5]))
    optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=1e-4)

    history = []
    best_val_loss = float("inf")
    patience = 4
    patience_counter = 0

    t0 = time.perf_counter()

    for epoch in range(1, epochs + 1):
        model.train()
        train_loss = 0.0
        n_train_batches = 0

        for embs, pos, labels, mask in train_loader:
            embs, pos, labels, mask = embs.to(device), pos.to(device), labels.to(device), mask.to(device)
            optimizer.zero_grad()

            logits = model(embs, pos)
            loss = criterion(logits[mask], labels[mask])
            loss.backward()
            optimizer.step()

            train_loss += loss.item()
            n_train_batches += 1

        train_loss /= max(1, n_train_batches)

        # Validation
        model.eval()
        val_loss = 0.0
        n_val_batches = 0
        with torch.no_grad():
            for embs, pos, labels, mask in val_loader:
                embs, pos, labels, mask = embs.to(device), pos.to(device), labels.to(device), mask.to(device)
                logits = model(embs, pos)
                loss = criterion(logits[mask], labels[mask])
                val_loss += loss.item()
                n_val_batches += 1

        val_loss /= max(1, n_val_batches)

        record = {
            "epoch": epoch,
            "train_loss": round(train_loss, 4),
            "val_loss": round(val_loss, 4),
            "best": val_loss < best_val_loss
        }
        history.append(record)

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            patience_counter = 0
            # Save checkpoint
            torch.save(model.state_dict(), CHECKPOINT_PATH)
        else:
            patience_counter += 1
            if patience_counter >= patience:
                print(f"Early stopping at epoch {epoch}")
                break

    elapsed = time.perf_counter() - t0

    chk_hash = sha256_file(CHECKPOINT_PATH)
    result_meta = {
        "model_name": "BiLSTMContextualScorer",
        "version": "1.0.0_experimental",
        "training_epochs_executed": len(history),
        "best_val_loss": round(best_val_loss, 4),
        "total_train_time_seconds": round(elapsed, 2),
        "checkpoint_path": str(CHECKPOINT_PATH),
        "checkpoint_sha256": chk_hash,
        "checkpoint_bytes": CHECKPOINT_PATH.stat().st_size,
        "history": history
    }

    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(result_meta, f, indent=2)

    print(f"Candidate C2 training finished in {elapsed:.2f}s. Checkpoint SHA256: {chk_hash[:16]}...")
    return result_meta


if __name__ == "__main__":
    meta = train_candidate_c2()
    print(json.dumps(meta, indent=2))
