"""
src/feedback/storage.py — Hybrid SQLite / PostgreSQL storage for Tier-2 feedback (Prompt 18).

Supports both local SQLite and containerized/managed PostgreSQL transparently via DATABASE_URL.
"""
import os
import sqlite3
from contextlib import closing
from typing import List, Optional, Any
from pathlib import Path

from src.config import FEEDBACK_DB_PATH
from src.feedback.schema import FeedbackRecord

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False


def is_postgres() -> bool:
    """Returns True if DATABASE_URL points to a PostgreSQL instance."""
    db_url = os.environ.get("DATABASE_URL", "")
    return db_url.startswith("postgresql://") or db_url.startswith("postgres://")


def _get_connection(db_path: Path = FEEDBACK_DB_PATH) -> Any:
    """Gets a connection to PostgreSQL or SQLite based on environment."""
    if is_postgres():
        if not PSYCOPG2_AVAILABLE:
            raise RuntimeError("DATABASE_URL is set to PostgreSQL, but psycopg2 is not installed.")
        db_url = os.environ["DATABASE_URL"]
        conn = psycopg2.connect(db_url)
        return conn
    else:
        db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn


def init_db(db_path: Path = FEEDBACK_DB_PATH):
    """
    Initializes the schema for feedback in PostgreSQL or SQLite.
    """
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
    
    with closing(_get_connection(db_path)) as conn:
        with conn:
            cursor = conn.cursor()
            cursor.execute(create_table_sql)


def insert_feedback(record: FeedbackRecord, db_path: Path = FEEDBACK_DB_PATH):
    """
    Inserts a single feedback record into the active database (Postgres or SQLite).
    """
    if is_postgres():
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
    else:
        insert_sql = """
        INSERT OR REPLACE INTO feedback (
            feedback_id, doc_id, clause_id, original_severity, reviewer_verdict,
            corrected_severity, reviewer_id, timestamp, model_version,
            provenance, anomaly_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
    
    params = (
        record.feedback_id,
        record.doc_id,
        record.clause_id,
        record.original_severity,
        record.reviewer_verdict,
        record.corrected_severity,
        record.reviewer_id,
        record.timestamp,
        record.model_version,
        record.provenance,
        record.anomaly_id
    )

    with closing(_get_connection(db_path)) as conn:
        with conn:
            cursor = conn.cursor()
            cursor.execute(insert_sql, params)


def get_all_feedback(provenance_filter: Optional[str] = None, db_path: Path = FEEDBACK_DB_PATH) -> List[FeedbackRecord]:
    """
    Retrieves feedback records from PostgreSQL or SQLite.
    """
    use_pg = is_postgres()
    placeholder = "%s" if use_pg else "?"
    
    query = "SELECT * FROM feedback"
    params = []
    
    if provenance_filter:
        query += f" WHERE provenance = {placeholder}"
        params.append(provenance_filter)
        
    with closing(_get_connection(db_path)) as conn:
        if use_pg:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
        else:
            cursor = conn.cursor()
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        
    records = []
    for row in rows:
        records.append(FeedbackRecord(
            feedback_id=row['feedback_id'],
            doc_id=row['doc_id'],
            clause_id=row['clause_id'],
            original_severity=row['original_severity'],
            reviewer_verdict=row['reviewer_verdict'],
            corrected_severity=row['corrected_severity'],
            reviewer_id=row['reviewer_id'],
            timestamp=row['timestamp'],
            model_version=row['model_version'],
            provenance=row['provenance'],
            anomaly_id=row['anomaly_id']
        ))
    return records
