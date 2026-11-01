"""
scripts/create_phase4c_snapshot.py — Phase 4C Non-Destructive Snapshot & Hash Manifest.
Creates backup outside repo at artifact scratch directory and verifies readability.
"""
import os
import shutil
import hashlib
from pathlib import Path

REPO_ROOT = Path("f:/projects/nlp/Legal-contract-coherence-auditor-")
conv_id = os.environ.get("CONVERSATION_ID", "69e9beaf-b94a-4f84-8c17-05ea3face92e")
SNAPSHOT_DIR = Path(rf"C:\Users\gowth\.gemini\antigravity-ide\brain\{conv_id}\scratch\phase4c_backup_snapshot")

# Key source and configuration files that could be touched or read during Phase 4C
FILES_TO_SNAPSHOT = [
    "src/api/v1/router.py",
    "src/api/schema.py",
    "src/api/main.py",
    "src/scoring/channel_a.py",
    "src/scoring/channel_b.py",
    "src/scoring/pipeline.py",
    "src/scoring/ensemble.py",
    "src/scoring/severity.py",
    "src/scoring/schema.py",
    "src/coherence/fine_tuned.py",
    "src/coherence/model.py",
    "src/embeddings/frozen.py",
    "frontend/src/app/page.tsx",
    "frontend/src/app/globals.css",
    "frontend/src/app/layout.tsx",
    "frontend/src/components/review/ContractReviewWorkspace.tsx",
    "frontend/src/components/review/FindingsInspector.tsx",
    "frontend/src/components/review/ScoreEvidencePanel.tsx",
    "frontend/package.json",
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
        
        # Verify readability & hash parity
        if src_hash != dst_hash:
            raise RuntimeError(f"Hash mismatch copying {rel_path} to snapshot!")
            
        # Verify dst is readable
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

    import json
    manifest_path = SNAPSHOT_DIR / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
        
    print(f"\nSnapshot complete. {len(manifest)} files backed up and verified.")
    print(f"Manifest written to: {manifest_path}")

if __name__ == "__main__":
    main()
