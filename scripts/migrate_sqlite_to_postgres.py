"""
scripts/migrate_sqlite_to_postgres.py — Migrates SQLite Feedback Records to PostgreSQL (Prompt 18).

Usage:
    python scripts/migrate_sqlite_to_postgres.py [--sqlite-path PATH] [--pg-url URL]
"""
import os
import sys
import argparse
import sqlite3
from pathlib import Path
from contextlib import closing

try:
    import psycopg2
    from psycopg2.extras import execute_batch
except ImportError:
    psycopg2 = None

from src.config import FEEDBACK_DB_PATH


def migrate(sqlite_path: Path, pg_url: str):
    print(f"[*] Starting feedback database migration...")
    print(f"    Source (SQLite): {sqlite_path}")
    print(f"    Target (Postgres): {pg_url.split('@')[-1] if '@' in pg_url else pg_url}")

    if not sqlite_path.exists():
        print(f"[!] Source SQLite database does not exist at {sqlite_path}. Nothing to migrate.")
        return 0

    if psycopg2 is None:
        print("[!] psycopg2 is not installed. Please install psycopg2-binary.")
        return 1

    # 1. Read records from SQLite
    with closing(sqlite3.connect(sqlite_path)) as s_conn:
        s_conn.row_factory = sqlite3.Row
        with s_conn:
            cursor = s_conn.cursor()
            # Check if table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='feedback'")
            if not cursor.fetchone():
                print("[!] Table 'feedback' does not exist in SQLite source. Nothing to migrate.")
                return 0
            cursor.execute("SELECT * FROM feedback")
            rows = cursor.fetchall()

    record_count = len(rows)
    print(f"[*] Found {record_count} feedback records in SQLite.")
    if record_count == 0:
        print("[*] No records to migrate. Exiting clean.")
        return 0

    # 2. Connect to Postgres & Ensure Schema
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS feedback (
        feedback_id TEXT PRIMARY KEY,
        doc_id TEXT NOT NULL,
        clause_id TEXT NOT NULL,
        original_severity TEXT NOT NULL,
        reviewer_verdict TEXT NOT NULL,
        corrected_severity TEXT,
        reviewer_id TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        model_version TEXT NOT NULL,
        provenance TEXT NOT NULL,
        anomaly_id TEXT
    );
    """

    insert_sql = """
    INSERT INTO feedback (
        feedback_id, doc_id, clause_id, original_severity, reviewer_verdict,
        corrected_severity, reviewer_id, timestamp, model_version,
        provenance, anomaly_id
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (feedback_id) DO UPDATE SET
        reviewer_verdict = EXCLUDED.reviewer_verdict,
        corrected_severity = EXCLUDED.corrected_severity;
    """

    with closing(psycopg2.connect(pg_url)) as p_conn:
        with p_conn:
            with p_conn.cursor() as p_cur:
                p_cur.execute(create_table_sql)

                data = [
                    (
                        r["feedback_id"],
                        r["doc_id"],
                        r["clause_id"],
                        r["original_severity"],
                        r["reviewer_verdict"],
                        r["corrected_severity"],
                        r["reviewer_id"],
                        r["timestamp"],
                        r["model_version"],
                        r["provenance"],
                        r["anomaly_id"]
                    )
                    for r in rows
                ]

                execute_batch(p_cur, insert_sql, data)

            # Validate target count
            with p_conn.cursor() as p_cur:
                p_cur.execute("SELECT COUNT(*) FROM feedback")
                target_count = p_cur.fetchone()[0]

    print(f"[OK] Successfully migrated {record_count} records. PostgreSQL table now contains {target_count} records.")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Migrate feedback database from SQLite to PostgreSQL")
    parser.add_argument("--sqlite-path", type=Path, default=FEEDBACK_DB_PATH)
    parser.add_argument("--pg-url", type=str, default=os.environ.get("DATABASE_URL", ""))

    args = parser.parse_args()

    if not args.pg_url:
        print("[!] Error: DATABASE_URL environment variable or --pg-url argument is required.")
        sys.exit(1)

    sys.exit(migrate(args.sqlite_path, args.pg_url))
