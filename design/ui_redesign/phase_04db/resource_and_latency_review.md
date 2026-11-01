# RESOURCE AND LATENCY REVIEW
**LEXAUDIT RESEARCH EXTENSION — PHASE 4D-B**
**Author:** ML Systems Engineer & Performance Architect
**Date:** 2026-10-22
**Hardware Target:** Intel Core i7-1360P, 15.65 GB RAM, CPU-only PyTorch 2.13.0+cpu

---

## 1. Measured Computational Profiles

| Model | Mean Inference Latency | p95 Latency | Peak RAM Allocation | Model File Size | Relative CPU Cost vs B0 |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Baseline B0 (Channel B)** | 12.68 ms | 24.01 ms | ~42.5 MB | 397 KB | 1.00x |
| **Baseline B1 (Ensemble)** | 40.78 ms | 42.09 ms | ~58.2 MB | 397 KB | 3.22x |
| **Baseline B2 (Cosine)** | 7.26 ms | 8.11 ms | ~12.1 MB | 0 KB | 0.57x |
| **Candidate C1 (Boundary)** | 22.96 ms | 29.04 ms | ~38.4 MB | 0 KB | 1.81x |
| **Candidate C2 (BiLSTM)** | 25.64 ms | 53.79 ms | ~64.8 MB | 5.46 MB | 2.02x |
| **Candidate C3 (Topological DAG)** | **0.20 ms** | **0.25 ms** | **< 2.0 MB** | **0 KB** | **0.016x (60x faster)** |

---

## 2. Resource Feasibility Assessment

1. **Candidate C3 is Extremely Lightweight:**
   At 0.20 ms execution time and under 2 MB RAM allocation, Candidate C3 introduces negligible overhead, running over $200\times$ faster than the production ensemble. It requires zero PyTorch tensors or matrix multiplications during inference.
2. **Candidate C2 Confirms Neural Overhead:**
   The recurrent sequence BiLSTM required 25-54 ms per contract and added 5.46 MB in checkpoint storage, while producing inferior detection results.
3. **Laptop Environment Compliance:**
   All candidate evaluations executed strictly within local hardware bounds with zero out-of-memory errors, zero system paging, and zero GPU dependencies.
