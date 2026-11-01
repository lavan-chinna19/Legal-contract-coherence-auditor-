# Scientific Integrity & Research Claims Review — Prompt 24A

**Author:** Technical Documentation Auditor & ML Validation Lead  
**Audit Phase:** Prompt 24A (Final Release Corrections & Verification)  
**Date:** October 10, 2026  

---

## 1. Core Principles of Academic Integrity Enforced

The Legal Contract Coherence Auditor is an **Academic Research Prototype** developed to explore dual-channel anomaly detection and token-level explainability in legal texts. In accordance with ethical AI research practices:

1. **Software Verification $\neq$ Model Generalization:**
   - The test suite execution of 116 passing pytest tests proves that API endpoints, encryption handlers, retention cleaners, and UI components function without regression errors.
   - It **does not** constitute evidence of high semantic classification accuracy on unseen commercial legal contracts.
2. **No Fabricated Accuracy Claims:**
   - The project explicitly **rejects** and omits any claim of "95% classification accuracy", "replaces legal counsel", or "guaranteed statutory compliance".
   - Empirical performance metrics from Prompt 14 are published honestly without cherry-picking:
     - Kendall's Tau: $\tau = -0.0285$ ($p = 0.6225$), 95% CI: $[-0.1254, 0.0730]$.
     - High Severity FPR on 50 Clean SEC Contracts: $1.18\%$ (7/595 clauses).
     - Med + High Severity FPR on 50 Clean SEC Contracts: $44.54\%$ (265/595 clauses).
     - CUAD Generalization Mean Combined Anomaly: $0.3922$.
3. **Conformal Prediction Exchangeability Scope:**
   - Conformal confidence intervals are computed using inductive conformal prediction (`crepes`) on nonconformity scores derived from **synthetic clause shuffle permutations**.
   - These bounds represent empirical confidence under synthetic exchangeability assumptions, not guaranteed coverage over real-world contractual defect distributions.
4. **Qualification of Demonstration Output Metrics:**
   - The specific KPI values demonstrated in the walkthrough (5 clauses, 2 anomalies, 2 high-severity, 0.341 mean score, 26 Integrated Gradients token badges) are traceable to the verified demonstration fixture `audit/prompt_23/evidence/fixtures/valid_multiclause.txt` (SHA-256: `55558d95947bb2050782035de4f7a9f938d29c5b3d0b8e53014cf22c8c085825`).
   - Demonstration scripts explicitly describe these numbers as sample-specific empirical findings under the frozen checkpoint, not hardcoded invariants or guaranteed outputs for arbitrary documents.
5. **Reviewer Feedback Mechanics:**
   - Reviewer feedback submission records verdicts (`CONFIRM_ANOMALY` or `REJECT_ANOMALY`) into persistent SQLite storage.
   - It is explicitly documented that recording feedback does not alter model parameters online, avoiding potential adversarial instability.
