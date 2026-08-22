# Handoff — Prompt 01: Environment Bootstrap & Repository Baseline

**Date:** 2026-08-22  |  **Status: ALL 4 ACCEPTANCE GATES PASSED**

---

## What Was Built

A clean, verified Python environment for the Legal Contract Coherence Auditor
(RESEARCH/DEMO PROJECT — not production-ready).

**`requirements.txt`** was rewritten with exact pinned versions for every
required package, matching the verified installed state of the `.venv`.

---

## Commands Run and Results (all provenance: REAL RUN this session)

| # | Command | Exit Code | Key Output |
|---|---------|-----------|------------|
| 1 | `.venv\Scripts\pip install -r requirements.txt` | **0** | All requirements already satisfied |
| 2 | `.venv\Scripts\python -m spacy download en_core_web_sm` | **0** | en_core_web_sm-3.8.0 installed (12.8 MB, github release) |
| 3 | `python -c "import torch, transformers, spacy, mapie, captum; nlp=spacy.load('en_core_web_sm'); print('BOOTSTRAP SUCCESS')"` | **0** | `BOOTSTRAP SUCCESS` printed |
| 4 | `pytest tests/test_cuad_order.py -v` | **0** | 4 passed, 2 skipped, 0 failed (7.85s) |

---

## Acceptance Gates

| Gate | Description | Status |
|------|-------------|--------|
| AG1-1 | `requirements.txt` written with pinned exact versions | ✅ PASSED |
| AG1-2 | `pip install -r requirements.txt` exits 0 | ✅ PASSED |
| AG1-3 | `en_core_web_sm` downloaded and loadable | ✅ PASSED |
| AG1-4 | `BOOTSTRAP SUCCESS` printed by importability one-liner | ✅ PASSED |

---

## Key Package Versions (REAL — from pip list in this session)

| Package | Version |
|---------|---------|
| torch | 2.13.0 (CPU-only) |
| transformers | 5.15.1 |
| sentence-transformers | 6.0.0 |
| scikit-learn | 1.7.2 |
| spacy | 3.8.15 |
| en_core_web_sm | 3.8.0 |
| MAPIE | 1.5.0 |
| captum | 0.9.0 |
| crepes | 0.9.1 |
| datasets | 5.0.1 |
| fastapi | 0.135.2 |
| streamlit | 1.56.0 |
| pytest | 9.1.1 |

All packages are **free / open-source**. No paid API dependency. CPU-only torch.

---

## pytest Detail

```
tests/test_cuad_order.py::test_synthetic_monotone_dataset        PASSED
tests/test_cuad_order.py::test_synthetic_non_monotone_dataset    PASSED
tests/test_cuad_order.py::test_synthetic_empty_answers_ignored   PASSED
tests/test_cuad_order.py::test_verification_report_keys          PASSED
tests/test_cuad_order.py::test_live_cuad_order_report_exists     SKIPPED (expected)
tests/test_cuad_order.py::test_live_cuad_report_has_verdict      SKIPPED (expected)
```

The 2 skipped tests require `ingest_cuad.py` to have been run first.
That is Prompt 02 work — the skips are expected and correct.

---

## Known Gaps / Deferred Work

| ID | Description | Deferred To |
|----|-------------|-------------|
| GAP-01 | pip 23.0.1 installed; 26.2.1 available (non-blocking) | Optional |
| GAP-02 | `aethergrid-sovereign` editable package visible in pip list (unrelated project, same venv) | No action |
| GAP-03 | 2 live-data pytest tests SKIPPED pending ingest run | Prompt 02 |
| GAP-04 | Contract §4 confidentiality (encryption, retention, privacy notice) — no storage code yet | Prompt 15+ |
| GAP-05 | No ML metrics produced yet — all future metrics must come from real runs per Contract §1 | Prompt 04+ |

---

## Contract Compliance

All 8 clauses of the Global Execution Contract are met for this prompt.
No fabricated numbers, no synthetic feedback presented as real,
no paid APIs, no Kubernetes, no production-ready claims.

---

## Starting Point for Prompt 02

**Goal:** Data ingestion — run the three ingest scripts, populate
`data/raw/` and `data/processed/`, make the 2 skipped live tests pass,
produce `data/processed/cuad/clause_order_verification.json`.

**First command:**
```
.venv\Scripts\python -m src.data.ingest_cuad
```

**Preconditions already met:**
- Python 3.10.11 venv fully operational
- All packages installed and importable
- `en_core_web_sm-3.8.0` loads cleanly
- 4/4 synthetic pytest tests passing
