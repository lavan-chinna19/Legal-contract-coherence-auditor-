# Phase 4D-D Dataset Sufficiency and Statistical Power Review
## Evaluation Targets, Stopping Rules, and Pilot Benchmark Viability

### 1. Benchmark Target Compliance and Stopping Rules

The specification for Phase 4D-D defined the following target parameters:
- **Pilot Objective**: A manageable pilot of approximately 20–40 well-supported positive and 20–40 well-supported negative development examples across diverse source families.
- **Strict Quality Hierarchy**:
  1. Correctness of ground truth.
  2. Independent parent diversity.
  3. Hard-negative coverage.
  4. Reproducibility.
  5. Sample quantity.
- **Stopping Rule Mandate**: Do not manufacture arbitrary synthetic cases to inflate counts. If verified positives are scarce, halt generation and report the empirical gap.

#### Empirical Yield vs. Target

| Metric / Dimension | Phase 4D-D Target | Achieved Pilot Count | Compliance Status |
| :--- | :--- | :--- | :--- |
| **Verified Positives** | 20–40 cases | **30 cases** | **Met (Optimal Midpoint)** |
| **Hard Negatives** | 20–40 cases | **30 cases** | **Met (Optimal Midpoint)** |
| **Ambiguous Cases (Queued)** | Ad hoc | **12 cases** | **Isolated for Adjudication** |
| **Total Benchmark Cases** | 40–80 cases | **72 cases** | **Met (Robust Pilot)** |
| **Unique Parent Contracts** | $\ge 8$ parents | **19 parents** | **Exceeded (+137.5%)** |
| **Independent Source Families** | $\ge 5$ families | **10 families** | **Exceeded (+100.0%)** |
| **Granularity Scopes Tested** | Clause-level | Clause-level with sentence locality | **Met** |

---

### 2. Statistical Power and Evaluation Viability

With $N = 60$ verified development cases (30 positive, 30 negative) and 12 ambiguous edge cases:
1. **Binary Classification Power**:
   - For a candidate detector evaluated on the 60 verified cases, a 95% binomial confidence interval around an observed accuracy of 80% (48/60) spans $\pm 10.1\%$.
   - This provides sufficient discriminatory power to identify catastrophically failing models (e.g., historical C2 with 0% sensitivity or detectors with high false-alarm rates on hard negatives) while avoiding over-indexing on statistical noise.
2. **Hard-Negative Diagnostic Utility**:
   - The 30 hard negatives provide a balanced stress test against naive heuristics:
     - 10 cases test whether a model misidentifies moved intra-clause discourse as cross-clause breakage.
     - 8 cases test whether a model mistakenly triggers when coupled dependent provisions move together.
     - 6 cases test whether a model penalizes commutative covenant ordering.
     - 6 cases test whether a model penalizes standard front-loaded drafting styles.
   - Any detector achieving high accuracy on this subset must genuinely attend to dependency semantics rather than simple positional dislocation.

---

### 3. Identified Gaps and Scientific Boundaries

While Phase 4D-D successfully establishes a defensible, reproducible pilot benchmark, several scientific boundaries must be clearly articulated:
1. **Pilot Scope**:
   - 72 cases represent an evaluation pilot, not a large-scale neural pre-training corpus. Its purpose is regression testing, model auditing, and failure-mode diagnostics.
2. **All Development Allocation**:
   - Because all 19 parent documents were previously exposed during Phase 4D-C investigations, this entire dataset is allocated to `development`. It cannot serve as an unexposed sealed test set.
3. **Ambiguous Cases Require Adjudication**:
   - The 12 ambiguous cases in [ambiguous_cases.csv](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/research/dependency_ground_truth_phase_04dd/ambiguous_cases.csv) represent real contractual edge cases (deictic conflicts, subsection boundary disruptions) that cannot be resolved purely algorithmically. They remain pending until admitted legal counsel provides adjudication.

---

### 4. Expansion Plan for Future True Holdout Benchmark (Post Phase 4D-D)

To construct an untainted, sealed evaluation test set in future phases:
1. **Source Acquisition**:
   - Ingest 20 newly filed SEC EDGAR annual reports (10-K exhibits) from registrants with CIKs strictly disjoint from the 10 development families in [source_family_manifest.csv](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/research/dependency_ground_truth_phase_04dd/source_family_manifest.csv).
2. **Automated Pipeline Execution**:
   - Run `src.research.dependency_ground_truth.builder` directly on the new corpus to extract cross-clause candidates and generate balanced positive and negative sets.
3. **Sealed Cryptographic Archive**:
   - Compute SHA-256 manifest digests, seal the test partition, and withhold all test sequence orders from model developers.
