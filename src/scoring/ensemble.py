"""
src/scoring/ensemble.py - Prompt 8 Score Ensembling for Channel B
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
import numpy as np

from src.config import ClauseRecord
from src.scoring.channel_b import ChannelBScorer
from src.evaluation.completeness import CompletenessChecker, CompletenessResult

@dataclass
class EnsembleClauseResult:
    clause_id: str
    sequence_idx: int
    fine_tuned_score: float
    zero_shot_score: float
    combined_score: float
    confidence_interval: Optional[tuple] = None  # (lower_bound, upper_bound)
    calibration_source: str = "synthetic_shuffle_only"

@dataclass
class EnsembleDocumentResult:
    doc_id: str
    ensemble_mode: str
    ensemble_weight: float
    clauses: List[EnsembleClauseResult]
    metadata: Dict[str, Any] = field(default_factory=dict)
    calibration_source: str = "synthetic_shuffle_only"

class ChannelBEnsembler:
    def __init__(
        self,
        mode: str = "combined",
        alpha: float = 0.5,
        channel_b: Optional[ChannelBScorer] = None,
        completeness_checker: Optional[CompletenessChecker] = None,
        calibrator: Optional[Any] = None
    ):
        """
        mode: "fine_tuned", "zero_shot", or "combined"
        alpha: Weight for fine_tuned_score (INITIAL DEFAULT — NOT EMPIRICALLY TUNED)
        """
        self.mode = mode
        self.alpha = alpha
        self.channel_b = channel_b or ChannelBScorer()
        self.completeness_checker = completeness_checker or CompletenessChecker(threshold=0.5)
        self.calibrator = calibrator
        
    def _get_zero_shot_score(self, clause_id: str, comp_res: CompletenessResult) -> float:
        """
        Converts a completeness report into a per-clause anomaly score [0.0, 1.0].
        If a clause is the best evidence for an expected type, its anomaly is low.
        If it's not expected evidence, we assign a neutral 0.5 anomaly.
        """
        fulfilled = [r for r in comp_res.reports if r.evidence_clause_id == clause_id and r.is_present]
        if fulfilled:
            return 1.0 - max(r.nli_score for r in fulfilled)
        return 0.5

    def score_document(self, clauses: List[ClauseRecord], doc_id: str, category: str = "Default") -> EnsembleDocumentResult:
        if not clauses:
            return EnsembleDocumentResult(doc_id=doc_id, ensemble_mode=self.mode, ensemble_weight=self.alpha, clauses=[])
            
        # 1. Fine-tuned scores
        ft_results = self.channel_b.score_document_clauses(clauses)
        
        # 2. Zero-shot scores
        comp_res = self.completeness_checker.check_document(doc_id, clauses, category=category)
        
        # 3. Ensemble
        ensemble_clauses = []
        for i, clause in enumerate(clauses):
            ft_score = ft_results[i][0]
            zs_score = self._get_zero_shot_score(clause.clause_id, comp_res)
            
            if self.mode == "fine_tuned":
                combined = ft_score
            elif self.mode == "zero_shot":
                combined = zs_score
            else: # combined
                # Both scores are in [0, 1]. No additional normalization needed.
                combined = self.alpha * ft_score + (1.0 - self.alpha) * zs_score
                
            combined = float(np.clip(combined, 0.0, 1.0))
            
            ci = None
            if self.calibrator is not None and getattr(self.calibrator, "is_fitted", False):
                ci = self.calibrator.predict_interval(combined)
            
            ensemble_clauses.append(EnsembleClauseResult(
                clause_id=clause.clause_id,
                sequence_idx=clause.sequence_idx,
                fine_tuned_score=ft_score,
                zero_shot_score=zs_score,
                combined_score=combined,
                confidence_interval=ci,
                calibration_source="synthetic_shuffle_only"
            ))
            
        return EnsembleDocumentResult(
            doc_id=doc_id,
            ensemble_mode=self.mode,
            ensemble_weight=self.alpha,
            clauses=ensemble_clauses,
            metadata={
                "fine_tuned_model": "distilbert-base-uncased",
                "zero_shot_model": self.completeness_checker.model_name,
                "calibration_source": "synthetic_shuffle_only"
            },
            calibration_source="synthetic_shuffle_only"
        )
