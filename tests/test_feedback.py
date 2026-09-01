"""
tests/test_feedback.py — Tests for Tier-2 human feedback loop.
"""
import pytest
import os
import sqlite3
from pathlib import Path
from src.feedback.storage import init_db, insert_feedback, get_all_feedback
from src.feedback.schema import FeedbackRecord
from src.feedback.reviewer import submit_verdict
from src.feedback.refit import run_refit
from src.config import FEEDBACK_DB_PATH, THRESHOLDS_PATH, SEVERITY_HIGH_THRESHOLD, SEVERITY_MED_THRESHOLD

@pytest.fixture(autouse=True)
def setup_teardown():
    # Setup: Use a test database
    if FEEDBACK_DB_PATH.exists():
        os.remove(FEEDBACK_DB_PATH)
    if THRESHOLDS_PATH.exists():
        os.remove(THRESHOLDS_PATH)
    
    init_db()
    
    yield
    
    # Teardown
    if FEEDBACK_DB_PATH.exists():
        os.remove(FEEDBACK_DB_PATH)
    if THRESHOLDS_PATH.exists():
        os.remove(THRESHOLDS_PATH)

def test_schema_creation():
    # Verify DB file is created
    assert FEEDBACK_DB_PATH.exists()
    
    # Verify table structure
    conn = sqlite3.connect(FEEDBACK_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='feedback';")
    assert cursor.fetchone() is not None
    conn.close()

def test_insert_and_retrieve_synthetic():
    record = FeedbackRecord.create(
        doc_id="doc-123",
        clause_id="cl-1",
        original_severity="HIGH",
        reviewer_verdict="OVERKILL",
        reviewer_id="test_runner",
        provenance="SYNTHETIC_TEST"
    )
    insert_feedback(record)
    
    records = get_all_feedback()
    assert len(records) == 1
    assert records[0].feedback_id == record.feedback_id
    assert records[0].doc_id == "doc-123"
    assert records[0].provenance == "SYNTHETIC_TEST"
    
    # Text content shouldn't be here
    assert not hasattr(records[0], "text")
    
def test_reviewer_mechanism():
    submit_verdict(
        doc_id="doc-456",
        clause_id="cl-2",
        original_severity="MEDIUM",
        reviewer_verdict="VALID",
        reviewer_id="human_1",
        provenance="REAL"
    )
    
    real_records = get_all_feedback(provenance_filter="REAL")
    assert len(real_records) == 1
    assert real_records[0].reviewer_verdict == "VALID"
    assert real_records[0].doc_id == "doc-456"

def test_refit_job_updates_thresholds():
    # Insert some synthetic feedback indicating HIGH is OVERKILL
    for _ in range(3):
        submit_verdict(
            doc_id="doc-test",
            clause_id="cl-test",
            original_severity="HIGH",
            reviewer_verdict="OVERKILL",
            reviewer_id="test",
            provenance="SYNTHETIC_TEST"
        )
        
    old, new, count = run_refit(provenance="SYNTHETIC_TEST")
    
    assert count == 3
    # If overkill > valid, high threshold should go up
    assert new["SEVERITY_HIGH_THRESHOLD"] > old["SEVERITY_HIGH_THRESHOLD"]
    assert THRESHOLDS_PATH.exists()
    
def test_refit_job_empty():
    old, new, count = run_refit(provenance="REAL")
    assert count == 0
    assert new["SEVERITY_HIGH_THRESHOLD"] == SEVERITY_HIGH_THRESHOLD
    
def test_no_plaintext():
    record = FeedbackRecord.create(
        doc_id="doc-123",
        clause_id="cl-1",
        original_severity="HIGH",
        reviewer_verdict="VALID",
        reviewer_id="test",
        provenance="SYNTHETIC_TEST"
    )
    # The record should not accept arbitrary kwargs that leak text
    # Data classes enforce fields, so passing `text="Some contract"` would fail at creation time.
    d = record.to_dict()
    assert "text" not in d
