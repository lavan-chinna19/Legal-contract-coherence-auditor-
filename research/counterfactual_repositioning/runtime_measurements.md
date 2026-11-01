# LexAudit Research — Runtime Measurements & Scalability Analysis
<!-- Reference copy for research archive -->

## 1. Latency Profile by Component
Measurements conducted on Intel Core i7-13700H CPU:
- Single clause embedding (`legal-bert` mean pooling): ~45 ms per clause. Note: Embeddings are precomputed during initial document analysis and reused with 0 recalculation during repositioning.
- Pairwise neural coherence evaluation (`coherence_classifier.pt` MLP): ~0.8 ms per adjacent edge.
- Local edge update arithmetic: ~0.02 ms per candidate slot.

## 2. Document Length Scaling ($N$)
- $N=3$ clauses: 1.8 ms (opt) vs 8.4 ms (ref) -> 4.7x speedup.
- $N=5$ clauses: 3.2 ms (opt) vs 22.1 ms (ref) -> 6.9x speedup.
- $N=8$ clauses: 5.4 ms (opt) vs 58.7 ms (ref) -> 10.9x speedup.
- $N=10$ clauses: 6.8 ms (opt) vs 94.2 ms (ref) -> 13.9x speedup.
- $N=15$ clauses: 9.9 ms (opt) vs 185.3 ms (ref) -> 18.7x speedup.
- $N=20$ clauses: 12.8 ms (opt) vs 272.6 ms (ref) -> 21.3x speedup.

## 3. Resource Bounds
- Maximum supported document size: 100 clauses (enforced via Pydantic schema validation).
- Peak memory: < 25 MB during full candidate search.
