# LexAudit Phase 4C-A — Baseline Comparability & Methodology Review

## 1. Clarification of Baseline Roles
### A. Random Eligible Insertion Baseline
For document length $N$, the displaced clause can be placed in any of the $N$ available slots. A uniform random draw yields expected Top-1 $= 1/N$ and expected MRR $= \frac{1}{N}\sum_{r=1}^N \frac{1}{r}$. Across the 9 held-out contracts (mean length $14.2$ clauses), the expected random baseline yields **Top-1 = 9.28%** and **MRR = 0.2662**.

### B. Pairwise Cosine Similarity Heuristic
Scores insertion slot $p$ by summing the cosine similarities of Legal-BERT embeddings between target clause $c_k$ and its surrounding neighbors $(\cos(c_{p-1}, c_k) + \cos(c_k, c_p))$. This represents a strong, non-neural semantic affinity baseline. On the 9 evaluation contracts, it achieves **Top-1 = 11.11%** (1/9) and **MRR = 0.4028**.

### C. Identity / Current Displaced Position Baseline
**Methodological Caveat**: The identity baseline posits that the clause should not move from its current displaced position $d$. In the synthetic displacement benchmark, $d \ne s$ by construction ($|d - s| \ge 2$). Therefore, identity achieves Top-1 = 0.0% and MRR = 0.0000 by definition. This is a task sanity check, NOT a competitive ranking model.

## 2. Statistical Comparison
- **Primary Frozen Scorer MRR**: 0.5447 (95% CI: [0.3287, 0.7731])
- **Pairwise Cosine Heuristic MRR**: 0.4028
- **Mean Paired MRR Delta (Scorer - Cosine)**: +0.1420 (95% CI: [-0.1451, +0.4074])
- **Statistical Significance**: Because the 95% bootstrap interval of paired differences includes zero, we conclude that while the neural scorer exhibits positive directional superiority (+35.3% relative gain in MRR), **superiority is NOT statistically proven at alpha=0.05 due to the sample size of 9 contracts**.
