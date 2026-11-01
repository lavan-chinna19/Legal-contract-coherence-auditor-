# LexAudit Phase 4A — Analytics Data Contract & Field Mapping Specification

## 1. Specification Baseline
- **Authoritative Endpoint**: `GET /v1/jobs/{job_id}/results`
- **Response Schema Model**: `UnifiedAuditReportModel` (`src/api/schema.py`)
- **Transport Security**: `X-API-Key` required, responses served over HTTPS/HTTP session.
- **Client Processing Policy**: Zero client-side persistent caching; strictly React memory state.

---

## 2. Document-Level Field Contract

| Backend Field | Data Type | Value Domain | UI Component | Visual Representation | Scientific Interpretation | Missing / Null Handling |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `doc_id` | `string` | Regex `^doc_[a-f0-9]+$` | `AnalyticsSummary` | Monospace badge | Ephemeral document cryptographic token. | Render `"N/A"` |
| `total_clauses` | `integer` | $[1, \infty)$ | `AnalyticsSummary`, `SeverityDistribution` | Primary KPI value | Authoritative sequential segments extracted by segmentation factory. | Defaults to `0` |
| `ml_anomaly_count` | `integer` | $[0, \text{total\_clauses}]$ | `AnalyticsSummary` | Medium severity colored KPI | Total clauses where $S_i \ge \tau$ (calibrated decision threshold). | Defaults to `0` |
| `high_severity_count` | `integer` | $[0, \text{total\_clauses}]$ | `AnalyticsSummary`, `SeverityDistribution` | High severity colored KPI | Clauses where $S_i \ge 0.65$ (critical structural anomaly). | Defaults to `0` |
| `medium_severity_count`| `integer` | $[0, \text{total\_clauses}]$ | `SeverityDistribution` | Medium severity colored KPI | Clauses where $0.40 \le S_i < 0.65$. | Defaults to `0` |
| `low_severity_count` | `integer` | $[0, \text{total\_clauses}]$ | `SeverityDistribution` | Low severity warning KPI | Mild irregularities or edge warnings. | Defaults to `0` |
| `rule_violation_count` | `integer` | $[0, \infty)$ | `AnalyticsSummary`, `RuleFindingsSummary` | Warning colored KPI | Deterministic heuristic violations (broken cross-references, invalid dates). | Defaults to `0` |
| `total_flags` | `integer` | $[0, \infty)$ | AppShell Header | Flag count pill | Aggregate count: $\text{ml\_anomaly\_count} + \text{rule\_violation\_count}$. | Fallback to sum |
| `scoring_result.mean_combined_score` | `float` | $[0.000, 1.000]$ | `AnalyticsSummary` | Accent colored KPI | Document-wide average dual-channel score: $\frac{1}{N} \sum_{i=1}^N S_i$. | Render `0.000` |
| `scoring_result.max_combined_score` | `float` | $[0.000, 1.000]$ | `AnalyticsSummary` | Subtitle annotation | Maximum clause combined score in document. | Render `0.000` |
| `scoring_result.calibration_source` | `string` | Categorical string | `AnalyticsSummary`, `CalibrationTransparency`| Metadata pill | Statistical origin of decision thresholds (`synthetic_shuffle_ledgar`). | Render `"unknown"` |

---

## 3. Clause-Level Field Contract (`clauses[]`)

