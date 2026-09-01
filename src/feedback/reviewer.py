"""
src/feedback/reviewer.py — Reviewer mechanism for tier-2 feedback collection.
"""
from typing import Optional
from src.feedback.schema import FeedbackRecord
from src.feedback.storage import insert_feedback, init_db

def submit_verdict(
    doc_id: str,
    clause_id: str,
    original_severity: str,
    reviewer_verdict: str,
    reviewer_id: str,
    provenance: str,
    corrected_severity: Optional[str] = None,
    model_version: str = "v1",
    anomaly_id: Optional[str] = None
) -> FeedbackRecord:
    """
    Submits a verdict to the feedback storage.
    Ensures that the DB is initialized before inserting.
    
    Valid verdicts might be: VALID, OVERKILL, MISSED
    """
    init_db()
    
    record = FeedbackRecord.create(
        doc_id=doc_id,
        clause_id=clause_id,
        original_severity=original_severity,
        reviewer_verdict=reviewer_verdict,
        reviewer_id=reviewer_id,
        provenance=provenance,
        corrected_severity=corrected_severity,
        model_version=model_version,
        anomaly_id=anomaly_id
    )
    
    insert_feedback(record)
    return record
