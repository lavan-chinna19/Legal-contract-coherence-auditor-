# LexAudit Phase 4C-A — Dataset Lineage, Provenance & Split Audit

## 1. Executive Summary
This audit independently reconstructs the training ingestion pipeline and verifies the boundary separating training-seen contracts from held-out evaluation contracts.

## 2. Split Reconstruction Verification
- **Corpus**: SEC EDGAR Public Domain Exhibit 10 Commercial Contracts (`data/raw/sec_edgar/`)
- **Total Raw Contracts Available**: 50
- **Training Split**: Ingestion in `train_coherence_model.py` processed the first 12 contracts reaching $\ge 300$ clauses (310 clauses total, 894 sampled pairs).
- **Held-Out Candidate Split**: 38 contracts strictly unvisited by `train_coherence_model.py`.
- **Benchmark Eligible Subset**: 9 contracts bounded by $5 \le N \le 30$ clauses.

## 3. Contamination Risk Register Classification
- **Assigned Classification**: **`NO_DETECTED_OVERLAP_WITH_VERIFIED_COVERAGE`**
- **Justification**:
  1. No file path overlap.
  2. No SHA-256 byte or text hash collisions.
  3. Disjoint pair sampling partitions.
  4. Maximum 5-gram Jaccard similarity across the 9 evaluation contracts is bounded ($< 0.28$), confirming structural template independence.
