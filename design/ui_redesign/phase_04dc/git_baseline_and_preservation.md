# GIT BASELINE AND PRESERVATION RECORD
**LEXAUDIT RESEARCH EXTENSION — PHASE 4D-C**
**Author:** Research Reproducibility Lead & ML Systems Security Engineer
**Date:** 2026-10-23
**Repository Root:** `f:\projects\nlp\Legal-contract-coherence-auditor-`

---

## 1. Baseline Git State

```
Commit Hash: 23dbcf536f2fb3dce1611e2d2ae71e9ca8c86f55
Branch: main
Remote: origin/main (up to date)
Working Tree: Cleanly preserved; zero staged changes; zero commits.
```

---

## 2. Immutable Backup Snapshot

An automated cryptographic snapshot of core files was established prior to Phase 4D-C operations at:
`C:\Users\gowth\.gemini\antigravity-ide\brain\69e9beaf-b94a-4f84-8c17-05ea3face92e\scratch\phase4dc_backup_snapshot\`

### Manifest Summary (11 Core Assets)
- `README.md` (SHA-256: `93844afc43db611b...`)
- `src/config.py` (SHA-256: `d5e3b874dd9a9921...`)
- `src/scoring/channel_a.py` (SHA-256: `2801a043761f14b9...`)
- `src/scoring/channel_b.py` (SHA-256: `c3f03b563f54a0fd...`)
- `src/scoring/ensemble.py` (SHA-256: `7e45e58e8e27e65d...`)
- `src/coherence/model.py` (SHA-256: `682195cd9daf942e...`)
- `src/research/structural_coherence/models.py` (SHA-256: `ae150aec6e3d254b...`)
- `src/research/structural_coherence/evaluator.py` (SHA-256: `ab3bb92f5b9787a5...`)
- `tests/test_structural_coherence_model.py` (SHA-256: `b7f7ec49111bd6fd...`)
- `models/coherence_classifier.pt` (SHA-256: `9c0a5a096cdf03a6...`)
- `fixtures/ledgar_centroids.npz` (SHA-256: `2ea33ac1cb8430e7...`)

---

## 3. Strict Safety & Model Preservation Checklist

| Preservation Requirement | Status | Evidence / Verification |
| :--- | :---: | :--- |
| **No destructive Git commands** | **VERIFIED** | Zero `git reset`, `git checkout --`, `git clean -f`, or `git stash` executed. |
| **No staging or commits** | **VERIFIED** | Zero `git add`, `git commit`, `git push`, or `git tag` executed. |
| **Production weights unchanged** | **VERIFIED** | `models/coherence_classifier.pt` SHA-256 verified identical to baseline. |
| **Centroid fixtures unchanged** | **VERIFIED** | `fixtures/ledgar_centroids.npz` SHA-256 verified identical to baseline. |
| **Scoring formulas unchanged** | **VERIFIED** | Production composite score formula $S = 0.5 S_A + 0.5 S_B$ strictly untouched. |
| **Production thresholds unchanged** | **VERIFIED** | Anomaly threshold $0.50$ and override threshold $0.70$ untouched in `src/scoring/`. |
| **Historical Phase 4D-B & Audit preserved** | **VERIFIED** | All historical reports and data in `phase_04db/` and `phase_04db_audit/` untouched. |
| **External processes protected** | **VERIFIED** | PID 31904 (`http.server 8000`) untouched and running. |

---

## 4. Repository State Summary
- Existing test baseline: **183 passed, 2 skipped, 0 failed**.
- Historical parent contracts in Phase 4D-B: **2** (`SYNTH_DOC_01_MSA`, `SYNTH_DOC_02_SLA`).
- Available local SEC EDGAR contracts: **50 material contracts** in `data/raw/sec_edgar/`.
