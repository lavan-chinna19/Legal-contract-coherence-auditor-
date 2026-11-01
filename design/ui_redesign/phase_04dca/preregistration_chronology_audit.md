# Pre-Registration Chronology & Held-Out Test Evaluation Audit

**Audit Program**: LexAudit Reproducibility and Scientific Integrity Audit (Phase 4D-C-A)  
**Investigation Scope**: Audit B — Evaluation Protocol Pre-Registration & Sealed Test Chronology  
**Auditor**: Independent ML Research Auditor, Experimental Methodology Specialist  
**Authoritative Verdict**: **EXECUTION_REPEATED_WITH_FROZEN_CONFIGURATION — EXPLORATORY PILOT ONLY**

---

## 1. Executive Summary

Phase 4D-C reported a "Single sealed held-out evaluation pass" with "Pre-registered evaluation protocol and hashed checkpoints."

This audit reconstructed the exact execution timeline using file creation times, modification times, code structure analysis, and execution traces. The audit revealed that **the evaluation protocol markdown and the cryptographic protocol hash manifest were generated programmatically by the reporting engine AFTER (or simultaneously with) the model predictions on the held-out test cases**.

While there is **zero evidence of post-test threshold tuning or model tampering** (all models ran with pre-fixed historical thresholds and exhibited unoptimized, failure-prone performance), the experiment fails the strict scientific standard for pre-registered confirmatory trials. Phase 4D-C must be classified as an **exploratory source-disjoint pilot**, and its confirmatory claims must be formally withdrawn.

---

## 2. Reconstructed Event Chronology

| Sequence | Exact Timestamp (UTC) | Pipeline Event | Artifact Affected | Provenance Evidence & Technical Mechanism |
| :---: | :---: | :--- | :--- | :--- |
| **1** | 2026-10-22 18:43:47 | Code Creation: Splitter | `src/research/independent_benchmark/splitter.py` | Implementation of deterministic family hashing and disjoint partition algorithm. |
| **2** | 2026-10-22 18:45:05 | Code Creation: Perturbations | `src/research/independent_benchmark/perturbations.py` | Implementation of N1-N4, P1-P2, and A1 perturbation functions. |
| **3** | 2026-10-22 18:45:54 | Code Creation: Dataset Builder | `src/research/independent_benchmark/dataset_builder.py` | Implementation of corpus loader, deduplication, and case generation pipeline. |
| **4** | 2026-10-22 18:48:20 | Initial Dataset Generation | `research/.../parent_contract_manifest.csv` | Initial file creation timestamp (CTime) for 32 parents, 15 families, and 174 perturbations. |
| **5** | 2026-10-22 18:49:48 | Code Creation: Evaluator | `src/research/independent_benchmark/evaluation.py` | Model evaluation harness implemented with frozen baseline thresholds (B0=0.70, B1=0.50, B2=0.60, C1-C3=0.50). |
| **6** | 2026-10-22 18:56:34 | Code Creation: Reporting Engine | `src/research/independent_benchmark/reporting.py` | Automated batch reporting script coded to execute steps 1 through 14 sequentially. |
| **7** | 2026-10-22 18:58:10 | Automated Pipeline Execution: Manifests | `research/.../source_family_split_manifest.csv` | Re-export of dataset manifests during execution of `BenchmarkReportingEngine.run_full_pipeline_and_export_reports()`. |
| **8** | 2026-10-22 18:58:14 | Automated Pipeline Execution: Inference | `research/.../case_level_predictions.csv` | Evaluator computes predictions across 18 eligible test cases for all 6 models. |
| **9** | 2026-10-22 18:58:16 | Post-Hoc Protocol Generation | `research/.../protocol_hash_manifest.json` | `_export_json_manifests()` executes in Step 12, hashing the models and writing manifest after predictions exist. |
| **10** | 2026-10-22 18:58:16 | Post-Hoc Protocol Markdown | `research/.../preregistered_evaluation_protocol.md` | `_export_research_markdown_reports()` executes in Step 13, writing markdown protocol text after predictions exist. |
| **11** | 2026-10-22 18:58:17 | Final Benchmark Reporting | `research/.../final_benchmark_report.md` | Aggregated confusion matrices and narrative report emitted. |

---

## 3. Detailed Root-Cause Analysis

### A. Architectural Flaw in Reporting Pipeline
Inspection of `src/research/independent_benchmark/reporting.py` lines 40-100 demonstrates that the pipeline was structured as a single continuous method `run_full_pipeline_and_export_reports`:
```python
# Step 3: Run evaluation across sealed test partition (Line 56-60)
evaluator = BenchmarkEvaluator()
test_predictions = evaluator.evaluate_split(all_test_cases, filter_eligible=True)

# Export case-level predictions (Line 64)
evaluator.export_predictions_csv(test_predictions, pred_csv_path)

# ... Metrics aggregation (Lines 66-91) ...

# Step 12: Export JSON manifests (Line 93)
self._export_json_manifests(data, metrics_by_model)

# Step 13: Export Research Markdown Reports (Line 96)
self._export_research_markdown_reports(data, metrics_by_model)
```
In `_export_json_manifests()` (lines 288-305), the method creates `protocol_hash_manifest.json` with a hardcoded timestamp `"2026-10-23T00:00:00Z"`. In `_export_research_markdown_reports()`, it writes `preregistered_evaluation_protocol.md`.

Because Step 12 and Step 13 execute **after Step 3**, the "pre-registered protocol" was generated after model predictions were calculated. In scientific methodology, a protocol file generated simultaneously with or after test evaluation cannot retroactively establish pre-registration.

### B. Assessment of Model Tuning / Malpractice
The audit critically examined whether the authors inspected the test results and iteratively tuned model parameters or thresholds to produce favorable numbers:
1. **Zero Parameter Tuning**: Model thresholds were hardcoded to historical constants ($B_0 = 0.70$, $B_1 = 0.50$, $B_2 = 0.60$, $C_1 - C_3 = 0.50$) taken from Phase 4D-B and production defaults.
2. **Unfavorable Outcome Preserved**: Models $B_0, B_1, C_1, C_2$ achieved **0% specificity** (16 false positives out of 16 clean/hard negative cases). If tuning had occurred, thresholds would have been adjusted to increase specificity.
3. **Transparent Failure Reporting**: The report openly documented the 0% specificity and the severe failure mode of $C_1$ and $C_2$.

Therefore, there is **zero evidence of bad faith, data dredging, or p-hacking**. The flaw was purely an engineering pipeline ordering defect where protocol documentation was bundled into the output generation script.

---

## 4. Formal Acceptance Classification

Under the required audit standards:
- **Classification**: **`EXECUTION_REPEATED_WITH_FROZEN_CONFIGURATION`**
- **Secondary Classification**: **`TEST_EXPOSED_BEFORE_PROTOCOL_FREEZE`**
- **Prohibited Classification**: `PRE_REGISTRATION_VERIFIED` (Strictly Rejected)

### Required Corrective Action:
1. Re-label Phase 4D-C from "Pre-registered Sealed Held-Out Benchmark" to **"Exploratory Source-Disjoint Pilot Study"**.
2. Preserve all raw numerical results (TP=2, FP=16, FN=0, TN=0 for baselines) as genuine historical pilot measurements.
3. Prohibit claims that Phase 4D-C constitutes confirmatory proof of out-of-distribution generalization.
