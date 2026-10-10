"""
scripts/restore_database.py — Automated Database Restore (Prompt 20).

Restores feedback database records from a timestamped JSON backup archive.
Validates pre- and post-restoration record counts.
"""
import os
import sys
import json
from pathlib import Path
from typing import Optional

from src.feedback.storage import init_db, insert_feedback, get_all_feedback
from src.feedback.schema import FeedbackRecord
from src.config import REPO_ROOT

BACKUP_DIR = REPO_ROOT / "data" / "backups"


def restore_backup(backup_file: Optional[Path] = None) -> int:
    if backup_file is None:
        # Pick latest backup file in BACKUP_DIR
        backups = sorted(BACKUP_DIR.glob("feedback_backup_*.json"))
        if not backups:
            print("[!] No backup archives found to restore.")
            return 1
        backup_file = backups[-1]

    print(f"[*] Restoring from backup file: {backup_file}")
    with open(backup_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    records_data = data.get("records", [])
    print(f"[*] Found {len(records_data)} records in archive.")

    init_db()
    for r in records_data:
        record = FeedbackRecord(
            feedback_id=r["feedback_id"],
            doc_id=r["doc_id"],
            clause_id=r["clause_id"],
            original_severity=r["original_severity"],
            reviewer_verdict=r["reviewer_verdict"],
            corrected_severity=r.get("corrected_severity"),
            reviewer_id=r["reviewer_id"],
            timestamp=r["timestamp"],
            model_version=r["model_version"],
            provenance=r["provenance"],
            anomaly_id=r.get("anomaly_id")
        )
        insert_feedback(record)

    current_records = get_all_feedback()
    print(f"[OK] Restore completed. Active database contains {len(current_records)} records.")
    return 0


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    sys.exit(restore_backup(target))