| Backend Field | Data Type | Value Domain | UI Component | Visual Representation | Scientific Interpretation | Missing / Null Handling |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `clause_id` | `string` | Unique identifier | `ClauseScoreDistribution`, Inspector | Data attribute & label | Authoritative segmentation identity token. | Required field |
| `sequence_idx` | `integer` | $[0, N-1]$ | Timeline & badges | $\S$ prefix label | Monotonic sequence position in original contract. | Use array index |
| `combined_score` | `float` | $[0.000, 1.000]$ | `ClauseScoreDistribution` | Bar height (4% to 100%) | Calibrated weighted score: $w_A S_A + w_B S_B$ ($w_A=0.5, w_B=0.5$). | Clamped to 0.0 |
| `channel_a_score` | `float` | $[0.000, 1.000]$ | `ChannelEvidenceComparison`| Value metric | Normalized centroid OOD distance score. | Render `0.000` |
| `channel_b_score` | `float` | $[0.000, 1.000]$ | `ChannelEvidenceComparison`| Value metric | Normalized discourse transition anomaly: $1.0 - P(\text{transition})$. | Render `0.000` |
| `severity` | `enum` | `HIGH`, `MEDIUM`, `LOW`, `CLEAN` | `SeverityDistribution`, Bar Colors | Severity color tokens | Discrete risk tier from threshold comparison. | Defaults to `CLEAN` |
| `channel_a_evidence.centroid_distance` | `float` | $[0.000, 2.000]$ | `ChannelEvidenceComparison`| Numeric readout ($d$) | Raw cosine distance to nearest LEDGAR centroid in $\mathbb{R}^{768}$. **NOT a probability.** | Render `"N/A"` |
| `channel_a_evidence.nearest_centroid_label` | `string` | LEDGAR category (66 classes) | `ChannelEvidenceComparison`| Cluster name text | Nearest canonical legal topic category. | Render `"Unknown"` |
| `channel_a_evidence.is_ood` | `boolean` | `true`, `false` | `ChannelEvidenceComparison`| Status badge | Out-of-distribution flag based on cluster distance radius. | Defaults to `false` |
| `channel_b_evidence.incoming_prob` | `float` | $[0.000, 1.000]$ | `ChannelEvidenceComparison`| Flow rate readout ($P_{in}$) | Model transition likelihood: $P(c_{i-1} \to c_i)$. | Render `"First Clause"` |
| `channel_b_evidence.outgoing_prob` | `float` | $[0.000, 1.000]$ | `ChannelEvidenceComparison`| Flow rate readout ($P_{out}$)| Model transition likelihood: $P(c_i \to c_{i+1})$. | Render `"Terminal Clause"`|
| `channel_b_evidence.incoming_anomaly` | `float` | $[0.000, 1.000]$ | `ChannelEvidenceComparison`| Metric readout | Discontinuity term: $1.0 - P_{in}$. | Render `"0.000"` |
| `channel_b_evidence.outgoing_anomaly` | `float` | $[0.000, 1.000]$ | `ChannelEvidenceComparison`| Metric readout | Discontinuity term: $1.0 - P_{out}$. | Render `"0.000"` |
| `confidence_interval` | `[float, float]` | $[0.000, 1.000]$ | `CalibrationTransparency` | $[ci_{lo}, ci_{hi}]$ range | Conformal prediction bounds at nominal 90% coverage level. | Render `"N/A"` |
| `interval_width` | `float` | $[0.000, 1.000]$ | `CalibrationTransparency` | Metric readout | Predictive interval width: $ci_{hi} - ci_{lo}$. | Computed dynamically |

---

## 4. Deterministic Rule Flags Contract (`rule_flags[]`)

| Backend Field | Data Type | UI Component | Visual Representation | Scientific Interpretation |
| :--- | :--- | :--- | :--- | :--- |
| `flag_id` | `string` | `RuleFindingsSummary` | Unique React key | Rule match identifier. |
| `flag_type` / `category` | `string` | `RuleFindingsSummary` | Category pill (`CROSS_REFERENCE`, `DATE_ORDER`) | Deterministic check classification. |
| `severity` | `enum` | `RuleFindingsSummary` | Severity badge (`HIGH`, `MEDIUM`) | Impact severity assigned by static rules. |
| `title` | `string` | `RuleFindingsSummary` | Section heading | Descriptive violation title. |
| `description` | `string` | `RuleFindingsSummary` | Paragraph text | Explanation of broken reference or inverted chronology. |
| `clause_id` | `string` | `RuleFindingsSummary` | Link button | Specific affected clause (synchronizes selection). |
| `evidence` | `object` | `RuleFindingsSummary` | Monospace code snippet | Raw matched syntactic evidence (e.g. `{"missing_section": "12.4"}`). |

---

## 5. Completeness Evidence Availability Check
- **Backend Schema Audit Result**: In `UnifiedAuditReportModel`, an optional `completeness_report` exists in `src/completeness/` but is currently **NOT returned** by default in `/v1/jobs/{job_id}/results` unless explicitly requested via separate completeness analysis pipelines.
- **UI Policy**: Completeness is explicitly documented as unpopulated in the standard job results payload. No fake completeness percentages or checklists are displayed in the Analytics workspace.
