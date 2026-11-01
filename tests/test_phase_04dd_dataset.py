"""
tests/test_phase_04dd_dataset.py
Unit and validation test suite for Phase 4D-D Contract Dependency Benchmark.
Enforces empirical correctness, antecedent resolution, split immutability,
hard-negative validity, and oracle isolation.
"""
import os
import csv
import re
import pytest

OUTPUT_DIR = "research/dependency_ground_truth_phase_04dd"


@pytest.fixture(scope="module")
def dataset_manifest():
    path = os.path.join(OUTPUT_DIR, "dataset_manifest.csv")
    assert os.path.exists(path), f"Missing {path}"
    with open(path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


@pytest.fixture(scope="module")
def positive_cases():
    path = os.path.join(OUTPUT_DIR, "positive_cases.csv")
    assert os.path.exists(path), f"Missing {path}"
    with open(path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


@pytest.fixture(scope="module")
def negative_cases():
    path = os.path.join(OUTPUT_DIR, "negative_cases.csv")
    assert os.path.exists(path), f"Missing {path}"
    with open(path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


@pytest.fixture(scope="module")
def ambiguous_cases():
    path = os.path.join(OUTPUT_DIR, "ambiguous_cases.csv")
    assert os.path.exists(path), f"Missing {path}"
    with open(path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


@pytest.fixture(scope="module")
def candidates():
    path = os.path.join(OUTPUT_DIR, "dependency_candidates.csv")
    assert os.path.exists(path), f"Missing {path}"
    with open(path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


@pytest.fixture(scope="module")
def resolutions():
    path = os.path.join(OUTPUT_DIR, "antecedent_resolution.csv")
    assert os.path.exists(path), f"Missing {path}"
    with open(path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


@pytest.fixture(scope="module")
def source_families():
    path = os.path.join(OUTPUT_DIR, "source_family_manifest.csv")
    assert os.path.exists(path), f"Missing {path}"
    with open(path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


@pytest.fixture(scope="module")
def annotation_queue():
    path = os.path.join(OUTPUT_DIR, "annotation_queue.csv")
    assert os.path.exists(path), f"Missing {path}"
    with open(path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def test_dataset_manifest_integrity(dataset_manifest):
    """Test overall manifest volume, class balance, and cryptographic hash validity."""
    assert len(dataset_manifest) == 72, f"Expected 72 cases, got {len(dataset_manifest)}"

    pos = [r for r in dataset_manifest if r["case_type"] == "POSITIVE"]
    neg = [r for r in dataset_manifest if r["case_type"] == "HARD_NEGATIVE"]
    amb = [r for r in dataset_manifest if r["case_type"] == "AMBIGUOUS"]

    assert len(pos) == 30, f"Expected 30 positives, got {len(pos)}"
    assert len(neg) == 30, f"Expected 30 negatives, got {len(neg)}"
    assert len(amb) == 12, f"Expected 12 ambiguous, got {len(amb)}"

    for row in dataset_manifest:
        assert len(row["source_text_hash"]) == 64, "source_text_hash must be 64-char SHA-256"
        assert len(row["perturbed_text_hash"]) == 64, "perturbed_text_hash must be 64-char SHA-256"
        assert row["source_text_hash"] != row["perturbed_text_hash"], "Perturbation must alter text hash"


def test_split_immutability(dataset_manifest, source_families):
    """Enforce that 100% of benchmark records are assigned strictly to development."""
    for row in dataset_manifest:
        assert row["split_assignment"] == "development", (
            f"Case {row['case_id']} has forbidden split assignment: {row['split_assignment']}"
        )

    for fam in source_families:
        assert fam["split_eligibility"] == "DEVELOPMENT_ONLY", (
            f"Family {fam['document_family_id']} has forbidden eligibility: {fam['split_eligibility']}"
        )


def test_positive_case_ground_truth_validity(positive_cases, dataset_manifest):
    """Verify that all positive cases feature verified cross-clause sequence inversions."""
    assert len(positive_cases) == 30
    manifest_dict = {r["case_id"]: r for r in dataset_manifest}

    for pos in positive_cases:
        cid = pos["case_id"]
        meta = manifest_dict[cid]
        assert meta["ground_truth_label"] == "VERIFIED_POSITIVE"
        assert meta["transformation_type"] == "CROSS_CLAUSE_SECTION_INVERSION"
        assert int(meta["displaced_clause_idx"]) > int(meta["target_clause_idx"]), (
            f"Inversion failed for {cid}: displaced={meta['displaced_clause_idx']}, target={meta['target_clause_idx']}"
        )
        assert len(pos["referencing_text_span"]) > 0
        assert len(pos["antecedent_text_span"]) > 0


def test_hard_negative_preservation_validity(negative_cases, dataset_manifest):
    """Verify that hard negatives preserve intra-clause cohesion or coupled blocks."""
    assert len(negative_cases) == 30
    manifest_dict = {r["case_id"]: r for r in dataset_manifest}

    transformations = [r["transformation_type"] for r in negative_cases]
    assert transformations.count("INTRA_CLAUSE_DISCOURSE_PRESERVATION") == 10
    assert transformations.count("COUPLED_BLOCK_PRESERVATION") == 8
    assert transformations.count("INDEPENDENT_COVENANT_COMMUTATIVE_SWAP") == 6
    assert transformations.count("FRONT_LOADED_DEFINITIONS") == 3
    assert transformations.count("FRONT_LOADED_DISPUTE_RESOLUTION") == 3

    for neg in negative_cases:
        cid = neg["case_id"]
        meta = manifest_dict[cid]
        assert meta["ground_truth_label"] == "VERIFIED_NEGATIVE"
        assert meta["verification_status"] == "COMPUTATIONALLY_VERIFIED"
        assert len(neg["preservation_rationale"]) > 20


def test_ambiguous_case_isolation(ambiguous_cases, dataset_manifest):
    """Verify ambiguous cases are properly categorized and flagged for expert adjudication."""
    assert len(ambiguous_cases) == 12
    manifest_dict = {r["case_id"]: r for r in dataset_manifest}

    transformations = [r["transformation_type"] for r in ambiguous_cases]
    assert "DEICTIC_DIRECTIONAL_CONTRADICTION" in transformations
    assert "UNRESOLVED_DISCOURSE_REFERENCE_DISPLACEMENT" in transformations
    assert "INTERVENING_SUBSECTION_DISPLACEMENT" in transformations
    assert "CROSS_ARTICLE_RELOCATION_AMBIGUITY" in transformations

    for amb in ambiguous_cases:
        cid = amb["case_id"]
        meta = manifest_dict[cid]
        assert meta["ground_truth_label"] == "AMBIGUOUS"
        assert meta["verification_status"] == "EXPERT_ADJUDICATION_REQUIRED"
        assert amb["adjudication_status"] == "EXPERT_ADJUDICATION_REQUIRED"


def test_antecedent_resolution_records(candidates, resolutions):
    """Verify 1-to-1 alignment between candidates and antecedent resolution records."""
    assert len(candidates) == 339
    assert len(resolutions) == 339

    cand_dict = {c["candidate_id"]: c for c in candidates}
    for res in resolutions:
        cid = res["candidate_id"]
        assert cid in cand_dict
        cand = cand_dict[cid]

        if cand["is_intra_clause"] == "True":
            assert res["locality"] == "INTRA_CLAUSE"
            assert res["spans_clause_boundaries"] == "False"
        else:
            assert res["locality"] == "CROSS_CLAUSE"
            assert res["spans_clause_boundaries"] == "True"


def test_source_family_diversity_and_rights(source_families):
    """Verify source family diversity (>= 10 families) and correct rights metadata."""
    assert len(source_families) >= 10, f"Expected at least 10 families, found {len(source_families)}"

    for fam in source_families:
        assert fam["rights_classification"] == "PUBLICLY_ACCESSIBLE_RIGHTS_UNDETERMINED"
        assert int(fam["total_cases"]) > 0
        assert int(fam["parent_contract_count"]) > 0


def test_annotation_queue_oracle_isolation(annotation_queue):
    """Verify annotation queue does not leak model predictions or detector scores."""
    assert len(annotation_queue) == 72
    forbidden_columns = ["model_score", "prediction", "detector_output", "prob_positive"]

    with open(os.path.join(OUTPUT_DIR, "annotation_queue.csv"), "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        for col in forbidden_columns:
            assert col not in header, f"Forbidden column '{col}' exposed in annotation queue header"

    for item in annotation_queue:
        assert item["reviewer_verdict"] == "PENDING_REVIEW"
