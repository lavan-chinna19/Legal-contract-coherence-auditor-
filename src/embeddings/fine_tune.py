import json
import random
import os
import torch
import numpy as np
from pathlib import Path
from collections import defaultdict
from typing import List, Tuple

from src.config import ClauseRecord, MODEL_DIR, LEGAL_BERT_MODEL
from src.embeddings.base import EmbeddingInterface
from src.embeddings.cache import EmbeddingCache

class FineTunedEmbedder(EmbeddingInterface):
    """
    Produces clause-level embeddings using the contrastively fine-tuned model.
    """
    def __init__(self):
        self._model_name = str(MODEL_DIR / "fine_tuned_legal_bert")
        if not os.path.exists(self._model_name):
            raise FileNotFoundError(f"Fine-tuned model not found at {self._model_name}. You must train it first.")
        
        self._model = None
        self._cache = EmbeddingCache("fine_tuned_legal_bert")

    def _load_model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self._model_name)
            self._model.eval()

    @property
    def model_name(self) -> str:
        return "fine_tuned_legal_bert"

    @property
    def embedding_dim(self) -> int:
        self._load_model()
        return self._model.get_embedding_dimension()

    def embed_clauses(self, clauses: List[ClauseRecord], batch_size: int = 32) -> Tuple[List[dict], np.ndarray]:
        if not clauses:
            return [], np.array([])
            
        missing_clauses, cached_vectors = self._cache.get_cached_embeddings(clauses)
        
        if missing_clauses:
            self._load_model()
            texts = [c.text for c in missing_clauses]
            
            computed_embeddings = self._model.encode(
                texts,
                batch_size=batch_size,
                show_progress_bar=False,
                convert_to_numpy=True,
                normalize_embeddings=True
            )
            
            self._cache.save_embeddings(missing_clauses, computed_embeddings)
            
            for i, c in enumerate(missing_clauses):
                cached_vectors[c.clause_id] = computed_embeddings[i]

        final_embeddings = []
        final_metadata = []
        
        for c in clauses:
            final_embeddings.append(cached_vectors[c.clause_id])
            final_metadata.append({
                "clause_id": c.clause_id,
                "doc_id": c.doc_id,
                "label": c.label,
                "model": self.model_name
            })

        return final_metadata, np.vstack(final_embeddings)

def load_train_data(limit=5000) -> List[ClauseRecord]:
    from src.config import LEDGAR_PROCESSED
    path = LEDGAR_PROCESSED / "train.jsonl"
    clauses = []
    if not path.exists():
        return clauses
    with open(path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i >= limit:
                break
            clauses.append(ClauseRecord(**json.loads(line)))
    return clauses

def prepare_contrastive_pairs(clauses: List[ClauseRecord], num_pairs=1000):
    """
    Constructs positive and negative pairs from LEDGAR labels.
    """
    from sentence_transformers import InputExample
    
    label_to_clauses = defaultdict(list)
    for c in clauses:
        label_to_clauses[c.label].append(c.text)
        
    labels = list(label_to_clauses.keys())
    examples = []
    
    # We want an even mix of positive (score=1) and negative (score=0) pairs
    pos_target = num_pairs // 2
    neg_target = num_pairs - pos_target
    
    # Create positive pairs
    pos_created = 0
    while pos_created < pos_target:
        lbl = random.choice(labels)
        group = label_to_clauses[lbl]
        if len(group) < 2:
            continue
        text_a, text_b = random.sample(group, 2)
        examples.append(InputExample(texts=[text_a, text_b], label=1.0))
        pos_created += 1
        
    # Create negative pairs
    neg_created = 0
    while neg_created < neg_target:
        lbl_a, lbl_b = random.sample(labels, 2)
        group_a = label_to_clauses[lbl_a]
        group_b = label_to_clauses[lbl_b]
        if not group_a or not group_b:
            continue
        text_a = random.choice(group_a)
        text_b = random.choice(group_b)
        examples.append(InputExample(texts=[text_a, text_b], label=0.0))
        neg_created += 1
        
    random.shuffle(examples)
    return examples

def run_fine_tuning(num_pairs=1000, epochs=1):
    """
    Attempts to fine-tune Legal-BERT using ContrastiveLoss on CPU.
    """
    print("--- Contrastive Fine-Tuning ---")
    clauses = load_train_data(limit=5000)
    if not clauses:
        print("No training data found.")
        return
        
    print(f"Loaded {len(clauses)} clauses for pair generation.")
    train_examples = prepare_contrastive_pairs(clauses, num_pairs=num_pairs)
    print(f"Created {len(train_examples)} contrastive pairs (50% pos / 50% neg).")
    
    try:
        from sentence_transformers import SentenceTransformer, losses
        from torch.utils.data import DataLoader
        import time
        
        # Determine device
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"Training on device: {device}")
        if device == 'cpu':
            print("WARNING: CPU training will be slow. Running tiny subset for demonstration.")
            # If on CPU, limit to extremely tiny batch just to prove mechanics work without timing out
            train_examples = train_examples[:200]
            epochs = 1
            print(f"Reduced to {len(train_examples)} pairs for CPU demonstration.")

        model = SentenceTransformer(LEGAL_BERT_MODEL, device=device)
        
        train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=8)
        train_loss = losses.ContrastiveLoss(model=model)
        
        MODEL_DIR.mkdir(parents=True, exist_ok=True)
        output_path = str(MODEL_DIR / "fine_tuned_legal_bert")
        
        print("Starting training...")
        t0 = time.perf_counter()
        
        model.fit(
            train_objectives=[(train_dataloader, train_loss)],
            epochs=epochs,
            warmup_steps=10,
            output_path=output_path,
            show_progress_bar=False
        )
        
        t1 = time.perf_counter()
        print(f"Training completed in {t1-t0:.2f} seconds.")
        print(f"Model saved to {output_path}")
        
    except Exception as e:
        print(f"Training failed: {e}")

if __name__ == "__main__":
    run_fine_tuning()
