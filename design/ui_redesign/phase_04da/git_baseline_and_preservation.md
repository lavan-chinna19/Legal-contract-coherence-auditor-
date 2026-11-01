# Git Baseline and Data Preservation Audit — Phase 4D-A

**Audit Date**: October 22, 2026  
**Auditor**: Independent ML Research Auditor & Scientific Verification Lead  
**Scope**: LexAudit Phase 4D-A Only  

---

## 1. Read-Only Git State Verification

Prior to modifying any files, all read-only Git commands were executed to establish baseline provenance:

- **Branch**: `main`
- **HEAD Commit**: `23dbcf536f2fb3dce1611e2d2ae71e9ca8c86f55`
- **Remote Tracking**: `origin/main` at `23dbcf536f2fb3dce1611e2d2ae71e9ca8c86f55`
- **Diff Check**: `git diff --check` reported 0 whitespace or merge-conflict errors.
- **Pre-existing Working Tree State**:
  The working tree contained uncommitted work from prior phases (Phase 4B, 4C, 4CA, 4D), including frontend components, redteam modules, and experimental benchmarks. 
  Under the Non-Negotiable Execution Rules:
  - Zero git commits performed.
  - Zero files staged (`git add`).
  - Zero git stashes, resets, or clean commands executed.
  - Zero branches switched.
  - No code deployed or pushed to remote repositories.

---

## 2. External Non-Destructive Backup Snapshot

Before performing any edits, an external byte-for-byte snapshot was archived OUTSIDE the repository in the designated IDE scratch storage:
`C:\Users\gowth\.gemini\antigravity-ide\brain\69e9beaf-b94a-4f84-8c17-05ea3face92e\scratch\phase4da_backup_snapshot`

### Snapshot Inventory & SHA-256 Checksums
Every critical file across the scoring, redteam, API, and frontend subsystems was backed up and its SHA-256 checksum recorded:

| Original Repository File | Status | Backup File Path | SHA-256 Checksum |
| :--- | :--- | :--- | :--- |
| `src/scoring/severity.py` | Tracked (Modified) | `.../scratch/phase4da_backup_snapshot/src/scoring/severity.py` | `0507e155ea7e20b6f9fe4bfe2b45050f28823ba40a3592c3a593e820c71a3962` |
| `src/scoring/pipeline.py` | Tracked (Modified) | `.../scratch/phase4da_backup_snapshot/src/scoring/pipeline.py` | `ba36eb01dc110f03e85eefbdf7fba7e2d92d4766bb32d84784a92c0023a101f3` |
| `src/scoring/channel_a.py` | Tracked (Modified) | `.../scratch/phase4da_backup_snapshot/src/scoring/channel_a.py` | `611dae6c2cbcc45187766ef838eb04a297fc93bf813a8fe9ea22858ef9c7e0b5` |
| `src/scoring/channel_b.py` | Tracked (Modified) | `.../scratch/phase4da_backup_snapshot/src/scoring/channel_b.py` | `2e08a680fa2aee370aa749aa523eb03a5578ee1994e09fef2011fe078b5ce538` |
| `src/redteam/runner.py` | Untracked | `.../scratch/phase4da_backup_snapshot/src/redteam/runner.py` | `d7f3db62f8319e623eb6368d18d4ee47be15da493011409e5b22557ffcb0457f` |
| `src/redteam/oracle.py` | Untracked | `.../scratch/phase4da_backup_snapshot/src/redteam/oracle.py` | `ee95a9d20c576594d216503c5354922ca59f7df43e26f59df1ae67ff8df5b3ba` |
| `src/redteam/scenarios.py` | Untracked | `.../scratch/phase4da_backup_snapshot/src/redteam/scenarios.py` | `903ebc03eebbb3805eb39665ec1d2551cf43c080f4cf5b36440b8f4c0c92019c` |
| `src/redteam/fixtures.py` | Untracked | `.../scratch/phase4da_backup_snapshot/src/redteam/fixtures.py` | `8c14656fa5f050228c29fa9c44569ca7a6df10bb870c5e3151eb32ceb453e9cb` |
| `src/redteam/reporting.py` | Untracked | `.../scratch/phase4da_backup_snapshot/src/redteam/reporting.py` | `295e8654c8fe221443729e2e6044b604cb7427f714eb6c934f079744c8c7f20e` |
| `src/rules/unified_pipeline.py` | Tracked (Modified) | `.../scratch/phase4da_backup_snapshot/src/rules/unified_pipeline.py` | `dd4a0815467e23118fa395e50953bf64df088fc23f66c0e5a973a90890e0c034` |
| `src/config.py` | Tracked (Modified) | `.../scratch/phase4da_backup_snapshot/src/config.py` | `c0dbda979ee98da96a6d65fe833075c328e353c9e6bb024220b221aa90eb3e2e` |
| `frontend/src/components/redteam/RedTeamLabWorkspace.tsx` | Untracked | `.../scratch/phase4da_backup_snapshot/frontend/src/components/redteam/RedTeamLabWorkspace.tsx` | `ee418ee4f37803a55da3e3bb519e49a15bc265e3a35b1c70e28a9b2d8e96bf1d` |
| `frontend/src/components/redteam/RedTeamCaseRunner.tsx` | Untracked | `.../scratch/phase4da_backup_snapshot/frontend/src/components/redteam/RedTeamCaseRunner.tsx` | `d78b8744186596919241fe231ec69a92a7a974b70dbbebeee5e2c65f02c63ae2` |

Complete manifest saved at: `scratch/phase4da_backup_snapshot/manifest.json`.

---

## 3. Preservation of Historical Phase 4D Evidence

In strict compliance with evaluation integrity rules:
- No file in `design/ui_redesign/phase_04d/` was overwritten, deleted, or renamed.
- All new Phase 4D-A audit artifacts, logs, and evidence screenshots are housed in:
  `design/ui_redesign/phase_04da/` and `design/ui_redesign/phase_04da/evidence/`.
- Scientific claims from Phase 4D are preserved as original historical hypotheses to be audited, recalculated, and contextualized.
