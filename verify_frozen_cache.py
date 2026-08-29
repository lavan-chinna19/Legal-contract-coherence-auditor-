import json
import time
from pathlib import Path

from src.config import LEDGAR_PROCESSED, EDGAR_RAW_DIR, ClauseRecord
from src.embeddings.factory import get_embedder
from src.segmentation.factory import get_segmenter


def load_ledgar_sample(limit=1000) -> list[ClauseRecord]:
    clauses = []
    path = LEDGAR_PROCESSED / "test.jsonl"
    if not path.exists():
        print("LEDGAR test.jsonl not found.")
        return []
        
    with open(path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i >= limit:
                break
            data = json.loads(line)
            clauses.append(ClauseRecord(**data))
    return clauses

def load_edgar_sample() -> list[ClauseRecord]:
    segmenter = get_segmenter("v1")
    clauses = []
    if not EDGAR_RAW_DIR.exists():
        return clauses
    
    docs_processed = 0
    for txt_file in EDGAR_RAW_DIR.glob("*.txt"):
        with open(txt_file, "r", encoding="utf-8") as f:
            text = f.read()
            doc_id = txt_file.stem
            doc_clauses = segmenter.segment(text, doc_id)
            clauses.extend(doc_clauses)
            docs_processed += 1
            if docs_processed >= 50: # Use all 50 EDGAR docs as required
                break
    return clauses

def run_pipeline():
    print("--- 1. Loading data ---")
    ledgar_clauses = load_ledgar_sample(limit=5000)
    edgar_clauses = load_edgar_sample()
    
    all_clauses = ledgar_clauses + edgar_clauses
    print(f"Loaded {len(ledgar_clauses)} LEDGAR clauses.")
    print(f"Loaded {len(edgar_clauses)} SEC EDGAR clauses.")
    print(f"Total to embed: {len(all_clauses)}")
    
    if not all_clauses:
        print("No clauses found. Exiting.")
        return

    embedder = get_embedder("frozen")
    print(f"\n--- 2. First Run (Populate Cache) ---")
    print(f"Model: {embedder.model_name}")
    print(f"Dimension: {embedder.embedding_dim}")
    
    t0 = time.perf_counter()
    # Batch size 32 is default, we can do 64 for speed if memory allows
    meta1, embs1 = embedder.embed_clauses(all_clauses, batch_size=64)
    t1 = time.perf_counter()
    print(f"First run completed in {t1 - t0:.2f} seconds.")
    print(f"Shape of embeddings: {embs1.shape}")
    
    print(f"\n--- 3. Second Run (Verify Cache Hit) ---")
    t2 = time.perf_counter()
    meta2, embs2 = embedder.embed_clauses(all_clauses, batch_size=64)
    t3 = time.perf_counter()
    print(f"Second run completed in {t3 - t2:.2f} seconds.")
    print(f"Shape of embeddings: {embs2.shape}")
    
    # Validation
    assert embs1.shape == embs2.shape, "Shapes do not match!"
    if t3 - t2 < 1.0:
        print("SUCCESS: Second run took < 1s, cache reuse confirmed!")
    else:
        print("WARNING: Second run was slow, caching might have failed.")
        
if __name__ == "__main__":
    run_pipeline()
