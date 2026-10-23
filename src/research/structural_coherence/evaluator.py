"""
src/research/structural_coherence/evaluator.py — Scientific Evaluation and Benchmarking Suite.
Phase 4D-B Research Extension.

Executes matched, reproducible comparisons across:
- Baselines: B0 (Frozen Channel B), B1 (Production Ensemble), B2 (Adjacent Cosine)
- Candidates: C1 (Contextual Boundary), C2 (Sequence BiLSTM), C3 (Topological Dependency)
Across:
- Partition 1: Historical Diagnostic Benchmark (6 Phase 4D cases: 3 P1 displacements, 3 P2 swaps)
- Partition 2: Development / Validation Set (SLA structural violations + SLA hard negative reorderings)
- Partition 3: Held-Out Test Set (Fresh structural test cases + canonical clean contracts)
"""
import os
import sys
import json
import csv
import time
import math
from pathlib import Path
from typing import List, Dict, Tuple, Any, Optional
import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.config import ClauseRecord
from src.redteam.fixtures import get_synthetic_msa_clauses, get_synthetic_sla_clauses
from src.redteam.scenarios import get_canonical_benchmark_scenarios
from src.redteam.runner import RedTeamExperimentRunner
from src.research.structural_coherence.schema import (
    StructuralAnomalyLabel,
    DocumentStructuralResult,
    EvaluationMetrics
)
from src.research.structural_coherence.models import (
    BaselineB0_ChannelB,
    BaselineB1_ProductionEnsemble,
    BaselineB2_CosineDistance,
    CandidateC1_ContextualBoundaryDetector,
    CandidateC2_ContextualSequenceModel,
    CandidateC3_StructureAwareDependencyModel
)


def compute_wilson_score_interval(k: int, n: int, confidence: float = 0.95) -> Tuple[float, float]:
    """Computes exact two-sided Wilson 95% confidence interval [lower, upper]."""
    if n <= 0:
        return 0.0, 0.0
    z = 1.959963984540054
    p = k / n
    denom = 1.0 + (z ** 2) / n
    center = (p + (z ** 2) / (2.0 * n)) / denom
    spread = (z * math.sqrt((p * (1.0 - p) / n) + ((z ** 2) / (4.0 * (n ** 2))))) / denom
    return round(max(0.0, center - spread), 4), round(min(1.0, center + spread), 4)


class BenchmarkCase:
    def __init__(
        self,
        case_id: str,
        split: str,
        doc_id: str,
        clauses: List[ClauseRecord],
        ground_truth_label: StructuralAnomalyLabel,
        is_positive: bool,
        target_clause_ids: List[str],
        description: str
    ):
        self.case_id = case_id
        self.split = split
        self.doc_id = doc_id
        self.clauses = clauses
        self.ground_truth_label = ground_truth_label
        self.is_positive = is_positive
        self.target_clause_ids = target_clause_ids
        self.description = description


