# Prompt 12 Handoff Summary: XAI / Explainability Layer

## 1. What Was Built
- **Integrated Gradients**: Token-level attribution for Channel A semantic OOD distance using `captum`.
- **Channel B Sensitivity**: Perturbation analysis masking neighboring clauses to measure coherence delta. (Fixed an embedding caching bug where perturbed clauses matched original clause IDs).
- **Nearest-Neighbor Retrieval**: Finding top-k semantically similar clauses from the training corpus (`train.jsonl`).
- **Unified Schema**: `ExplanationResult` container storing the explanation payload and a strict `ClaimScope`.

## 2. Real Data Verification
- Real SEC EDGAR clauses evaluated under a controlled structural-shuffling perturbation.
- Zero fake clauses fabricated. Channel B sensitivity deltas are non-zero after fixing caching bug.

## 3. Security and Claim Scoping
- Strict `ClaimScope` guarantees that explanations do not overclaim causal or legal significance.
- Automated tests verify presence of the claim scope and prevent raw plaintext leaks in serialized payloads.

## 4. Known Gaps
- Nearest Neighbor is unindexed (brute-force dot product on 500 items in memory).
- IG is computationally heavy.
