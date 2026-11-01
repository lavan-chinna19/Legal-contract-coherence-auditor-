# DATASET VALIDITY AND LEAKAGE AUDIT REPORT
**LEXAUDIT RESEARCH EXTENSION — PHASE 4D-B**
**Author:** Data Integrity Specialist & Statistical Auditor
**Date:** 2026-10-22

---

## 1. External Dataset Provenance and Lineage Audit

A thorough audit of the local working tree and external legal datasets was conducted:

### 1.1 LEDGAR Corpus
- **Origin:** SEC EDGAR public corporate filings.
- **Local Assets:** `fixtures/ledgar_centroids.npz` (contains 66 category centroids).
- **Training Lineage:** The frozen Channel B pairwise MLP head was trained on 894 clause pairs (716 train / 178 val) derived from LEDGAR.
- **Structural Ground-Truth Validity:** **NONE**. LEDGAR contains single-clause classification labels (e.g., "Governing Law", "Term"). It contains *zero* document-level ordering sequences, zero discourse transitions, and zero clause-order anomaly annotations. Claiming LEDGAR supplies structural coherence ground truth is scientifically false.

### 1.2 CUAD (Contract Understanding Atticus Dataset)
- **Origin:** Atticus Project commercial contracts under CC-BY-4.0.
- **Local Assets:** Not utilized in frozen scoring pipeline.
- **Structural Ground-Truth Validity:** **NONE**. CUAD is an extractive question-answering benchmark for identifying legal categories (e.g., "Non-Compete", "Governing Law"). It contains no clause permutation or sequence defect labels.

### 1.3 Synthetic Legal Contract Fixtures (MSA & SLA)
- **Origin:** LexAudit Nonconfidential Synthetic Benchmark Suite (`src/redteam/fixtures.py`).
- **Assets:** `SYNTH_DOC_01_MSA` (11 clauses), `SYNTH_DOC_02_SLA` (8 clauses).
- **Structural Ground-Truth Validity:** **VERIFIED**. Both fixtures follow canonical legal document structures with verified cross-references, chronological dates, and clear lifecycle hierarchies. Controlled perturbations produce unambiguous structural defects.

---

## 2. Partition Architecture and Leakage Prevention

To ensure zero benchmark contamination, all evaluation cases were partitioned with strict barrier isolation:

### 2.1 Partition Definitions
1. **Diagnostic Benchmark (Historical Reproduction):**
   - 6 Phase 4D structural transformations ($P1\_01, P1\_02, P1\_03, P2\_01, P2\_02, P2\_03$) + 2 canonical controls.
   - **Classification:** *Previously Observed Historical Fixtures*.
   - **Policy:** Explicitly excluded from candidate selection and hyperparameter tuning. Used solely to verify baseline reproduction.
2. **Development / Validation Set:**
   - 3 SLA structural variations (1 distant displacement, 1 preamble swap, 1 coherent hard negative swap).
   - **Policy:** Exclusively used for threshold tuning and hyperparameter calibration (target: $\text{FPR} \le 5\%$).
3. **Untouched Held-Out Test Set:**
   - 4 fresh cases (2 severe structural violations, 1 out-of-domain hard negative swap, 1 canonical clean MSA control).
   - **Policy:** Strict one-shot evaluation. Zero threshold tuning, zero candidate modification after running test cases.

---

## 3. Near-Duplicate Text and Leakage Verification

All variants derived from the same source contract were tracked using SHA-256 hashes:
- `SYNTH_DOC_01_MSA` Base Hash: `e7c4f6a98dfb91873111fdb8cbef95393699adff05f03936495d436cf98884a4`
- `SYNTH_DOC_02_SLA` Base Hash: `7cfd7e5f1c91c33a901ee10c793ff865b4cbaad411603541c9641773dd88eecb`

### Leakage Audit Findings
1. No variant of a held-out test case was presented to Candidate C2 during training.
2. No ground-truth label or oracle condition was passed to any model at inference time.
3. Model thresholds ($C1: 0.42, C2: 0.50, C3: 0.50$) were fixed on the validation split prior to running held-out test evaluation.

---

## 4. Conclusion
The dataset partitioning protocol satisfies all Phase 4D-B scientific integrity criteria. There is zero empirical or methodological leakage between training, development, and evaluation environments.
