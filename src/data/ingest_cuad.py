"""
src/data/ingest_cuad.py — CUAD dataset ingestion + clause-order verification.

RESEARCH/DEMO PROJECT — not production-ready.

Downloads CUAD_v1.json directly from the Atticus Project's HuggingFace repository
(SQuAD-format QA JSON, 40 MB). The theatticusproject/cuad HuggingFace dataset
uses features=['pdf'] and cannot provide answer_start spans without pdfplumber
PDF extraction — so we bypass load_dataset entirely and use the canonical JSON.

Source URL (confirmed 200/40 MB by live probe 2026-08-23):
  https://huggingface.co/datasets/theatticusproject/cuad/resolve/main/CUAD_v1/CUAD_v1.json

License: CUAD is licensed CC BY 4.0.
See docs/data_governance.md for full notes.

Usage
-----
    python -m src.data.ingest_cuad [--limit N] [--dry-run]
"""

import argparse
import json
import sys
import time
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.config import (
    CUAD_HF_DATASET,
    CUAD_RAW_DIR,
    CUAD_PROCESSED,
    CUAD_ORDER_REPORT,
    ClauseRecord,
)

CUAD_JSON_URL = (
    "https://huggingface.co/datasets/theatticusproject/cuad"
    "/resolve/main/CUAD_v1/CUAD_v1.json"
)
CUAD_JSON_CACHE = CUAD_RAW_DIR / "CUAD_v1.json"

# CUAD question labels — 41 clause categories in the dataset
# Source: https://www.atticusprojectai.org/cuad
CUAD_CLAUSE_TYPES = [
    "Document Name", "Parties", "Agreement Date", "Effective Date",
    "Expiration Date", "Renewal Term", "Notice Period to Terminate Renewal",
    "Governing Law", "Most Favored Nation", "Non-Compete", "Exclusivity",
    "No-Solicit of Customers", "No-Solicit of Employees", "Non-Disparagement",
    "Limitation of Liability", "Uncapped Liability", "Cap on Liability",
    "Liquidated Damages", "Intellectual Property Ownership", "Joint IP Ownership",
    "License Grant", "Non-Transferable License", "Irrevocable or Perpetual License",
    "Source Code Escrow", "Post-Termination Services", "Audit Rights",
    "Uncapped Audit Rights", "Anti-Assignment", "Revenue/Profit Sharing",
    "Price Restrictions", "Minimum Commitment", "Volume Restriction",
    "IP Indemnification", "Third Party Beneficiary", "Warranty Duration",
    "Insurance", "Covenant Not to Sue", "Change of Control",
    "ROFR/ROFO/ROFN", "Competitive Restriction Exception", "General Description",
]


def download_cuad_json(force: bool = False) -> Path:
    """
    Download CUAD_v1.json from HuggingFace if not already cached.
    Returns local path to the JSON file.
    """
    import requests

    CUAD_RAW_DIR.mkdir(parents=True, exist_ok=True)
    if CUAD_JSON_CACHE.exists() and not force:
        size_mb = CUAD_JSON_CACHE.stat().st_size / 1_000_000
        print(f"[ingest_cuad] Using cached CUAD_v1.json ({size_mb:.1f} MB)")
        return CUAD_JSON_CACHE

    print(f"[ingest_cuad] Downloading CUAD_v1.json from HuggingFace (~40 MB)...")
    print(f"[ingest_cuad] URL: {CUAD_JSON_URL}")
    s = requests.Session()
    s.headers["User-Agent"] = "LegalCoherenceAuditor research@example.com"

    resp = s.get(CUAD_JSON_URL, timeout=120, stream=True)
    resp.raise_for_status()

    total = int(resp.headers.get("content-length", 0))
    downloaded = 0
    t0 = time.perf_counter()
    with open(CUAD_JSON_CACHE, "wb") as f:
        for chunk in resp.iter_content(chunk_size=1 << 20):
            f.write(chunk)
            downloaded += len(chunk)
            if total:
                pct = 100 * downloaded / total
                print(f"\r[ingest_cuad]   {pct:.0f}% ({downloaded//1_000_000} MB / {total//1_000_000} MB)",
                      end="", flush=True)
    elapsed = time.perf_counter() - t0
    print(f"\n[ingest_cuad] Downloaded in {elapsed:.1f}s -> {CUAD_JSON_CACHE}")
    return CUAD_JSON_CACHE


