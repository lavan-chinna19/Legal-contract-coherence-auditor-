"""
src/redteam/runner.py — Experiment execution engine for Self Red-Team Robustness Laboratory.
Executes the unchanged, frozen UnifiedAuditor on original vs perturbed document copies in memory,
evaluating transformation validity, ground-truth oracle satisfaction, detector sensitivity,
channel ablations, attribution validity, and failure diagnosis.
"""
import time
from typing import List, Dict, Any, Optional, Tuple

from src.config import ClauseRecord
from src.rules.unified_pipeline import UnifiedAuditor
from src.rules.schema import UnifiedAuditReport, RuleFlag
from src.scoring.schema import DocumentScoringResult, ClauseScoringResult
from src.redteam.schema import (
    PerturbationType,
    PerturbationDifficulty,
    DetectionStatus,
    PerturbationScenario,
    OracleValidationResult,
    ChannelAblationScores,
    RedTeamCaseResult,
    RedTeamBatchReport
)
from src.redteam.transformations import (
    compute_clauses_checksum,
    apply_clause_displacement,
    apply_clause_swap,
    apply_exact_duplication,
    apply_near_duplication,
    apply_broken_reference,
    apply_missing_exhibit,
    apply_date_inversion,
    apply_clause_deletion,
    apply_negative_control,
    apply_combined_perturbation
)
from src.redteam.oracle import IndependentGroundTruthOracle


