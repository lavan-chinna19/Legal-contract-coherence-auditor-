"""
Completeness Checker (Tier 1) - Prompt 7

Implements zero-shot NLI based completeness checking using facebook/bart-large-mnli.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from transformers import pipeline
import logging

from src.config import ClauseRecord

# Set up local logger
logger = logging.getLogger(__name__)
# Do not log raw text to avoid plaintext leakage.

@dataclass
class CompletenessReportItem:
    expected_type: str
    is_present: bool
    nli_score: float
    threshold: float
    evidence_clause_id: Optional[str] = None
    evidence_location: Optional[str] = None
    contract_category: str = "Unknown"
    checker_version: str = "facebook/bart-large-mnli"

@dataclass
class CompletenessResult:
    doc_id: str
    category: str
    reports: List[CompletenessReportItem]
    is_complete: bool
    
    def to_dict(self) -> dict:
        return {
            "doc_id": self.doc_id,
            "category": self.category,
            "is_complete": self.is_complete,
            "reports": [
                {
                    "expected_type": r.expected_type,
                    "is_present": r.is_present,
                    "nli_score": r.nli_score,
                    "threshold": r.threshold,
                    "evidence_clause_id": r.evidence_clause_id,
                    "evidence_location": r.evidence_location,
                    "contract_category": r.contract_category,
                    "checker_version": r.checker_version
                } for r in self.reports
            ]
        }

class CompletenessChecker:
    def __init__(self, threshold: float = 0.5):
        """
        threshold: The NLI entailment threshold.
        Derived as an INITIAL DEFAULT — NOT EMPIRICALLY TUNED.
        Reasoning: A neutral default of 0.5 distinguishes entailment from contradiction/neutral in a standard softmax 
        distribution when used with zero-shot classification (entailment vs contradiction). 
        """
        self.threshold = threshold
        self.model_name = "facebook/bart-large-mnli"
        # Load zero-shot classification pipeline
        # Only loading on initialization.
        logger.info(f"Loading zero-shot pipeline: {self.model_name}")
        self.classifier = pipeline("zero-shot-classification", model=self.model_name)
        
        # Expected clause-type checklists based on LEDGAR analysis
        self.checklists = {
            "NDA": ["Confidentiality", "Governing Laws", "Notices", "Terminations"],
            "Employment Agreement": ["Base Salary", "Benefits", "Terminations", "Governing Laws"],
            "Service Agreement": ["Payments", "Indemnifications", "Governing Laws", "Terminations"],
            "Default": ["Governing Laws", "Notices", "Entire Agreements"]
        }

    def check_document(self, doc_id: str, clauses: List[ClauseRecord], category: str = "Default") -> CompletenessResult:
        if category not in self.checklists:
            category = "Default"
            
        expected_types = self.checklists[category]
        reports = []
        is_complete = True
        
        texts = [clause.text for clause in clauses]
        if not texts:
            return CompletenessResult(doc_id=doc_id, category=category, reports=[], is_complete=False)
            
        # Batch inference
        # We classify all clauses against all expected types at once
        results = self.classifier(texts, expected_types, multi_label=True)
        # If single clause, pipeline might not return a list
        if not isinstance(results, list):
            results = [results]
            
        for exp_type in expected_types:
            best_score = 0.0
            best_clause = None
            
            for i, res in enumerate(results):
                # find index of exp_type in res['labels']
                if exp_type in res['labels']:
                    idx = res['labels'].index(exp_type)
                    score = res['scores'][idx]
                    if score > best_score:
                        best_score = score
                        best_clause = clauses[i]
                        
            is_present = best_score >= self.threshold
            if not is_present:
                is_complete = False
                
            report = CompletenessReportItem(
                expected_type=exp_type,
                is_present=is_present,
                nli_score=best_score,
                threshold=self.threshold,
                evidence_clause_id=best_clause.clause_id if best_clause else None,
                evidence_location=f"Char {best_clause.char_start}-{best_clause.char_end}" if best_clause else None,
                contract_category=category,
                checker_version=self.model_name
            )
            reports.append(report)
            
        return CompletenessResult(doc_id=doc_id, category=category, reports=reports, is_complete=is_complete)
