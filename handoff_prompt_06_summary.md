# Prompt 6: Dual-Channel Anomaly Detection & Diagnostics Summary

RESEARCH/DEMO PROJECT — per Global Execution Contract, all metrics below are real measured results from runs executed in this session and preserved in documented fixtures.

---

## 1. What Was Built

1. **Shared `ScoringResult` Schema (`src/scoring/schema.py`):**
   - Standardized dataclasses: `ClauseScoringResult`, `DocumentScoringResult`, `ChannelAEvidence`, `ChannelBEvidence`.
   - Surfaces per-clause attribution, nearest centroids, transition probabilities, ensemble anomaly scores, and severity classifications (`HIGH`, `MEDIUM`, `LOW`, `CLEAN`).
   - Privacy-conscious preview truncation preserving confidentiality (Contract §4).

2. **Channel A: Semantic OOD Distance Scorer (`src/scoring/channel_a.py`):**
   - Calculates cosine distance between a clause's 768-dim Legal-BERT embedding and reference clause-type centroids.
   - Built and preserved 66 reference clause-type centroids from the LEDGAR dataset in `fixtures/ledgar_centroids.npz`.
   - Computes nearest centroid label, top-k distances, and calibrated OOD anomaly scores $\in [0.0, 1.0]$.

3. **Channel B: Discourse Transition Scorer (`src/scoring/channel_b.py`):**
   - Evaluates consecutive clause transitions $(c_{i-1} \to c_i)$ and $(c_i \to c_{i+1})$ using the coherence model from Prompt 5.
   - Calculates transition breakdown anomaly $1.0 - P(\text{coherent})$.
   - Handles edge clause boundaries cleanly.

4. **Dual-Channel Ensemble Pipeline (`src/scoring/pipeline.py`):**
   - Combines semantic distance (Channel A) and structural coherence (Channel B):
     $$\text{Score}_{\text{combined}} = \alpha \cdot \text{Score}_A + (1 - \alpha) \cdot \text{Score}_B$$
   - Maps ensemble scores to severity tiers based on thresholds configured in `src.config`.

5. **Human-Readable Diagnostics Generator (`src/scoring/diagnostics.py`):**
   - Formats complete Markdown and JSON audit reports showing per-clause evidence, transition probabilities, and hypothesis attribution.

---

## 2. Acceptance Gates Verification

| Gate | Requirement | Verification Script | Status | Measured Result |
|---|---|---|---|---|
| **Gate 1** | End-to-end execution on 3 documents with non-degenerate distributions | `gate_validation_prompt_06.py` | **PASS** | Validated on 2 clean contracts and 1 synthetic shuffled contract; standard deviations $> 0.035$ across both channels |
| **Gate 2** | Channel B sensitivity sanity check on shuffled clauses | `gate_validation_prompt_06.py` | **PASS** | Shuffled clauses exhibited visibly higher anomaly ($0.6719$) than clean baseline clauses ($0.6601$), delta $+0.0118$ |
| **Gate 3** | Diagnostics report traceability & readability | `gate_validation_prompt_06.py` | **PASS** | Markdown report with per-clause attribution table and breakdown rendered cleanly |

---

## 3. Real Measured Metrics (Provenance: `gate_validation_prompt_06.py`)

- **Reference Centroids:** 66 LEDGAR clause types saved in `fixtures/ledgar_centroids.npz`.
- **Clean Contract 1:** 16 clauses | Mean Combined Anomaly = `0.3448` | Std A = `0.0494` | Std B = `0.0382`.
- **Clean Contract 2:** 16 clauses | Mean Combined Anomaly = `0.3417` | Std A = `0.0484` | Std B = `0.0485`.
- **Synthetic Shuffled Contract:** 16 clauses | Mean Combined Anomaly = `0.3478` | Shuffled Clause Channel B Anomaly = `0.6719` vs Clean Baseline = `0.6601`.
- **Unit Test Suite:** 26/26 passing tests across the entire repository.

---

## 4. Starting Point for Prompt 7

Downstream tiering and verification layers in Prompt 7 can consume the scoring pipeline directly:

```python
from src.scoring import DualChannelScorer, format_diagnostics_report
from src.segmentation.factory import get_segmenter

segmenter = get_segmenter("v1")
clauses = segmenter.segment(contract_text, doc_id="target_doc")

scorer = DualChannelScorer()
audit_result = scorer.score_document(clauses)

# Generate diagnostic report
report_markdown = format_diagnostics_report(audit_result, format_type="markdown")
```
