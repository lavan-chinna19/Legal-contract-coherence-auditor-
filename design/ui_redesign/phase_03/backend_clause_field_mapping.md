# Backend Clause Field Mapping & Authoritative Data Alignment
**LexAudit Phase 3 UI Redesign Program**

## 1. Schema Authority & Ingestion Contract
The FastAPI backend produces analysis outputs structured by `UnifiedAuditReportModel` (`src/api/schema.py`). Every per-clause value displayed in the Phase 3 `FindingsInspector` maps directly to authoritative backend fields without synthetic interpolation or mock defaults.

---

## 2. Field-Level Specification & DOM Binding

| Backend Schema Path (`UnifiedAuditReportModel`) | Frontend Prop (`EnrichedClause`) | UI Component & Selector | Display Transformation & Formatting |
|---|---|---|---|
| `scoring_result.clauses[i].clause_id` | `clause.clause_id` | `ClauseCard[data-clause-id]`, `FindingsInspector` ID pill | Raw string (`doc_xxxxxxxx_i`), used as React key and authoritative selection anchor. |
| `scoring_result.clauses[i].sequence_idx` | `clause.sequence_idx` | `ClauseCard` header (`§ {idx}`), `ClauseNavigator` | Zero-indexed integer formatted as section number (`§ 0`, `§ 1`, etc.). |
| `scoring_result.clauses[i].combined_score` | `clause.combined_score` | `ScoreEvidencePanel .inspector-combined-score` | `value.toFixed(3)` with severity-based coloring (danger for HIGH, warning for MEDIUM). |
| `scoring_result.clauses[i].severity` | `clause.severity` | `ClauseCard <Badge>`, `FindingsInspector <Badge>` | Non-color text badges: `[!] HIGH`, `[^] MEDIUM`, `[~] LOW`, `[✓] CLEAN`. |
| `scoring_result.clauses[i].channel_a_score` | `clause.channel_a_score` | `ScoreEvidencePanel .inspector-cha-score` | `value.toFixed(3)` displaying normalized semantic divergence. |
| `scoring_result.clauses[i].channel_b_score` | `clause.channel_b_score` | `ScoreEvidencePanel .inspector-chb-score` | `value.toFixed(3)` displaying normalized sequence transition divergence. |
| `scoring_result.clauses[i].cross_channel_agreement` | `clause.cross_channel_agreement` | `ScoreEvidencePanel .inspector-agreement-score` | `(value * 100).toFixed(0) + "%"`. |
| `scoring_result.clauses[i].channel_a_evidence.nearest_centroid_label` | `clause.channel_a_evidence.nearest_centroid_label` | `ScoreEvidencePanel` Nearest Cluster | String cluster label (`type_89`, `type_20`) or `"Not available"`. |
| `scoring_result.clauses[i].channel_a_evidence.centroid_distance` | `clause.channel_a_evidence.centroid_distance` | `ScoreEvidencePanel .metric-cha-dist` | `value.toFixed(3)` displaying Euclidean/cosine distance in Legal-BERT embedding space. |
| `scoring_result.clauses[i].channel_a_evidence.is_ood` | `clause.channel_a_evidence.is_ood` | `ScoreEvidencePanel` Distribution Status | Boolean tagged as `"Out-of-Distribution (OOD)"` or `"In-Distribution"`. |
| `scoring_result.clauses[i].channel_b_evidence.incoming_anomaly` | `clause.channel_b_evidence.incoming_anomaly` | `ScoreEvidencePanel .metric-chb-incoming` | `value.toFixed(3)` if non-null, or `"Boundary (None)"` for document start. |
| `scoring_result.clauses[i].channel_b_evidence.outgoing_anomaly` | `clause.channel_b_evidence.outgoing_anomaly` | `ScoreEvidencePanel` Outgoing Anomaly | `value.toFixed(3)` if non-null, or `"Boundary (None)"` for document end. |
| `scoring_result.clauses[i].confidence_interval` | `clause.confidence_interval` | `ScoreEvidencePanel` Confidence Interval | `[lower.toFixed(2), upper.toFixed(2)]` representing conformal error bounds. |
| `scoring_result.clauses[i].calibration_source` | `clause.calibration_source` | `ScoreEvidencePanel` Calibration Source | Direct metadata string (`"synthetic_shuffle_only"`, `"uncalibrated_baseline"`). |
| `scoring_result.clauses[i].agreement_type` | `clause.agreement_type` | `ScoreEvidencePanel` Agreement Type | Classification string (`"CONCORDANT"`, `"CHANNEL_B_DOMINANT"`, `"DISCORDANT"`). |
| `scoring_result.clauses[i].severity_justification` | `clause.severity_justification` | `ScoreEvidencePanel` Severity Justification | Authentic NLP pipeline explanation text. |
| `rule_flags[j]` (where `clause_id == selectedClause.clause_id`) | `associated_rules` | `RuleFindingsPanel` Clause Violations | Displays `rule_type`, severity, reason, and text evidence. |
| `rule_flags[j]` (where `clause_id` is null or missing) | `documentRules` | `RuleFindingsPanel` Document-Level | Rendered in dedicated "Document-Level Rule Findings" card to prevent clause mismatch. |

---

## 3. Mandatory Non-Distortion Rules
1. **Document Mean Isolation**: The document mean score (`scoring_result.mean_combined_score`) is kept in top-level KPI cards and never substituted for per-clause anomaly scores.
2. **Metric Scales**: Centroid distance is explicitly labeled as distance (not probability). Markov transition anomaly is labeled as transition negative log-likelihood (not certainty).
3. **Null-Safety**: Boundary clauses (§ 0 and § N-1) safely display `"Boundary (None)"` when transition values are `null`, avoiding crashes or fabricated values.
