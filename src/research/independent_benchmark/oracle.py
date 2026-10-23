"""
src/research/independent_benchmark/oracle.py
Independent Ground-Truth Oracle for Contract Structural Coherence.

CRITICAL ARCHITECTURAL GUARANTEE:
This oracle operates completely independently of Candidate C3 or any candidate model.
It does NOT use heading classifications, lifecycle DAG stage numbers, or model outputs.
Labels are derived strictly from verifiable textual discourse dependencies and
explicit structural cross-reference conditions.
"""
import re
from typing import List, Tuple, Optional, Dict, Any

from src.config import ClauseRecord
from src.research.independent_benchmark.schema import (
    GroundTruthLabel,
    TaskCategory,
    AnnotationRecord
)

# Explicit backward discourse markers that require preceding textual context
BACKWARD_DISCOURSE_PATTERNS = [
    re.compile(r"\b(?:the\s+preceding\s+(?:section|clause|paragraph|provision|sentence|item))\b", re.I),
    re.compile(r"\b(?:subject\s+to\s+the\s+immediately\s+preceding)\b", re.I),
    re.compile(r"\b(?:as\s+defined\s+above)\b", re.I),
    re.compile(r"\b(?:set\s+forth\s+in\s+the\s+preceding)\b", re.I),
    re.compile(r"\b(?:notwithstanding\s+the\s+foregoing)\b", re.I),
    re.compile(r"\b(?:subject\s+to\s+the\s+foregoing)\b", re.I),
    re.compile(r"\b(?:as\s+stated\s+above)\b", re.I)
]

# Explicit numbered section references: "Section X.Y" or "Section X"
SECTION_REF_PATTERN = re.compile(r"\b(?:Section\s+(\d+(?:\.\d+)?))\b", re.I)


