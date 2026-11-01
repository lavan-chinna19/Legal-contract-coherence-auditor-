# Phase 4D-C-A: Program Handoff & Governance Summary

**Project**: LexAudit — Legal Contract Structural Coherence Auditor  
**Phase**: 4D-C-A (Scientific Evidence & Reproducibility Correction)  
**Date**: October 23, 2026  
**Auditor**: Independent ML Research Auditor, Senior ML Validation Specialist  
**Authoritative Final Verdict**: **EXPLORATORY BENCHMARK ONLY — PREREGISTRATION COMPROMISED**

---

## 1. Summary of Audit Determinations

| Audit Category | Technical Finding | Resolution Status | Downstream Impact |
| :--- | :--- | :---: | :--- |
| **Audit A: Checkpoint Hashes** | Physical weights and centroid arrays are 100% byte-identical to initial Git commits `490a429` and `b0ee639`. Discrepancies in Phase 4D-B docs were documentation typos. | **RESOLVED** (`IDENTICAL_BYTES_VERIFIED`) | Production model weights and fixtures confirmed untampered and frozen. |
| **Audit B: Chronology & Freeze** | Evaluation protocol and protocol hash manifest were co-generated with or after test predictions at 18:58 UTC. No model tuning was detected. | **RESOLVED** (`EXECUTION_REPEATED_WITH_FROZEN_CONFIGURATION`) | Benchmark downgraded from confirmatory trial to exploratory source-disjoint pilot. |
| **Audit C: Denominators & SEC Inventory** | Narrative typo (19+7+5=31 vs 32) resolved: 18 Dev + 9 Val + 5 Test = 32 Parents across 15 Families. SEC inventory corrected: `edgar_manifest.json` has 10 metadata keys (not filings), containing 50 exhibit entries across 19 accession numbers and 19 CIKs, matching 50 downloaded files and yielding 32 eligible parents. | **RESOLVED** (`MATHEMATICALLY_VERIFIED`) | Dataset denominators and family split disjointness certified. SEC source inventory fully authenticated. |
| **Audit D: Source Rights** | Rejected erroneous claim that EDGAR exhibits are public domain under 17 U.S.C. §105. Privately authored contracts classified as rights undetermined. | **RESOLVED** (`PUBLICLY_ACCESSIBLE_RIGHTS_UNDETERMINED`) | Full contract text redistribution prohibited; provenance packages restricted to URLs, offsets, and hashes. |
| **Audit E: Ground-Truth Validity** | Target backward discourse markers were self-contained within multi-sentence clauses. Swapping clauses (P1) did not break discourse dependencies. Test positive $N=2$ (1 parent). | **RESOLVED** (`GROUND_TRUTH_REPAIR_REQUIRED`) | P1 cases classified as `INVALID_TRANSFORMATION`; confirmatory claims withdrawn; sensitivity views generated. |
| **Audit F: Metric Consistency & C2 Reconciliation** | Candidate C2 metrics reconciled between raw thresholded predictions ($TP=2, FP=16$) and historical reported underfitting ($TP=0, FP=0, FN=2, TN=16$). Handled undefined precision/F1 under explicit convention as `NOT_ESTIMABLE`. In View 2 (0 confirmed positives), strict positive recall is `NOT_ESTIMABLE`. Historical regression baseline reconciled (Phase 4D-B: 183 passed; Phase 4D-C: 193 passed). | **RESOLVED** (`POSTHOC_EXPLORATORY_ESTABLISHED`) | Realistic assessment established: all models exhibit high false positive rates on commercial contracts. |

---

## 2. Mandatory Behavioral Mandates & Non-Negotiable Stops

The engineering and research teams must adhere strictly to the following constraints upon completion of Phase 4D-C-A:

1. **STRICT STOP**: Execution terminates immediately upon delivery of this audit.
2. **NO MODEL RETRAINING**: Do not retrain `nlpaueb/legal-bert-base-uncased`, `coherence_classifier.pt`, or any experimental head.
3. **NO THRESHOLD TUNING**: Do not alter anomaly thresholds in production (`CHANNEL_A_OOD_THRESHOLD = 0.65`, `CHANNEL_B_COHERENCE_THRESHOLD = 0.70`, composite anomaly threshold $= 0.50$).
4. **NO RE-SEALING OF EXPOSED FAMILIES**: Do not attempt to construct a "new sealed test set" using any of the 15 corporate entity families or 50 contracts already exposed in Phase 4D-C.
5. **NO PROGRESSION**: Do not start Phase 4D-D, Phase 4E, or production PDF/DOCX integration without explicit stakeholder authorization.
6. **NO GIT STAGING OR DEPLOYMENT**: Do not run `git add`, `git commit`, `git push`, or deploy to staging/production environments.

---

## 3. Recommended Next Research Steps

When authorized for future research phases, the recommended sequence is:
1. **Acquire Fresh Corporate Entities**: Collect a minimum of 20 novel, unexposed Exhibit 10 contracts from 20 novel corporate CIK families.
2. **Pre-Register Protocol Prior to Ingestion**: Formally commit and tag the evaluation protocol, scoring functions, and exact decision thresholds in Git *before* ingesting the new contracts.
3. **Double-Blind Legal Annotation**: Partner with qualified legal experts to annotate objective structural and discourse defects, avoiding multi-sentence intra-clause antecedent artifacts.
4. **Independent Confirmatory Trial**: Execute the frozen evaluation harness strictly once against the sealed dataset to establish statistically sound generalization metrics.
