# FALSE-POSITIVE ANALYSIS
**LEXAUDIT RESEARCH EXTENSION — PHASE 4D-B**
**Author:** Independent Verification Lead & Legal Systems Architect
**Date:** 2026-10-22

---

## 1. Exhaustive False-Positive Register

| Case ID | Split | Model | Score | Threshold | Margin | Root Cause Category | Diagnostic Finding |
| :--- | :--- | :--- | :---: | :---: | :---: | :--- | :--- |
| `VAL_SLA_03_HN_COHERENT_SWAP` | VALIDATION | Candidate C1 | 0.5695 | 0.42 | +0.1495 | Boundary Contrast Sensitivity | Swapping Permitted Users and Fee Schedule juxtaposes two clauses with higher cosine distance, causing boundary contrast to spike above 0.42. |
| `TEST_03_HN_AUDIT_WARRANTY_SWAP`| HELDOUT_TEST| Candidate C1 | 0.6239 | 0.42 | +0.2039 | Boundary Contrast Sensitivity | Juxtaposing Audit Rights and Warranty Disclaimer causes adjacent neural coherence to drop from 0.33 to 0.31, raising local contrast above the anomaly cutoff. |
| Clean Controls & Hard Negatives | ALL | Candidate C3 | 0.0000 | 0.50 | -0.5000 | **ZERO FALSE POSITIVES** | Candidate C3 achieved exactly 0 false positives across all clean contracts and hard negatives in all splits. |
| Clean Controls & Hard Negatives | ALL | Baseline B0 | 0.6865 | 0.70 | -0.0135 | **ZERO FALSE POSITIVES** | Baseline B0 achieved 0 false positives due to logit saturation (never reaches 0.70). |

---

## 2. In-Depth Root-Cause Analysis for Candidate C1

The false-positive vulnerability in Candidate C1 stems from its **local boundary contrast formula**:
$$\text{Contrast}(c_i) = \frac{(1 - P_i) - \mu_{\text{doc}}}{\sigma_{\text{doc}}}$$
When two independent clauses are swapped, the model encounters a transition pair not seen in standard boilerplate. Even though both clauses are valid and compatible in a legal sense, their semantic vector distance is slightly higher than identical sequential boilerplate. This causes $\text{Contrast}(c_i)$ to exceed the $1.5\sigma$ z-score cutoff, inflating the composite score above $0.42$.

---

## 3. Engineering Remediation
To resolve this error mode before any future candidate promotion:
1. Downweight the boundary contrast term ($w_{\text{contrast}} \le 0.10$).
2. Require an explicit lifecycle regression ($\text{Disc}(c_i) > 0$) as an essential prerequisite gating condition before asserting a structural anomaly.
