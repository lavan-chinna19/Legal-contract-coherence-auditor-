# Phase 4D-C-A: Git Baseline and Artifact Preservation Audit

**Audit Program**: LexAudit Benchmark Integrity, Scientific Evidence & Reproducibility Correction  
**Phase**: 4D-C-A  
**Auditor**: Independent ML Research Auditor, Legal NLP Evaluation Specialist & Reproducibility Auditor  
**Date**: October 23, 2026  
**Status**: VERIFIED & ENFORCED  

---

## 1. Git Repository Baseline State

Measurements recorded directly from the local repository working tree prior to and during Phase 4D-C-A execution:

```text
Repository Root: F:\projects\nlp\Legal-contract-coherence-auditor-
Git Remote Origin: https://github.com/lavan-chinna19/Legal-contract-coherence-auditor-
Active Branch: main
Git Commit HEAD: 23dbcf536f2fb3dce1611e2d2ae71e9ca8c86f55
Commit Subject: fix(security): prompt-22a authorization closure and regression verification
Working Tree Status: Pre-existing uncommitted modifications preserved intact
```

### Tracked Modified Files (Preserved Unmodified):
- `README.md`
- `fixtures/load_test_results.json`
- `frontend/package-lock.json`
- `frontend/package.json`
- `frontend/src/app/globals.css`
- `frontend/src/app/layout.tsx`
- `frontend/src/app/page.tsx`
- `frontend/tsconfig.json`
- `src/api/schema.py`
- `src/api/v1/router.py`
- `tests/test_api_integration.py`

### Untracked Directories Preserved:
- `data/` (including `data/raw/sec_edgar/`)
- `design/` (including `phase_04b/`, `phase_04db/`, `phase_04db_audit/`, `phase_04dc/`)
- `research/` (including `structural_coherence_phase_04db/`, `independent_contract_benchmark_phase_04dc/`)
- `audit/`
- `src/research/`
- `src/redteam/`

---

## 2. Frozen Production & Model Checkpoint Verification

All core model weights, centroid fixtures, and scoring parameters were verified by cryptographic SHA-256 hash digests before and during the audit. Zero model weights, feature vectors, or production code were modified or replaced:

| Artifact Path | Absolute Local Path | File Size (Bytes) | Authoritative SHA-256 Hash | Verification Status |
| :--- | :--- | :---: | :--- | :---: |
| `models/coherence_classifier.pt` | `F:\projects\nlp\Legal-contract-coherence-auditor-\models\coherence_classifier.pt` | 3,218,819 | `9c0a5a096cdf03a63615134500a64f4bc559314be64366812d6a6f1762d4017f` | **FROZEN & VERIFIED** |
| `fixtures/ledgar_centroids.npz` | `F:\projects\nlp\Legal-contract-coherence-auditor-\fixtures\ledgar_centroids.npz` | 203,763 | `2ea33ac1cb8430e720be85cd501f11539c143901b2173b63b942b34b9d31ce07` | **FROZEN & VERIFIED** |
| `models/experimental/phase_04db/contextual_sequence_coherence.pt` | `F:\projects\nlp\Legal-contract-coherence-auditor-\models\experimental\phase_04db\contextual_sequence_coherence.pt` | 7,162,139 | `cac804594959a419126463191c3c520206f00244540133492ffd98bbd4a4c9aa` | **FROZEN & VERIFIED** |

---

## 3. Historical Backend Regression Baseline Reconciliation

A rigorous audit of raw test logs reconciled historical backend regression counts across phases:

```text
========================================================================================
EVALUATION PHASE   COLLECTED   PASSED   SKIPPED   FAILED   DURATION   LOG EVIDENCE SOURCE
========================================================================================
Phase 4D-B               185      183         2        0    162.24s   phase_04db/backend_regression_results.json
Phase 4D-C (Full)        195      193         2        0    188.14s   phase_04dc/backend_test_evidence.log
Phase 4D-C-A (Focused)    26       26         0        0     15.82s   phase_04dca/test_results.log
========================================================================================
```

### Clarification of the 183 vs. 193 Count:
- **Phase 4D-B Suite**: Collected 185 test items; **183 passed**, 2 skipped (CUAD live report network tests).
- **Phase 4D-C Suite**: Introduced 10 new tests in `tests/test_independent_benchmark.py`. Total collected was 195; **193 passed**, 2 skipped, 0 failed, 4 warnings. The raw pytest evidence is preserved in `design/ui_redesign/phase_04dc/backend_test_evidence.log` (line 219: `193 passed, 2 skipped, 4 warnings in 188.14s`).
- **Typo Root Cause**: Some narrative preservation documents in Phase 4D-C carried forward the string "183 passed" from the Phase 4D-B baseline without adding the 10 newly introduced independent benchmark tests ($183 + 10 = 193$).

---

## 4. Strict Safety & Model Preservation Checklist

| Preservation Requirement | Audit Verdict | Empirical Evidence / Rationale |
| :--- | :---: | :--- |
| **No destructive Git commands** | **VERIFIED** | Zero `git reset`, `git checkout --`, `git clean -f`, or `git stash` executed. Working tree strictly preserved. |
| **No staging, commits or pushes** | **VERIFIED** | Zero `git add`, `git commit`, `git push`, or `git branch` executed. |
| **Preserve uncommitted/untracked files** | **VERIFIED** | All preexisting files in `design/`, `research/`, `data/`, and `src/` remain completely untouched. |
| **Preserve model checkpoints** | **VERIFIED** | Byte-level SHA-256 digests identical to initial Git commits `490a429` and `b0ee639`. |
| **Preserve historical experiment files** | **VERIFIED** | Historical files in `phase_04db/`, `phase_04db_audit/`, and `phase_04dc/` preserved without alteration. |
| **Do not overwrite raw predictions** | **VERIFIED** | `research/independent_contract_benchmark_phase_04dc/case_level_predictions.csv` strictly untouched. |
| **Do not re-label to improve metrics** | **VERIFIED** | Historical test metrics preserved unchanged; sensitivity analysis segregated in exploratory views. |
| **Do not retrospectively alter timestamps** | **VERIFIED** | All historical timestamps preserved; chronology discrepancy audited transparently. |
| **Zero changes to production modules** | **VERIFIED** | Production scoring (`src/scoring/`), auth, storage, API, and frontend modules strictly untouched. |
| **Zero external downloads** | **VERIFIED** | Zero models or external datasets downloaded; operations strictly bounded to local repository. |
