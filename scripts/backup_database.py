"""
scripts/backup_database.py — Automated Database Backup (Prompt 20).

Exports feedback database records to a versioned, timestamped JSON archive.
Compatible with both SQLite and PostgreSQL backends.
"""
import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, Any

from src.feedback.storage import get_all_feedback
from src.config import REPO_ROOT

BACKUP_DIR = REPO_ROOT / "data" / "backups"


def create_backup(dest_dir: Path = BACKUP_DIR) -> Path:
    dest_dir.mkdir(parents=True, exist_ok=True)
    records = get_all_feedback()
    
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    backup_file = dest_dir / f"feedback_backup_{timestamp}.json"
    
    payload: Dict[str, Any] = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "record_count": len(records),
        "records": [r.to_dict() for r in records]
    }
    
    with open(backup_file, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
        
    print(f"[OK] Backup successfully created at: {backup_file}")
    print(f"     Records archived: {len(records)}")
    return backup_file


if __name__ == "__main__":
    create_backup()
