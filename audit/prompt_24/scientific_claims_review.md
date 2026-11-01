# Scientific Claims & Research Integrity Review — Prompt 24

**Audit Date:** October 10, 2026  
**Auditor:** Technical Documentation Architect & ML Validation Lead  
**Scope:** UI text, README.md, benchmark tables, and release documentation  

---

## 1. Principles of Academic & Scientific Integrity

In accordance with responsible AI research practices:
1. **Software Verification is Not ML Performance:** Passing 116 automated pytest unit and integration tests verifies software correctness, interface adherence, and test suite health—**not** model generalization accuracy on unseen legal contracts.
2. **Conformal Prediction Scope:** Conformal coverage bounds (95% confidence intervals) are computed under exchangeability assumptions using **synthetic shuffle permutations**, not real-world human-annotated defect distributions.
3. **No Fabricated Performance:** No unverified metrics (precision, recall, F1, AUC, human agreement) are presented as established facts. Unmeasured metrics are explicitly marked **NOT ESTABLISHED**.
4. **No Promotional Claims:** The application makes no claims of "100% accuracy", "replaces legal counsel", "guaranteed compliance", or "production-ready legal analysis".

---

## 2. Benchmark Claims Audit

| Claim Axis | Evaluation Basis | Reported Value | Integrity Status | Explicit Disclosure |
|---|---|:---:|:---:|---|
| **Kendall's Tau ($\tau$)** | LEDGAR Test Split (200 clauses, 5 perms) | $\tau = -0.0285$ ($p=0.6225$) | **VERIFIED** | Indicates weak rank correlation on out-of-distribution clauses. |
| **False Positive Rate (High)** | 50 Clean SEC EDGAR Contracts (595 clauses) | $1.18\%$ (7/595) | **VERIFIED** | High severity threshold is conservative on clean SEC contracts. |
| **False Positive Rate (Med+High)**| 50 Clean SEC EDGAR Contracts (595 clauses) | $44.54\%$ (265/595) | **VERIFIED** | Discloses that medium threshold flags benign stylistic variations. |
| **Out-of-Distribution Transfer** | CUAD Commercial Agreements | Mean Combined = $0.3922$ | **VERIFIED** | Demonstrates cross-corpus distribution shift. |
| **Baseline Linear Classifier** | Identical Test Split | Acc = $55.0\%$, F1 = $0.6087$ | **VERIFIED** | Logistic regression baseline for reference. |
| **95% Classification Accuracy** | Not measured on real human test set | None | **REJECTED** | Explicitly stated that 95% classification accuracy is NOT CLAIMED. |
| **Human Expert Validation** | Simulated test fixtures only | `SYNTHETIC_TEST` | **DISCLOSED** | Real human legal study is future work. |

---

## 3. UI and Documentation Guardrails

- **Banner Display:** `⚠️ RESEARCH PROTOTYPE — NOT LEGAL ADVICE` prominently displayed on the Next.js header and README.md.
- **XAI Limitations:** Integrated Gradients attributions and perturbation sensitivity deltas are framed as model-internal gradient and score fluctuations, not authoritative statutory explanations.
- **Transparency Tab:** Explains the dual-channel scoring methodology, synthetic permutation calibration source, and known limitations to the end user.
