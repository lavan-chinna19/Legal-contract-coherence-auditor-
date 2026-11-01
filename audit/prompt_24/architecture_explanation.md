# System Architecture Explanation — Prompt 24

**Author:** Technical Documentation Architect  
**Scope:** Legal Contract Coherence Auditor Architecture  

---

## 1. High-Level Architecture Diagram

```text
┌─────────────────────────────────────────────────────────────────┐
│                    Next.js 16 Research UI                       │
│  - App Router / TypeScript / Turbopack                         │
│  - Privacy Checkbox & Pre-Upload Guard                         │
│  - KPI Cards, Heatmap & Table Views                            │
│  - Integrated Gradients Token Attribution & Sensitivity Delta   │
│  - Reviewer Feedback Submission Form                           │
└───────────────────────────────┬─────────────────────────────────┘
                                │ HTTP / REST (X-API-Key)
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                     FastAPI Backend Core                        │
│  - Auth Middleware & Constant-Time Token Check                 │
│  - Sliding-Window IP Rate Limiting                             │
│  - Automated 24h Data Retention Purge Worker                   │
│  - Process-Local Async Job Store (_jobs dict)                  │
└──────────┬────────────────────┬────────────────────┬────────────┘
           │                    │                    │
           ▼                    ▼                    ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────────┐
│ Storage & Crypto │ │  NLP Pipeline    │ │ Rule Checkers        │
│ - Fernet AES-128 │ │ - Segmentation   │ │ - Reference Checker  │
│ - HMAC-SHA256    │ │ - Legal-BERT Emb │ │   (Dangling § refs)  │
│ - SQLite/Postgres│ │ - Channel A (OOD)│ │ - Date Checker       │
│   (Feedback Store│ │ - Channel B (Seq)│ │   (Timeline order)   │
│                  │ │ - Severity Ranker│ │ - Boilerplate Audit  │
└──────────────────┘ └─────────┬────────┘ └──────────────────────┘
                               │
                               ▼
                     ┌──────────────────┐
                     │ Explainability   │
                     │ - Integrated     │
                     │   Gradients      │
                     │ - Perturbations  │
                     │ - Conformal CI   │
                     └──────────────────┘
```

---

## 2. Component Descriptions

### 2.1 Ingestion & Security Subsystem
- **API Entrypoint:** `src/api/main.py` provides RESTful endpoints.
- **Authentication:** `verify_api_key` dependency verifies the `X-API-Key` header against constant-time hashes.
- **Encryption at Rest:** Uploaded files in `data/uploads/` are encrypted using cryptography's `Fernet` scheme (`AES-128-CBC` with `HMAC-SHA256`).
- **Retention Purge:** Expired contract blobs older than 24 hours are deleted by `retention_worker`.

### 2.2 NLP Dual-Channel Core
- **Segmentation:** Text is segmented into numbered sections and paragraphs using regular expressions and spaCy (`en_core_web_sm`).
- **Channel A (Semantic Out-of-Distribution):** Extracts dense 768-dimensional representations using Legal-BERT (`nlpaueb/legal-bert-base-uncased`) and measures Mahalanobis/Cosine distance from LEDGAR legal topic centroids.
- **Channel B (Discourse Transition):** Evaluates sequential probabilities between adjacent clauses using a sequential transition model.
- **Severity Ranking:** Merges Channel A and Channel B outputs into a composite score and assigns `HIGH`, `MEDIUM`, or `LOW` severity flags.

### 2.3 Deterministic Rule Checkers
- **Reference Checker (`src/rules/reference_checker.py`):** Parses internal section references (e.g., "subject to Section 4.2") and flags references pointing to non-existent clauses.
- **Date Checker (`src/rules/date_checker.py`):** Extracts dates and milestones to verify that effective dates precede termination dates and renewal milestones.

### 2.4 Explainability & Feedback
- **Integrated Gradients (`src/xai/integrated_gradients.py`):** Computes token-level importance by accumulating gradients along an interpolation path from baseline embeddings.
- **Sensitivity Analysis (`src/xai/sensitivity.py`):** Evaluates the resilience of Channel B transition scores under sentence perturbations.
- **Feedback Database (`src/feedback/storage.py`):** Stores reviewer verdicts (`ACCEPT`, `REJECT`, `UNSURE`), user IDs, and timestamps in SQLite or PostgreSQL.