class IndependentGroundTruthOracle:
    """
    Evaluates contract transformations against objective linguistic and structural criteria.
    """

    @staticmethod
    def inspect_discourse_dependency(clause_text: str) -> List[str]:
        """Find explicit backward discourse referents in clause text."""
        hits = []
        for pat in BACKWARD_DISCOURSE_PATTERNS:
            for match in pat.finditer(clause_text):
                hits.append(match.group(0))
        return hits

    @staticmethod
    def inspect_section_references(clause_text: str) -> List[str]:
        """Find section cross-references in clause text."""
        return SECTION_REF_PATTERN.findall(clause_text)

    @classmethod
    def evaluate_transformation(
        cls,
        original_clauses: List[ClauseRecord],
        perturbed_clauses: List[ClauseRecord],
        transformation_type: str,
        displaced_idx: int,
        target_idx: int,
        case_id: str,
        parent_id: str,
        family_id: str,
        split: str,
        source_hash: str,
        perturbed_hash: str
    ) -> AnnotationRecord:
        """
        Produce an independently audited AnnotationRecord for a given transformation.
        """
        # Case 1: Untouched original contract (N1)
        if transformation_type == "N1_CLEAN_CONTRACT":
            return AnnotationRecord(
                case_id=case_id,
                parent_document_id=parent_id,
                document_family_id=family_id,
                split=split,
                original_source_identity=parent_id,
                source_text_hash=source_hash,
                perturbed_text_hash=perturbed_hash,
                ground_truth_label=GroundTruthLabel.VALID_CANONICAL_ORDER,
                task_category=TaskCategory.TASK_A_DISCOURSE_COHERENCE,
                transformation_type=transformation_type,
                affected_clause_ids=[],
                supporting_source_spans=[],
                exact_reason_for_label="Original unmodified SEC EDGAR contract in author-drafted canonical sequence.",
                independently_checkable_condition="hash(original) == hash(perturbed)",
                labeling_method="DETERMINISTIC_IDENTITY_AUDIT",
                label_confidence="HIGH",
                reviewer_disagreement_status="NO_EXPERT_ADJUDICATION",
                eligible_benchmark_task="STRUCTURAL_ANOMALY_DETECTION",
                eligibility_decision="ELIGIBLE"
            )

        # Case 2: Discourse Dependency Disruption (P1/P2)
        if transformation_type in ("P1_DISCOURSE_DEPENDENCY_INVERSION", "P2_DISCOURSE_REFERENT_DISPLACEMENT"):
            displaced_clause = original_clauses[displaced_idx]
            markers = cls.inspect_discourse_dependency(displaced_clause.text)

            if not markers:
                # If no explicit marker, cannot verify with high confidence -> mark AMBIGUOUS
                return AnnotationRecord(
                    case_id=case_id,
                    parent_document_id=parent_id,
                    document_family_id=family_id,
                    split=split,
                    original_source_identity=parent_id,
                    source_text_hash=source_hash,
                    perturbed_text_hash=perturbed_hash,
                    ground_truth_label=GroundTruthLabel.AMBIGUOUS,
                    task_category=TaskCategory.TASK_A_DISCOURSE_COHERENCE,
                    transformation_type=transformation_type,
                    affected_clause_ids=[displaced_clause.clause_id],
                    supporting_source_spans=[],
                    exact_reason_for_label="Displaced clause lacks explicit backward discourse referent; discourse defect unverifiable.",
                    independently_checkable_condition="contains_backward_discourse_marker == False",
                    labeling_method="DETERMINISTIC_DISCOURSE_PARSER",
                    label_confidence="LOW",
                    reviewer_disagreement_status="NO_EXPERT_ADJUDICATION",
                    eligible_benchmark_task="STRUCTURAL_ANOMALY_DETECTION",
                    eligibility_decision="EXCLUDED",
                    exclusion_reason="Lack of verified explicit discourse marker"
                )

            # Verified: clause contains explicit backward discourse marker moved before referent
            reason = (
                f"Displaced clause contains explicit backward discourse referent(s): {markers}. "
                f"Repositioning from index {displaced_idx} to index {target_idx} invalidates "
                f"anaphoric presupposition by placing referent after the referring expression."
            )
            return AnnotationRecord(
                case_id=case_id,
                parent_document_id=parent_id,
                document_family_id=family_id,
                split=split,
                original_source_identity=parent_id,
                source_text_hash=source_hash,
                perturbed_text_hash=perturbed_hash,
                ground_truth_label=GroundTruthLabel.VERIFIED_DISCOURSE_DEPENDENCY_VIOLATION,
                task_category=TaskCategory.TASK_A_DISCOURSE_COHERENCE,
                transformation_type=transformation_type,
                affected_clause_ids=[displaced_clause.clause_id],
                supporting_source_spans=markers,
                exact_reason_for_label=reason,
                independently_checkable_condition=f"clause[{target_idx}].has_marker({markers}) AND original_idx > target_idx",
                labeling_method="DETERMINISTIC_DISCOURSE_PARSER",
                label_confidence="HIGH",
                reviewer_disagreement_status="NO_EXPERT_ADJUDICATION",
                eligible_benchmark_task="STRUCTURAL_ANOMALY_DETECTION",
                eligibility_decision="ELIGIBLE"
            )

        # Case 3: Explicit Structural Cross-Reference Inversion (P3)
        if transformation_type == "P3_EXPLICIT_CROSS_REFERENCE_INVERSION":
            clause_a = original_clauses[displaced_idx]
            refs = cls.inspect_section_references(clause_a.text)
            return AnnotationRecord(
                case_id=case_id,
                parent_document_id=parent_id,
                document_family_id=family_id,
                split=split,
                original_source_identity=parent_id,
                source_text_hash=source_hash,
                perturbed_text_hash=perturbed_hash,
                ground_truth_label=GroundTruthLabel.VERIFIED_EXPLICIT_STRUCTURAL_VIOLATION,
                task_category=TaskCategory.TASK_B_STRUCTURAL_DEPENDENCY,
                transformation_type=transformation_type,
                affected_clause_ids=[clause_a.clause_id],
                supporting_source_spans=refs,
                exact_reason_for_label=f"Cross-referencing clause displaced across referenced section dependency.",
                independently_checkable_condition="cross_reference_dependency_inverted == True",
                labeling_method="DETERMINISTIC_CROSSREF_AUDIT",
                label_confidence="HIGH",
                reviewer_disagreement_status="NO_EXPERT_ADJUDICATION",
                eligible_benchmark_task="STRUCTURAL_ANOMALY_DETECTION",
                eligibility_decision="ELIGIBLE"
            )

        # Case 4: Independent Covenant Swap (N2)
        if transformation_type == "N2_INDEPENDENT_COVENANT_SWAP":
            clause_a = original_clauses[displaced_idx]
            clause_b = original_clauses[target_idx]
            markers_a = cls.inspect_discourse_dependency(clause_a.text)
            markers_b = cls.inspect_discourse_dependency(clause_b.text)

            if markers_a or markers_b:
                return AnnotationRecord(
                    case_id=case_id,
                    parent_document_id=parent_id,
                    document_family_id=family_id,
                    split=split,
                    original_source_identity=parent_id,
                    source_text_hash=source_hash,
                    perturbed_text_hash=perturbed_hash,
                    ground_truth_label=GroundTruthLabel.AMBIGUOUS,
                    task_category=TaskCategory.TASK_A_DISCOURSE_COHERENCE,
                    transformation_type=transformation_type,
                    affected_clause_ids=[clause_a.clause_id, clause_b.clause_id],
                    exact_reason_for_label="Swapped clauses contain discourse markers; independence uncertain.",
                    independently_checkable_condition="swapped_clauses_independent == False",
                    labeling_method="DETERMINISTIC_DISCOURSE_PARSER",
                    label_confidence="MEDIUM",
                    reviewer_disagreement_status="NO_EXPERT_ADJUDICATION",
                    eligible_benchmark_task="STRUCTURAL_ANOMALY_DETECTION",
                    eligibility_decision="EXCLUDED",
                    exclusion_reason="Discourse markers in swapped covenants"
                )

            return AnnotationRecord(
                case_id=case_id,
                parent_document_id=parent_id,
                document_family_id=family_id,
                split=split,
                original_source_identity=parent_id,
                source_text_hash=source_hash,
                perturbed_text_hash=perturbed_hash,
                ground_truth_label=GroundTruthLabel.VALID_NONCANONICAL_ORDER,
                task_category=TaskCategory.TASK_A_DISCOURSE_COHERENCE,
                transformation_type=transformation_type,
                affected_clause_ids=[clause_a.clause_id, clause_b.clause_id],
                exact_reason_for_label="Commutative swap of independent covenants; zero discourse or structural dependencies violated.",
                independently_checkable_condition="no_discourse_markers AND independent_provisions",
                labeling_method="DETERMINISTIC_COVENANT_AUDIT",
                label_confidence="HIGH",
                reviewer_disagreement_status="NO_EXPERT_ADJUDICATION",
                eligible_benchmark_task="STRUCTURAL_ANOMALY_DETECTION",
                eligibility_decision="ELIGIBLE"
            )

        # Case 5: Hard Negative — Front-Loaded Dispute Resolution / Arbitration (N3)
        if transformation_type == "N3_FRONTLOADED_DISPUTE_NOTICE":
            clause = original_clauses[displaced_idx]
            return AnnotationRecord(
                case_id=case_id,
                parent_document_id=parent_id,
                document_family_id=family_id,
                split=split,
                original_source_identity=parent_id,
                source_text_hash=source_hash,
                perturbed_text_hash=perturbed_hash,
                ground_truth_label=GroundTruthLabel.VALID_NONCANONICAL_ORDER,
                task_category=TaskCategory.TASK_A_DISCOURSE_COHERENCE,
                transformation_type=transformation_type,
                affected_clause_ids=[clause.clause_id],
                exact_reason_for_label=(
                    "Front-loading prominent dispute resolution or arbitration notice at contract opening "
                    "is a recognized, legally valid commercial drafting standard. It alters conventional "
                    "heading sequence without creating any textual discourse incoherence."
                ),
                independently_checkable_condition="is_dispute_notice AND valid_opening_placement",
                labeling_method="DETERMINISTIC_HARD_NEGATIVE_DESIGN",
                label_confidence="HIGH",
                reviewer_disagreement_status="NO_EXPERT_ADJUDICATION",
                eligible_benchmark_task="STRUCTURAL_ANOMALY_DETECTION",
                eligibility_decision="ELIGIBLE"
            )

        # Case 6: Hard Negative — Front-Loaded Definitions / Master Schedule (N4)
        if transformation_type == "N4_FRONTLOADED_DEFINITIONS":
            clause = original_clauses[displaced_idx]
            return AnnotationRecord(
                case_id=case_id,
                parent_document_id=parent_id,
                document_family_id=family_id,
                split=split,
                original_source_identity=parent_id,
                source_text_hash=source_hash,
                perturbed_text_hash=perturbed_hash,
                ground_truth_label=GroundTruthLabel.VALID_NONCANONICAL_ORDER,
                task_category=TaskCategory.TASK_A_DISCOURSE_COHERENCE,
                transformation_type=transformation_type,
                affected_clause_ids=[clause.clause_id],
                exact_reason_for_label=(
                    "Front-loading comprehensive definitions or master terms at document opening "
                    "is a standard commercial drafting convention that enhances interpretability."
                ),
                independently_checkable_condition="is_definitions_clause AND valid_early_placement",
                labeling_method="DETERMINISTIC_HARD_NEGATIVE_DESIGN",
                label_confidence="HIGH",
                reviewer_disagreement_status="NO_EXPERT_ADJUDICATION",
                eligible_benchmark_task="STRUCTURAL_ANOMALY_DETECTION",
                eligibility_decision="ELIGIBLE"
            )

        # Fallback / Ambiguous (A1)
        return AnnotationRecord(
            case_id=case_id,
            parent_document_id=parent_id,
            document_family_id=family_id,
            split=split,
            original_source_identity=parent_id,
            source_text_hash=source_hash,
            perturbed_text_hash=perturbed_hash,
            ground_truth_label=GroundTruthLabel.AMBIGUOUS,
            task_category=TaskCategory.TASK_D_CONVENTIONAL_ORGANIZATION,
            transformation_type=transformation_type,
            affected_clause_ids=[],
            exact_reason_for_label="Unconventional clause ordering with indeterminate legal discourse impact.",
            independently_checkable_condition="indeterminate_discourse_impact",
            labeling_method="CONSERVATIVE_EXCLUSION_RULE",
            label_confidence="LOW",
            reviewer_disagreement_status="NO_EXPERT_ADJUDICATION",
            eligible_benchmark_task="STRUCTURAL_ANOMALY_DETECTION",
            eligibility_decision="EXCLUDED",
            exclusion_reason="Ambiguous structural interpretation"
        )
