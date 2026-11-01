# GIT BASELINE AND PRESERVATION RECORD
**LEXAUDIT RESEARCH EXTENSION — PHASE 4D-B**
**Author:** ML Systems Engineer & Security QA Lead
**Date:** 2026-10-22
**Repository:** `f:\projects\nlp\Legal-contract-coherence-auditor-`

---

## 1. Baseline Git State

```
Commit Hash: 23dbcf536f2fb3dce1611e2d2ae71e9ca8c86f55
Branch: main
Remote: origin/main (up to date)
Working Directory: Cleanly preserved; zero destructive commands executed.
```

---

## 2. Immutable Backup Snapshot

An automated, cryptographically verified backup snapshot of all critical system files was created prior to any Phase 4D-B development at:
`C:\Users\gowth\.gemini\antigravity-ide\brain\69e9beaf-b94a-4f84-8c17-05ea3face92e\scratch\phase4db_backup_snapshot\`

### Manifest Summary (25 Backed-up Files)
All backed up files were verified against SHA-256 digests in `phase4db_backup_manifest.json`:
- `README.md`
- `src/api/main.py`
- `src/api/schema.py`
- `src/api/v1/router.py`
- `src/scoring/channel_a.py`
- `src/scoring/channel_b.py`
- `src/scoring/ensemble.py`
- `src/scoring/repositioning.py`
- `src/coherence/model.py`
- `src/coherence/fine_tuned.py`
- `src/embeddings/frozen.py`
- `src/redteam/fixtures.py`
- `src/redteam/transformations.py`
- `src/redteam/scenarios.py`
- `src/redteam/runner.py`
- `src/redteam/oracle.py`
- `tests/test_api_integration.py`
- `frontend/src/app/page.tsx`
- `frontend/src/app/layout.tsx`
- `frontend/src/app/globals.css`
- `frontend/package.json`
- `fixtures/load_test_results.json`

---

## 3. Strict Safety & Model Preservation Checklist

| Preservation Requirement | Status | Evidence / Verification |
| :--- | :---: | :--- |
| **No destructive Git commands** | **VERIFIED** | Zero `git reset`, `git checkout --`, `git clean -f`, or `git stash` executed. |
| **No staging or commits** | **VERIFIED** | Zero `git add`, `git commit`, `git push`, or `git tag` executed. |
| **Production weights unchanged** | **VERIFIED** | `models/coherence_classifier.pt` SHA-256 identical to baseline. |
| **Centroid fixtures unchanged** | **VERIFIED** | `fixtures/ledgar_centroids.npz` SHA-256 identical to baseline. |
| **Scoring formulas unchanged** | **VERIFIED** | Production composite score formula $S = 0.5 S_A + 0.5 S_B$ strictly untouched. |
| **Production thresholds unchanged** | **VERIFIED** | Anomaly threshold $0.50$ and override threshold $0.70$ untouched in `src/scoring/`. |
| **Phase 4D/4D-A artifacts intact** | **VERIFIED** | All historical red-team CSVs, reports, and browser evidence untouched. |
| **Experimental isolation** | **VERIFIED** | All new candidate code isolated in `src/research/structural_coherence/` and `models/experimental/phase_04db/`. |
| **External processes protected** | **VERIFIED** | PID 31904 (`http.server 8000`) untouched and running. |

---

## 4. Preserved SHA-256 Hashes of Core Models

- `models/coherence_classifier.pt`:
  `7e3bc48b30fa5852ef76e5df4854589d84639e44f80c68ea702cf0f951e73708`
- `fixtures/ledgar_centroids.npz`:
  `f748282b5825227c4b7d34190ad62e92c2df9e5bc3d705c754d92ebc9a59bba6`
- `models/experimental/phase_04db/contextual_sequence_coherence.pt` (NEW EXPERIMENTAL):
  `cac804594959a419126463191c3c520206f00244540133492ffd98bbd4a4c9aa`
