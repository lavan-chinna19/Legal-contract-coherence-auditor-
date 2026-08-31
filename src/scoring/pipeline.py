"""
src/scoring/pipeline.py — Dual-Channel Anomaly Scoring Pipeline.
Integrates Channel A (Semantic OOD) and Channel B (Discourse Transition Coherence).
"""
import time
from typing import List, Optional, Dict, Any
import numpy as np

from src.config import (
    ClauseRecord,
    ENSEMBLE_ALPHA,
    SEVERITY_HIGH_THRESHOLD,
    SEVERITY_MED_THRESHOLD
)
from src.scoring.schema import ClauseScoringResult, DocumentScoringResult
from src.scoring.channel_a import ChannelAScorer
from src.scoring.channel_b import ChannelBScorer
from src.scoring.severity import SeverityRanker


class DualChannelScorer:
    """
    Dual-Channel Anomaly Detection Pipeline.
    Evaluates legal documents across both semantic (Channel A) and structural (Channel B) axes,
    with calibrated severity ranking and cross-channel agreement analysis.
    """

    def __init__(
        self,
        channel_a: Optional[ChannelAScorer] = None,
        channel_b: Optional[ChannelBScorer] = None,
        alpha: float = ENSEMBLE_ALPHA,
        high_threshold: float = SEVERITY_HIGH_THRESHOLD,
        med_threshold: float = SEVERITY_MED_THRESHOLD,
        calibrator: Optional[Any] = None,
        severity_ranker: Optional[SeverityRanker] = None
    ):
        self.channel_a = channel_a or ChannelAScorer()
        self.channel_b = channel_b or ChannelBScorer()
        self.alpha = alpha
        self.high_threshold = high_threshold
        self.med_threshold = med_threshold
        self.calibrator = calibrator
        self.severity_ranker = severity_ranker or SeverityRanker(
            high_threshold=high_threshold,
            med_threshold=med_threshold
        )

    def score_document(
        self,
        clauses: List[ClauseRecord],
        doc_id: Optional[str] = None
    ) -> DocumentScoringResult:
        """
        Runs dual-channel scoring across all clauses in a document.
        
        Args:
            clauses: List of ClauseRecord objects ordered by sequence_idx.
            doc_id: Optional document identifier.
            
        Returns:
            DocumentScoringResult: Document-level audit report.
        """
        if not clauses:
            effective_doc_id = doc_id or "empty_doc"
            return DocumentScoringResult(
                doc_id=effective_doc_id,
                total_clauses=0,
                anomaly_count=0,
                high_severity_count=0,
                medium_severity_count=0,
                mean_combined_score=0.0,
                max_combined_score=0.0,
                clauses=[],
                calibration_source="synthetic_shuffle_only"
            )

        effective_doc_id = doc_id or clauses[0].doc_id
        # Ensure ordered by sequence_idx
        sorted_clauses = sorted(clauses, key=lambda c: c.sequence_idx)

        # 1. Run Channel A (Semantic OOD)
        scores_a = self.channel_a.score_clauses(sorted_clauses)

        # 2. Run Channel B (Transition Coherence)
        scores_b = self.channel_b.score_document_clauses(sorted_clauses)

        # 3. Ensemble & Severity Assignment
        clause_results: List[ClauseScoringResult] = []
        high_count = 0
        med_count = 0
        anomaly_count = 0

        for i, c in enumerate(sorted_clauses):
            score_a, ev_a = scores_a[i]
            score_b, ev_b = scores_b[i]

            # Ensemble combination
            combined = self.alpha * score_a + (1.0 - self.alpha) * score_b
            combined = round(float(np.clip(combined, 0.0, 1.0)), 4)

            # Conformal interval
            ci = None
            if self.calibrator is not None and getattr(self.calibrator, "is_fitted", False):
                ci = self.calibrator.predict_interval(combined)

            # Decision-Support Severity Assessment
            assessment = self.severity_ranker.assess_clause(
                channel_a_score=score_a,
                channel_b_score=score_b,
                combined_score=combined,
                confidence_interval=ci
            )

            severity = assessment.severity
            is_anom = assessment.is_anomaly
            if severity == "HIGH":
                high_count += 1
                anomaly_count += 1
            elif severity == "MEDIUM":
                med_count += 1
                anomaly_count += 1

            # Preview text (bounded to max 120 chars to avoid logging full contract plaintext)
            preview = c.text[:100] + "..." if len(c.text) > 100 else c.text

            res = ClauseScoringResult(
                clause_id=c.clause_id,
                doc_id=effective_doc_id,
                sequence_idx=c.sequence_idx,
                text_preview=preview,
                channel_a_score=score_a,
                channel_b_score=score_b,
                combined_score=combined,
                channel_a_evidence=ev_a,
                channel_b_evidence=ev_b,
                is_anomaly=is_anom,
                severity=severity,
                source_label=c.label,
                confidence_interval=ci,
                calibration_source="synthetic_shuffle_only",
                cross_channel_agreement=assessment.cross_channel_agreement,
                agreement_type=assessment.agreement_type,
                interval_width=assessment.interval_width,
                severity_justification=assessment.severity_justification
            )
            clause_results.append(res)

        all_combined = [r.combined_score for r in clause_results]
        mean_score = round(float(np.mean(all_combined)), 4) if all_combined else 0.0
        max_score = round(float(np.max(all_combined)), 4) if all_combined else 0.0

        return DocumentScoringResult(
            doc_id=effective_doc_id,
            total_clauses=len(clause_results),
            anomaly_count=anomaly_count,
            high_severity_count=high_count,
            medium_severity_count=med_count,
            mean_combined_score=mean_score,
            max_combined_score=max_score,
            clauses=clause_results,
            metadata={
                "alpha_weight": self.alpha,
                "high_threshold": self.high_threshold,
                "med_threshold": self.med_threshold,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
            }
        )