def assemble_benchmark_cases() -> List[BenchmarkCase]:
    """
    Assembles all evaluation cases partitioned by split:
    - DIAGNOSTIC (Previously Observed Phase 4D/4D-A cases): 6 structural transformations + 2 clean controls.
    - VALIDATION: 3 SLA ordering variations (1 positive displacement, 1 positive prerequisite inversion, 1 hard negative swap).
    - HELDOUT_TEST: 4 fresh test cases (2 positive structural violations, 1 hard negative independent reordering, 1 clean control).
    """
    cases = []
    msa = get_synthetic_msa_clauses()
    sla = get_synthetic_sla_clauses()
    runner = RedTeamExperimentRunner()
    scenarios = {s.scenario_id: s for s in get_canonical_benchmark_scenarios()}

    # --- PARTITION 1: DIAGNOSTIC BENCHMARK (6 Phase 4D Cases + 2 Controls) ---
    # Diagnostic 1: P1_01 Distant Displacement (Scope slot 1 -> 10)
    pert_clauses, _ = runner._apply_transformation(scenarios["SCEN_P1_01_DISP_DISTANT"], msa)
    cases.append(BenchmarkCase(
        "DIAG_P1_01_DISP_SCOPE", "DIAGNOSTIC", "SYNTH_DOC_01_MSA", pert_clauses,
        StructuralAnomalyLabel.VERIFIED_STRUCTURAL_DEPENDENCY_VIOLATION, True,
        ["SYNTH_DOC_01_MSA_c01"], "Distant displacement of Scope (slot 1 to slot 10)"
    ))

    # Diagnostic 2: P1_02 Moderate Displacement (Term slot 5 -> 2)
    pert_clauses, _ = runner._apply_transformation(scenarios["SCEN_P1_02_DISP_MODERATE"], msa)
    cases.append(BenchmarkCase(
        "DIAG_P1_02_DISP_TERM", "DIAGNOSTIC", "SYNTH_DOC_01_MSA", pert_clauses,
        StructuralAnomalyLabel.VERIFIED_STRUCTURAL_DEPENDENCY_VIOLATION, True,
        ["SYNTH_DOC_01_MSA_c05"], "Moderate displacement of Term (slot 5 to slot 2)"
    ))

    # Diagnostic 3: P1_03 Subtle Displacement (IP slot 3 -> 4)
    pert_clauses, _ = runner._apply_transformation(scenarios["SCEN_P1_03_DISP_SUBTLE"], msa)
    cases.append(BenchmarkCase(
        "DIAG_P1_03_DISP_IP", "DIAGNOSTIC", "SYNTH_DOC_01_MSA", pert_clauses,
        StructuralAnomalyLabel.VERIFIED_STRUCTURAL_DEPENDENCY_VIOLATION, True,
        ["SYNTH_DOC_01_MSA_c03"], "Subtle displacement of IP (slot 3 to slot 4)"
    ))

    # Diagnostic 4: P2_01 Adjacent Swap (Preamble <-> Scope, slots 0 <-> 1)
    pert_clauses, _ = runner._apply_transformation(scenarios["SCEN_P2_01_SWAP_ADJACENT"], msa)
    cases.append(BenchmarkCase(
        "DIAG_P2_01_SWAP_PREAMBLE", "DIAGNOSTIC", "SYNTH_DOC_01_MSA", pert_clauses,
        StructuralAnomalyLabel.VERIFIED_STRUCTURAL_DEPENDENCY_VIOLATION, True,
        ["SYNTH_DOC_01_MSA_c00", "SYNTH_DOC_01_MSA_c01"], "Swap Preamble and Scope (slots 0 and 1)"
    ))

    # Diagnostic 5: P2_02 Distant Swap (Payment <-> Gov Law, slots 2 <-> 8)
    pert_clauses, _ = runner._apply_transformation(scenarios["SCEN_P2_02_SWAP_DISTANT"], msa)
    cases.append(BenchmarkCase(
        "DIAG_P2_02_SWAP_PAYMENT_GOVLAW", "DIAGNOSTIC", "SYNTH_DOC_01_MSA", pert_clauses,
        StructuralAnomalyLabel.VERIFIED_STRUCTURAL_DEPENDENCY_VIOLATION, True,
        ["SYNTH_DOC_01_MSA_c02", "SYNTH_DOC_01_MSA_c08"], "Swap Payment and Governing Law (slots 2 and 8)"
    ))

    # Diagnostic 6: P2_03 Subtle Swap (Confidentiality <-> Indemnification, slots 4 <-> 6) [Ambiguous]
    pert_clauses, _ = runner._apply_transformation(scenarios["SCEN_P2_03_SWAP_SUBTLE"], msa)
    cases.append(BenchmarkCase(
        "DIAG_P2_03_SWAP_CONF_INDEMN", "DIAGNOSTIC", "SYNTH_DOC_01_MSA", pert_clauses,
        StructuralAnomalyLabel.AMBIGUOUS_ORDER, False,  # Strict negative: ambiguous covenant swap
        ["SYNTH_DOC_01_MSA_c04", "SYNTH_DOC_01_MSA_c06"], "Swap Confidentiality and Indemnification (ambiguous)"
    ))

    # Diagnostic 7: Clean MSA Negative Control
    cases.append(BenchmarkCase(
        "DIAG_P9_01_CLEAN_MSA", "DIAGNOSTIC", "SYNTH_DOC_01_MSA", msa,
        StructuralAnomalyLabel.VALID_ORDER, False,
        [], "Unperturbed clean MSA negative control"
    ))

    # Diagnostic 8: Clean SLA Negative Control
    cases.append(BenchmarkCase(
        "DIAG_P9_02_CLEAN_SLA", "DIAGNOSTIC", "SYNTH_DOC_02_SLA", sla,
        StructuralAnomalyLabel.VALID_ORDER, False,
        [], "Unperturbed clean SLA negative control"
    ))

    # --- PARTITION 2: DEVELOPMENT / VALIDATION SET ---
    # Val 1: SLA Term Displaced into Scope slot (Positive)
    val_disp_clauses = [sla[0], sla[6], sla[1], sla[2], sla[3], sla[4], sla[5], sla[7]]
    cases.append(BenchmarkCase(
        "VAL_SLA_01_DISP_TERM", "VALIDATION", "SYNTH_DOC_02_SLA", val_disp_clauses,
        StructuralAnomalyLabel.VERIFIED_STRUCTURAL_DEPENDENCY_VIOLATION, True,
        ["SYNTH_DOC_02_SLA_c06"], "Displacement of SLA Term clause into operational definitions"
    ))

    # Val 2: SLA Dispute Resolution Swapped to Top (slot 0 <-> 7) (Positive)
    val_swap_clauses = [sla[7], sla[1], sla[2], sla[3], sla[4], sla[5], sla[6], sla[0]]
    cases.append(BenchmarkCase(
        "VAL_SLA_02_SWAP_DISPUTE_PREAMBLE", "VALIDATION", "SYNTH_DOC_02_SLA", val_swap_clauses,
        StructuralAnomalyLabel.VERIFIED_STRUCTURAL_DEPENDENCY_VIOLATION, True,
        ["SYNTH_DOC_02_SLA_c07", "SYNTH_DOC_02_SLA_c00"], "Swap Dispute Resolution to document opening"
    ))

    # Val 3: SLA Hard Negative: Permitted Users <-> Fees Schedule (slots 1 <-> 3) (Coherent Hard Negative)
    val_hn_clauses = [sla[0], sla[3], sla[2], sla[1], sla[4], sla[5], sla[6], sla[7]]
    cases.append(BenchmarkCase(
        "VAL_SLA_03_HN_COHERENT_SWAP", "VALIDATION", "SYNTH_DOC_02_SLA", val_hn_clauses,
        StructuralAnomalyLabel.INDEPENDENT_REORDERING, False,
        [], "Valid non-canonical reordering of Users and Fee schedule"
    ))

    # --- PARTITION 3: UNTOUCHED HELD-OUT TEST SET ---
    # Test 1: Fresh Held-Out Positive 1: MSA Exhibit A moved before Section 2 Scope (slots 1 <-> 10)
    test_p1_clauses = [msa[0], msa[10], msa[2], msa[3], msa[4], msa[5], msa[6], msa[7], msa[8], msa[9], msa[1]]
    cases.append(BenchmarkCase(
        "TEST_01_EXHIBIT_SCOPE_INVERSION", "HELDOUT_TEST", "SYNTH_DOC_01_MSA", test_p1_clauses,
        StructuralAnomalyLabel.VERIFIED_STRUCTURAL_DEPENDENCY_VIOLATION, True,
        ["SYNTH_DOC_01_MSA_c10", "SYNTH_DOC_01_MSA_c01"], "Exhibit A Statement of Work placed before Scope of Services"
    ))

    # Test 2: Fresh Held-Out Positive 2: Governing Law moved before Scope (slot 8 -> 1)
    test_p2_clauses = [msa[0], msa[8], msa[1], msa[2], msa[3], msa[4], msa[5], msa[6], msa[7], msa[9], msa[10]]
    cases.append(BenchmarkCase(
        "TEST_02_GOVLAW_BEFORE_SCOPE", "HELDOUT_TEST", "SYNTH_DOC_01_MSA", test_p2_clauses,
        StructuralAnomalyLabel.VERIFIED_STRUCTURAL_DEPENDENCY_VIOLATION, True,
        ["SYNTH_DOC_01_MSA_c08"], "Governing Law placed between Preamble and Scope"
    ))

    # Test 3: Fresh Held-Out Hard Negative: Audit Rights <-> Warranty Disclaimer (slots 4 <-> 5 in SLA)
    test_hn_clauses = [sla[0], sla[1], sla[2], sla[3], sla[5], sla[4], sla[6], sla[7]]
    cases.append(BenchmarkCase(
        "TEST_03_HN_AUDIT_WARRANTY_SWAP", "HELDOUT_TEST", "SYNTH_DOC_02_SLA", test_hn_clauses,
        StructuralAnomalyLabel.INDEPENDENT_REORDERING, False,
        [], "Coherent swap of Audit Rights and Warranty Disclaimer (Hard Negative)"
    ))

    # Test 4: Fresh Held-Out Negative Control: Canonical Clean MSA
    cases.append(BenchmarkCase(
        "TEST_04_CLEAN_CONTROL", "HELDOUT_TEST", "SYNTH_DOC_01_MSA", msa,
        StructuralAnomalyLabel.VALID_ORDER, False,
        [], "Fresh untouched clean MSA control"
    ))

    return cases


