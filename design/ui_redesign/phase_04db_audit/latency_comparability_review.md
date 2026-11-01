# LATENCY COMPARABILITY AND MEASUREMENT BOUNDARY REVIEW
**LEXAUDIT INDEPENDENT RESEARCH AUDIT — PHASE 4D-B**
**Auditor:** Independent ML Systems Engineer & Performance Auditor
**Date:** 2026-10-22

---

## 1. Executive Summary

The Phase 4D-B report claimed that Candidate C3 runs in **$0.17\text{ ms}$**, declaring it **"$246\times$ faster than the production ensemble"** and **"$45\times$ faster than frozen Channel B"**.

This performance audit investigated the **measurement boundaries** of each model and determined that:
1. **Apples-to-Oranges Comparison:** Candidate C3 and Baseline B0/B1 were benchmarked across fundamentally asymmetric computation boundaries.
2. **Dense Neural Model vs. 10-Line String Check:** Baseline B0 and Ensemble B1 execute dense tokenization and neural transformer embedding generation (`all-MiniLM-L6-v2`) followed by PyTorch matrix multiplications. Candidate C3 executes **zero neural models, zero tokenization, zero PyTorch tensors, and zero linear algebra**. It runs simple substring checks on the first 80 characters of clause strings.
3. **Misleading Full-Document Speedup Claim:** Claiming Candidate C3 provides a "$246\times$ faster coherence analysis pipeline" is scientifically misleading. In an end-to-end production workflow, contract ingestion, clause segmentation, and semantic embeddings still must be computed for Channel A and XAI explanations.

---

## 2. Granular Computation Breakdown by Model

| Model Component | Operations Executed | PyTorch Tensors? | Dense Embeddings Computed? | Measured Mean Latency | Primary Driver of Latency |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **Baseline B0 (Channel B)** | Tokenization $\to$ Transformer Embedding $\to$ 768-d Pair Tensor $\to$ MLP Forward Pass | **YES** | **YES** (384-d MiniLM) | **7.68 ms** | Transformer embedding generation and PyTorch MLP inference |
| **Baseline B1 (Ensemble)** | Tokenization $\to$ Embedding $\to$ 66 Centroid Cosine Matrix $\to$ Channel B MLP | **YES** | **YES** (384-d MiniLM) | **38.31 ms** | Full dual-channel pipeline and centroid matrix distance computations |
| **Candidate C1 (Boundary)** | Embedding $\to$ Channel B Pairs $\to$ Context Centroid Cosine $\to$ Discordance | **YES** | **YES** (384-d MiniLM) | **14.98 ms** | Neural embeddings + pair scoring + rolling window cosine aggregation |
| **Candidate C2 (BiLSTM)** | Embedding $\to$ Sequence BiLSTM $\to$ Linear Projection Head | **YES** | **YES** (384-d MiniLM) | **53.79 ms** | Dense embeddings + recurrent bidirectional sequence forward pass |
| **Candidate C3 (Topological)**| Substring `in` checks on 80 chars $\to$ 55 integer comparisons | **NO** | **NO** | **0.17 ms** | Standard Python string matching and integer loop |

---

## 3. Dissecting the Candidate C3 Computation

Candidate C3's entire execution in `src/research/structural_coherence/models.py` consists of:
```python
# 1. Heading stage extraction (11 iterations of string checks):
stages = [infer_clause_lifecycle_stage(c) for c in clauses]

# 2. Integer precedence check (11 * 10 / 2 = 55 integer comparisons):
for i in range(n):
    for j in range(i + 1, n):
        if stages[i] >= 5 and stages[j] <= 1:
            violations[j] = 1.0
```
- In Python, evaluating 11 small strings against a dictionary of keywords and running 55 integer comparisons takes **$\approx 0.15 - 0.20\text{ ms}$**.
- This is not an accelerated machine learning model; it is a **rule-based string heuristic**.

---

## 4. Latency Audit Conclusion

The reported $0.17\text{ ms}$ latency for Candidate C3 is technically accurate for the 20 lines of Python code executed. However, presenting this as an architectural breakthrough that outperforms neural scorers by "$246\times$" is scientifically invalid:
- Neural baselines were timed including transformer embedding inference.
- Candidate C3 bypassed all neural computation.
- Candidate C3 cannot replace the neural embedding pipeline if semantic search, clause clustering, or cross-channel anomaly scoring are required by the application.
