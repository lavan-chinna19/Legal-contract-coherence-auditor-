"""
tests/test_independent_benchmark.py
Unit and Regression Tests for Phase 4D-C Independent Contract Benchmark.
"""
import pytest
import os
import hashlib
from typing import List

from src.config import ClauseRecord
from src.research.independent_benchmark.schema import (
    SourceDocumentRecord,
    SplitPartition,
    GroundTruthLabel,
    TaskCategory,
    BenchmarkCase
)
from src.research.independent_benchmark.provenance import (
    compute_normalized_text,
    compute_sha256,
    compute_content_fingerprint,
    load_edgar_source_corpus
)
from src.research.independent_benchmark.deduplication import (
    calculate_jaccard_similarity,
    run_corpus_deduplication_audit
)
from src.research.independent_benchmark.splitter import (
    partition_source_families,
    verify_split_disjointness
)
from src.research.independent_benchmark.oracle import (
    IndependentGroundTruthOracle,
    BACKWARD_DISCOURSE_PATTERNS
)
from src.research.independent_benchmark.perturbations import (
    make_clause_copy,
    reindex_clauses,
    BenchmarkPerturbationEngine
)
from src.research.independent_benchmark.statistics import (
    compute_wilson_score_interval,
    compute_family_grouped_bootstrap_ci
)
from src.research.independent_benchmark.metrics import calculate_detection_metrics


# -----------------------------------------------------------------------------
# Fixtures
# -----------------------------------------------------------------------------

@pytest.fixture
def sample_clauses() -> List[ClauseRecord]:
    return [
        ClauseRecord(clause_id="doc1_0", doc_id="doc1", text="This Agreement is made between Party A and Party B.", label="Preamble", sequence_idx=0, char_start=0, char_end=51, source="sec_edgar"),
        ClauseRecord(clause_id="doc1_1", doc_id="doc1", text="Section 1. Services. Party A shall provide software engineering services.", label="Services", sequence_idx=1, char_start=52, char_end=125, source="sec_edgar"),
        ClauseRecord(clause_id="doc1_2", doc_id="doc1", text="Section 2. Fees. The fees for the services shall be $100 per hour.", label="Payment", sequence_idx=2, char_start=126, char_end=192, source="sec_edgar"),
        ClauseRecord(clause_id="doc1_3", doc_id="doc1", text="The preceding provision shall not apply to emergency services.", label="Exceptions", sequence_idx=3, char_start=193, char_end=255, source="sec_edgar"),
        ClauseRecord(clause_id="doc1_4", doc_id="doc1", text="Section 3. Governing Law. This Agreement is governed by Delaware law.", label="Governing Law", sequence_idx=4, char_start=256, char_end=324, source="sec_edgar"),
        ClauseRecord(clause_id="doc1_5", doc_id="doc1", text="Section 4. Notices. All notices must be in writing sent to legal address.", label="Notices", sequence_idx=5, char_start=325, char_end=397, source="sec_edgar"),
        ClauseRecord(clause_id="doc1_6", doc_id="doc1", text="Section 5. Arbitration. Any dispute shall be settled by binding arbitration in New York.", label="Arbitration", sequence_idx=6, char_start=398, char_end=486, source="sec_edgar"),
    ]


@pytest.fixture
def mock_source_docs() -> List[SourceDocumentRecord]:
    docs = []
    # 6 documents across 3 distinct CIK families
    ciks = ["100001", "100002", "100003"]
    for i, cik in enumerate(ciks):
        for ex in ["EX-10.1", "EX-10.2"]:
            doc_id = f"SEC_CIK{cik}_{ex}"
            fam_id = f"FAM_CIK_{cik}"
            text = f"Agreement for CIK {cik} exhibit {ex}. Some text for contract body."
            docs.append(SourceDocumentRecord(
                parent_document_id=doc_id,
                document_family_id=fam_id,
                source_uri_or_reference=f"https://sec.gov/{doc_id}",
                source_type="SEC_EDGAR_EXHIBIT_10",
                contract_type="Commercial Agreement",
                source_organization=f"Company {cik}",
                acquisition_date="2023-12-31",
                license_status="PUBLIC_DOMAIN",
                raw_sha256=compute_sha256(text),
                normalized_text_sha256=compute_sha256(compute_normalized_text(text)),
                content_fingerprint=compute_content_fingerprint(text),
                parser_version="1.0",
                clause_segmentation_version="1.0",
                split_assignment="UNASSIGNED",
                provenance_confidence="HIGH",
                clause_count=10,
                char_length=len(text)
            ))
    return docs


# -----------------------------------------------------------------------------
# Test 1: Provenance & Fingerprinting
# -----------------------------------------------------------------------------

