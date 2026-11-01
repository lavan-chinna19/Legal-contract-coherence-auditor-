# LexAudit Research — Failure Cases, Statistical Limitations & Non-Enforceability

## 1. Analysis of Benchmark Failure Cases
In the synthetic displacement recovery benchmark on held-out SEC EDGAR contracts, 2 out of 9 trials failed to place the true original slot in the Top-3:

### Trial 1: `0001493152_23_045259_EX-10_14` ($N=28$ clauses)
- **Target Clause**: `clause_21` (Governing Law / Jurisdiction boilerplate).
- **Original Slot**: 21. Displaced Slot: 3.
- **Model Truth Rank**: Rank 8 (Predicted slot: 17).
- **Root Cause**: Commercial boilerplate clauses (such as governing law, counterparts, or severability) frequently exhibit high semantic compatibility with multiple alternative boilerplate sections in the latter third of an agreement. When multiple legal slots are equally plausible narratively, the coherence score cannot distinguish the draftsman's arbitrary ordering preference.

### Trial 2: `0001558370_23_019892_EX-10_88` ($N=13$ clauses)
- **Target Clause**: `clause_2` (Definitions section).
- **Original Slot**: 2. Displaced Slot: 11.
- **Model Truth Rank**: Rank 9 (Predicted slot: 10).
- **Root Cause**: The displaced clause contained specific cross-references to defined terms that appeared later in the document. Because Channel B operates on local pairwise adjacent transitions rather than tracking global variable scope or cross-reference resolution, it placed the clause adjacent to other operative terms using those definitions.

---

## 2. Statistical Limitations
- **Sample Size**: 9 held-out contract sequences with rich section structures were evaluated for recovery and negative controls. Grouped bootstrap 95% confidence intervals were computed to reflect this sample size honestly:
  - Top-1: `[11.11%, 66.67%]`
  - MRR: `[0.3318, 0.7731]`
- **Unconstrained vs Constrained**: Unconstrained search was executed across all $N$ positions. Incorporating structural priors (e.g. definitions must precede operative terms) will be an area for future research.

---

## 3. Legal Non-Enforceability Mandate
- Model suggestions are strictly empirical coherence score comparisons and **never** constitute legal advice, statutory compliance checks, or guarantee of enforceability.
