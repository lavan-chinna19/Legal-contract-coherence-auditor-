# Data Governance

**Project:** Legal Contract Coherence Auditor  
**Status:** RESEARCH/DEMO PROJECT — not production-ready  
**Last updated:** 2026-08-22

---

## Datasets Used

### 1. LEDGAR

| Field | Detail |
|---|---|
| Full name | LEDGAR — Large-Scale Legal Document Corpus |
| Source | HuggingFace: `lex_glue` / `ledgar` config |
| Original paper | Tuggener et al. (2020), "LEDGAR: A Large-Scale Multi-label Corpus for Text Classification of Legal Provisions" |
| License | Research use; distributed via `lex_glue` benchmark. No commercial redistribution. |
| Cost | Free — downloaded via HuggingFace `datasets` library |
| Content | ~60,000 labelled contract provisions from SEC EDGAR filings |
| Redistribution | NOT redistributed — data is downloaded at ingestion time and stored in git-ignored `data/` directory |
| Citation | `@inproceedings{tuggener2020ledgar, ...}` |

### 2. SEC EDGAR Filings

| Field | Detail |
|---|---|
| Source | https://www.sec.gov/cgi-bin/browse-edgar |
| License | US federal government works — **public domain** (17 U.S.C. § 105) |
| Cost | Free — accessed via public EDGAR full-text search API |
| Rate limit | 10 requests/second per SEC policy; this project uses ≤7 req/s |
| User-Agent | Required by SEC: see `EDGAR_USER_AGENT` in `src/config.py` |
| Redistribution | Public domain; may be redistributed. This project does NOT redistribute raw filings — they are downloaded on demand and stored in git-ignored `data/raw/sec_edgar/` |
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
| Legal-BERT | `nlpaueb/legal-bert-base-uncased` | MIT | Free |
| BART-large-MNLI | `facebook/bart-large-mnli` | MIT | Free |

No paid API (e.g., GPT-4, Claude) is used for core inference — Contract §6.

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

### Deployed Application (Prompts 15–19)
- Uploaded contract files: stored in Render/Railway local disk or free-tier
  S3-compatible bucket (e.g., Cloudflare R2 free tier).
- **Retention policy:** Uploaded files are deleted after 24 hours unless
  the user explicitly opts into longer retention (to be implemented in Prompt 16).
- **Encryption at rest:** Enforced wherever the hosting tier supports it
  (Cloudflare R2 encrypts at rest by default; Render/Railway disk: AES-256).
- **No plaintext contract content in application logs** — Contract §4(a).

### Privacy Notice Requirement
A visible privacy notice must be displayed in the UI **before** a user uploads
a real contract — to be implemented in Prompt 17 (frontend). This is a
**forward requirement** from Contract §4(d).

---

## Cache Strategy

HuggingFace `datasets` caches downloads in `~/.cache/huggingface/datasets/`
(OS default). This directory is outside the repo and not git-tracked.
To clear: `rm -rf ~/.cache/huggingface/datasets/`

Model weights cached in `~/.cache/huggingface/hub/` by default.

---

## What Is NOT In This Repository

- Raw dataset files (LEDGAR, CUAD, SEC EDGAR filings)
- Model weight files (`.bin`, `.pt`, `.safetensors`)
- Any uploaded user contract content
- API keys or credentials (use `.env` — git-ignored)
