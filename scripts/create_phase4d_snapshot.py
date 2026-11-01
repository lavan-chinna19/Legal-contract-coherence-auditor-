"""
scripts/create_phase4d_snapshot.py — Creates an immutable non-destructive external backup snapshot
for Phase 4D before any modifications.
"""
import os
import json
import shutil
import hashlib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BACKUP_DIR = Path(r"C:\Users\gowth\.gemini\antigravity-ide\brain\69e9beaf-b94a-4f84-8c17-05ea3face92e\scratch\phase4d_backup_snapshot")

FILES_TO_BACKUP = [
    "src/api/schema.py",
    "src/api/v1/router.py",
    "src/api/main.py",
    "src/scoring/pipeline.py",
    "src/scoring/channel_a.py",
    "src/scoring/channel_b.py",
    "src/scoring/severity.py",
    "src/rules/reference_checker.py",
    "src/rules/date_checker.py",
    "src/rules/unified_pipeline.py",
    "src/scoring/repositioning.py",
    "frontend/src/app/page.tsx",
    "frontend/src/app/layout.tsx",
    "frontend/src/app/globals.css",
    "frontend/package.json",
    "README.md",
]

def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def create_snapshot():
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    manifest = {
        "phase": "PHASE 4D",
        "timestamp": "2026-10-21T14:36:00Z",
        "git_head": "23dbcf536f2fb3dce1611e2d2ae71e9ca8c86f55",
        "files": []
    }
    
    for rel_path in FILES_TO_BACKUP:
        src = REPO_ROOT / rel_path
        if not src.exists():
            print(f"Skipping nonexistent {rel_path}")
            continue
        dst = BACKUP_DIR / rel_path
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        
        orig_hash = sha256_file(src)
        bk_hash = sha256_file(dst)
        assert orig_hash == bk_hash, f"Hash mismatch on {rel_path}"
        
        manifest["files"].append({
            "rel_path": rel_path,
            "repo_path": str(src),
            "backup_path": str(dst),
            "sha256": orig_hash,
            "size_bytes": src.stat().st_size
        })
        print(f"Backed up: {rel_path} ({orig_hash[:12]}...)")
        
    manifest_path = BACKUP_DIR / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
        
    print(f"\nSnapshot complete. {len(manifest['files'])} files backed up to {BACKUP_DIR}")
    print(f"Manifest written to {manifest_path}")

if __name__ == "__main__":
    create_snapshot()
