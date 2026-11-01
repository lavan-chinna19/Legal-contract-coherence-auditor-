"""
tests/test_phase_04dca_audit.py
Independent ML Research Auditor & Scientific Reproducibility Verification Suite.
Validates Phase 4D-C-A audit deliverables, mathematical invariants,
and integrity guarantees without loading heavy language models.
"""
import os
import csv
import json
import hashlib
import pytest
from collections import Counter, defaultdict


# -----------------------------------------------------------------------------
# Test 1: Checkpoint Hash Reconciliation and Immutability
# -----------------------------------------------------------------------------

def test_checkpoint_hash_manifest_consistency():
    """Verify physical model checkpoint and centroid fixture match verified SHA-256 digests."""
    pt_path = "models/coherence_classifier.pt"
    npz_path = "fixtures/ledgar_centroids.npz"

    assert os.path.exists(pt_path), f"Checkpoint missing: {pt_path}"
    assert os.path.exists(npz_path), f"Centroids missing: {npz_path}"

    with open(pt_path, "rb") as f:
        pt_hash = hashlib.sha256(f.read()).hexdigest()
    with open(npz_path, "rb") as f:
        npz_hash = hashlib.sha256(f.read()).hexdigest()

    expected_pt = "9c0a5a096cdf03a63615134500a64f4bc559314be64366812d6a6f1762d4017f"
    expected_npz = "2ea33ac1cb8430e720be85cd501f11539c143901b2173b63b942b34b9d31ce07"

    assert pt_hash == expected_pt, f"Unexpected PT hash: {pt_hash}"
    assert npz_hash == expected_npz, f"Unexpected NPZ hash: {npz_hash}"


