# Five-Minute Faculty Demonstration Script — Prompt 24

**Target Duration:** 5 minutes  
**Format:** Live Screen Share & Walkthrough  
**Objective:** Demonstrate core workflow, dual-channel scoring concept, explainability (XAI), and reviewer feedback loop to faculty evaluators.

---

## Timeline & Talking Points

### Minute 0:00 – 1:00 | Introduction & Privacy Enforcement
1. **Screen:** Display `http://localhost:3000` in Google Chrome.
2. **Talking Points:**
   - "Good morning, professors. Today I am demonstrating the **Legal Contract Coherence Auditor**, an academic NLP research prototype exploring dual-channel coherence analysis and explainability in legal agreements."
   - "Notice the browser tab title and prominent header disclaimer: *'Research Prototype — Not Legal Advice'*. We strictly scope this system as a decision-support audit tool."
   - "Before any contract text can be transmitted, our system enforces privacy. Watch what happens if I click *'Run Coherence Audit'* without acknowledging the privacy terms: the interface disables the action and prompts the operator to review data retention policies."
   - Check the **'I understand and acknowledge the privacy policy'** checkbox.

### Minute 1:00 – 2:00 | Contract Submission & Asynchronous Pipeline
1. **Screen:** Click *'Run Coherence Audit'*.
2. **Talking Points:**
   - "We submit a synthetic 5-clause commercial agreement (`audit/prompt_23/evidence/fixtures/valid_multiclause.txt`) to our FastAPI backend (`POST /v1/upload` and `POST /v1/analyze`)."
   - "The backend assigns an asynchronous job ID and polls via `GET /v1/jobs/{job_id}`. In just 3 seconds, the analysis completes."
   - "Our dual-channel pipeline has executed:
     - **Channel A (Semantic Out-of-Distribution):** Uses Legal-BERT (`nlpaueb/legal-bert-base-uncased`) to measure semantic distance against reference clause centroids from the LEDGAR corpus.
     - **Channel B (Discourse Transition):** Evaluates sequential coherence probabilities between adjacent clauses."

### Minute 2:00 – 3:15 | Audit Results & Deterministic Rules
1. **Screen:** Review the **KPI Summary Cards** and **Audit Results Table**.
2. **Talking Points:**
   - "Here are the top-level findings: 5 clauses parsed, 2 anomalous clauses identified, with a mean combined anomaly score of 0.341."
   - *"Note on Sample Values:* These metrics (5 clauses, 2 anomalies, 2 high-severity, 0 rule violations, 0.341 score) are observed with the verified demonstration fixture (`valid_multiclause.txt`, SHA256: `55558d95947bb2050782035de4f7a9f938d29c5b3d0b8e53014cf22c8c085825`). They are sample-specific empirical results, not hardcoded constants or universal outputs for arbitrary contracts."
   - "We also apply deterministic heuristic checkers for cross-reference dangling pointers and chronological date inversions. In this clean sample, 0 rule violations occurred."
   - "Review the sequence list: Clause 1 (Term and Duration) and Clause 5 (Dispute Resolution) exhibit elevated anomaly scores corresponding to document boundary transitions."

### Minute 3:15 – 4:15 | Explainability (XAI)
1. **Screen:** Click on the **'Explainability (XAI)'** tab.
2. **Talking Points:**
   - "A critical challenge in legal NLP is black-box decision making. Our system implements token-level Integrated Gradients."
   - "Look at the 26 token attribution badges rendered for Clause 1. Tokens shaded in green, like *'Term'*, *'commences'*, and *'terminates'*, influenced the model's feature projections most strongly."
   - "Alongside token attribution, our Channel B sensitivity analysis shows how perturbing neighboring clauses alters the transition score delta."
   - "We emphasize to users that these attributions reflect model-internal activations, not definitive statutory legal reasoning."

### Minute 4:15 – 5:00 | Reviewer Feedback & Conclusion
1. **Screen:** Click on the **'Reviewer Feedback'** tab.
2. **Talking Points:**
   - "Finally, legal audit systems require human-in-the-loop oversight. In the Feedback tab, a legal reviewer can record their verdict using our supported API options: `CONFIRM_ANOMALY` (true positive anomaly) or `REJECT_ANOMALY` (false alarm)."
   - "I select Clause 1, select `CONFIRM_ANOMALY`, leave provenance as `REAL`, and click *'Submit Feedback to API'*."
   - "The feedback is recorded with cryptographic provenance in our backend database (`data/processed/feedback.sqlite`). We emphasize that recording feedback does not automatically trigger live model retraining; rather, it creates an auditable calibration dataset for offline active learning."
   - "To conclude: our prototype demonstrates a reproducible, end-to-end pipeline with hardened security, full test coverage, and transparent XAI. Thank you, and I welcome your questions."
