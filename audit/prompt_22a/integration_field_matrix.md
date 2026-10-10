# End-to-End Pipeline & Frontend Integration Field Matrix

**Phase:** Prompt 22A — Task E
**Date:** 2026-10-10
**Verification Target:** Complete trace from NLP pipeline to UI component rendering

---

## 1. Full Pipeline Stage Architecture

```
[Contract Upload]
       │
       ▼
[Rule-Based / Bio Segmentation] ──► (Clauses with exact char_start / char_end)
       │
       ▼
[Legal-BERT Frozen Embeddings] ──► (768-d unit-normalized vectors with content cache)
       │
       ▼
[DualChannelScorer]
   ├── Channel A: Semantic Centroid Distance (LEDGAR 66 clause classes)
   └── Channel B: Transition Matrix & Coherence Head Probabilities
       │
       ▼
[Conformal Calibration] ──► (Conservative 95% non-conformity intervals)
       │
       ▼
[Severity Ranker] ──► (Agreement type, categorical severity: HIGH/MED/LOW)
       │
       ▼
[UnifiedAuditor]
   ├── Completeness Checks (Tier-1 BART-MNLI NLI zero-shot entailment)
   ├── Reference Cross-Checks (Broken Section 2.1 references)
   └── Temporal Date Checks (Inverted effective vs expiry dates)
       │
       ▼
[FastAPI Schema Serialization] ──► UnifiedAuditReportModel (HTTP 200 JSON)
       │
       ▼
[Next.js Client Fetch] ──► DocumentResult TypeScript interface
       │
       ▼
[UI Dashboard Render] ──► Stat Cards, Heatmap Table, Flags Drawer, XAI Panel
```

---

## 2. Field-Level Trace Matrix