def test_checkpoint_reconciliation_csv_integrity():
    """Verify checkpoint_hash_reconciliation.csv records both artifacts with correct status."""
    csv_path = "design/ui_redesign/phase_04dca/checkpoint_hash_reconciliation.csv"
    assert os.path.exists(csv_path), f"Missing reconciliation CSV: {csv_path}"

    with open(csv_path, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    assert len(rows) == 2, f"Expected 2 rows, found {len(rows)}"
    for r in rows:
        assert "IDENTICAL_BYTES_VERIFIED" in r["audit_verdict"]
        assert "HISTORICAL_REPORTING_ERROR" in r["audit_verdict"]


# -----------------------------------------------------------------------------
# Test 2: SEC Source Inventory Verification (No Dictionary Key Conflation)
# -----------------------------------------------------------------------------

def test_sec_edgar_source_inventory_invariants():
    """
    Verify edgar_manifest.json actual entries, accession numbers, CIKs,
    downloaded files, and parent agreements without confusing top-level keys with filings.
    """
    manifest_path = "data/raw/sec_edgar/edgar_manifest.json"
    assert os.path.exists(manifest_path), f"Missing manifest: {manifest_path}"

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest_data = json.load(f)

    # 1. Top-level keys count is 10 (metadata keys, not filings)
    assert len(manifest_data.keys()) == 10, f"Expected 10 metadata keys, got {len(manifest_data.keys())}"
    assert "entries" in manifest_data

    entries = manifest_data["entries"]
    # 2. Total exhibit entries in manifest is exactly 50
    assert len(entries) == 50, f"Expected 50 exhibit entries, got {len(entries)}"

    # 3. Unique accession numbers across entries is 19
    accessions = set(e["accession_no"] for e in entries if e.get("accession_no"))
    assert len(accessions) == 19, f"Expected 19 unique accessions, got {len(accessions)}"

    # 4. Unique CIKs across entries is 19
    ciks = set(e["cik"] for e in entries if e.get("cik"))
    assert len(ciks) == 19, f"Expected 19 unique CIKs, got {len(ciks)}"

    # 5. Downloaded .txt files in storage is 50
    raw_dir = "data/raw/sec_edgar"
    txt_files = [f for f in os.listdir(raw_dir) if f.endswith(".txt")]
    assert len(txt_files) == 50, f"Expected 50 downloaded text files, got {len(txt_files)}"

    # 6. Authoritative parent agreements passing bounds filter (10 to 125 clauses) is 32
    parent_path = "research/independent_contract_benchmark_phase_04dc/parent_contract_manifest.csv"
    with open(parent_path, "r", encoding="utf-8") as f:
        parents = list(csv.DictReader(f))
    assert len(parents) == 32, f"Expected 32 eligible parent contracts, got {len(parents)}"


# -----------------------------------------------------------------------------
# Test 3: Backend Regression Baseline Reconciliation (183 vs 193 Passed)
# -----------------------------------------------------------------------------

def test_backend_regression_counts_reconciliation():
    """
    Verify historical regression counts:
    - Phase 4D-B: 185 collected, 183 passed, 2 skipped, 0 failed.
    - Phase 4D-C: 195 collected, 193 passed, 2 skipped, 0 failed (verified in raw log).
    """
    # 1. Phase 4D-B results
    p4db_json = "design/ui_redesign/phase_04db/backend_regression_results.json"
    with open(p4db_json, "r", encoding="utf-8") as f:
        res_4db = json.load(f)
    assert res_4db["total_collected"] == 185
    assert res_4db["passed"] == 183
    assert res_4db["skipped"] == 2
    assert res_4db["failed"] == 0

    # 2. Phase 4D-C results JSON
    p4dc_json = "design/ui_redesign/phase_04dc/backend_regression_results.json"
    with open(p4dc_json, "r", encoding="utf-8") as f:
        res_4dc = json.load(f)
    assert res_4dc["summary"]["total_collected"] == 195
    assert res_4dc["summary"]["passed"] == 193
    assert res_4dc["summary"]["skipped"] == 2
    assert res_4dc["summary"]["failed"] == 0

    # 3. Phase 4D-C raw pytest log
    p4dc_log = "design/ui_redesign/phase_04dc/backend_test_evidence.log"
    with open(p4dc_log, "r", encoding="utf-8") as f:
        log_content = f.read()
    assert "193 passed, 2 skipped" in log_content


# -----------------------------------------------------------------------------
# Test 4: Parent Contract & Split Denominator Invariants
# -----------------------------------------------------------------------------

def test_parent_split_count_reconciliation():
    """
    Verify authoritative parent counts:
    18 development + 9 validation + 5 sealed_test = 32 total parents across 15 families.
    """
    manifest_path = "research/independent_contract_benchmark_phase_04dc/parent_contract_manifest.csv"
    with open(manifest_path, "r", encoding="utf-8") as f:
        parents = list(csv.DictReader(f))

    assert len(parents) == 32, f"Expected 32 parent contracts, got {len(parents)}"

    split_counts = Counter(r["split_assignment"] for r in parents)
    assert split_counts["development"] == 18, f"Expected 18 dev, got {split_counts['development']}"
    assert split_counts["validation"] == 9, f"Expected 9 val, got {split_counts['validation']}"
    assert split_counts["sealed_test"] == 5, f"Expected 5 test, got {split_counts['sealed_test']}"
    assert sum(split_counts.values()) == 32


def test_parent_family_strict_disjointness():
    """Verify that every corporate entity family appears in exactly one split."""
    manifest_path = "research/independent_contract_benchmark_phase_04dc/parent_contract_manifest.csv"
    with open(manifest_path, "r", encoding="utf-8") as f:
        parents = list(csv.DictReader(f))

    family_to_splits = defaultdict(set)
    for p in parents:
        family_to_splits[p["document_family_id"]].add(p["split_assignment"])

    assert len(family_to_splits) == 15, f"Expected 15 families, got {len(family_to_splits)}"
    for fam, splits in family_to_splits.items():
        assert len(splits) == 1, f"Family {fam} crosses splits: {splits}"


def test_no_child_perturbation_split_crossing():
    """Verify that every perturbation case strictly inherits its parent's split assignment."""
    p_path = "research/independent_contract_benchmark_phase_04dc/parent_contract_manifest.csv"
    c_path = "research/independent_contract_benchmark_phase_04dc/perturbation_catalog.csv"

    with open(p_path, "r", encoding="utf-8") as f:
        parent_splits = {r["parent_document_id"]: r["split_assignment"] for r in csv.DictReader(f)}

    with open(c_path, "r", encoding="utf-8") as f:
        perts = list(csv.DictReader(f))

    assert len(perts) == 174, f"Expected 174 perturbations, got {len(perts)}"
    for p in perts:
        pid = p["parent_document_id"]
        assert p["split"] == parent_splits[pid], f"Split mismatch for {p['case_id']}: {p['split']} != {parent_splits[pid]}"


def test_test_case_denominators():
    """
    Verify test partition case denominators:
    23 total test cases = 18 eligible (2 positive, 16 negative) + 5 excluded (ambiguous).
    """
    anno_path = "research/independent_contract_benchmark_phase_04dc/annotation_records.csv"
    with open(anno_path, "r", encoding="utf-8") as f:
        test_annos = [r for r in csv.DictReader(f) if r["split"] == "sealed_test"]

    assert len(test_annos) == 23, f"Expected 23 test cases, got {len(test_annos)}"
    eligible = [r for r in test_annos if r["eligibility_decision"] == "ELIGIBLE"]
    excluded = [r for r in test_annos if r["eligibility_decision"] == "EXCLUDED"]

    assert len(eligible) == 18, f"Expected 18 eligible test cases, got {len(eligible)}"
    assert len(excluded) == 5, f"Expected 5 excluded test cases, got {len(excluded)}"

    labels = Counter(r["ground_truth_label"] for r in eligible)
    assert labels["VERIFIED_DISCOURSE_DEPENDENCY_VIOLATION"] == 2
    assert labels["VALID_CANONICAL_ORDER"] == 5
    assert labels["VALID_NONCANONICAL_ORDER"] == 11


# -----------------------------------------------------------------------------
# Test 5: Detection Matrix Regeneration & Candidate C2 Discrepancy Reconciliation
# -----------------------------------------------------------------------------

def test_stored_prediction_matrix_regeneration_all_six_models():
    """
    Reconstruct confusion matrices directly from case_level_predictions.csv
    and verify exact agreement across all 6 models including Candidate C2 raw rows.
    """
    pred_path = "research/independent_contract_benchmark_phase_04dc/case_level_predictions.csv"
    with open(pred_path, "r", encoding="utf-8") as f:
        preds = list(csv.DictReader(f))

    assert len(preds) == 108, f"Expected 108 predictions (18 cases * 6 models), got {len(preds)}"

    # Exact confusion matrices as recorded in raw stored rows
    expected_raw = {
        "Baseline_B0_FrozenChannelB": {"tp": 2, "fp": 16, "fn": 0, "tn": 0},
        "Baseline_B1_ProductionDualChannel": {"tp": 2, "fp": 16, "fn": 0, "tn": 0},
        "Baseline_B2_AdjacentCosine": {"tp": 2, "fp": 10, "fn": 0, "tn": 6},
        "Candidate_C1_ContextualBoundary": {"tp": 2, "fp": 16, "fn": 0, "tn": 0},
        "Candidate_C2_SequenceBiLSTM": {"tp": 2, "fp": 16, "fn": 0, "tn": 0},
        "Candidate_C3_TopologicalDependency": {"tp": 2, "fp": 11, "fn": 0, "tn": 5},
    }

    models = sorted(list(set(r["model_name"] for r in preds)))
    for m in models:
        m_preds = [r for r in preds if r["model_name"] == m]
        tp = sum(1 for r in m_preds if r["is_gt_anomaly"] == "True" and r["predicted_anomaly"] == "True")
        fp = sum(1 for r in m_preds if r["is_gt_anomaly"] == "False" and r["predicted_anomaly"] == "True")
        fn = sum(1 for r in m_preds if r["is_gt_anomaly"] == "True" and r["predicted_anomaly"] == "False")
        tn = sum(1 for r in m_preds if r["is_gt_anomaly"] == "False" and r["predicted_anomaly"] == "False")

        assert {"tp": tp, "fp": fp, "fn": fn, "tn": tn} == expected_raw[m], f"Raw mismatch for model {m}"


def test_candidate_c2_historical_reported_underfitting_reconciliation():
    """
    Verify that Candidate C2's canonical historical reported underfitting classification
    (TP=0, FP=0, FN=2, TN=16) is preserved and reconciled in corrected_metric_consistency.json
    with explicit NOT_ESTIMABLE handling for undefined precision and F1.
    """
    json_path = "design/ui_redesign/phase_04dca/corrected_metric_consistency.json"
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 1. Check reported baseline section
    reported_models = data["canonical_historical_reported_metrics"]["models"]
    assert "Candidate_C2_SequenceBiLSTM_ReportedUnderfitting" in reported_models
    c2_rep = reported_models["Candidate_C2_SequenceBiLSTM_ReportedUnderfitting"]

    assert c2_rep["tp"] == 0
    assert c2_rep["fp"] == 0
    assert c2_rep["fn"] == 2
    assert c2_rep["tn"] == 16
    assert c2_rep["recall"] == 0.0
    assert c2_rep["specificity"] == 1.0
    assert c2_rep["precision"] == "NOT_ESTIMABLE"
    assert c2_rep["f1"] == "NOT_ESTIMABLE"
    assert c2_rep["balanced_accuracy"] == 0.5

    # 2. Check raw stored predictions section
    raw_models = data["raw_stored_predictions_direct_reconstruction"]["models"]
    assert "Candidate_C2_SequenceBiLSTM_RawThresholded" in raw_models
    c2_raw = raw_models["Candidate_C2_SequenceBiLSTM_RawThresholded"]
    assert c2_raw["tp"] == 2
    assert c2_raw["fp"] == 16
    assert c2_raw["fn"] == 0
    assert c2_raw["tn"] == 0


def test_c2_silent_reporting_drift_guard():
    """
    Regression assertion ensuring Candidate C2's classification cannot silently change
    between raw stored rows and reported underfitting without audit traceability.
    """
    pred_path = "research/independent_contract_benchmark_phase_04dc/case_level_predictions.csv"
    with open(pred_path, "r", encoding="utf-8") as f:
        c2_preds = [r for r in csv.DictReader(f) if r["model_name"] == "Candidate_C2_SequenceBiLSTM"]

    assert len(c2_preds) == 18
    # Assert every single raw prediction score is in [0.52, 0.53]
    for r in c2_preds:
        score = float(r["anomaly_score"])
        assert 0.52 <= score <= 0.53, f"Score drifted: {score}"
        assert r["predicted_anomaly"] == "True"


# -----------------------------------------------------------------------------
# Test 6: Wilson Score Interval Exactness
# -----------------------------------------------------------------------------

def test_wilson_score_interval_exactness():
    """Verify Wilson 95% confidence interval calculations."""
    from src.research.independent_benchmark.statistics import compute_wilson_score_interval

    ci_2_2 = compute_wilson_score_interval(2, 2, confidence_level=0.95)
    assert ci_2_2.point_estimate == 1.0
    assert round(ci_2_2.lower_bound, 4) == 0.3424
    assert ci_2_2.upper_bound == 1.0

    ci_0_2 = compute_wilson_score_interval(0, 2, confidence_level=0.95)
    assert ci_0_2.point_estimate == 0.0
    assert ci_0_2.lower_bound == 0.0
    assert round(ci_0_2.upper_bound, 4) == 0.6576

    ci_0_16 = compute_wilson_score_interval(0, 16, confidence_level=0.95)
    assert ci_0_16.point_estimate == 0.0
    assert ci_0_16.lower_bound == 0.0
    assert round(ci_0_16.upper_bound, 4) == 0.1936

    ci_6_16 = compute_wilson_score_interval(6, 16, confidence_level=0.95)
    assert ci_6_16.point_estimate == 0.375
    assert round(ci_6_16.lower_bound, 4) == 0.1848
    assert round(ci_6_16.upper_bound, 4) == 0.6136

    ci_16_16 = compute_wilson_score_interval(16, 16, confidence_level=0.95)
    assert ci_16_16.point_estimate == 1.0
    assert round(ci_16_16.lower_bound, 4) == 0.8064
    assert ci_16_16.upper_bound == 1.0


# -----------------------------------------------------------------------------
# Test 7: Legal & Provenance Status Invariants
# -----------------------------------------------------------------------------

def test_source_rights_classification_no_false_public_domain():
    """Verify that source rights status rejects automatic public domain claims under Section 105."""
    csv_path = "design/ui_redesign/phase_04dca/source_rights_status.csv"
    assert os.path.exists(csv_path), f"Missing source rights CSV: {csv_path}"

    with open(csv_path, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    assert len(rows) == 50, f"Expected 50 rows in source_rights_status.csv, got {len(rows)}"
    for r in rows:
        assert r["corrected_legal_classification"] == "PUBLICLY_ACCESSIBLE_RIGHTS_UNDETERMINED"
        assert r["sec_105_public_domain_applies"] == "False"
        assert "DO_NOT_REDISTRIBUTE_FULL_TEXT" in r["redistribution_recommendation"]


# -----------------------------------------------------------------------------
# Test 8: Ground-Truth Validity & Post-Hoc Sensitivity Invariants
# -----------------------------------------------------------------------------

def test_positive_case_review_completeness():
    """Verify that all 28 positive cases across all splits are reviewed in positive_case_evidence_review.csv."""
    csv_path = "design/ui_redesign/phase_04dca/positive_case_evidence_review.csv"
    assert os.path.exists(csv_path), f"Missing positive case review CSV: {csv_path}"

    with open(csv_path, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    assert len(rows) == 28, f"Expected 28 reviewed positive cases, got {len(rows)}"
    p1_rows = [r for r in rows if r["category_code"] == "P1"]
    assert len(p1_rows) == 14
    for r in p1_rows:
        assert r["evidence_strength_category"] == "INVALID_TRANSFORMATION"
        assert r["objective_defect_verdict"] == "NO_OBJECTIVE_DISCOURSE_DEFECT"


def test_posthoc_sensitivity_metrics_integrity():
    """Verify posthoc sensitivity analysis in corrected_metric_consistency.json."""
    json_path = "design/ui_redesign/phase_04dca/corrected_metric_consistency.json"
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    views = data.get("posthoc_sensitivity_analysis_views", {})
    assert "view_1_exclude_invalid_p1" in views
    assert "view_2_exclude_both_unsupported_positives" in views

    # View 2: Zero positive cases -> Recall, Precision, F1, Balanced Accuracy are NOT_ESTIMABLE
    v2_models = views["view_2_exclude_both_unsupported_positives"]["models"]
    for m_name, m_metrics in v2_models.items():
        assert m_metrics["recall"] == "NOT_ESTIMABLE"
        assert m_metrics["precision"] == "NOT_ESTIMABLE"
        assert m_metrics["f1"] == "NOT_ESTIMABLE"
        assert m_metrics["balanced_accuracy"] == "NOT_ESTIMABLE"


# -----------------------------------------------------------------------------
# Test 9: Chronology and Pre-registration Classification
# -----------------------------------------------------------------------------

def test_chronology_decision_and_timeline():
    """Verify that benchmark timeline records chronology as co-generated rather than pre-registered."""
    timeline_path = "design/ui_redesign/phase_04dca/benchmark_execution_timeline.csv"
    assert os.path.exists(timeline_path), f"Missing timeline CSV: {timeline_path}"

    with open(timeline_path, "r", encoding="utf-8") as f:
        events = list(csv.DictReader(f))

    assert len(events) >= 10
    handoff_path = "design/ui_redesign/phase_04dca/handoff_phase_04dca.json"
    with open(handoff_path, "r", encoding="utf-8") as f:
        handoff = json.load(f)

    assert "PREREGISTRATION COMPROMISED" in handoff["final_verdict"]
