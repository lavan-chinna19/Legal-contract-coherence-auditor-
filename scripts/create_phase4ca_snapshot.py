"""
scripts/create_phase4ca_snapshot.py — Phase 4C-A Non-Destructive Snapshot & Hash Manifest.
Creates immutable backup outside repo at artifact scratch directory and verifies readability.
"""
import os
import shutil
import hashlib
from pathlib import Path
import json

REPO_ROOT = Path("f:/projects/nlp/Legal-contract-coherence-auditor-")
SNAPSHOT_DIR = Path(r"C:\Users\gowth\.gemini\antigravity-ide\brain\69e9beaf-b94a-4f84-8c17-05ea3face92e\scratch\phase4ca_backup_snapshot")

FILES_TO_SNAPSHOT = [
    "src/scoring/repositioning.py",
    "src/api/schema.py",
    "src/api/v1/router.py",
    "src/api/main.py",
    "src/api/security.py",
    "src/scoring/channel_a.py",
    "src/scoring/channel_b.py",
    "src/scoring/pipeline.py",
    "src/scoring/ensemble.py",
    "src/scoring/severity.py",
    "src/coherence/fine_tuned.py",
    "src/coherence/model.py",
    "src/embeddings/frozen.py",
    "tests/test_repositioning.py",
    "tests/test_api_reposition.py",
    "scripts/benchmark_repositioning_parity_and_runtime.py",
    "scripts/run_synthetic_recovery_benchmark.py",
    "scripts/run_phase4c_browser_verification.py",
    "frontend/src/components/repair/types.ts",
    "frontend/src/components/repair/CounterfactualRepairWorkspace.tsx",
    "frontend/src/components/repair/RepairCandidateList.tsx",
    "frontend/src/components/repair/RepairScoreComparison.tsx",
    "frontend/src/components/repair/RepairClausePreview.tsx",
    "frontend/src/components/repair/RepairAbstentionNotice.tsx",
    "frontend/src/components/repair/RepairMethodology.tsx",
    "frontend/src/components/repair/RepairEmptyState.tsx",
    "frontend/src/components/repair/index.ts",
    "frontend/src/components/review/FindingsInspector.tsx",
    "frontend/src/components/review/ContractReviewWorkspace.tsx",
    "README.md",
]

def sha256_file(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def main():
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    manifest = []
    
    print(f"Creating verified non-destructive snapshot at:\n  {SNAPSHOT_DIR}\n")
    
    for rel_path in FILES_TO_SNAPSHOT:
        src = REPO_ROOT / rel_path
        if not src.exists():
            print(f"[WARN] File not found: {rel_path}")
            continue
            
        dst = SNAPSHOT_DIR / rel_path
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        
        src_hash = sha256_file(src)
        dst_hash = sha256_file(dst)
        
        if src_hash != dst_hash:
            raise RuntimeError(f"Hash mismatch copying {rel_path} to snapshot!")
            
        with open(dst, "rb") as f:
            data = f.read()
            assert len(data) == os.path.getsize(dst)
            
        manifest.append({
            "relative_path": rel_path,
            "sha256": src_hash,
            "size_bytes": os.path.getsize(src),
            "status": "VERIFIED_IDENTICAL"
        })
        print(f"[OK] {rel_path} -> SHA256: {src_hash[:16]}... ({os.path.getsize(src)} bytes)")

    manifest_path = SNAPSHOT_DIR / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
        
    print(f"\nSnapshot complete. {len(manifest)} files backed up and verified.")
    print(f"Manifest written to: {manifest_path}")

if __name__ == "__main__":
    main()
