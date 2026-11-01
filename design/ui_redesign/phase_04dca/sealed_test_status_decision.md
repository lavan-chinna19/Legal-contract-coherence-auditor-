# Sealed Test Status Decision & Scientific Scoping

**Program**: LexAudit ML Research Audit — Phase 4D-C-A  
**Document ID**: `SEALED_TEST_STATUS_DECISION`  
**Auditor**: Independent ML Research Auditor, Experimental Governance Specialist  
**Formal Decision**: **DOWNGRADED TO EXPLORATORY SOURCE-DISJOINT PILOT — PREVIOUSLY OBSERVED**

---

## 1. Formal Decision Statement

Based on the forensic reconstruction of execution timestamps and script architecture in `preregistration_chronology_audit.md`, the held-out test partition in Phase 4D-C **cannot be classified as an unexposed, pre-registered sealed test**.

The evaluation pass executed on October 22, 2026 at 18:58:14 UTC must formally be designated:
$$\mathbf{EXPLORATORY\text{ }SOURCE\text{-}DISJOINT\text{ }PILOT\text{ }BENCHMARK}$$

All claims that Phase 4D-C provides definitive confirmatory proof of generalization or sealed-evaluation validation are **hereby formally withdrawn**.

---

## 2. Preserved Scientific Value of the Pilot

Downgrading the benchmark from confirmatory to exploratory does **not** invalidate the empirical measurements or engineering achievements of Phase 4D-C:
1. **Source-Disjoint Validity**: The 15 corporate entity families remain 100% strictly disjoint across splits ($0$ family overlap, $0$ parent overlap).
2. **Realistic Baseline Failure Discovery**: The pilot provided critical, authentic scientific evidence that production pairwise models ($B_0, B_1$) and embedding contrast models ($C_1, C_2$) suffer from severe false positive collapse ($0\%$ specificity, $100\%$ false alarm rate) on real, uncurated commercial contracts.
3. **Engineering Parity**: The pipeline proved the feasibility of in-memory, copy-on-write structural perturbation generation and sub-second evaluation on CPU hardware.
4. **Transparent Historical Record**: The historical predictions and confusion matrices are preserved exactly as executed without alteration.

---

## 3. Strict Non-Resealing Rules (Anti-Contamination Mandate)

To protect research integrity and prevent p-hacking, the following actions are **strictly prohibited**:
1. **No Re-Sampling from Same Pool**: The team shall NOT re-sample a "replacement sealed test" from the existing 50 SEC EDGAR contracts or 15 corporate families. Those corporate families and document structures have already been inspected and observed.
2. **No Post-Hoc Threshold Optimization**: The team shall NOT adjust candidate thresholds (e.g. tuning $C_3$ threshold from 0.50 to optimize F1) and claim it represents a successful held-out result.
3. **No Retrospective Timestamps**: The team shall NOT alter Git commit dates or manifest timestamps to pretend protocol pre-registration occurred prior to evaluation.

---

## 4. Requirements for Future Independent Confirmatory Trials

When LexAudit is ready to conduct a true confirmatory benchmark in future research phases, it must adhere to the following pre-registration protocol:
1. **Fresh Corporate Families**: Acquire a minimum of 20 novel material contracts from corporate CIK families never previously exposed to development, validation, or auditing.
2. **Prior Protocol Publication & Cryptographic Hashing**: The exact evaluation script, scoring functions, thresholds, and metric formulas must be committed to Git with an immutable tag and SHA-256 hash manifest **before** downloading or processing the test contracts.
3. **Double-Blind Expert Annotation**: Positive and negative cases must be reviewed and certified by qualified legal NLP specialists to eliminate intra-clause antecedent artifacts.
4. **Immutable One-Way Inference**: The inference pipeline must execute in read-only mode against the frozen protocol without co-generating documentation.
