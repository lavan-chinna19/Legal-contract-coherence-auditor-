# Pre-Registered Research Questions (Phase 4D-B)

**Audit Program**: LexAudit Research Extension — Phase 4D-B  
**Document ID**: `PHASE_04DB_RQ_SPEC`  
**Date**: October 22, 2026  
**Auditor**: Principal Legal NLP Research Scientist  
**Pre-Registration Status**: **LOCKED PRIOR TO MODEL SELECTION & HELD-OUT EVALUATION**  

---

## 1. Primary Research Questions

### RQ1: Sensitivity to Independently Validated Structural Anomalies
> **Can contextual structural features or sequence-level coherence modeling detect independently validated clause-order anomalies that the frozen Channel B baseline completely fails to detect (0/5 strict, 0/6 broad)?**
- **Hypothesis $H_{1A}$**: Incorporating multi-clause boundary contrast or bidirectional sequence representations will yield structural recall significantly greater than the frozen baseline's 0.0% recall on strictly eligible positive anomalies.
- **Null Hypothesis $H_{10}$**: Neither local boundary contrast nor sequence representations produce sufficient signal separation to detect structural anomalies above production false-positive constraints ($\Delta \text{Recall} = 0$).

### RQ2: Specificity on Non-Canonical Coherent Orders (Hard Negatives)
> **Does an improved structural detection method preserve low false-positive rates ($\le 10\%$) when presented with coherent but non-canonical clause sequences, such as standard covenant swaps (`Confidentiality` $\leftrightarrow$ `Indemnification`) and alternative boilerplate layouts?**
- **Hypothesis $H_{2A}$**: A calibrated structural model with localized boundary contrast will identify non-defective reorderings as `VALID_ORDER` or `AMBIGUOUS_ORDER`, maintaining high specificity ($\ge 90\%$).
- **Null Hypothesis $H_{20}$**: The candidate detector relies on template memorization and over-penalizes harmless ordering variants, causing high false-positive rates on valid agreements ($FPR > 20\%$).

### RQ3: Component Ablation: Local Transitions vs. Global Discourse Context
> **Do local pairwise transition discontinuities or global document-level contextual representations contribute more to structural ordering sensitivity and anomaly localization?**
- **Hypothesis $H_{3A}$**: Combining local transition contrast with document-level positional context outperforms either local transition scores alone or bag-of-clauses representations.
- **Investigation**: Evaluated via systematic ablation isolating (a) local pairwise baseline, (b) local boundary contrast, (c) global document context, and (d) hybrid representations.

### RQ4: Generalization Across Unseen Contract Types & Templates
> **Does structural detection improvement observed on synthetic contracts generalize to unseen commercial agreements, different contract lengths ($N=8$ to $N=25$), and distinct drafting styles without retraining?**
- **Hypothesis $H_{4A}$**: Normalized relative boundary contrast generalizes across document families because it measures internal contract discontinuity rather than absolute template layout.
- **Investigation**: Evaluated on fresh, unseen SEC EDGAR commercial contracts and held-out test fixtures strictly disjoint from training fixtures.

### RQ5: Computational Feasibility and Clause-Level Explainability
> **Can an improved structural detector operate within the strict CPU resource limits of a standard workstation ($< 2.5\text{ GB}$ RAM, $< 50\text{ ms}$ inference per contract) while outputting interpretable clause-level and boundary-level evidence?**
- **Hypothesis $H_{5A}$**: A lightweight contextual boundary architecture over cached Legal-BERT embeddings satisfies the latency bound ($< 50\text{ ms}$) and produces explicit boundary contrast metrics identifying the exact disrupted transition edges.
