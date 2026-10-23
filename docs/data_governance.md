# Data Governance

**Project:** Legal Contract Coherence Auditor  
**Status:** RESEARCH/DEMO PROJECT — not production-ready  
**Last updated:** 2026-10-24

Current publication review: [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
No project-wide license is declared. Source publication preserves contributor
history and does not establish unrestricted model/data redistribution rights.

---

## Datasets Used

### 1. LEDGAR

| Field | Detail |
|---|---|
| Full name | LEDGAR — Large-Scale Legal Document Corpus |
| Source | HuggingFace: `lex_glue` / `ledgar` config |
| Original paper | Tuggener et al. (2020), "LEDGAR: A Large-Scale Multi-label Corpus for Text Classification of Legal Provisions" |
| License | The [LexGLUE card](https://huggingface.co/datasets/coastalcph/lex_glue) displays CC BY 4.0 metadata; its detailed licensing section requests more information. Underlying document and derived-asset terms require separate review. |
| Cost | Free — downloaded via HuggingFace `datasets` library |
| Content | ~60,000 labelled contract provisions from SEC EDGAR filings |
| Redistribution | NOT redistributed — data is downloaded at ingestion time and stored in git-ignored `data/` directory |
| Citation | `@inproceedings{tuggener2020ledgar, ...}` |

### 2. SEC EDGAR Filings

| Field | Detail |
|---|---|
| Source | https://www.sec.gov/cgi-bin/browse-edgar |
| License | Public access to issuer filings is not a blanket copyright grant. [17 USC 105](https://www.copyright.gov/title17/92chap1.html#105) concerns government works, not all privately authored documents filed with an agency. |
| Cost | Free — accessed via public EDGAR full-text search API |
| Rate limit | 10 requests/second per SEC policy; this project uses ≤7 req/s |
| User-Agent | Required by SEC: see `EDGAR_USER_AGENT` in `src/config.py` |
| Redistribution | Per-document rights review required; raw filings are excluded and stored in git-ignored `data/raw/sec_edgar/`. No blanket public-domain claim is made. |
| Privacy note | Filed contracts are public record. However, the system processes them as potentially sensitive business documents. Contract §4 applies: no plaintext content in logs. |

### 3. CUAD (Contract Understanding Atticus Dataset)

| Field | Detail |
|---|---|
| Source | HuggingFace: `cuad` |
| Original paper | Hendrycks et al. (2021), "CUAD: An Expert-Annotated NLP Dataset for Legal Contract Review" |
| License | **CC BY 4.0** — https://creativecommons.org/licenses/by/4.0/ |
| Cost | Free |
| Content | 510 contracts with 13,000+ expert annotations across 41 clause types |
| Redistribution | Permitted under CC BY 4.0 with attribution |
| Citation | `@article{hendrycks2021cuad, ...}` |

---

## Models Used

| Model | HuggingFace ID | License | Cost |
|---|---|---|---|
| Legal-BERT | `nlpaueb/legal-bert-base-uncased` | [CC BY-SA 4.0](https://huggingface.co/nlpaueb/legal-bert-base-uncased) | Public download |
| BART-large-MNLI | `facebook/bart-large-mnli` | MIT | Free |

No paid API (e.g., GPT-4, Claude) is used for core inference. Public weight caches
are excluded from Git. Existing small frozen head/centroid assets are preserved
with their provenance; no independent redistribution clearance is asserted.

---

## Python Dependencies (key packages)

| Package | License | Cost |
|---|---|---|
| PyTorch | BSD-style | Free |
| Transformers (HuggingFace) | Apache 2.0 | Free |
| sentence-transformers | Apache 2.0 | Free |
| datasets (HuggingFace) | Apache 2.0 | Free |
| scikit-learn | BSD | Free |
| spaCy | MIT | Free |
| MAPIE | BSD | Free |
| crepes | BSD | Free |
| captum | BSD | Free |
| dateparser | BSD | Free |
| FastAPI | MIT | Free |
| Streamlit | Apache 2.0 | Free |

---

## Data Storage & Retention Policy

### Local Development
- All raw and processed data is stored in `data/` — which is **git-ignored**.
- No dataset blobs are committed to the repository.
- Developers must re-run ingestion scripts to populate local data.

### Verified local application
- Uploads, filenames and completed snapshots are encrypted with a stable Fernet
  key and stored locally; Compose retains them on `uploads_data`.
- Native reviewer feedback uses SQLite; verified Compose feedback uses PostgreSQL.
  Derived embeddings and file-based threshold settings have separate storage.
- Retention defaults to 24 hours, with startup, periodic and authenticated admin
  cleanup. Feedback retention is not represented as identical to upload cleanup.
- No plaintext contract content is logged. Runtime inference is offline.
- Legacy cloud/S3/MinIO configuration is retained but is not the verified storage
  path. No external production deployment is claimed.

### Privacy Notice Requirement
A visible privacy notice and acknowledgment are implemented before frontend
upload. This UI safeguard does not replace authorization or the user's duty to
have permission to process a document.

---

## Cache Strategy

HuggingFace `datasets` caches downloads in `~/.cache/huggingface/datasets/`
(OS default). This directory is outside the repo and not git-tracked.
Preserve existing research caches; they are not included in publication.

Model weights cached in `~/.cache/huggingface/hub/` by default.

---

## What Is NOT In This Repository

- Raw dataset files (LEDGAR, CUAD, SEC EDGAR filings)
- Upstream model caches (`.bin`, `.safetensors`) and optional experimental weights.
  The existing small `models/coherence_classifier.pt` is intentionally tracked;
  its original hash and contributor provenance are preserved.
- Any uploaded user contract content
- API keys or credentials (use `.env` — git-ignored)
