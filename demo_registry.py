import time
from src.embeddings.factory import get_embedder
from src.config import ClauseRecord

def demonstrate_registry():
    print("--- 1. Testing Frozen Embedder Registry ---")
    embedder_frozen = get_embedder("frozen")
    print(f"Loaded embedder: {type(embedder_frozen).__name__}")
    
    sample_clause = [
        ClauseRecord(
            clause_id="demo_1",
            doc_id="demo_doc",
            text="This is a test of the frozen embedding registry.",
            label="General",
            sequence_idx=0,
            char_start=0,
            char_end=46,
            source="demo"
        )
    ]
    
    meta, embs = embedder_frozen.embed_clauses(sample_clause)
    print(f"Generated embedding shape: {embs.shape}")
    print(f"Model used according to metadata: {meta[0]['model']}")
    
    print("\n--- 2. Testing Fine-Tuned Embedder Registry ---")
    try:
        embedder_ft = get_embedder("fine_tuned")
        print(f"Loaded embedder: {type(embedder_ft).__name__}")
        meta, embs = embedder_ft.embed_clauses(sample_clause)
        print(f"Generated embedding shape: {embs.shape}")
        print(f"Model used according to metadata: {meta[0]['model']}")
    except FileNotFoundError as e:
        print(f"Registry correctly recognized unavailable model state: {e}")
    except NotImplementedError as e:
        print(f"Registry correctly recognized incomplete implementation state: {e}")

if __name__ == "__main__":
    demonstrate_registry()