def test_provenance_hashing_and_fingerprinting():
    text1 = "This is a contract with   spaces\nand tabs."
    text2 = "this is a contract with spaces and tabs."
    assert compute_normalized_text(text1) == compute_normalized_text(text2)
    assert compute_sha256(compute_normalized_text(text1)) == compute_sha256(compute_normalized_text(text2))

    fp1 = compute_content_fingerprint(text1)
    fp2 = compute_content_fingerprint(text2)
    assert fp1 == fp2
    assert len(fp1) == 16


# -----------------------------------------------------------------------------
# Test 2: Deduplication & Near-Duplicate Logic
# -----------------------------------------------------------------------------

def test_jaccard_similarity_calculation():
    s1 = "This agreement is governed by the laws of the State of Delaware."
    s2 = "This agreement is governed by the laws of the State of New York."
    jaccard = calculate_jaccard_similarity(s1, s2, shingle_size=2)
    assert 0.4 <= jaccard <= 0.95

    # Completely disjoint strings
    s3 = "Apple banana orange pear."
    assert calculate_jaccard_similarity(s1, s3) == 0.0


# -----------------------------------------------------------------------------
# Test 3: Source-Family Split Isolation (Zero Leakage)
# -----------------------------------------------------------------------------

def test_source_family_split_disjointness(mock_source_docs):
    updated_docs, split_records = partition_source_families(mock_source_docs, dev_ratio=0.34, val_ratio=0.33, test_ratio=0.33)

    dev_docs = [d for d in updated_docs if d.split_assignment == SplitPartition.DEVELOPMENT.value]
    val_docs = [d for d in updated_docs if d.split_assignment == SplitPartition.VALIDATION.value]
    test_docs = [d for d in updated_docs if d.split_assignment == SplitPartition.SEALED_TEST.value]

    integrity = verify_split_disjointness(dev_docs, val_docs, test_docs)
    assert integrity["is_disjoint"] is True
    assert len(integrity["dev_val_family_overlap"]) == 0
    assert len(integrity["dev_test_family_overlap"]) == 0
    assert len(integrity["val_test_family_overlap"]) == 0
    assert len(integrity["parent_overlap"]) == 0

    # Every child document of the same family has the exact same split
    fams = {}
    for d in updated_docs:
        if d.document_family_id not in fams:
            fams[d.document_family_id] = d.split_assignment
        else:
            assert fams[d.document_family_id] == d.split_assignment


# -----------------------------------------------------------------------------
# Test 4: Independent Ground-Truth Oracle Behavior
# -----------------------------------------------------------------------------

def test_oracle_discourse_inversion_positive(sample_clauses):
    orig = sample_clauses
    # Clause 3 has "The preceding provision"
    assert IndependentGroundTruthOracle.inspect_discourse_dependency(orig[3].text) != []

    # Invert clause 3 and clause 2
    perturbed = list(orig)
    perturbed[2], perturbed[3] = perturbed[3], perturbed[2]

    ann = IndependentGroundTruthOracle.evaluate_transformation(
        original_clauses=orig,
        perturbed_clauses=perturbed,
        transformation_type="P1_DISCOURSE_DEPENDENCY_INVERSION",
        displaced_idx=3,
        target_idx=2,
        case_id="case_p1",
        parent_id="doc1",
        family_id="fam1",
        split="test",
        source_hash="hash1",
        perturbed_hash="hash2"
    )

    assert ann.ground_truth_label == GroundTruthLabel.VERIFIED_DISCOURSE_DEPENDENCY_VIOLATION
    assert ann.eligibility_decision == "ELIGIBLE"
    assert "The preceding provision" in ann.supporting_source_spans[0]


def test_oracle_commutative_covenant_swap_negative(sample_clauses):
    orig = sample_clauses
    # Swap Governing Law (idx 4) and Notices (idx 5)
    perturbed = list(orig)
    perturbed[4], perturbed[5] = perturbed[5], perturbed[4]

    ann = IndependentGroundTruthOracle.evaluate_transformation(
        original_clauses=orig,
        perturbed_clauses=perturbed,
        transformation_type="N2_INDEPENDENT_COVENANT_SWAP",
        displaced_idx=4,
        target_idx=5,
        case_id="case_n2",
        parent_id="doc1",
        family_id="fam1",
        split="test",
        source_hash="hash1",
        perturbed_hash="hash2"
    )

    assert ann.ground_truth_label == GroundTruthLabel.VALID_NONCANONICAL_ORDER
    assert ann.eligibility_decision == "ELIGIBLE"