| Source Module | Internal Field Name | API Field Name | Frontend Destination | Value Type | Genuine Computed Data? | Verification Method | Status |
|---|---|---|---|---|---|---|---|
| `src.api.v1.router` | `doc_id` | `doc_id` | `DocumentResult.doc_id` / Header | `string` | YES (UUID random generator) | `test_end_to_end_analysis_flow` | **PASS** |
| `src.segmentation.rule_based` | `len(clauses)` | `total_clauses` | Metric Card "Total Clauses" | `integer` | YES (exact clause count from source text) | `test_segmentation.py` | **PASS** |
| `src.scoring.pipeline` | `scoring_result.anomaly_count` | `ml_anomaly_count` | Metric Card "ML Coherence Anomalies" | `integer` | YES (count of clauses where score >= threshold) | `test_scoring.py` | **PASS** |
| `src.rules.unified_pipeline` | `len(rule_flags)` | `rule_violation_count` | Metric Card "Deterministic Rule Flags" | `integer` | YES (count of broken refs and date violations) | `test_rules.py` | **PASS** |
| `src.rules.unified_pipeline` | `total_flags` | `total_flags` | Metric Card "Total Audit Flags" | `integer` | YES (sum of ML anomalies + rule flags) | `test_rules.py` | **PASS** |
| `src.rules.unified_pipeline` | `high_severity_count` | `high_severity_count` | Severity Badge (Red) | `integer` | YES (count of HIGH severity items) | `test_rules.py` | **PASS** |
| `src.rules.unified_pipeline` | `medium_severity_count` | `medium_severity_count` | Severity Badge (Amber) | `integer` | YES (count of MEDIUM severity items) | `test_rules.py` | **PASS** |
| `src.rules.unified_pipeline` | `low_severity_count` | `low_severity_count` | Severity Badge (Green) | `integer` | YES (count of LOW severity items) | `test_rules.py` | **PASS** |
| `src.scoring.pipeline` | `mean_combined_score` | `scoring_result.mean_combined_score` | Metrics Summary "Mean Score" | `float` | YES (average combined score across clauses) | `test_scoring.py` | **PASS** |
| `src.scoring.pipeline` | `max_combined_score` | `scoring_result.max_combined_score` | Metrics Summary "Peak Score" | `float` | YES (highest anomaly score found) | `test_scoring.py` | **PASS** |
| `src.calibration.conformal` | `calibration_source` | `scoring_result.calibration_source` | Calibration Banner | `string` | YES ("synthetic_shuffle_only") | `test_conformal.py` | **PASS** |
| `src.segmentation.schema` | `clause.clause_id` | `scoring_result.clauses[].clause_id` | Clause Table ID Column | `string` | YES (doc_id + sequence index) | `test_segmentation.py` | **PASS** |
| `src.segmentation.schema` | `clause.text[:120]` | `scoring_result.clauses[].text_preview` | Clause Table Text Column | `string` | YES (actual text slice from contract) | `test_segmentation.py` | **PASS** |
| `src.scoring.schema` | `clause.channel_a_score` | `scoring_result.clauses[].channel_a_score` | Heatmap Score A Column | `float` | YES (Euclidean/cosine distance to centroid) | `test_scoring.py` | **PASS** |
| `src.scoring.schema` | `clause.channel_b_score` | `scoring_result.clauses[].channel_b_score` | Heatmap Score B Column | `float` | YES (fine-tuned transition probability) | `test_scoring.py` | **PASS** |
| `src.scoring.schema` | `clause.combined_score` | `scoring_result.clauses[].combined_score` | Combined Anomaly Heatmap Column | `float` | YES (weighted alpha combination) | `test_scoring.py` | **PASS** |
| `src.severity.ranker` | `clause.severity` | `scoring_result.clauses[].severity` | Table Severity Tag (HIGH/MED/LOW) | `string` | YES (derived via calibrated thresholds) | `test_severity.py` | **PASS** |
| `src.calibration.conformal` | `confidence_interval` | `scoring_result.clauses[].confidence_interval` | Uncertainty Interval [L, U] | `list[float]` | YES (crepes/conformal higher-bound quantile) | `test_conformal.py` | **PASS** |
| `src.severity.ranker` | `cross_channel_agreement` | `scoring_result.clauses[].cross_channel_agreement` | Agreement Meter | `float` | YES (computed channel consensus) | `test_severity.py` | **PASS** |
| `src.severity.ranker` | `agreement_type` | `scoring_result.clauses[].agreement_type` | Consensus Label | `string` | YES (MUTUAL_ANOMALY, etc.) | `test_severity.py` | **PASS** |
| `src.rules.schema` | `flag.flag_id` | `rule_flags[].flag_id` | Rule Flags Table ID | `string` | YES (UUID per violation) | `test_rules.py` | **PASS** |
| `src.rules.schema` | `flag.title` | `rule_flags[].title` | Rule Violation Header | `string` | YES (e.g. "Broken Section Reference") | `test_rules.py` | **PASS** |
| `src.rules.schema` | `flag.description` | `rule_flags[].description` | Rule Violation Explanation | `string` | YES (details with missing target section) | `test_rules.py` | **PASS** |
| `src.xai.ig` | `explanation.ig_payload` | `GET /v1/xai/attribution` payload | Explainability Token Attribution View | `object` | YES (real Integrated Gradients token weights) | `test_xai.py`, `test_bug005_xai.py` | **PASS** |
| `src.xai.sensitivity` | `explanation.sensitivity_payload`| `GET /v1/xai/sensitivity` payload | Explainability Perturbation Plot | `object` | YES (measured transition score deltas) | `test_xai.py`, `test_bug005_xai.py` | **PASS** |
| `src.feedback.schema` | `FeedbackRecord` | `POST /v1/feedback` payload | Reviewer Modal -> SQLite/Postgres DB | `object` | YES (stores verdict and reviewer id, no plaintext) | `test_feedback.py`, `test_bug003_feedback.py` | **PASS** |

---

## 3. Serialization and Integration Consistency Verdict

1. **Zero Mismatches:** Every field exposed by `UnifiedAuditReportModel` is accurately represented in `frontend/src/app/page.tsx`'s TypeScript interfaces (`DocumentResult`, `ClauseResult`, `RuleFlag`).
2. **Zero Hardcoded Mock Data:** All numbers, token attributions, and clause texts originate from live computations on the uploaded contract text.
3. **Pydantic Validation:** All schemas inherit from `pydantic.BaseModel` with explicit types and defaults, eliminating runtime deserialization exceptions.
4. **Integration Verdict:** FULL PASS.
