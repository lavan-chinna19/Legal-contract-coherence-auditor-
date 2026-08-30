"""
src/coherence/trainer.py — Training pipeline for Discourse Coherence Model.
Uses cached Legal-BERT embeddings, computes real loss & accuracy curves,
and exports model checkpoint and evaluation fixtures.
"""
import os
import json
import time
from typing import List, Dict, Any, Tuple
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, roc_auc_score

from src.config import (
    ClauseRecord,
    COHERENCE_CHECKPOINT_PATH,
    COHERENCE_TRAINING_CURVES_PATH,
    MODEL_DIR,
    FIXTURES_DIR
)
from src.embeddings.factory import get_embedder
from src.coherence.pair_sampler import CoherencePair
from src.coherence.model import CoherenceScorerHead


def prepare_pair_tensors(
    pairs: List[CoherencePair],
    embedder=None
) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """
    Extracts cached embeddings for all unique clauses in the pairs,
    and returns aligned U, V tensors and Y labels.
    """
    if embedder is None:
        embedder = get_embedder("frozen")

    # Collect unique clauses
    unique_clauses_dict: Dict[str, ClauseRecord] = {}
    for p in pairs:
        unique_clauses_dict[p.clause_a.clause_id] = p.clause_a
        unique_clauses_dict[p.clause_b.clause_id] = p.clause_b

    unique_clauses = list(unique_clauses_dict.values())
    
    # Fast cached embedding retrieval
    _, embeddings_matrix = embedder.embed_clauses(unique_clauses)
    clause_id_to_idx = {c.clause_id: i for i, c in enumerate(unique_clauses)}

    u_indices = [clause_id_to_idx[p.clause_a.clause_id] for p in pairs]
    v_indices = [clause_id_to_idx[p.clause_b.clause_id] for p in pairs]
    labels = [p.label for p in pairs]

    u_tensor = torch.from_numpy(embeddings_matrix[u_indices]).float()
    v_tensor = torch.from_numpy(embeddings_matrix[v_indices]).float()
    y_tensor = torch.tensor(labels, dtype=torch.float32).unsqueeze(-1)

    return u_tensor, v_tensor, y_tensor


def train_coherence_model(
    pairs: List[CoherencePair],
    epochs: int = 10,
    batch_size: int = 32,
    lr: float = 1e-3,
    val_split: float = 0.2,
    seed: int = 42,
    embedder=None,
    save_checkpoint: bool = True,
    save_fixture: bool = True
) -> Tuple[CoherenceScorerHead, Dict[str, Any]]:
    """
    Trains CoherenceScorerHead on prepared pairs with actual loss & accuracy tracking.
    """
    torch.manual_seed(seed)
    np.random.seed(seed)

    if embedder is None:
        embedder = get_embedder("frozen")

    # Prepare embedding tensors
    u_tensor, v_tensor, y_tensor = prepare_pair_tensors(pairs, embedder=embedder)
    num_samples = len(pairs)

    # Train / Val Split
    indices = np.arange(num_samples)
    np.random.shuffle(indices)
    val_size = int(num_samples * val_split)
    train_idx, val_idx = indices[val_size:], indices[:val_size]

    train_dataset = TensorDataset(u_tensor[train_idx], v_tensor[train_idx], y_tensor[train_idx])
    val_dataset = TensorDataset(u_tensor[val_idx], v_tensor[val_idx], y_tensor[val_idx])

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)

    embedding_dim = u_tensor.shape[-1]
    model = CoherenceScorerHead(embedding_dim=embedding_dim)
    criterion = nn.BCEWithLogitsLoss()
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)

    history = {
        "metadata": {
            "num_total_pairs": num_samples,
            "num_train_pairs": len(train_idx),
            "num_val_pairs": len(val_idx),
            "embedding_dim": embedding_dim,
            "epochs": epochs,
            "batch_size": batch_size,
            "learning_rate": lr,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            "provenance": "REAL_MEASURED_RUN"
        },
        "epochs": []
    }

    best_val_loss = float("inf")
    best_state_dict = None

    for epoch in range(1, epochs + 1):
        # --- Training Phase ---
        model.train()
        train_loss_sum = 0.0
        train_batches = 0

        for u_b, v_b, y_b in train_loader:
            optimizer.zero_grad()
            logits = model(u_b, v_b)
            loss = criterion(logits, y_b)
            loss.backward()
            optimizer.step()

            train_loss_sum += loss.item()
            train_batches += 1

        avg_train_loss = train_loss_sum / max(1, train_batches)

        # --- Validation Phase ---
        model.eval()
        val_loss_sum = 0.0
        val_batches = 0
        all_val_preds = []
        all_val_targets = []

        with torch.no_grad():
            for u_b, v_b, y_b in val_loader:
                logits = model(u_b, v_b)
                loss = criterion(logits, y_b)
                val_loss_sum += loss.item()
                val_batches += 1

                probs = torch.sigmoid(logits).squeeze(-1).cpu().numpy()
                all_val_preds.extend(probs.tolist())
                all_val_targets.extend(y_b.squeeze(-1).cpu().numpy().tolist())

        avg_val_loss = val_loss_sum / max(1, val_batches)
        val_targets_arr = np.array(all_val_targets)
        val_preds_arr = np.array(all_val_preds)
        val_pred_labels = (val_preds_arr >= 0.5).astype(int)

        acc = float(accuracy_score(val_targets_arr, val_pred_labels))
        prec, rec, f1, _ = precision_recall_fscore_support(val_targets_arr, val_pred_labels, average="binary", zero_division=0)
        
        try:
            auc = float(roc_auc_score(val_targets_arr, val_preds_arr))
        except Exception:
            auc = 0.5

        epoch_stats = {
            "epoch": epoch,
            "train_loss": round(float(avg_train_loss), 6),
            "val_loss": round(float(avg_val_loss), 6),
            "val_accuracy": round(float(acc), 4),
            "val_precision": round(float(prec), 4),
            "val_recall": round(float(rec), 4),
            "val_f1": round(float(f1), 4),
            "val_roc_auc": round(float(auc), 4),
        }
        history["epochs"].append(epoch_stats)

        if avg_val_loss < best_val_loss:
            best_val_loss = avg_val_loss
            best_state_dict = {k: v.cpu().clone() for k, v in model.state_dict().items()}

    # Load best weights
    if best_state_dict is not None:
        model.load_state_dict(best_state_dict)

    # Save checkpoint
    if save_checkpoint:
        MODEL_DIR.mkdir(parents=True, exist_ok=True)
        torch.save(model.state_dict(), COHERENCE_CHECKPOINT_PATH)
        history["metadata"]["checkpoint_saved_to"] = str(COHERENCE_CHECKPOINT_PATH)

    # Save training curves fixture
    if save_fixture:
        FIXTURES_DIR.mkdir(parents=True, exist_ok=True)
        with open(COHERENCE_TRAINING_CURVES_PATH, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2)
        history["metadata"]["fixture_saved_to"] = str(COHERENCE_TRAINING_CURVES_PATH)

    return model, history
