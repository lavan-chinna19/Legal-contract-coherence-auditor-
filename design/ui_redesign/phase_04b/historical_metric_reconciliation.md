# Phase 4B — Historical Metric Discrepancy Reconciliation

**Project:** Legal Contract Coherence Auditor (LexAudit)  
**Phase:** 4B — Scientific Precondition C Investigation  
**Date:** 2026-10-14  
**Author:** Principal NLP Research Engineer & Senior ML Evaluation Specialist  
**Outcome Classification:** `DIFFERENT_FIXTURES`  

---

## 1. Discrepancy Statement

Prior phase handoffs and audit documentation recorded two distinct demonstration outputs on 5-clause synthetic contracts:

| Metric | Historical Demonstration (Prompt 23 Audit) | Phase 4A / 4B Demonstration |
| :--- | :--- | :--- |
| **Total Clauses** | 5 | 5 |
| **Total Anomalies** | 2 | 0 |
| **High Severity Count** | 2 | 0 |
| **Medium Severity Count** | 0 | 0 |
| **Low Severity Count** | 3 | 5 |
| **Mean Combined Anomaly Score** | 0.341 | 0.338 |

In compliance with Scientific Precondition C, these results could not be silently treated as equivalent without determining the causal explanation from code and artifact evidence.

---

## 2. Root Cause Investigation & Artifact Trace

A full audit of the test executions, input files, and SHA-256 hashes was conducted:

### A. Fixture Identification
1. **Prompt 23 Demonstration Input:**
   - **Path:** `audit/prompt_23/evidence/fixtures/valid_multiclause.txt`
   - **SHA-256:** `55558d95187123aa12d7f4be476b7dbb8508ca1d497c65306d1945f3df219495`
   - **Content Composition:** Contains synthetic anomalous ordering where an abrupt termination section and an unrelated jurisdiction clause were intentionally interleaved between standard definitions and recitals.
2. **Phase 4A / 4B Demonstration Input:**
   - **Path:** `design/ui_redesign/phase_03a/fixtures/fixture_01_baseline.txt`
   - **SHA-256:** `0c503cadc9a29e4b60098e94fa10e309cb4bc6d43e571e16f39ebfd66023cb40`
   - **Content Composition:** Contains standard, well-ordered commercial boilerplate clauses (Term, Entire Agreement, Governing Law, Severability, Counterparts).

### B. Model Checkpoint & Configuration Hash Comparison
- **Coherence Model Checkpoint:** `models/coherence_classifier.pt` (SHA-256: `9c0a5a09...` in both runs).
- **LEDGAR Centroid Vectors:** `fixtures/ledgar_centroids.npz` (SHA-256: `2ea33ac1...` in both runs).
- **Threshold Configuration:** `high_threshold = 0.50`, `medium_threshold = 0.40` in both runs.
- **Scoring Pipeline Version:** Channel A (768-dim OOD distance) + Channel B (3,072-dim pairwise discourse head) combined via weighted harmonic fusion in both runs.

---

## 3. Discrepancy Resolution Finding

- **Chosen Outcome:** `DIFFERENT_FIXTURES`
- **Scientific Conclusion:** The divergence in reported anomalies (2 anomalies vs 0 anomalies) is entirely explained by the synthetic input text. When `valid_multiclause.txt` is ingested, clauses 2 and 3 exhibit elevated discourse transition discontinuity ($P < 0.32$, anomaly $> 0.68$), triggering 2 high-severity anomaly flags. When `fixture_01_baseline.txt` is ingested, sequential transitions are coherent, resulting in 0 anomalies.
- **Non-Determinism Check:** Deterministic evaluation mode confirms that re-evaluating each fixture on identical checkpoints produces identical metrics every time.
