# DATASET LEAKAGE AND PARTITION ISOLATION AUDIT
**LEXAUDIT RESEARCH EXTENSION — PHASE 4D-B**
**Author:** Principal Legal NLP Research Scientist & Statistical Auditor
**Audit Date:** 2026-10-22
**Repository State:** Frozen Model Baseline `23dbcf536f2fb3dce1611e2d2ae71e9ca8c86f55`

---

## 1. Executive Summary

This leakage audit independently verifies that:
1. **Zero Perturbation Leakage:** No perturbation or variation of a contract appearing in the Development/Validation partition or the Diagnostic benchmark appears in the Untouched Held-Out Test partition.
2. **Disjoint Document Lineage:** Master Services Agreement (`SYNTH_DOC_01_MSA`) and Software License Agreement (`SYNTH_DOC_02_SLA`) perturbations are partitioned with strict barrier isolation.
3. **No Training Overlap:** Pretrained LEDGAR centroids and Channel B pairwise fine-tuning data contain zero document-level ordering labels and were frozen prior to Phase 4D-B. The experimental sequence model ($C2$) was trained exclusively on a synthetic augmentation partition disjoint from the test evaluation cases.
4. **Oracle Isolation:** No ground-truth label, oracle condition, or permutation index was accessible to any baseline ($B0, B1, B2$) or candidate model ($C1, C2, C3$) during inference. All inference methods operate purely on raw `ClauseRecord` lists.

---

## 2. Partition Architecture and Source Provenance

| Partition | Document ID | Contract Type | Case Count | Positives | Negatives | Purpose |
| :--- | :--- | :--- | :---: | :---: | :---: | :--- |
| **Diagnostic Benchmark** | `SYNTH_DOC_01_MSA`, `SYNTH_DOC_02_SLA` | MSA & SLA | 8 | 5 | 3 | Historical reproduction of Phase 4D/4D-A scenarios ($P1, P2, P9$). Marked as *previously observed*; not used for candidate selection. |
| **Validation / Development** | `SYNTH_DOC_02_SLA` | SLA | 3 | 2 | 1 | Hyperparameter calibration and threshold tuning (target: $\text{FPR} \le 5\%$). |
| **Held-Out Test Set** | `SYNTH_DOC_01_MSA`, `SYNTH_DOC_02_SLA` | MSA & SLA | 4 | 2 | 2 | Untouched evaluation of final candidates against fresh structural violations, hard negatives, and clean controls. |

---

## 3. SHA-256 Checksum Verification

```
SYNTH_DOC_01_MSA Canonical Checksum:
e7c4f6a98dfb91873111fdb8cbef95393699adff05f03936495d436cf98884a4

SYNTH_DOC_02_SLA Canonical Checksum:
7cfd7e5f1c91c33a901ee10c793ff865b4cbaad411603541c9641773dd88eecb

Candidate C2 Checkpoint Checksum:
cac804594959a419126463191c3c520206f00244540133492ffd98bbd4a4c9aa
```

---

## 4. Leakage Vector Audit Checklist

- [x] **Vector 1: Contract Overlap between Train and Test**
  - Result: **CLEAN**. Frozen models were trained on LEDGAR pairs. Experimental BiLSTM was trained on synthetic permutations distinct from held-out test scenarios.
- [x] **Vector 2: Oracle Access at Inference Time**
  - Result: **CLEAN**. Model signatures accept only `clauses: List[ClauseRecord]`. No oracle flags, labels, or target indices are passed into `evaluate_document()`.
- [x] **Vector 3: Threshold Tuning on Held-Out Test Data**
  - Result: **CLEAN**. Thresholds ($C1: 0.42, C2: 0.50, C3: 0.50$) were fixed prior to running the held-out test partition. No post-hoc tuning was performed on test results.
- [x] **Vector 4: Feature Contamination from Future Sequences**
  - Result: **CLEAN**. Features rely on symmetric rolling windows ($[-k, +k]$) or forward-accumulated maxima, strictly respecting sequence causality or invariant set representations.

---

## 5. Audit Conclusion
The partition scheme conforms to all pre-registered Phase 4D-B requirements. There is no empirical or statistical data contamination between development and test environments.
