# Pre-Registered Experimental Protocol (Phase 4D-B)

**Audit Program**: LexAudit Research Extension — Phase 4D-B  
**Document ID**: `PHASE_04DB_PREREGISTERED_PROTOCOL`  
**Date**: October 22, 2026  
**Auditor**: Principal ML Research Auditor & Experimental Evaluation Architect  
**Pre-Registration Status**: **LOCKED BEFORE CANDIDATE MODEL EVALUATION ON HELD-OUT TEST DATA**  

---

## 1. Task Definitions & Clear Boundaries

To prevent task conflation, five distinct tasks are formally separated:

| Task Name | Input Representation | Model Output | Ground Truth Label Condition |
| :--- | :--- | :--- | :--- |
| **Task 1: Structural Anomaly Detection** (*Primary Target*) | Clause sequence $(c_1, \dots, c_n)$ | Binary decision $\hat{y} \in \{0, 1\}$ and continuous anomaly score $S_{\text{struct}} \in [0.0, 1.0]$ | An independently validated structural ordering or dependency defect exists in the document. |
| **Task 2: Clause-Position Recovery** (*Separately Evaluated*) | Displaced clause $c^*$ and candidate insertion slots $p \in \{0, \dots, n-1\}$ | Ranked list of positions $\text{Rank}(p)$ | Original pre-displacement index $p^*$. |
| **Task 3: Local Transition Compatibility** | Adjacent pair $(c_i, c_{i+1})$ | Local score $P(c_i \to c_{i+1})$ | Pairwise adjacency validity (binary). |
| **Task 4: Global Discourse Coherence** | Entire clause sequence $C$ | Global coherence index $J(C) \in [0, 1]$ | Overall discourse continuity. |
| **Task 5: Rule-Based Dependency Violation** | Clause text with citations / ISO dates | Deterministic flag / violation code | Unresolved symbol or temporal contradiction. |

**Critical Constraint**: Improvements in Task 2 (Clause Recovery) or Task 5 (Rule Checkers) must NOT be reported as Task 1 (Structural Anomaly Detection) improvements.

---

## 2. Pre-Registered Operational Definitions

### Positive Label Definition (`VERIFIED_STRUCTURAL_DEPENDENCY_VIOLATION`)
A document sequence is labeled as a **Positive ($y=1$)** structural anomaly if and only if:
1. It contains a verified functional sequencing violation (e.g. Preamble moved after Scope/covenants, Scope moved after signature blocks/exhibits, Payment terms moved into dispute resolution boilerplate), OR
2. It violates an explicit, independently stated chronological or procedural contractual prerequisite where order dictates operational dependency.

### Negative Label Definition (`VALID_ORDER`)
A document sequence is labeled as a **Negative ($y=0$)** if:
1. It is a genuine, unperturbed canonical contract, OR
2. It contains an alternative but coherent clause order with no legal or structural contradiction (e.g. standard covenant ordering variation).

### Exclusions & Ambiguous Cases
- **Ambiguous Ordering (`AMBIGUOUS_ORDER`)**: Ordering variations that alter text positions but represent standard commercial drafting alternatives (e.g. `Confidentiality` swapped with `Indemnification`). **Excluded from strict primary positive denominators**.
- **Arbitrary Deletion (`DESCRIPTIVE_ONLY`)**: Omitting optional boilerplate without consequence. Excluded from structural detection denominators.
- **Clause Duplication**: Excluded from structural detection (no dedicated duplicate detector).

---

## 3. Pre-Registered Evaluation Metrics

### Primary Metric:
- **Structural Anomaly Recall at Controlled False-Positive Rate ($\text{Recall} @ \text{FPR} \le 5\%$)**:
  $$\text{Recall} = \frac{\text{TP}}{\text{TP} + \text{FN}}$$
  subject to $\text{FPR} = \frac{\text{FP}}{\text{FP} + \text{TN}} \le 0.05$ on matched negative controls.

### Secondary Metrics:
- **Precision**: $\frac{\text{TP}}{\text{TP} + \text{FP}}$ (where defined).
- **Balanced Accuracy**: $0.5 \times (\text{Sensitivity} + \text{Specificity})$.
- **Area Under the Precision-Recall Curve (PR-AUC)**.
- **Two-Sided Wilson 95% Confidence Interval for Recall**:
  $$\text{CI} = \frac{k + \frac{z^2}{2}}{n + z^2} \pm \frac{z}{n + z^2}\sqrt{\frac{k(n-k)}{n} + \frac{z^2}{4}}, \quad z = 1.959964$$
- **Localization Hit Rate**: Fraction of detected anomalies where the predicted anomaly index matches the actual target/swapped clause index.
- **Inference Latency**: Average and p95 CPU execution time per document in milliseconds.

---

## 4. Threshold Selection Policy (Anti-Overfitting Protection)

1. **Strict Dev-Set Tuning**: All experimental decision thresholds $\tau^*$ must be chosen **solely using the Development / Validation partition**.
2. **Predeclared Objective**: $\tau^*$ is selected to maximize balanced F1 score on the validation split under the constraint that zero false positives occur on valid canonical controls ($\text{FPR} = 0.0$).
3. **Zero Retrospective Test Tuning**: Once evaluated on the untouched Held-Out Test partition, the threshold is fixed. No post-hoc threshold adjustment is permitted.

---

## 5. Pre-Registered Resource Budget

- **Device**: Strictly CPU (`torch.device('cpu')`).
- **Peak RAM Budget**: $\le 300\text{ MB}$ additional memory consumption.
- **Training Wall-Clock Limit**: $\le 120\text{ seconds}$ total CPU training time.
- **Model Checkpoint Footprint**: $\le 10\text{ MB}$ total storage.
- **Inference Budget**: $\le 50\text{ ms}$ per 10-clause document on cached embeddings.
