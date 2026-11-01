# Phase 4B — Track B XAI Backend Schema & Semantics Audit

**Project:** Legal Contract Coherence Auditor (LexAudit)  
**Phase:** 4B — Professional Explainability Workspace  
**Date:** 2026-10-14  
**Author:** Explainable AI Engineer & Principal NLP Research Engineer  
**Status:** PASS — VERIFIED & ALIGNED  

---

## 1. Integrated Gradients API Schema (`GET /v1/xai/attribution`)

### Backend Route & Model Binding
- **Endpoint:** `GET /v1/xai/attribution?doc_id={doc_id}&clause_id={clause_id}`
- **Implementation:** `src/xai/ig.py` via Captum `LayerIntegratedGradients` targeting the Legal-BERT embedding layer (`embeddings.word_embeddings`).
- **Response Schema (`ExplanationResult` in `src/xai/schema.py`):**
  ```json
  {
    "explanation_id": "string (UUID)",
    "doc_id": "string",
    "clause_id": "string",
    "explanation_type": "INTEGRATED_GRADIENTS",
    "model_version": "nlpaueb/legal-bert-base-uncased",
    "timestamp": "ISO-8601 UTC",
    "claim_scope": {
      "what_this_shows": "Relative token gradient attribution driving Legal-BERT embedding away from reference clusters.",
      "what_this_does_not_show": "Normative legal ambiguity or enforceability."
    },
    "ig_payload": {
      "tokens": ["string"],
      "attributions": ["float"],
      "target_score": "float",
      "baseline_score": "float"
    }
  }
  ```

### Attribution Sign Semantics
1. **Target Function:** The gradient objective explains the Channel A Out-of-Distribution distance metric $D(x) = 1.0 - \max_k \cos(x, c_k)$.
2. **Positive Attribution ($+a_i > 0$):** Tokens that push the clause embedding away from the nearest reference centroid, increasing the OOD anomaly score (Anomaly Drivers).
3. **Negative Attribution ($-a_i < 0$):** Tokens that pull the clause embedding closer to the canonical cluster, reducing the anomaly score (Coherence Anchors).
4. **Zero Attribution ($a_i \approx 0$):** Neutral or syntactic tokens having negligible influence on cluster distance.
5. **Array Alignment:** Length of `tokens` strictly equals length of `attributions` ($N = N$).

---

## 2. Neighbor Sensitivity API Schema (`GET /v1/xai/sensitivity`)

### Backend Route & Model Binding
- **Endpoint:** `GET /v1/xai/sensitivity?doc_id={doc_id}&clause_id={clause_id}`
- **Implementation:** `src/xai/sensitivity.py` using Channel B sequential scoring under neighbor masking interventions.
- **Response Schema:**
  ```json
  {
    "explanation_id": "string (UUID)",
    "doc_id": "string",
    "clause_id": "string",
    "explanation_type": "SENSITIVITY",
    "model_version": "CoherenceScorerHead",
    "timestamp": "ISO-8601 UTC",
    "claim_scope": {
      "what_this_shows": "Measures how sensitive the model score is to neighboring content under tested intervention.",
      "what_this_does_not_show": "Does not establish that the neighbor is legally responsible for the anomaly."
    },
    "sensitivity_payload": {
      "neighbor_clause_id": "string",
      "neighbor_position": "prev | next | none",
      "original_score": "float",
      "perturbed_score": "float",
      "score_delta": "float",
      "perturbation_method": "mask_neighbor_text"
    }
  }
  ```

### Sensitivity Semantics
- **Baseline Anomaly Score ($S_B$):** The Channel B anomaly score ($1.0 - P$) with intact document sequence.
- **Perturbed Anomaly Score ($S'_B$):** The anomaly score when the immediate neighboring clause is masked (`[MASK]`).
- **Score Delta ($|\Delta| = |S_B - S'_B|$):** Measures sequential dependency. Delta $> 0.05$ indicates strong contextual coupling.