def load_cuad_squad_json(path: Path) -> dict:
    """
    Load CUAD_v1.json and convert SQuAD format into a datasets-compatible dict.

    SQuAD format:
      {"data": [{"title": str, "paragraphs": [{"context": str, "qas": [...]}]}]}

    Returns a dict {"train": list_of_rows} where each row has:
      title, context, question, answers: {answer_start: [int], text: [str]}
    """
    print(f"[ingest_cuad] Parsing CUAD SQuAD JSON ({path.stat().st_size//1_000_000} MB)...")
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)

    rows = []
    for article in raw.get("data", []):
        title = article.get("title", "unknown")
        for para in article.get("paragraphs", []):
            context = para.get("context", "")
            for qa in para.get("qas", []):
                question = qa.get("question", "")
                answers = qa.get("answers", [])
                starts = [a["answer_start"] for a in answers if "answer_start" in a]
                texts = [a["text"] for a in answers if "text" in a]
                rows.append({
                    "title": title,
                    "context": context,
                    "question": question,
                    "answers": {"answer_start": starts, "text": texts},
                })

    print(f"[ingest_cuad] Parsed {len(rows):,} QA rows from CUAD SQuAD JSON.")

    class _SimpleDataset:
        def __init__(self, rows):
            self._rows = rows
        def __len__(self):
            return len(self._rows)
        def __getitem__(self, idx):
            return self._rows[idx]
        def get(self, key, default=None):
            if key == "train":
                return self
            return default

    return {"train": _SimpleDataset(rows)}


def verify_clause_order(dataset) -> dict:
    """
    Explicitly verify whether CUAD preserves clause order from source documents.

    The CUAD dataset provides question-answer pairs where each answer is an
    extracted span with character offsets (answer_start). If clause order is
    preserved, the character offsets for answers within a contract should be
    monotonically non-decreasing when iterated in dataset order.

    CUAD is structured as a QA dataset — each row is a (document, question) pair.
    'Clause order preservation' means: within a single document's answers, are
    character offsets monotonically non-decreasing?

    This function:
    1. Groups all answer spans by document title.
    2. Checks whether offsets are monotonically non-decreasing within each doc.
    3. Reports the fraction of documents where order IS preserved.

    Returns a dict with the verification result and raw statistics.
    """
    results = {
        "verification_method": (
            "Group CUAD QA answers by document title; check if answer_start offsets "
            "are monotonically non-decreasing within each document when iterated "
            "in dataset row order."
        ),
        "dataset_source": "CUAD_v1.json (SQuAD format, CC BY 4.0)",
        "source_url": CUAD_JSON_URL,
        "note": (
            "CUAD is a QA dataset, not a sequential clause list. 'Order preservation' "
            "here means: within a given contract's extracted spans, are character "
            "offsets non-decreasing in dataset row order? This is a necessary but "
            "not sufficient condition for full clause-order preservation."
        ),
    }

    doc_spans: dict[str, list[int]] = defaultdict(list)

    train_data = dataset.get("train")
    if train_data is None:
        results["status"] = "ERROR: train split not found"
        return results

    n_rows = len(train_data)
    n_with_answers = 0
    n_no_answers = 0

    for i in range(n_rows):
        row = train_data[i]
        title = row.get("title", f"doc_{i}")
        answers = row.get("answers", {})
        starts = answers.get("answer_start", [])

        if starts:
            doc_spans[title].append(starts[0])
            n_with_answers += 1
        else:
            n_no_answers += 1

    results["total_rows"] = n_rows
    results["rows_with_answers"] = n_with_answers
    results["rows_without_answers"] = n_no_answers
    results["unique_documents"] = len(doc_spans)

    monotone_docs = 0
    non_monotone_docs = 0
    non_monotone_examples: list[dict] = []

    for title, offsets in doc_spans.items():
        if len(offsets) < 2:
            monotone_docs += 1
            continue
        is_monotone = all(offsets[i] <= offsets[i + 1] for i in range(len(offsets) - 1))
        if is_monotone:
            monotone_docs += 1
        else:
            non_monotone_docs += 1
            if len(non_monotone_examples) < 3:
                non_monotone_examples.append({
                    "title": title,
                    "offsets_sample": offsets[:10],
                })

    docs_checked = monotone_docs + non_monotone_docs
    pct_monotone = 100.0 * monotone_docs / docs_checked if docs_checked > 0 else 0.0

    results["documents_checked"] = docs_checked
    results["documents_monotone_ordered"] = monotone_docs
    results["documents_non_monotone"] = non_monotone_docs
    results["pct_documents_monotone"] = round(pct_monotone, 2)
    results["non_monotone_examples"] = non_monotone_examples

    if non_monotone_docs == 0:
        results["order_preserved"] = True
        results["verdict"] = (
            "VERIFIED: All CUAD documents in the train split have answer spans "
            "in monotonically non-decreasing character-offset order when iterated "
            "in dataset row order. Clause order IS preserved under this definition."
        )
    else:
        results["order_preserved"] = False
        results["verdict"] = (
            f"NOT FULLY VERIFIED: {non_monotone_docs} of {docs_checked} "
            f"documents ({100 - pct_monotone:.1f}%) have answer spans that are NOT "
            f"monotonically ordered. See non_monotone_examples."
        )

    print(f"[ingest_cuad] Order check: {results['verdict'][:120]}")
    return results


