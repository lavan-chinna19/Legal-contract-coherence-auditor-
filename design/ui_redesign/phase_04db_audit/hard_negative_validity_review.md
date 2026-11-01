# HARD-NEGATIVE VALIDITY AND FALSE-POSITIVE HAZARD REVIEW
**LEXAUDIT INDEPENDENT RESEARCH AUDIT — PHASE 4D-B**
**Auditor:** Independent Legal NLP Research Auditor & Adversarial Evaluation Specialist
**Date:** 2026-10-22

---

## 1. Executive Summary

This review investigates the validity of negative controls in Phase 4D-B, examining:
1. Whether the tested hard negatives represent realistic legal variability.
2. Whether Candidate C3's reported 0.0% false-positive rate is genuinely robust or merely an artifact of evaluating only two benign covenant permutations.
3. Plausible real-world contract structures that would trigger false-positive failures in Candidate C3.

---

## 2. Evaluation of Tested Hard Negatives

The Phase 4D-B benchmark evaluated only **two** hard-negative cases:
1. `VAL_SLA_03_HN_COHERENT_SWAP`: Permitted Users (c01) swapped with Fee Schedule (c03).
2. `TEST_03_HN_AUDIT_WARRANTY_SWAP`: Audit Rights (c04) swapped with Warranty Disclaimer (c05).

### Findings on Tested Negatives:
- Both cases are authentic examples of **commutative legal covenants**. In commercial drafting, the relative ordering of operational covenants (fees vs users, audit vs warranty disclaimers) is legally indifferent.
- **Candidate C1 Failed Completely:** Candidate C1 asserted false-positive anomalies on **both** cases (score $0.5695$ on `VAL_SLA_03`, score $0.6239$ on `TEST_03`, threshold $0.42$). Candidate C1's local boundary contrast mechanism is inherently flawed for legal coherence because it treats any unfamiliar adjacent clause pairing as an anomaly.
- **Candidate C3 Passed Both:** Candidate C3 assigned score $0.0000$ to both cases, because neither permutation involved moving Stage 5/6 (Boilerplate/Exhibits) before Stage 0/1 (Preamble/Scope).

---

## 3. Real-World False-Positive Hazards for Candidate C3

While Candidate C3 did not flag the two synthetic hard negatives, an audit of its architectural logic reveals **severe false-positive vulnerabilities on standard commercial contract drafting practices**:

### 3.1 Statutory Upfront Dispute Disclosures
- **Legal Context:** Many jurisdictions legally mandate upfront dispute or arbitration notices. For example, Tennessee construction contracts, California medical agreements, and commercial consumer arbitration clauses frequently mandate prominent arbitration clauses on Page 1 (before Section 1 Scope or Grant).
- **Candidate C3 Vulnerability:**
  Because the arbitration notice contains `"dispute"` or `"arbitration"`, `infer_clause_lifecycle_stage` assigns it **Stage 5**.
  Because it precedes Section 1 (Scope, Stage 1), Candidate C3 evaluates:
  $$\text{Stage}(c_0) = 5 \ge 5 \quad \land \quad \text{Stage}(c_1) = 1 \le 1 \implies \mathbf{\text{VIOLATION ASSERTED (Score 1.0)}}$$
  **Result:** Candidate C3 will assert a catastrophic false positive on legally mandated contract formats.

### 3.2 Upfront Definitions Schedules and Master Exhibits
- **Legal Context:** Financial credit agreements, master intercompany agreements, and syndicated loans frequently place "Schedule 1: Defined Terms and Master Definitions" at the front of the agreement (before Section 2 Scope).
- **Candidate C3 Vulnerability:**
  `infer_clause_lifecycle_stage` maps `"schedule"` or `"appendix"` to **Stage 6**.
  Appearing before Scope (Stage 1), Candidate C3 asserts:
  $$\text{Stage}(c_0) = 6 \ge 5 \quad \land \quad \text{Stage}(c_1) = 1 \le 1 \implies \mathbf{\text{VIOLATION ASSERTED (Score 1.0)}}$$
  **Result:** Standard financial contract architectures will be falsely flagged as defective.

### 3.3 Executive Summary and Key Terms Term Sheets
- **Legal Context:** Modern SaaS contracts (e.g. Ironclad, Common Paper) feature an upfront "Cover Page / Term Summary" containing governing law, term, and payment fees on Page 1, followed by standard General Terms and Scope.
- **Candidate C3 Vulnerability:**
  Governing law in the cover box (Stage 5) followed by General Scope (Stage 1) triggers Candidate C3's rule:
  $$\text{Stage}(c_{\text{cover}}) = 5 \ge 5 \quad \land \quad \text{Stage}(c_{\text{scope}}) = 1 \le 1 \implies \mathbf{\text{VIOLATION ASSERTED (Score 1.0)}}$$

---

## 4. Audit Conclusion on Negative Controls

Candidate C3's 0.0% false-positive rate on the held-out test set is an artifact of an extremely narrow negative control set ($n=2$ covenant swaps). When presented with legitimate noncanonical contract architectures—such as upfront statutory arbitration disclosures, front-loaded schedules, or modern SaaS cover pages—Candidate C3 will produce uncalibrated false positives due to its rigid, hardcoded precedence constraints.
