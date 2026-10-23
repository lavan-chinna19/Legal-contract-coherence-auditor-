"""
src/research/independent_benchmark/dataset_builder.py
Orchestrates Corpus Ingestion, Family Partitioning, Perturbation and Manifest Generation.
"""
import csv
import json
import os
from typing import List, Dict, Tuple, Any

from src.segmentation.rule_based import RuleBasedSegmenter
from src.research.independent_benchmark.schema import (
    SourceDocumentRecord,
    DuplicateAuditRecord,
    SplitAssignmentRecord,
    AnnotationRecord,
    PerturbationRecord,
    BenchmarkCase,
    SplitPartition
)
from src.research.independent_benchmark.provenance import load_edgar_source_corpus
from src.research.independent_benchmark.deduplication import run_corpus_deduplication_audit
from src.research.independent_benchmark.splitter import partition_source_families, verify_split_disjointness
from src.research.independent_benchmark.perturbations import BenchmarkPerturbationEngine


class BenchmarkDatasetBuilder:
    """
    Builds the complete Phase 4D-C Independent Legal Contract Coherence Benchmark.
    """

    def __init__(
        self,
        edgar_manifest_path: str = "data/raw/sec_edgar/edgar_manifest.json",
        min_clauses: int = 10,
        max_clauses: int = 125,
        target_output_dir: str = "research/independent_contract_benchmark_phase_04dc"
    ):
        self.manifest_path = edgar_manifest_path
        self.min_clauses = min_clauses
        self.max_clauses = max_clauses
        self.output_dir = target_output_dir
        self.segmenter = RuleBasedSegmenter()

    def build_benchmark(self) -> Dict[str, Any]:
        """
        Executes end-to-end benchmark construction:
        1. Ingests source contracts
        2. Deduplicates and audits families
        3. Assigns source-family splits strictly before perturbation
        4. Generates copy-on-write benchmark variants
        5. Performs oracle annotations
        6. Verifies zero leakage and manifest integrity
        """
        # Step 1: Ingest
        raw_docs = load_edgar_source_corpus(
            manifest_path=self.manifest_path,
            min_clauses=self.min_clauses,
            max_clauses=self.max_clauses
        )

        # Step 2: Deduplicate & Audit
        dup_records = run_corpus_deduplication_audit(raw_docs)

        # Step 3: Split source families BEFORE any transformations
        split_docs, split_records = partition_source_families(raw_docs)

        # Group docs by split
        dev_docs = [d for d in split_docs if d.split_assignment == SplitPartition.DEVELOPMENT.value]
        val_docs = [d for d in split_docs if d.split_assignment == SplitPartition.VALIDATION.value]
        test_docs = [d for d in split_docs if d.split_assignment == SplitPartition.SEALED_TEST.value]

        # Verify disjointness
        split_integrity = verify_split_disjointness(dev_docs, val_docs, test_docs)
        assert split_integrity["is_disjoint"], "Split disjointness check failed!"

        # Step 4: Generate perturbation cases strictly inside assigned split
        cases: List[BenchmarkCase] = []

        for doc in split_docs:
            with open(doc.file_path, "r", encoding="utf-8", errors="ignore") as f:
                raw_text = f.read()
            clauses = self.segmenter.segment(raw_text)

            # N1: Clean contract control
            c_n1 = BenchmarkPerturbationEngine.create_n1_clean_case(doc, clauses)
            cases.append(c_n1)

            # P1: Discourse dependency inversion
            c_p1 = BenchmarkPerturbationEngine.create_p1_discourse_inversion_case(doc, clauses)
            if c_p1 is not None:
                cases.append(c_p1)

            # P2: Long-range discourse displacement
            c_p2 = BenchmarkPerturbationEngine.create_p2_discourse_displacement_case(doc, clauses)
            if c_p2 is not None:
                cases.append(c_p2)

            # N2: Commutative independent covenant swap
            c_n2 = BenchmarkPerturbationEngine.create_n2_covenant_swap_case(doc, clauses)
            if c_n2 is not None:
                cases.append(c_n2)

            # N3: Hard Negative — Front-loaded dispute resolution
            c_n3 = BenchmarkPerturbationEngine.create_n3_hard_negative_dispute_case(doc, clauses)
            if c_n3 is not None:
                cases.append(c_n3)

            # N4: Hard Negative — Front-loaded definitions
            c_n4 = BenchmarkPerturbationEngine.create_n4_hard_negative_definitions_case(doc, clauses)
            if c_n4 is not None:
                cases.append(c_n4)

            # A1: Ambiguous non-canonical order
            c_a1 = BenchmarkPerturbationEngine.create_a1_ambiguous_case(doc, clauses)
            if c_a1 is not None:
                cases.append(c_a1)

        # Automated Assertion: Zero cross-split family leakage for all generated cases
        dev_cases = [c for c in cases if c.perturbation.split == SplitPartition.DEVELOPMENT.value]
        val_cases = [c for c in cases if c.perturbation.split == SplitPartition.VALIDATION.value]
        test_cases = [c for c in cases if c.perturbation.split == SplitPartition.SEALED_TEST.value]

        dev_case_fams = set(c.perturbation.document_family_id for c in dev_cases)
        val_case_fams = set(c.perturbation.document_family_id for c in val_cases)
        test_case_fams = set(c.perturbation.document_family_id for c in test_cases)

        assert len(dev_case_fams & val_case_fams) == 0, "Case leakage between Dev and Val!"
        assert len(dev_case_fams & test_case_fams) == 0, "Case leakage between Dev and Test!"
        assert len(val_case_fams & test_case_fams) == 0, "Case leakage between Val and Test!"

        return {
            "source_documents": split_docs,
            "duplicate_audit_records": dup_records,
            "split_records": split_records,
            "split_integrity": split_integrity,
            "benchmark_cases": cases,
            "dev_cases": dev_cases,
            "val_cases": val_cases,
            "test_cases": test_cases
        }

    def export_manifests(self, benchmark_data: Dict[str, Any]) -> None:
        """Export all benchmark CSV manifests to output directory."""
        os.makedirs(self.output_dir, exist_ok=True)

        # 1. parent_contract_manifest.csv
        p_path = os.path.join(self.output_dir, "parent_contract_manifest.csv")
        with open(p_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "parent_document_id", "document_family_id", "source_uri_or_reference",
                "source_type", "contract_type", "source_organization", "acquisition_date",
                "license_status", "raw_sha256", "normalized_text_sha256", "content_fingerprint",
                "parser_version", "clause_segmentation_version", "split_assignment",
                "provenance_confidence", "clause_count", "char_length"
            ])
            for d in benchmark_data["source_documents"]:
                writer.writerow([
                    d.parent_document_id, d.document_family_id, d.source_uri_or_reference,
                    d.source_type, d.contract_type, d.source_organization, d.acquisition_date,
                    d.license_status, d.raw_sha256, d.normalized_text_sha256, d.content_fingerprint,
                    d.parser_version, d.clause_segmentation_version, d.split_assignment,
                    d.provenance_confidence, d.clause_count, d.char_length
                ])

        # 2. source_family_clusters.csv
        c_path = os.path.join(self.output_dir, "source_family_clusters.csv")
        with open(c_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["document_family_id", "source_organization", "parent_contract_count", "split_assignment", "parent_contract_ids"])
            for r in benchmark_data["split_records"]:
                writer.writerow([
                    r.document_family_id, r.source_organization, r.parent_contract_count,
                    r.split_assignment.value, ";".join(r.parent_document_ids)
                ])

        # 3. duplicate_and_near_duplicate_audit.csv
        d_path = os.path.join(self.output_dir, "duplicate_and_near_duplicate_audit.csv")
        with open(d_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "doc_id_a", "doc_id_b", "family_id_a", "family_id_b",
                "is_exact_byte_duplicate", "is_normalized_duplicate",
                "jaccard_similarity", "audit_verdict", "notes"
            ])
            for dup in benchmark_data["duplicate_audit_records"]:
                writer.writerow([
                    dup.doc_id_a, dup.doc_id_b, dup.family_id_a, dup.family_id_b,
                    dup.is_exact_byte_duplicate, dup.is_normalized_duplicate,
                    dup.jaccard_similarity, dup.audit_verdict, dup.notes
                ])

        # 4. source_family_split_manifest.csv
        s_path = os.path.join(self.output_dir, "source_family_split_manifest.csv")
        with open(s_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["document_family_id", "source_organization", "split_partition", "parent_count", "parent_ids"])
            for r in benchmark_data["split_records"]:
                writer.writerow([
                    r.document_family_id, r.source_organization, r.split_assignment.value,
                    r.parent_contract_count, ";".join(r.parent_document_ids)
                ])

        # 5. annotation_records.csv
        a_path = os.path.join(self.output_dir, "annotation_records.csv")
        with open(a_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "case_id", "parent_document_id", "document_family_id", "split",
                "original_source_identity", "source_text_hash", "perturbed_text_hash",
                "ground_truth_label", "task_category", "transformation_type",
                "affected_clause_ids", "supporting_source_spans", "exact_reason_for_label",
                "independently_checkable_condition", "labeling_method", "label_author",
                "label_confidence", "reviewer_disagreement_status", "eligible_benchmark_task",
                "eligibility_decision", "exclusion_reason"
            ])
            for case in benchmark_data["benchmark_cases"]:
                an = case.annotation
                writer.writerow([
                    an.case_id, an.parent_document_id, an.document_family_id, an.split,
                    an.original_source_identity, an.source_text_hash, an.perturbed_text_hash,
                    an.ground_truth_label.value, an.task_category.value, an.transformation_type,
                    ";".join(an.affected_clause_ids), ";".join(an.supporting_source_spans),
                    an.exact_reason_for_label, an.independently_checkable_condition,
                    an.labeling_method, an.label_author, an.label_confidence,
                    an.reviewer_disagreement_status, an.eligible_benchmark_task,
                    an.eligibility_decision, an.exclusion_reason or ""
                ])

        # 6. perturbation_catalog.csv
        pc_path = os.path.join(self.output_dir, "perturbation_catalog.csv")
        with open(pc_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "case_id", "parent_document_id", "document_family_id", "split",
                "category_code", "transformation_name", "is_positive", "is_hard_negative",
                "is_ambiguous", "source_clause_count", "perturbed_clause_count",
                "displaced_clause_indices", "target_clause_indices", "transformation_valid",
                "deterministic_seed", "description"
            ])
            for case in benchmark_data["benchmark_cases"]:
                p = case.perturbation
                writer.writerow([
                    p.case_id, p.parent_document_id, p.document_family_id, p.split,
                    p.category_code, p.transformation_name, p.is_positive, p.is_hard_negative,
                    p.is_ambiguous, p.source_clause_count, p.perturbed_clause_count,
                    ";".join(map(str, p.displaced_clause_indices)),
                    ";".join(map(str, p.target_clause_indices)),
                    p.transformation_valid, p.deterministic_seed, p.description
                ])

        # 7. positive_case_validity.csv
        pos_path = os.path.join(self.output_dir, "positive_case_validity.csv")
        with open(pos_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "case_id", "parent_document_id", "family_id", "split", "category",
                "ground_truth_label", "task", "supporting_discourse_spans", "checkable_condition", "eligibility"
            ])
            for c in benchmark_data["benchmark_cases"]:
                if c.perturbation.is_positive:
                    writer.writerow([
                        c.annotation.case_id, c.annotation.parent_document_id,
                        c.annotation.document_family_id, c.annotation.split,
                        c.perturbation.category_code, c.annotation.ground_truth_label.value,
                        c.annotation.task_category.value, ";".join(c.annotation.supporting_source_spans),
                        c.annotation.independently_checkable_condition, c.annotation.eligibility_decision
                    ])

        # 8. negative_case_validity.csv
        neg_path = os.path.join(self.output_dir, "negative_case_validity.csv")
        with open(neg_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "case_id", "parent_document_id", "family_id", "split", "category",
                "is_hard_negative", "ground_truth_label", "task", "exact_reason", "eligibility"
            ])
            for c in benchmark_data["benchmark_cases"]:
                if not c.perturbation.is_positive and not c.perturbation.is_ambiguous:
                    writer.writerow([
                        c.annotation.case_id, c.annotation.parent_document_id,
                        c.annotation.document_family_id, c.annotation.split,
                        c.perturbation.category_code, c.perturbation.is_hard_negative,
                        c.annotation.ground_truth_label.value, c.annotation.task_category.value,
                        c.annotation.exact_reason_for_label, c.annotation.eligibility_decision
                    ])

        # 9. ambiguous_case_register.csv
        amb_path = os.path.join(self.output_dir, "ambiguous_case_register.csv")
        with open(amb_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "case_id", "parent_document_id", "family_id", "split", "category",
                "ground_truth_label", "task", "exact_reason", "exclusion_reason", "eligibility"
            ])
            for c in benchmark_data["benchmark_cases"]:
                if c.perturbation.is_ambiguous or c.annotation.eligibility_decision == "EXCLUDED":
                    writer.writerow([
                        c.annotation.case_id, c.annotation.parent_document_id,
                        c.annotation.document_family_id, c.annotation.split,
                        c.perturbation.category_code, c.annotation.ground_truth_label.value,
                        c.annotation.task_category.value, c.annotation.exact_reason_for_label,
                        c.annotation.exclusion_reason or "Ambiguous interpretation",
                        c.annotation.eligibility_decision
                    ])

        # 10. hard_negative_catalog.csv
        hn_path = os.path.join(self.output_dir, "hard_negative_catalog.csv")
        with open(hn_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "case_id", "parent_document_id", "family_id", "split", "category",
                "transformation_name", "target_index", "ground_truth_label", "why_valid_commercial_practice"
            ])
            for c in benchmark_data["benchmark_cases"]:
                if c.perturbation.is_hard_negative:
                    writer.writerow([
                        c.annotation.case_id, c.annotation.parent_document_id,
                        c.annotation.document_family_id, c.annotation.split,
                        c.perturbation.category_code, c.perturbation.transformation_name,
                        ";".join(map(str, c.perturbation.target_clause_indices)),
                        c.annotation.ground_truth_label.value,
                        c.annotation.exact_reason_for_label
                    ])
