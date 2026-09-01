"""
src/feedback/schema.py — Data model for Tier-2 human feedback.
"""
from dataclasses import dataclass, asdict
from typing import Optional, Any, Dict
import datetime

@dataclass
class FeedbackRecord:
    """
    Schema for persisting human or synthetic feedback.
    Never stores plaintext contract clauses.
    """
    feedback_id: str
    doc_id: str
    clause_id: str
    original_severity: str
    reviewer_verdict: str  # e.g., 'VALID', 'OVERKILL', 'MISSED', 'CORRECT'
    corrected_severity: Optional[str]
    reviewer_id: str
    timestamp: str
    model_version: str
    provenance: str  # 'REAL' or 'SYNTHETIC_TEST'
    anomaly_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def create(
        cls,
        doc_id: str,
        clause_id: str,
        original_severity: str,
        reviewer_verdict: str,
        reviewer_id: str,
        provenance: str,
        corrected_severity: Optional[str] = None,
        model_version: str = "v1",
        anomaly_id: Optional[str] = None
    ) -> 'FeedbackRecord':
        import uuid
        import time
        return cls(
            feedback_id=str(uuid.uuid4()),
            doc_id=doc_id,
            clause_id=clause_id,
            original_severity=original_severity,
            reviewer_verdict=reviewer_verdict,
            corrected_severity=corrected_severity,
            reviewer_id=reviewer_id,
            timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            model_version=model_version,
            provenance=provenance,
            anomaly_id=anomaly_id
        )
