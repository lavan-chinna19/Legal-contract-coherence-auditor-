# LexAudit Research — Position Recovery Results Summary
<!-- Reference copy for research archive -->

## 1. Empirical Results on Held-out Contracts
- Test contracts: 9 unperturbed SEC EDGAR commercial agreements (held-out test split).
- Top-1 Recovery: 33.33% (95% CI: [0.1111, 0.6667]).
- Top-3 Recovery: 77.78%.
- MRR: 0.5448 (95% CI: [0.3318, 0.7731]).
- Median Rank: 2.0.
- Negative Control Abstention Rate: 100.0% (0.0% false repairs).
- Latency: 14.75 ms.

## 2. Comparison to Baselines
- Cosine Heuristic: Top-1 11.11%, Top-3 55.56%, MRR 0.4028.
- Random Insertion: Top-1 9.28%, Top-3 27.84%, MRR 0.2662.
- Performance Conclusion: Frozen neural coherence head provides significant predictive signal (+104.7% MRR over random) while abstaining completely on pristine legal drafting.