def run_benchmark_evaluation() -> Dict[str, Any]:
    """
    Executes full evaluation of all models across all benchmark partitions.
    """
    cases = assemble_benchmark_cases()
    models = [
        BaselineB0_ChannelB(threshold=0.70),
        BaselineB1_ProductionEnsemble(threshold=0.50),
        BaselineB2_CosineDistance(threshold=0.25),
        CandidateC1_ContextualBoundaryDetector(threshold=0.42),
        CandidateC2_ContextualSequenceModel(
            checkpoint_path=str(REPO_ROOT / "models" / "experimental" / "phase_04db" / "contextual_sequence_coherence.pt"),
            threshold=0.50
        ),
        CandidateC3_StructureAwareDependencyModel(threshold=0.50)
    ]

    all_case_predictions = []
    split_summaries = {}

    for model in models:
        m_name = model.name
        split_summaries[m_name] = {}

        for split in ["DIAGNOSTIC", "VALIDATION", "HELDOUT_TEST"]:
            split_cases = [c for c in cases if c.split == split]

            # For strict structural evaluation:
            # Positives: is_positive == True
            # Negatives: is_positive == False (clean controls and independent reorderings)
            # Ambiguous cases (like P2_03) are recorded but excluded from strict positive denominator
            eligible_cases = [c for c in split_cases if c.ground_truth_label != StructuralAnomalyLabel.AMBIGUOUS_ORDER]

            tp = 0
            fp = 0
            fn = 0
            tn = 0
            loc_hits = 0
            pos_count = 0
            latencies = []

            for c in split_cases:
                res = model.evaluate_document(c.clauses, doc_id=c.doc_id)
                latencies.append(res.execution_time_ms)

                # Check localization: did predicted clause overlap with true target clause?
                pred_targets = set(res.predicted_anomaly_clause_ids)
                true_targets = set(c.target_clause_ids)
                hit = bool(pred_targets.intersection(true_targets)) if true_targets else False

                all_case_predictions.append({
                    "model_name": m_name,
                    "split": split,
                    "case_id": c.case_id,
                    "ground_truth_label": c.ground_truth_label.value,
                    "is_positive": c.is_positive,
                    "model_detected": res.is_anomaly,
                    "max_structural_score": res.max_structural_score,
                    "mean_structural_score": res.mean_structural_score,
                    "predicted_clause_count": len(res.predicted_anomaly_clause_ids),
                    "target_clause_hit": hit,
                    "execution_time_ms": round(res.execution_time_ms, 2)
                })

                if c in eligible_cases:
                    if c.is_positive:
                        pos_count += 1
                        if res.is_anomaly:
                            tp += 1
                            if hit:
                                loc_hits += 1
                        else:
                            fn += 1
                    else:
                        if res.is_anomaly:
                            fp += 1
                        else:
                            tn += 1

            n_pos = tp + fn
            n_neg = fp + tn
            rec = tp / n_pos if n_pos > 0 else 0.0
            prec = tp / (tp + fp) if (tp + fp) > 0 else None
            f1 = (2 * prec * rec) / (prec + rec) if (prec is not None and (prec + rec) > 0) else None
            spec = tn / n_neg if n_neg > 0 else 1.0
            fpr = fp / n_neg if n_neg > 0 else 0.0
            b_acc = 0.5 * (rec + spec)
            wilson_low, wilson_high = compute_wilson_score_interval(tp, n_pos)
            loc_rate = loc_hits / tp if tp > 0 else None

            metrics = EvaluationMetrics(
                model_name=m_name,
                split_name=split,
                condition_positives=n_pos,
                condition_negatives=n_neg,
                tp=tp,
                fp=fp,
                fn=fn,
                tn=tn,
                recall=round(rec, 4),
                precision=round(prec, 4) if prec is not None else None,
                f1=round(f1, 4) if f1 is not None else None,
                specificity=round(spec, 4),
                fpr=round(fpr, 4),
                balanced_accuracy=round(b_acc, 4),
                pr_auc=None,
                roc_auc=None,
                wilson_95_ci_recall=(wilson_low, wilson_high),
                localization_hit_rate=round(loc_rate, 4) if loc_rate is not None else None,
                mean_latency_ms=round(float(np.mean(latencies)), 2)
            )
            split_summaries[m_name][split] = metrics.to_dict()

    out_dir = REPO_ROOT / "research" / "structural_coherence_phase_04db"
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Save case_level_predictions.csv
    pred_path = out_dir / "case_level_predictions.csv"
    with open(pred_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(all_case_predictions[0].keys()))
        writer.writeheader()
        writer.writerows(all_case_predictions)
    print(f"Saved {pred_path} ({len(all_case_predictions)} rows)")

    # 2. Save baseline_results.csv and candidate_selection_matrix.csv
    summary_path = out_dir / "evaluation_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(split_summaries, f, indent=2)
    print(f"Saved {summary_path}")

    return {
        "predictions": all_case_predictions,
        "summaries": split_summaries
    }


if __name__ == "__main__":
    results = run_benchmark_evaluation()
    print("\n=== EVALUATION RESULTS SUMMARY ===")
    for model, splits in results["summaries"].items():
        print(f"\nModel: {model}")
        for split, m in splits.items():
            print(f"  [{split}]: Recall={m['recall']} ({m['tp']}/{m['condition_positives']}), Wilson CI={m['wilson_95_ci_recall']}, Spec={m['specificity']}, Latency={m['mean_latency_ms']}ms")
