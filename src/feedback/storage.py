"""
src/feedback/storage.py — SQLite storage implementation for Tier-2 feedback.
"""
import sqlite3
from contextlib import closing
from typing import List, Optional
from pathlib import Path

from src.config import FEEDBACK_DB_PATH
from src.feedback.schema import FeedbackRecord

def _get_connection(db_path: Path = FEEDBACK_DB_PATH) -> sqlite3.Connection:
    """Gets a connection to the SQLite database."""
    # Ensure directory exists
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path: Path = FEEDBACK_DB_PATH):
    """
    Initializes the SQLite schema for feedback.
    Designed for easy migration to Postgres later.
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
    Inserts a single feedback record into the database.
    """
    insert_sql = """
    INSERT INTO feedback (
        feedback_id, doc_id, clause_id, original_severity, reviewer_verdict,
        corrected_severity, reviewer_id, timestamp, model_version,
        provenance, anomaly_id
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    
    with closing(_get_connection(db_path)) as conn:
        with conn:
            cursor = conn.cursor()
            cursor.execute(
                insert_sql,
                (
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
            )

def get_all_feedback(provenance_filter: Optional[str] = None, db_path: Path = FEEDBACK_DB_PATH) -> List[FeedbackRecord]:
    """
    Retrieves feedback records. If provenance_filter is provided, filters by 'REAL' or 'SYNTHETIC_TEST'.
    """
    query = "SELECT * FROM feedback"
    params = []
    
    if provenance_filter:
        query += " WHERE provenance = ?"
        params.append(provenance_filter)
        
    with closing(_get_connection(db_path)) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
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
