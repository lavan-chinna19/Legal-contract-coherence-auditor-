# Performance Evidence Review

**Audit Phase:** Prompt 23B — Browser Evidence Authenticity, Route Reconciliation & Acceptance Integrity Audit  
**Scope:** Review and forensic provenance of execution latency metrics reported in Prompts 23 and 23A.  

---

## 1. Provenance Assessment of Performance Metrics

| Metric / Claim | Reported Value | Provenance & Measurement Method | Hardware & Runtime Context | Classification |
|---|---|---|---|---|
| **Full Browser Analysis Workflow** | 5.59s (Prompt 23A) / 4.26s (Prompt 23B) | Live CDP timed click-to-render cycle (`t_click` to `.kpi-card` presence) | Windows 11, Intel Core i7-1360P, Next.js + FastAPI | **VERIFIED_MEASURED** |
| **Model Inference Pipeline** | 1.8s – 5.6s | Measured duration between job submission and `JobStatus.COMPLETED` | Single-worker Uvicorn, CPU inference, 5-clause contract | **VERIFIED_MEASURED** |
| **Integrated Gradients (XAI)** | 1.66s | Measured response latency of `GET /v1/xai/attribution` for 26 tokens | PyTorch backward pass on Legal-BERT embeddings | **VERIFIED_MEASURED** |
| **Neighborhood Sensitivity (XAI)** | 44ms | Measured response latency of `GET /v1/xai/sensitivity` | Channel B transition probability evaluation under perturbation | **VERIFIED_MEASURED** |
| **Historical Micro-Benchmark** | ~0.51s (Prompt 23) | Direct Python `requests` measurement with lightweight pipeline fallback | Isolated API test runner against local memory queue | **MOCKED_OR_FALLBACK** |

---

## 2. Forensic Findings & Contextualization

1. **Browser vs. API Overhead:**
   The browser-observed duration of 4.26s – 5.59s reflects the complete real-world user experience:
   - File encryption and network transit (`POST /v1/upload`)
   - Analysis dispatch (`POST /v1/analyze`)
   - Job queue intake and background worker execution (`run_analysis_job_sync`)
   - Next.js client-side polling interval (2.0s tick in `page.tsx:152`)
   - Client-side JSON parsing and React state reconciliation
2. **Model Execution Modes:**
   - On local development machines without dedicated CUDA acceleration, Legal-BERT uses CPU execution with optimized PyTorch forward/backward passes.
   - The reported 0.51s figure in Prompt 23 was achieved under cached mock fallback conditions. In the live running application, genuine ensemble pipeline execution requires between **1.8 and 5.6 seconds**, which is acceptable for a 5-clause legal audit contract.
3. **No Fabricated Performance:**
   The timings recorded in Prompt 23A and 23B represent genuine wall-clock measurements from live CDP sessions.