class RedTeamExperimentRunner:
    """
    Orchestrates pure in-memory red-team experiments.
    Never mutates original ClauseRecord instances or production document state.
    """

    def __init__(
        self,
        auditor: Optional[UnifiedAuditor] = None,
        oracle: Optional[IndependentGroundTruthOracle] = None,
        structural_anomaly_threshold: float = 0.08
    ):
        self.auditor = auditor or UnifiedAuditor()
        self.oracle = oracle or IndependentGroundTruthOracle()
        self.structural_anomaly_threshold = structural_anomaly_threshold

    def run_scenario(
        self,
        scenario: PerturbationScenario,
        original_clauses: List[ClauseRecord]
    ) -> RedTeamCaseResult:
        """
        Executes a single end-to-end red-team scenario.
        """
        start_time = time.perf_counter()
        orig_checksum = compute_clauses_checksum(original_clauses)

        # 1. Apply Transformation (copy-on-write)
        try:
            pert_clauses, meta = self._apply_transformation(scenario, original_clauses)
            pert_checksum = meta.get("perturbed_checksum", compute_clauses_checksum(pert_clauses))
        except Exception as e:
            exec_time = (time.perf_counter() - start_time) * 1000.0
            invalid_oracle = OracleValidationResult(
                scenario_id=scenario.scenario_id,
                valid_transformation=False,
                oracle_condition="TRANSFORMATION_FAILED",
                expected_detector="NONE",
                ground_truth_supported=False,
                ground_truth_reason=f"Transformation execution error: {str(e)}",
                affected_clause_ids=[],
                eligible_for_strict_evaluation=False
            )
            return RedTeamCaseResult(
                scenario_id=scenario.scenario_id,
                perturbation_type=scenario.perturbation_type,
                difficulty=scenario.difficulty,
                source_doc_id=scenario.source_doc_id,
                original_checksum=orig_checksum,
                perturbed_checksum="",
                oracle_result=invalid_oracle,
                detection_status=DetectionStatus.EXPERIMENT_FAILED,
                attribution_valid=False,
                original_mean_combined=0.0,
                perturbed_mean_combined=0.0,
                delta_mean_combined=0.0,
                original_anomaly_count=0,
                perturbed_anomaly_count=0,
                delta_anomaly_count=0,
                original_rule_flag_count=0,
                perturbed_rule_flag_count=0,
                new_rule_flags=[],
                mean_channel_a_delta=0.0,
                mean_channel_b_delta=0.0,
                max_affected_clause_b_delta=0.0,
                ablations=ChannelAblationScores(0.0, 0.0, 0.0, 0, 0),
                affected_clause_ids=[],
                failure_category="TRANSFORMATION_EXCEPTION",
                failure_explanation=str(e),
                execution_time_ms=exec_time
            )

        # 2. Independent Ground-Truth Oracle Validation (Zero checker calls)
        oracle_res = self.oracle.validate_scenario(
            scenario, original_clauses, pert_clauses, meta
        )

        if not oracle_res.valid_transformation:
            exec_time = (time.perf_counter() - start_time) * 1000.0
            return RedTeamCaseResult(
                scenario_id=scenario.scenario_id,
                perturbation_type=scenario.perturbation_type,
                difficulty=scenario.difficulty,
                source_doc_id=scenario.source_doc_id,
                original_checksum=orig_checksum,
                perturbed_checksum=pert_checksum,
                oracle_result=oracle_res,
                detection_status=DetectionStatus.INVALID_SCENARIO,
                attribution_valid=False,
                original_mean_combined=0.0,
                perturbed_mean_combined=0.0,
                delta_mean_combined=0.0,
                original_anomaly_count=0,
                perturbed_anomaly_count=0,
                delta_anomaly_count=0,
                original_rule_flag_count=0,
                perturbed_rule_flag_count=0,
                new_rule_flags=[],
                mean_channel_a_delta=0.0,
                mean_channel_b_delta=0.0,
                max_affected_clause_b_delta=0.0,
                ablations=ChannelAblationScores(0.0, 0.0, 0.0, 0, 0),
                affected_clause_ids=oracle_res.affected_clause_ids,
                failure_category="ORACLE_VALIDATION_FAILURE",
                failure_explanation=oracle_res.ground_truth_reason,
                execution_time_ms=exec_time
            )

        # 3. Execute Frozen Auditor on Original & Perturbed In-Memory Copies
        orig_report: UnifiedAuditReport = self.auditor.audit_document(original_clauses)
        pert_report: UnifiedAuditReport = self.auditor.audit_document(pert_clauses)

        # 4. Quantitative Score Deltas
        orig_scoring = orig_report.scoring_result
        pert_scoring = pert_report.scoring_result

        orig_mean_c = getattr(orig_scoring, "mean_combined_score", 0.0)
        pert_mean_c = getattr(pert_scoring, "mean_combined_score", 0.0)
        delta_mean_c = pert_mean_c - orig_mean_c

        orig_anomalies = getattr(orig_scoring, "anomaly_count", 0)
        pert_anomalies = getattr(pert_scoring, "anomaly_count", 0)
        delta_anomalies = pert_anomalies - orig_anomalies

        # Channel-specific score changes
        orig_a_scores = [c.channel_a_score for c in orig_scoring.clauses]
        pert_a_scores = [c.channel_a_score for c in pert_scoring.clauses]
        orig_b_scores = [c.channel_b_score for c in orig_scoring.clauses]
        pert_b_scores = [c.channel_b_score for c in pert_scoring.clauses]

        mean_a_delta = (sum(pert_a_scores) / max(len(pert_a_scores), 1)) - (sum(orig_a_scores) / max(len(orig_a_scores), 1))
        mean_b_delta = (sum(pert_b_scores) / max(len(pert_b_scores), 1)) - (sum(orig_b_scores) / max(len(orig_b_scores), 1))

        # Max Channel B delta on affected clauses / boundaries
        affected_ids = set(oracle_res.affected_clause_ids)
        affected_b_deltas = []
        for p_clause in pert_scoring.clauses:
            if p_clause.clause_id in affected_ids:
                # Find matching original clause score if present
                orig_match = next((c for c in orig_scoring.clauses if c.clause_id == p_clause.clause_id), None)
                if orig_match:
                    affected_b_deltas.append(p_clause.channel_b_score - orig_match.channel_b_score)
                else:
                    affected_b_deltas.append(p_clause.channel_b_score)

        max_affected_b_delta = max(affected_b_deltas) if affected_b_deltas else 0.0

        # Rule Flags Analysis
        orig_flag_keys = {
            (
                f.flag_type,
                f.clause_id or "",
                str(f.evidence.get("citation_text", "")),
                str(f.evidence.get("target_id", "")),
                str(f.evidence.get("start_date", "")),
                str(f.evidence.get("end_date", ""))
            )
            for f in orig_report.rule_flags
        }
        new_flags = []
        for f in pert_report.rule_flags:
            key = (
                f.flag_type,
                f.clause_id or "",
                str(f.evidence.get("citation_text", "")),
                str(f.evidence.get("target_id", "")),
                str(f.evidence.get("start_date", "")),
                str(f.evidence.get("end_date", ""))
            )
            if key not in orig_flag_keys:
                new_flags.append(f.to_dict())

        # 5. Evaluate Detection Status and Attribution
        detection_status, attribution_valid, failure_cat, failure_exp = self._evaluate_detection_outcome(
            scenario=scenario,
            oracle_res=oracle_res,
            orig_report=orig_report,
            pert_report=pert_report,
            new_flags=new_flags,
            max_affected_b_delta=max_affected_b_delta,
            delta_anomalies=delta_anomalies
        )

        # 6. Ablation Scores
        ablations = ChannelAblationScores(
            channel_a_only_anomaly_delta=mean_a_delta,
            channel_b_only_anomaly_delta=mean_b_delta,
            dual_channel_combined_delta=delta_mean_c,
            rule_checker_flags_count=len(new_flags),
            integrated_pipeline_flags_count=len(new_flags) + max(delta_anomalies, 0)
        )

        exec_time = (time.perf_counter() - start_time) * 1000.0

        return RedTeamCaseResult(
            scenario_id=scenario.scenario_id,
            perturbation_type=scenario.perturbation_type,
            difficulty=scenario.difficulty,
            source_doc_id=scenario.source_doc_id,
            original_checksum=orig_checksum,
            perturbed_checksum=pert_checksum,
            oracle_result=oracle_res,
            detection_status=detection_status,
            attribution_valid=attribution_valid,
            original_mean_combined=round(orig_mean_c, 5),
            perturbed_mean_combined=round(pert_mean_c, 5),
            delta_mean_combined=round(delta_mean_c, 5),
            original_anomaly_count=orig_anomalies,
            perturbed_anomaly_count=pert_anomalies,
            delta_anomaly_count=delta_anomalies,
            original_rule_flag_count=len(orig_report.rule_flags),
            perturbed_rule_flag_count=len(pert_report.rule_flags),
            new_rule_flags=new_flags,
            mean_channel_a_delta=round(mean_a_delta, 5),
            mean_channel_b_delta=round(mean_b_delta, 5),
            max_affected_clause_b_delta=round(max_affected_b_delta, 5),
            ablations=ablations,
            affected_clause_ids=oracle_res.affected_clause_ids,
            failure_category=failure_cat,
            failure_explanation=failure_exp,
            execution_time_ms=round(exec_time, 2)
        )

    def _apply_transformation(
        self,
        scenario: PerturbationScenario,
        clauses: List[ClauseRecord]
    ) -> Tuple[List[ClauseRecord], Dict[str, Any]]:
        ptype = scenario.perturbation_type
        params = scenario.parameters

        if ptype == PerturbationType.P1_DISPLACEMENT:
            source_slot = params.get("source_slot", 0)
            target_slot = params.get("target_slot", len(clauses) - 1)
            return apply_clause_displacement(clauses, source_slot, target_slot)

        elif ptype == PerturbationType.P2_SWAP:
            slot_a = params.get("slot_a", 0)
            slot_b = params.get("slot_b", 1)
            return apply_clause_swap(clauses, slot_a, slot_b)

        elif ptype == PerturbationType.P3_EXACT_DUPLICATION:
            source_slot = params.get("source_slot", 0)
            insert_slot = params.get("insert_slot", len(clauses))
            return apply_exact_duplication(clauses, source_slot, insert_slot)

        elif ptype == PerturbationType.P4_NEAR_DUPLICATION:
            source_slot = params.get("source_slot", 0)
            insert_slot = params.get("insert_slot", len(clauses))
            return apply_near_duplication(clauses, source_slot, insert_slot)

        elif ptype == PerturbationType.P5_BROKEN_REFERENCE:
            clause_id = scenario.target_clause_ids[0]
            old_sec = params.get("old_target_sec", "2")
            new_sec = params.get("new_nonexistent_sec", "Section 99")
            return apply_broken_reference(clauses, clause_id, old_sec, new_sec)

        elif ptype == PerturbationType.P6_MISSING_EXHIBIT:
            clause_id = scenario.target_clause_ids[0]
            new_ex = params.get("new_nonexistent_exhibit", "Exhibit Z")
            return apply_missing_exhibit(clauses, clause_id, new_nonexistent_exhibit=new_ex)

        elif ptype == PerturbationType.P7_DATE_INVERSION:
            clause_id = scenario.target_clause_ids[0]
            inv_type = params.get("inversion_type", "INVERTED_CONTRACT_TERM")
            new_date = params.get("new_date_str", "December 31, 2020")
            return apply_date_inversion(clauses, clause_id, inversion_type=inv_type, new_date_str=new_date)

        elif ptype == PerturbationType.P8_DELETION:
            target_slot = params.get("target_slot", 1)
            return apply_clause_deletion(clauses, target_slot)

        elif ptype == PerturbationType.P9_NEGATIVE_CONTROL:
            return apply_negative_control(clauses)

        elif ptype == PerturbationType.P10_COMBINED:
            steps = params.get("steps", [])
            return apply_combined_perturbation(clauses, steps)

        else:
            raise ValueError(f"Unsupported perturbation type: {ptype}")

    def _evaluate_detection_outcome(
        self,
        scenario: PerturbationScenario,
        oracle_res: OracleValidationResult,
        orig_report: UnifiedAuditReport,
        pert_report: UnifiedAuditReport,
        new_flags: List[Dict[str, Any]],
        max_affected_b_delta: float,
        delta_anomalies: int
    ) -> Tuple[DetectionStatus, bool, Optional[str], Optional[str]]:
        """
        Determines detection status, attribution validity, and failure diagnosis.
        """
        ptype = scenario.perturbation_type

        # Case 1: Negative Control
        if ptype == PerturbationType.P9_NEGATIVE_CONTROL:
            # For negative controls, we test for false positives
            false_positives = len(new_flags) + max(delta_anomalies, 0)
            if false_positives == 0:
                return DetectionStatus.NOT_APPLICABLE, True, None, "Clean negative control produced zero false positives."
            else:
                return DetectionStatus.DETECTED, False, "FALSE_POSITIVE_ON_CLEAN_CONTROL", f"Unperturbed control generated {false_positives} spurious findings."

        # Case 2: Ineligible for strict evaluation (e.g. Duplication where no dedicated detector exists)
        if not oracle_res.eligible_for_strict_evaluation:
            if ptype == PerturbationType.P3_EXACT_DUPLICATION:
                return (
                    DetectionStatus.NOT_APPLICABLE,
                    False,
                    "DEDICATED_DUPLICATE_DETECTOR_UNAVAILABLE",
                    "LexAudit does not possess a dedicated duplicate clause rule checker. Channel B transition response measured descriptively."
                )
            elif ptype == PerturbationType.P4_NEAR_DUPLICATION:
                return (
                    DetectionStatus.NOT_APPLICABLE,
                    False,
                    "EXPLORATORY_EVALUATION",
                    "Near-duplicate text variations are exploratory; semantic equivalence is not deterministically bound to OOD distance."
                )
            elif ptype == PerturbationType.P8_DELETION:
                return (
                    DetectionStatus.NOT_APPLICABLE,
                    False,
                    "DESCRIPTIVE_ONLY_NO_CONSEQUENCE",
                    "Arbitrary clause deletion without a surviving reference dependency lacks a universal completeness detector."
                )

        # Case 3: Structural Perturbations (P1 Displacement, P2 Swap)
        if ptype in (PerturbationType.P1_DISPLACEMENT, PerturbationType.P2_SWAP):
            # Evaluate Channel B discourse transition anomaly response
            if max_affected_b_delta >= self.structural_anomaly_threshold or delta_anomalies > 0:
                return DetectionStatus.DETECTED, True, None, None
            else:
                return (
                    DetectionStatus.NOT_DETECTED,
                    False,
                    "WEAK_TRANSITION_SCORE_RESPONSE",
                    f"Channel B score delta ({max_affected_b_delta:.4f}) fell below exploratory delta cutoff ({self.structural_anomaly_threshold}); production severity tier remained CLEAN (score < 0.35)."
                )

        # Case 4: Cross-Reference Rules (P5 Broken Ref, P6 Missing Exhibit, P8 Deletion with surviving ref)
        if ptype in (PerturbationType.P5_BROKEN_REFERENCE, PerturbationType.P6_MISSING_EXHIBIT) or (
            ptype == PerturbationType.P8_DELETION and oracle_res.eligible_for_strict_evaluation
        ):
            # Look for relevant reference flag
            ref_flags = [f for f in new_flags if "REFERENCE" in f.get("flag_type", "")]
            if ref_flags:
                # Check attribution: does involved_clause_ids or clause_id intersect with target
                matched = any(
                    f.get("clause_id") in oracle_res.affected_clause_ids or
                    any(cid in oracle_res.affected_clause_ids for cid in f.get("involved_clause_ids", []))
                    for f in ref_flags
                )
                if matched:
                    return DetectionStatus.DETECTED, True, None, None
                else:
                    return DetectionStatus.DETECTED, False, "ATTRIBUTION_MISMATCH", "Reference flag produced but attributed to non-target clause."
            else:
                return (
                    DetectionStatus.NOT_DETECTED,
                    False,
                    "UNSUPPORTED_RULE_GRAMMAR",
                    "CrossReferenceChecker did not recognize the perturbed citation syntax."
                )

        # Case 5: Date Logic Rule (P7 Date Inversion)
        if ptype == PerturbationType.P7_DATE_INVERSION:
            date_flags = [f for f in new_flags if any(k in f.get("flag_type", "") for k in ["DATE", "TERM", "TIMELINE", "PAYMENT"])]
            if date_flags:
                matched = any(
                    f.get("clause_id") in oracle_res.affected_clause_ids or
                    any(cid in oracle_res.affected_clause_ids for cid in f.get("involved_clause_ids", []))
                    for f in date_flags
                )
                if matched:
                    return DetectionStatus.DETECTED, True, None, None
                else:
                    return DetectionStatus.DETECTED, False, "ATTRIBUTION_MISMATCH", "Date contradiction flagged on non-target clause."
            else:
                return (
                    DetectionStatus.NOT_DETECTED,
                    False,
                    "DATE_EXTRACTION_FAILURE",
                    "DateLogicChecker failed to parse the temporal role or calculate chronological succession."
                )

        # Case 6: Combined Perturbations (P10)
        if ptype == PerturbationType.P10_COMBINED:
            has_rule = len(new_flags) > 0
            has_structural = (max_affected_b_delta >= self.structural_anomaly_threshold or delta_anomalies > 0)
            if has_rule and has_structural:
                return DetectionStatus.DETECTED, True, None, "Both rule violation and structural discourse anomaly detected."
            elif has_rule or has_structural:
                return DetectionStatus.DETECTED, True, None, "Partial detection: one of the compound disturbances was flagged."
            else:
                return (
                    DetectionStatus.NOT_DETECTED,
                    False,
                    "COMPOUND_DETECTION_FAILURE",
                    "Neither structural discourse model nor rule checkers registered the combined disturbances."
                )

        return DetectionStatus.INCONCLUSIVE, False, "INCONCLUSIVE", "Unable to establish definitive detection outcome."