def ingest_cuad(limit: int | None = None, dry_run: bool = False) -> dict:
    """
    Download CUAD_v1.json, run clause-order verification, and write ClauseRecord output.

    Returns dict with record counts and the order-verification report.
    """
    # Step 1: Download / use cached JSON
    json_path = download_cuad_json()

    # Step 2: Parse SQuAD JSON into dataset-like object
    t0 = time.perf_counter()
    dataset = load_cuad_squad_json(json_path)
    elapsed = time.perf_counter() - t0
    print(f"[ingest_cuad] Loaded in {elapsed:.1f}s.")

    # Step 3: Clause-order verification BEFORE any transformation
    print("[ingest_cuad] Running clause-order verification ...")
    order_report = verify_clause_order(dataset)

    if not dry_run:
        CUAD_PROCESSED.mkdir(parents=True, exist_ok=True)
        CUAD_ORDER_REPORT.parent.mkdir(parents=True, exist_ok=True)
        with open(CUAD_ORDER_REPORT, "w", encoding="utf-8") as f:
            json.dump(order_report, f, indent=2)
        print(f"[ingest_cuad] Order report -> {CUAD_ORDER_REPORT}")

    # Step 4: Convert to ClauseRecord schema
    train_data = dataset.get("train")
    counts: dict[str, int] = {}

    if train_data is None:
        print("[ingest_cuad] WARNING: train split not found.", file=sys.stderr)
        return {"counts": counts, "order_report": order_report}

    records: list[ClauseRecord] = []
    n = len(train_data)
    if limit:
        n = min(n, limit)

    doc_seq_counter: dict[str, int] = defaultdict(int)

    for idx in range(n):
        row = train_data[idx]
        title = row.get("title", f"doc_{idx}")
        question = row.get("question", "")
        answers = row.get("answers", {})
        starts = answers.get("answer_start", [])
        texts = answers.get("text", [])

        if not texts:
            continue

        answer_text = texts[0]
        char_start = starts[0] if starts else 0
        doc_id = f"cuad_{title[:40].replace(' ', '_').replace('/', '_')}"
        seq = doc_seq_counter[doc_id]
        doc_seq_counter[doc_id] += 1

        rec = ClauseRecord(
            clause_id=f"{doc_id}_{seq:04d}",
            doc_id=doc_id,
            text=answer_text,
            label=question[:100],
            sequence_idx=seq,
            char_start=char_start,
            char_end=char_start + len(answer_text),
            source="cuad",
            split="train",
        )
        records.append(rec)

    counts["train"] = len(records)
    print(f"[ingest_cuad]   train: {len(records):,} answer records from "
          f"{len(doc_seq_counter)} documents")

    if not dry_run and records:
        out_path = CUAD_PROCESSED / "train.jsonl"
        with open(out_path, "w", encoding="utf-8") as f:
            for rec in records:
                f.write(json.dumps(rec.to_dict(), ensure_ascii=False) + "\n")
        print(f"[ingest_cuad]   Written -> {out_path}")

    return {"counts": counts, "order_report": order_report}


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest CUAD dataset with order verification")
    parser.add_argument("--limit", type=int, default=None,
                        help="Cap records for quick testing")
    parser.add_argument("--dry-run", action="store_true",
                        help="Do not write output files")
    parser.add_argument("--force-download", action="store_true",
                        help="Re-download CUAD_v1.json even if cached")
    args = parser.parse_args()

    result = ingest_cuad(limit=args.limit, dry_run=args.dry_run)
    print(json.dumps({
        "status": "ok",
        "counts": result.get("counts"),
        "order_preserved": result.get("order_report", {}).get("order_preserved"),
        "unique_documents": result.get("order_report", {}).get("unique_documents"),
        "rows_with_answers": result.get("order_report", {}).get("rows_with_answers"),
        "verdict": result.get("order_report", {}).get("verdict"),
    }, indent=2))


if __name__ == "__main__":
    main()
