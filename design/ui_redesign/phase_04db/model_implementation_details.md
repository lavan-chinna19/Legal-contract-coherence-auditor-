# MODEL IMPLEMENTATION DETAILS
**LEXAUDIT RESEARCH EXTENSION — PHASE 4D-B**
**Author:** ML Systems Engineer & FastAPI Developer
**Date:** 2026-10-22
**Package Location:** `src/research/structural_coherence/`

---

## 1. Architectural Component Overview

The experimental structural coherence package is implemented in `src/research/structural_coherence/` with modular separation:

```
src/research/structural_coherence/
├── __init__.py           # Package namespace definition
├── schema.py             # Pydantic-style dataclasses (Evidence, Clause Scores, Document Result)
├── features.py           # Heading-first stage inference, contextual window distance, boundary contrast
├── models.py             # Implementations of Baselines (B0, B1, B2) and Candidates (C1, C2, C3)
├── training.py           # CPU PyTorch trainer with early stopping for Candidate C2
└── evaluator.py          # Benchmark harness computing Wilson CIs and case-level predictions
```

---

## 2. Technical Implementation Specifications

### 2.1 Candidate C3: `CandidateC3_StructureAwareDependencyModel`
- **Class:** `CandidateC3_StructureAwareDependencyModel(threshold=0.50)`
- **Heading-First Stage Extractor:**
  `infer_clause_lifecycle_stage(clause: ClauseRecord) -> int`
  - Examines `clause.label` and the first 80 characters of `clause.text`.
  - Prioritizes Stage 6 (Exhibits & Schedules) before Stage 1 (Scope) to avoid substring collisions when exhibits reference statements of work or deliverables.
  - Maps clauses into 7 discourse stages:
    - Stage 0: Preamble / Parties / Recitals
    - Stage 1: Scope & Substantive Services Grant
    - Stage 2: Payment, Fees, & Term
    - Stage 3: Operational Covenants (IP, Confidentiality, Audit)
    - Stage 4: Risk Allocation & Remedies (Indemnification, Liability, Warranties)
    - Stage 5: General Boilerplate (Governing Law, Entire Agreement, Miscellaneous)
    - Stage 6: Closing, Exhibits, Schedules, Signatures
- **Precedence DAG Edge Evaluation:**
  Checks for prohibited backward edges:
  $$\text{Edge Violation}: \text{Stage}(c_i) \ge 5 \land \text{Stage}(c_j) \le 1 \quad (i < j)$$
  Assigns score $1.0$ to displaced clauses and produces localized clause IDs.

### 2.2 Candidate C1: `CandidateC1_ContextualBoundaryDetector`
- **Class:** `CandidateC1_ContextualBoundaryDetector(threshold=0.42, w_ctx=0.35, w_contrast=0.25, w_discordance=0.40, window_size=2)`
- **Multi-Factor Score:** Combines rolling L2-normalized centroid distance, local boundary contrast deviation from document baseline, and forward-accumulated lifecycle discordance.

### 2.3 Candidate C2: `CandidateC2_ContextualSequenceModel`
- **Class:** `CandidateC2_ContextualSequenceModel(checkpoint_path, threshold=0.50)`
- **PyTorch Network:**
  Input $(B, N, 385)$ $\rightarrow$ `nn.LSTM(385, 64, batch_first=True, bidirectional=True)` $\rightarrow$ `nn.Linear(128, 1)`.
- **Checkpoint Location:** `models/experimental/phase_04db/contextual_sequence_coherence.pt` (SHA-256: `cac804594959a419126463191c3c520206f00244540133492ffd98bbd4a4c9aa`).
