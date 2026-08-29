import json
import numpy as np
from pathlib import Path
from sklearn.metrics import silhouette_score
from typing import List

from src.config import ClauseRecord, FIXTURES_DIR
from src.embeddings.factory import get_embedder

def load_ledgar_eval_sample(limit=1000) -> List[ClauseRecord]:
    # We use validation split for evaluation
    from src.config import LEDGAR_PROCESSED
    path = LEDGAR_PROCESSED / "val.jsonl"
    clauses = []
    if not path.exists():
        return clauses
    with open(path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i >= limit:
                break
            data = json.loads(line)
            clauses.append(ClauseRecord(**data))
    return clauses

def evaluate_silhouette_score(source: str = "frozen", limit: int = 1000) -> dict:
    """
    Computes silhouette score for embeddings from a given source model using
    LEDGAR clause-type labels as cluster assignments.
    """
    print(f"--- Evaluating Silhouette Score for {source} embedder ---")
    clauses = load_ledgar_eval_sample(limit)
    if not clauses:
        print("No evaluation clauses found.")
        return {}

    embedder = get_embedder(source)
    print(f"Embedding {len(clauses)} clauses with {embedder.model_name}...")
    
    meta, embeddings = embedder.embed_clauses(clauses, batch_size=64)
    
    # Extract labels
    labels = [m["label"] for m in meta]
    
    # We need at least 2 classes for silhouette score
    unique_labels = set(labels)
    if len(unique_labels) < 2:
        print("Not enough unique labels in sample to compute silhouette score.")
        return {}

    print(f"Computing Silhouette score over {len(unique_labels)} unique classes...")
    score = silhouette_score(embeddings, labels, metric='cosine')
    
    result = {
        "dataset": "ledgar_val",
        "sample_size": len(clauses),
        "num_classes": len(unique_labels),
        "embedding_dim": embedder.embedding_dim,
        "distance_metric": "cosine",
        "silhouette_score": float(score)
    }
    
    # Save as fixture
    fixture_path = FIXTURES_DIR / f"silhouette_score_{source}.json"
    FIXTURES_DIR.mkdir(parents=True, exist_ok=True)
    with open(fixture_path, "w") as f:
        json.dump(result, f, indent=2)
        
    print(f"Silhouette Score ({source}): {score:.4f}")
    print(f"Result saved to {fixture_path}")
    
    return result

if __name__ == "__main__":
    evaluate_silhouette_score("frozen", limit=2000)