def test_oracle_hard_negative_dispute_notice(sample_clauses):
    orig = sample_clauses
    # Front-load Arbitration (idx 6) to index 1
    ann = IndependentGroundTruthOracle.evaluate_transformation(
        original_clauses=orig,
        perturbed_clauses=orig,
        transformation_type="N3_FRONTLOADED_DISPUTE_NOTICE",
        displaced_idx=6,
        target_idx=1,
        case_id="case_n3",
        parent_id="doc1",
        family_id="fam1",
        split="test",
        source_hash="hash1",
        perturbed_hash="hash2"
    )

    assert ann.ground_truth_label == GroundTruthLabel.VALID_NONCANONICAL_ORDER
    assert ann.eligibility_decision == "ELIGIBLE"


# -----------------------------------------------------------------------------
# Test 5: Perturbation Copy-on-Write and Invariants
# -----------------------------------------------------------------------------

def test_perturbation_copy_on_write(sample_clauses):
    orig = sample_clauses
    reindexed = reindex_clauses(orig)
    assert len(reindexed) == len(orig)
    # Modify reindexed clause text should not mutate orig
    reindexed[0].text = "MODIFIED TEXT"
    assert orig[0].text != "MODIFIED TEXT"


# -----------------------------------------------------------------------------
# Test 6: Wilson Confidence Interval Calculations
# -----------------------------------------------------------------------------

def test_wilson_confidence_intervals():
    # Test 0/5 recall
    ci_0_5 = compute_wilson_score_interval(0, 5, confidence_level=0.95)
    assert ci_0_5.point_estimate == 0.0
    assert ci_0_5.lower_bound == 0.0
    assert 0.40 <= ci_0_5.upper_bound <= 0.45  # Approx ~0.4345

    # Test 0/6 recall
    ci_0_6 = compute_wilson_score_interval(0, 6, confidence_level=0.95)
    assert ci_0_6.point_estimate == 0.0
    assert ci_0_6.lower_bound == 0.0
    assert 0.35 <= ci_0_6.upper_bound <= 0.40  # Approx ~0.3903

    # Test 2/2 recall
    ci_2_2 = compute_wilson_score_interval(2, 2, confidence_level=0.95)
    assert ci_2_2.point_estimate == 1.0
    assert 0.30 <= ci_2_2.lower_bound <= 0.40
    assert ci_2_2.upper_bound == 1.0


# -----------------------------------------------------------------------------
# Test 7: Metric Consistency and Denominator Preservation
# -----------------------------------------------------------------------------

def test_metric_calculation_consistency():
    from src.research.independent_benchmark.schema import EvaluationPrediction, LatencyBreakdown
    preds = [
        EvaluationPrediction("c1", "M", "1.0", GroundTruthLabel.VERIFIED_DISCOURSE_DEPENDENCY_VIOLATION, True, True, 0.9, 0.5, ["c1"], LatencyBreakdown(), "F1", "test", "TASK_A"),
        EvaluationPrediction("c2", "M", "1.0", GroundTruthLabel.VERIFIED_DISCOURSE_DEPENDENCY_VIOLATION, True, False, 0.2, 0.5, [], LatencyBreakdown(), "F1", "test", "TASK_A"),
        EvaluationPrediction("c3", "M", "1.0", GroundTruthLabel.VALID_CANONICAL_ORDER, False, False, 0.1, 0.5, [], LatencyBreakdown(), "F2", "test", "TASK_A"),
        EvaluationPrediction("c4", "M", "1.0", GroundTruthLabel.VALID_NONCANONICAL_ORDER, False, True, 0.8, 0.5, ["c4"], LatencyBreakdown(), "F2", "test", "TASK_A"),
    ]

    bundle = calculate_detection_metrics(preds)
    assert bundle.total_cases == 4
    assert bundle.tp == 1
    assert bundle.fn == 1
    assert bundle.tn == 1
    assert bundle.fp == 1
    assert bundle.recall == 0.5
    assert bundle.precision == 0.5
    assert bundle.specificity == 0.5
    assert bundle.f1 == 0.5
    assert bundle.balanced_accuracy == 0.5
    assert bundle.family_count == 2


# -----------------------------------------------------------------------------
# Test 8: Frozen Checkpoint Preservation
# -----------------------------------------------------------------------------

def test_frozen_model_hashes_unchanged():
    ckpt_path = "models/coherence_classifier.pt"
    centroids_path = "fixtures/ledgar_centroids.npz"
    assert os.path.exists(ckpt_path), f"Checkpoint missing: {ckpt_path}"
    assert os.path.exists(centroids_path), f"Centroids missing: {centroids_path}"
    # Verify file sizes are non-trivial
    assert os.path.getsize(ckpt_path) > 100_000
    assert os.path.getsize(centroids_path) > 10_000
