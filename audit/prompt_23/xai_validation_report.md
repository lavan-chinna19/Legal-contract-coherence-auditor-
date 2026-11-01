# Explainability (XAI) Validation Report (Prompt 23)

**Phase:** Prompt 23 — Phase H  
**Execution Date:** 2026-10-10  
**Target:** XAI Endpoints (`/v1/xai/attribution` & `/v1/xai/sensitivity`)  

---

## 1. Overview & Verification Scope

The Explainability layer provides dual-channel model interpretability:
1. **Channel A:** Token-level Integrated Gradients (`IntegratedGradientsExplainer`) against the Legal-BERT embedding representation.
2. **Channel B:** Neighborhood context perturbation sensitivity (`ChannelBSensitivityAnalyzer`) evaluating the directional delta of coherence scores when neighboring clauses are masked.

---

## 2. Integrated Gradients Attribution Verification

### Test Execution
- **Request:** `GET /v1/xai/attribution?doc_id=doc_e949c13e&clause_id=doc_e949c13e_0`
- **Model Version:** `nlpaueb/legal-bert-base-uncased`
- **Tokens Extracted:** 26 tokens (`['[CLS]', '1', '.', 'term', 'and', 'duration', '.', 'this', 'agreement', 'commence', '##s', ...]`)
- **Attribution Weights:** Finite real-valued gradients computed across 5 baseline interpolation steps.
  - Sample values: `[-0.0008, -0.0175, -0.0182, -0.0116, -0.0086]`
  - Maximum attribution token: `'.'` (-0.0182) and `'term'` (-0.0116)
- **Claim Scope Rigor:**
  - `what_this_shows`: "Integrated Gradients indicates which input tokens/features contributed most to the Channel A semantic distance anomaly score."
  - `what_this_does_not_show`: "It does not prove that those tokens are legally significant, causally responsible for a contract defect, or that the model's prediction is correct."
- **Verification Verdict:** **PASS** (100% computed, no synthetic or placeholder tokens).

---

## 3. Channel B Perturbation Sensitivity Verification

### Test Execution
- **Request:** `GET /v1/xai/sensitivity?doc_id=doc_e949c13e&clause_id=doc_e949c13e_0`
- **Model Version:** `fine_tuned_coherence_head (dim=768)`
- **Neighbor Clause ID:** `doc_e949c13e_1` (position: `'next'`)
- **Perturbation Method:** `'mask_neighbor_text'`
- **Computed Scores:**
  - `original_score`: `0.6854`
  - `perturbed_score`: `0.7606`
  - `score_delta`: `+0.0752`
- **Claim Scope Rigor:**
  - `what_this_shows`: "This perturbation measures how sensitive the model score is to this neighboring content under the tested intervention."
  - `what_this_does_not_show`: "It does not establish that the neighbor is legally responsible for the anomaly or that the observed relationship is causal."
- **Verification Verdict:** **PASS** (Actual neural head forward pass under masked input context).

---

## 4. Negative and Security Boundaries

1. **Non-Existent Clause ID:**
   - `GET /v1/xai/attribution?doc_id=doc_e949c13e&clause_id=clause_invalid_999`
   - Returns: `404 Not Found` with detail `"Clause not found."`
2. **Cross-Client Ownership Isolation:**
   - Client B querying Client A document returns `404 Not Found`.
3. **Unauthenticated Access:**
   - Missing `X-API-Key` returns `401 Unauthorized`.

---

## 5. Conclusion
Both XAI calculation pipelines are fully integrated, mathematically sound, bounded by explicit claim-scope disclaimers, and enforce strict client ownership.
