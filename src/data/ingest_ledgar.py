"""
src/data/ingest_ledgar.py — LEDGAR dataset ingestion.

RESEARCH/DEMO PROJECT — not production-ready.

Downloads LEDGAR via the HuggingFace `datasets` library (lex_glue / ledgar config).
Normalises records into the ClauseRecord schema and saves processed splits as
newline-delimited JSON under data/processed/ledgar/.

License: LEDGAR is distributed for research purposes.
See docs/data_governance.md for full licensing notes.

Usage
-----
    python -m src.data.ingest_ledgar [--limit N]

Options
-------
    --limit N   If provided, cap each split at N records (useful for quick testing).
                Default: no limit (full dataset).
    --dry-run   Print counts only; do not write output files.
"""

import argparse
import json
import sys
import time
from pathlib import Path

# Ensure repo root is on path when called as a script
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.config import (
    LEDGAR_HF_DATASET,
    LEDGAR_HF_CONFIG,
    LEDGAR_TEXT_FIELD,
    LEDGAR_LABEL_FIELD,
    LEDGAR_PROCESSED,
    ClauseRecord,
)


def ingest_ledgar(limit: int | None = None, dry_run: bool = False) -> dict:
    """
    Download and process LEDGAR.

    Returns
    -------
    dict with keys 'train', 'val', 'test', each mapping to record count.
    Raises on download or parse failure.
    """
    try:
        from datasets import load_dataset
    except ImportError as exc:
        raise ImportError(
            "datasets package not installed. Run: pip install datasets"
        ) from exc

    print(f"[ingest_ledgar] Loading '{LEDGAR_HF_DATASET}' / '{LEDGAR_HF_CONFIG}' from HuggingFace...")
    t0 = time.perf_counter()

    # LEDGAR in lex_glue has pre-defined train/validation/test splits
    try:
        dataset = load_dataset(LEDGAR_HF_DATASET, LEDGAR_HF_CONFIG)
    except Exception as exc:
        print(f"[ingest_ledgar] ERROR loading dataset: {exc}", file=sys.stderr)
        raise

    elapsed = time.perf_counter() - t0
    print(f"[ingest_ledgar] Dataset loaded in {elapsed:.1f}s. Splits: {list(dataset.keys())}")

    split_map = {
        "train": dataset.get("train"),
        "val": dataset.get("validation"),
        "test": dataset.get("test"),
    }

    counts: dict[str, int] = {}

    if not dry_run:
        LEDGAR_PROCESSED.mkdir(parents=True, exist_ok=True)

    for split_name, split_data in split_map.items():
        if split_data is None:
            print(f"[ingest_ledgar] WARNING: split '{split_name}' not found; skipping.")
            counts[split_name] = 0
            continue

        records: list[ClauseRecord] = []
        n = len(split_data)
        if limit:
            n = min(n, limit)

        for idx in range(n):
            row = split_data[idx]
            text = row[LEDGAR_TEXT_FIELD]
            label = str(row[LEDGAR_LABEL_FIELD])
            # Build a deterministic doc_id from dataset + split + index
            doc_id = f"ledgar_{split_name}_{idx:06d}"
            clause_id = f"{doc_id}_0"  # LEDGAR records are single clauses

            rec = ClauseRecord(
                clause_id=clause_id,
                doc_id=doc_id,
                text=text,
                label=label,
                sequence_idx=0,
                char_start=0,
                char_end=len(text),
                source="ledgar",
                split=split_name,
            )
            records.append(rec)

        counts[split_name] = len(records)
        print(f"[ingest_ledgar]   {split_name}: {len(records):,} records")

        if not dry_run:
            out_path = LEDGAR_PROCESSED / f"{split_name}.jsonl"
            with open(out_path, "w", encoding="utf-8") as f:
                for rec in records:
                    # IMPORTANT (Contract §4): text is written to local processed data file,
                    # NOT to application logs. This file is git-ignored.
                    f.write(json.dumps(rec.to_dict(), ensure_ascii=False) + "\n")
            print(f"[ingest_ledgar]   Written to {out_path}")

    total = sum(counts.values())
    print(f"[ingest_ledgar] Done. Total records: {total:,}")
    return counts


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest LEDGAR dataset (lex_glue/ledgar)")
    parser.add_argument("--limit", type=int, default=None,
                        help="Cap records per split (for quick testing)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print counts only, do not write files")
    args = parser.parse_args()

    counts = ingest_ledgar(limit=args.limit, dry_run=args.dry_run)
    print(json.dumps({"status": "ok", "counts": counts}, indent=2))


if __name__ == "__main__":
    main()
