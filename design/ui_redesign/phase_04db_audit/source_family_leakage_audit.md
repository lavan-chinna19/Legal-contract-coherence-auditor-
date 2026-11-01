# SOURCE-FAMILY LEAKAGE AUDIT
**LEXAUDIT INDEPENDENT RESEARCH AUDIT — PHASE 4D-B**
**Auditor:** Independent Legal NLP Research Auditor & ML Evaluation Engineer
**Audit Target:** Phase 4D-B Dataset Partitions and Split Manifests
**Date:** 2026-10-22

---

## 1. Executive Summary

This independent audit evaluated whether the evaluation partitions in Phase 4D-B (`DIAGNOSTIC`, `VALIDATION`, and `HELDOUT_TEST`) represent genuinely source-disjoint, independent contract families or whether they suffer from cross-split parentage reuse and template contamination.

### Critical Audit Findings:
1. **Total Parent Contract Count = 2:** Across all 15 benchmark cases (8 diagnostic, 3 validation, 4 held-out test), there are **only two original parent contract templates** in existence:
   - `SYNTH_DOC_01_MSA` (11 clauses, Master Services Agreement)
   - `SYNTH_DOC_02_SLA` (8 clauses, Software License Agreement)
2. **Held-Out Test Set Reuses Both Parent Contracts:**
   - 3 of the 4 held-out test cases (`TEST_01`, `TEST_02`, `TEST_04`) are derived directly from `SYNTH_DOC_01_MSA`, which was the primary fixture in the Diagnostic benchmark (`DIAG_P1_01` through `DIAG_P2_03`, `DIAG_P9_01`).
   - 1 of the 4 held-out test cases (`TEST_03`) is derived directly from `SYNTH_DOC_02_SLA`, which was used in the Diagnostic partition (`DIAG_P9_02`) and the Validation partition (`VAL_SLA_01` through `VAL_SLA_03`).
3. **Verbatim Exact Duplicate in Held-Out Test Set:**
   - `TEST_04_CLEAN_CONTROL` is **bit-for-bit identical** to `DIAG_P9_01_CLEAN_MSA`. Both share the exact 64-character SHA-256 hash:
     `80de4cea0a1cfc9d6a39cc06b94c599665e4c5c3a9dc889ae0bc27cc53e522e8`
4. **False Claim of Source-Disjoint Partitioning:**
   - The Phase 4D-B report claimed "disjoint document lineage" and "leakage-safe split". In reality, the partition was created by splitting *perturbation instances*, **not** *parent contracts*.
   - There is **zero genuinely unseen, out-of-domain contract text** in the held-out test partition.

---

## 2. Parentage Distribution Across Partitions

| Partition | Total Cases | Parent: `SYNTH_DOC_01_MSA` | Parent: `SYNTH_DOC_02_SLA` | Genuinely Unseen Parent Documents |
| :--- | :---: | :---: | :---: | :---: |
| **DIAGNOSTIC** | 8 | 7 (87.5%) | 1 (12.5%) | Baseline Historical Reference |
| **VALIDATION** | 3 | 0 (0.0%) | 3 (100.0%) | 0 (Reuses SLA from Diagnostic) |
| **HELDOUT_TEST** | 4 | 3 (75.0%) | 1 (25.0%) | **0 (Reuses both MSA & SLA)** |
| **TOTAL** | **15** | **10** | **5** | **0** |

---

## 3. Case-by-Case Parentage and Hash Audit

```
DIAGNOSTIC CASES (8):
1. DIAG_P1_01_DISP_SCOPE:          Parent=SYNTH_DOC_01_MSA | Hash=153b3a313cc301a4... | Perturbation: Scope slot 1 -> 10
2. DIAG_P1_02_DISP_TERM:           Parent=SYNTH_DOC_01_MSA | Hash=49cdb63d90cd8b2b... | Perturbation: Term slot 5 -> 2
3. DIAG_P1_03_DISP_IP:             Parent=SYNTH_DOC_01_MSA | Hash=1cf1b0abd7c2855f... | Perturbation: IP slot 3 -> 4
4. DIAG_P2_01_SWAP_PREAMBLE:       Parent=SYNTH_DOC_01_MSA | Hash=548dc348d31ca27e... | Perturbation: Preamble <-> Scope
5. DIAG_P2_02_SWAP_PAYMENT_GOVLAW: Parent=SYNTH_DOC_01_MSA | Hash=c6cbb638432ca027... | Perturbation: Payment <-> GovLaw
6. DIAG_P2_03_SWAP_CONF_INDEMN:    Parent=SYNTH_DOC_01_MSA | Hash=1157bb5c52b3ffa0... | Perturbation: Conf <-> Indemn (Ambiguous)
7. DIAG_P9_01_CLEAN_MSA:           Parent=SYNTH_DOC_01_MSA | Hash=80de4cea0a1cfc9d... | Base unperturbed MSA
8. DIAG_P9_02_CLEAN_SLA:           Parent=SYNTH_DOC_02_SLA | Hash=b53597eb41a6b7d5... | Base unperturbed SLA

VALIDATION CASES (3):
9.  VAL_SLA_01_DISP_TERM:           Parent=SYNTH_DOC_02_SLA | Hash=bf7e8929b305b51d... | Perturbation: Term slot 6 -> 1
10. VAL_SLA_02_SWAP_DISPUTE_PREAMBLE: Parent=SYNTH_DOC_02_SLA | Hash=a959fb2f683e2b95... | Perturbation: Dispute <-> Grant
11. VAL_SLA_03_HN_COHERENT_SWAP:    Parent=SYNTH_DOC_02_SLA | Hash=da11910804cd999b... | Perturbation: Users <-> Fee Schedule

HELDOUT_TEST CASES (4):
12. TEST_01_EXHIBIT_SCOPE_INVERSION: Parent=SYNTH_DOC_01_MSA | Hash=b67b50be2ade9e77... | Perturbation: Exhibit A <-> Scope (REUSES MSA)
13. TEST_02_GOVLAW_BEFORE_SCOPE:     Parent=SYNTH_DOC_01_MSA | Hash=27da0aab95ab9ce0... | Perturbation: GovLaw slot 8 -> 1 (REUSES MSA)
14. TEST_03_HN_AUDIT_WARRANTY_SWAP:  Parent=SYNTH_DOC_02_SLA | Hash=e71b6365d62d73c2... | Perturbation: Audit <-> Warranty (REUSES SLA)
15. TEST_04_CLEAN_CONTROL:           Parent=SYNTH_DOC_01_MSA | Hash=80de4cea0a1cfc9d... | Base unperturbed MSA (VERBATIM DUPLICATE OF DIAG_P9_01)
```

---

## 4. Scientific Audit Verdict on Leakage

- **Finding:** The held-out test partition does **not** evaluate out-of-domain or unseen contract generalization. It evaluates alternative permutations of the exact same two synthetic contract templates that were used to diagnose the baseline and tune the candidate.
- **Consequence:** Reporting that Candidate C3 has "proven generalization to unseen contracts" is scientifically invalid. The evaluation measures only **within-template permutation sensitivity on two synthetic fixtures**.
