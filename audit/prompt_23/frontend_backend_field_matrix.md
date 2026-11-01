# Frontend to Backend Field Integration Matrix (Prompt 23)

**Phase:** Prompt 23 — Phase E & Task Trace  
**Date:** 2026-10-10  
**Repository:** Legal Contract Coherence Auditor  

---

## Field Traceability Matrix

| NLP Module / Source | Internal Field | API Response Key | Frontend TS Property | UI Component / Rendering | Data Type | Genuine Data Verified | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `src/segmentation/rule_based.py` | `clause_id` | `clause_id` | `clause.clause_id` | Clause table & dropdown | `string` | YES (`doc_e949c13e_0`) | **PASS** |
| `src/segmentation/rule_based.py` | `text` | `text_preview` | `clause.text_preview` | Clause preview text snippet | `string` | YES | **PASS** |
| `src/segmentation/rule_based.py` | `sequence_idx` | `sequence_idx` | `clause.sequence_idx` | Clause sequence badge | `number` | YES (0..4) | **PASS** |
| `src/scoring/channel_a.py` | `distance` | `channel_a_score` | `clause.channel_a_score` | Channel A score display | `number` | YES (float 0.0-1.0) | **PASS** |
| `src/scoring/channel_a.py` | `nearest_centroid` | `nearest_centroid_label`| `channel_a_evidence.nearest_centroid_label` | Cluster centroid pill | `string` | YES | **PASS** |
| `src/scoring/channel_a.py` | `is_ood` | `is_ood` | `channel_a_evidence.is_ood` | OOD indicator | `boolean` | YES | **PASS** |
| `src/scoring/channel_b.py` | `anomaly_prob` | `channel_b_score` | `clause.channel_b_score` | Channel B score display | `number` | YES (float 0.0-1.0) | **PASS** |
| `src/scoring/pipeline.py` | `combined_score` | `combined_score` | `clause.combined_score` | Combined anomaly score | `number` | YES (weighted sum) | **PASS** |
| `src/scoring/pipeline.py` | `is_anomaly` | `is_anomaly` | `clause.is_anomaly` | Flag badge (Anomaly vs Normal)| `boolean` | YES | **PASS** |
| `src/scoring/severity.py` | `severity` | `severity` | `clause.severity` | Severity badge (HIGH/MED/LOW) | `string` | YES | **PASS** |
| `src/scoring/severity.py` | `agreement_type` | `agreement_type` | `clause.agreement_type` | Diagnostic tooltip | `string` | YES | **PASS** |
| `src/calibration/conformal.py`| `interval` | `confidence_interval` | `clause.confidence_interval` | 95% Confidence interval [a,b] | `[number, number]`| YES (e.g. [0.0, 1.0]) | **PASS** |
| `src/calibration/conformal.py`| `source` | `calibration_source` | `clause.calibration_source` | Calibration provenance note | `string` | YES | **PASS** |
| `src/rules/unified_pipeline.py`| `total_clauses` | `total_clauses` | `documentResult.total_clauses` | Total Clauses metric card | `number` | YES | **PASS** |
| `src/rules/unified_pipeline.py`| `ml_anomaly_count` | `ml_anomaly_count` | `documentResult.ml_anomaly_count` | ML Anomalies metric card | `number` | YES | **PASS** |
| `src/rules/unified_pipeline.py`| `rule_violation_count` | `rule_violation_count`| `documentResult.rule_violation_count` | Rule Violations card | `number` | YES | **PASS** |
| `src/rules/unified_pipeline.py`| `total_flags` | `total_flags` | `documentResult.total_flags` | Total Flags metric card | `number` | YES | **PASS** |
| `src/rules/unified_pipeline.py`| `high_count` | `high_severity_count` | `documentResult.high_severity_count` | High severity count pill | `number` | YES | **PASS** |
| `src/rules/unified_pipeline.py`| `med_count` | `medium_severity_count`| `documentResult.medium_severity_count`| Medium severity count pill | `number` | YES | **PASS** |
| `src/rules/unified_pipeline.py`| `low_count` | `low_severity_count` | `documentResult.low_severity_count` | Low severity count pill | `number` | YES | **PASS** |
| `src/rules/unified_pipeline.py`| `mean_score` | `mean_combined_score` | `scoring_result.mean_combined_score` | Mean Coherence Score | `number` | YES | **PASS** |
| `src/rules/unified_pipeline.py`| `max_score` | `max_combined_score` | `scoring_result.max_combined_score` | Max Coherence Score | `number` | YES | **PASS** |
| `src/rules/reference.py` | `flag_id` | `flag_id` | `rule_flag.flag_id` | Rule flag ID badge | `string` | YES | **PASS** |
| `src/rules/reference.py` | `title` | `title` | `rule_flag.title` | Rule flag title header | `string` | YES | **PASS** |
| `src/rules/reference.py` | `description` | `description` | `rule_flag.description` | Detailed flag explanation | `string` | YES | **PASS** |
| `src/rules/date.py` | `evidence` | `evidence` | `rule_flag.evidence` | Evidence metadata breakdown | `dict` | YES | **PASS** |
| `src/xai/ig.py` | `tokens` | `tokens` | `xaiData.ig_payload.tokens` | Token stream rendering | `string[]` | YES (26 tokens) | **PASS** |
| `src/xai/ig.py` | `attributions` | `attributions` | `xaiData.ig_payload.attributions` | Heatmap token color weight | `number[]` | YES (gradient values) | **PASS** |
| `src/xai/sensitivity.py` | `score_delta` | `score_delta` | `xaiData.sensitivity_payload.score_delta` | Sensitivity delta display | `number` | YES (e.g. +0.0752) | **PASS** |
| `src/feedback/schema.py` | `feedback_id` | `feedback_id` | `feedbackSuccess` | Alert banner ID string | `string` | YES (UUIDv4) | **PASS** |

---

## Trace Summary
- Total Fields Mapped: **30**
- Genuine Backend Computations: **30 / 30** (100%)
- Field Incompatibilities / Undefined Renders: **0**
- Field Alignment Verdict: **PASS**
