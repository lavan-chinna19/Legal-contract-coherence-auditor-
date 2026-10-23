"""
src/research/independent_benchmark/evaluation.py
Pre-Registered Evaluation Engine for Baselines and Candidate Models.
"""
import csv
import os
import time
from typing import List, Dict, Any, Tuple, Optional

from src.research.structural_coherence.models import (
    BaselineB0_ChannelB,
    BaselineB1_ProductionEnsemble,
    BaselineB2_CosineDistance,
    CandidateC1_ContextualBoundaryDetector,
    CandidateC2_ContextualSequenceModel,
    CandidateC3_StructureAwareDependencyModel
)
from src.research.independent_benchmark.schema import (
    BenchmarkCase,
    EvaluationPrediction,
    GroundTruthLabel,
    MetricBundle
)
from src.research.independent_benchmark.latency import MatchedLatencyProfiler
from src.research.independent_benchmark.metrics import calculate_detection_metrics


def get_benchmark_models() -> Dict[str, Any]:
    """Instantiate frozen baselines and experimental candidate models."""
    return {
        "B0_ChannelB": BaselineB0_ChannelB(threshold=0.70),
        "B1_ProductionEnsemble": BaselineB1_ProductionEnsemble(threshold=0.50),
        "B2_CosineSimilarity": BaselineB2_CosineDistance(threshold=0.60),
        "C1_BoundaryContrast": CandidateC1_ContextualBoundaryDetector(threshold=0.50),
        "C2_SequenceBiLSTM": CandidateC2_ContextualSequenceModel(threshold=0.50),
        "C3_TopologicalDAG": CandidateC3_StructureAwareDependencyModel(threshold=0.50)
    }


class BenchmarkEvaluator:
    """
    Executes pre-registered evaluation protocol across benchmark cases.
    """

    def __init__(self, models: Optional[Dict[str, Any]] = None):
        self.models = models or get_benchmark_models()

    def evaluate_case(self, case: BenchmarkCase, model_key: str) -> EvaluationPrediction:
        """Run single model on a single benchmark case."""
        model = self.models[model_key]
        clauses = case.perturbed_clauses

        res, latency = MatchedLatencyProfiler.profile_evaluation(
            model=model,
            clauses=clauses,
            doc_id=case.annotation.case_id
        )

        gt_label = case.annotation.ground_truth_label
        is_gt_anomaly = gt_label in (
            GroundTruthLabel.VERIFIED_DISCOURSE_DEPENDENCY_VIOLATION,
            GroundTruthLabel.VERIFIED_EXPLICIT_STRUCTURAL_VIOLATION,
            GroundTruthLabel.VERIFIED_CONTENT_LOGIC_VIOLATION
        )

        return EvaluationPrediction(
            case_id=case.annotation.case_id,
            model_name=getattr(model, "name", model_key),
            model_version=getattr(model, "version", "1.0.0"),
            ground_truth_label=gt_label,
            is_ground_truth_anomaly=is_gt_anomaly,
            predicted_anomaly=res.is_anomaly,
            anomaly_score=round(float(res.max_structural_score), 4),
            threshold_used=float(res.threshold_used),
            predicted_clause_ids=res.predicted_anomaly_clause_ids,
            latency=latency,
            document_family_id=case.annotation.document_family_id,
            split=case.annotation.split,
            task_category=case.annotation.task_category.value
        )

    def evaluate_split(
        self,
        cases: List[BenchmarkCase],
        filter_eligible: bool = True
    ) -> Dict[str, List[EvaluationPrediction]]:
        """
        Evaluate all models across a specified split partition.
        """
        target_cases = [c for c in cases if not filter_eligible or c.annotation.eligibility_decision == "ELIGIBLE"]
        results = {m_key: [] for m_key in self.models}

        for case in target_cases:
            for m_key in self.models:
                pred = self.evaluate_case(case, m_key)
                results[m_key].append(pred)

        return results

    @staticmethod
    def export_predictions_csv(predictions: Dict[str, List[EvaluationPrediction]], output_path: str) -> None:
        """Export case-level prediction records to CSV."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "case_id", "model_name", "model_version", "document_family_id", "split",
                "task_category", "ground_truth_label", "is_gt_anomaly", "predicted_anomaly",
                "anomaly_score", "threshold_used", "predicted_clause_ids", "latency_total_ms",
                "latency_prep_ms", "latency_emb_ms", "latency_feat_ms", "latency_infer_ms", "latency_dec_ms"
            ])
            for m_key, preds in predictions.items():
                for p in preds:
                    writer.writerow([
                        p.case_id, p.model_name, p.model_version, p.document_family_id, p.split,
                        p.task_category, p.ground_truth_label.value, p.is_ground_truth_anomaly,
                        p.predicted_anomaly, p.anomaly_score, p.threshold_used,
                        ";".join(p.predicted_clause_ids), p.latency.total_end_to_end_ms,
                        p.latency.text_preparation_ms, p.latency.embedding_computation_ms,
                        p.latency.feature_extraction_ms, p.latency.model_inference_ms,
                        p.latency.decision_calculation_ms
                    ])
