"""
src/data/ingest_edgar.py — SEC EDGAR EX-10 contract ingestion.

RESEARCH/DEMO PROJECT — not production-ready.

Strategy (verified by live API probing, 2026-08-23):
  1. Query EDGAR EFTS full-text search for 10-K filings in the target date range.
     (The EFTS search-index endpoint returns 0 results for forms=EX-10.1; only
     primary form types like 10-K work. This was discovered by live probe and
     documented in scratch/probe_edgar*.py.)
  2. For each 10-K filing, fetch the HTML filing index and parse out EX-10.x
     exhibit document links (genuine material-contract exhibits, not EX-101.* XBRL).
  3. Download the exhibit text and save to git-ignored data/raw/sec_edgar/.
  4. Record provenance metadata in edgar_manifest.json (no contract text in manifest).

PRIVACY / CONTRACT §4 COMPLIANCE:
- Contract text written ONLY to git-ignored data/raw/sec_edgar/ — never to logs.
- Manifest records metadata only (URL, filing date, accession number, char_length).
- No contract content written to stdout or application logs.

License: SEC EDGAR filings are US federal government works — public domain.
See docs/data_governance.md for full notes.

Usage
-----
    python -m src.data.ingest_edgar [--target N] [--dry-run]
"""

import argparse
import json
import sys
import time
import re
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.config import (
    EDGAR_RAW_DIR,
    EDGAR_MANIFEST,
    EDGAR_USER_AGENT,
    EDGAR_RATE_LIMIT_SEC,
    EDGAR_TARGET_COUNT,
    EDGAR_DATE_START,
    EDGAR_DATE_END,
)

EFTS_SEARCH_URL = "https://efts.sec.gov/LATEST/search-index"
EDGAR_ARCHIVES_BASE = "https://www.sec.gov/Archives"

# EX-10.x genuine material-contract pattern.
# Excludes EX-101.* (XBRL taxonomy files) which are not contracts.
EX10_PATTERN = re.compile(r"^EX-10(\.\d+)?$", re.IGNORECASE)


def _headers(host: str = "efts.sec.gov") -> dict:
    """SEC requires a descriptive User-Agent. https://www.sec.gov/os/accessing-edgar-data"""
    return {
        "User-Agent": EDGAR_USER_AGENT,
        "Accept-Encoding": "gzip, deflate",
        "Host": host,
    }


def _sleep():
    time.sleep(EDGAR_RATE_LIMIT_SEC)


def search_10k_filings(session, target: int) -> list[dict]:
    """
    Query EFTS for 10-K filings in the configured date range.
    Returns list of dicts with keys: adsh, cik, display_name, file_date, form.

    NOTE: EFTS search-index returns 0 hits for forms=EX-10.1 (confirmed by
    live probe 2026-08-23). We search for 10-K filings and extract EX-10
    exhibits from their filing indexes.
    """
    filings = []
    from_idx = 0
    page_size = 100  # EFTS max per page

    while len(filings) < target * 3:  # fetch more 10-Ks than needed (many won't have EX-10)
        params = {
            "forms": "10-K",
            "dateRange": "custom",
            "startdt": EDGAR_DATE_START,
            "enddt": EDGAR_DATE_END,
            "from": from_idx,
        }
        print(f"[ingest_edgar] EFTS query from={from_idx} ...")
        try:
            resp = session.get(EFTS_SEARCH_URL, params=params, timeout=30)
            resp.raise_for_status()
        except Exception as exc:
            print(f"[ingest_edgar] EFTS query failed: {exc}", file=sys.stderr)
            break

        data = resp.json()
        hits = data.get("hits", {}).get("hits", [])
        total = data.get("hits", {}).get("total", {}).get("value", 0)

        if not hits:
            print(f"[ingest_edgar] No more hits (total={total}).")
            break

        for hit in hits:
            src = hit.get("_source", {})
            adsh = src.get("adsh", "")
            ciks = src.get("ciks", [])
            cik = ciks[0].lstrip("0") if ciks else ""
            name = src.get("display_names", ["unknown"])[0]
            file_date = src.get("file_date", "unknown")
            form = src.get("form", "10-K")
            if adsh and cik:
                filings.append({
                    "adsh": adsh,
                    "cik": cik,
                    "display_name": name,
                    "file_date": file_date,
                    "form": form,
                })

        from_idx += page_size
        _sleep()

        # Stop if we've gathered enough 10-K candidates
        if from_idx >= min(total, target * 5):
            break

    print(f"[ingest_edgar] Collected {len(filings)} 10-K filing candidates.")
    return filings


def get_ex10_docs_from_filing(session, adsh: str, cik: str) -> list[dict]:
    """
    Fetch the filing index HTML for a 10-K and extract EX-10.x document links.
    Returns list of dicts with keys: exhibit_type, doc_url.
    Excludes EX-101.* XBRL files.
    """
    acc_clean = adsh.replace("-", "")
    index_url = (
        f"{EDGAR_ARCHIVES_BASE}/edgar/data/{cik}/{acc_clean}/{adsh}-index.htm"
    )
    try:
        resp = session.get(
            index_url,
            headers={**_headers("www.sec.gov"), "Host": "www.sec.gov"},
            timeout=30,
        )
        if not resp.ok:
            return []
        html = resp.text
    except Exception as exc:
        print(f"[ingest_edgar]   Index fetch failed for {adsh}: {exc}", file=sys.stderr)
        return []

    # Parse the filing index table.
    # EDGAR HTML structure: rows contain <td> cells with:
    #   [seq] [description] [document link] [type] [size]
    # The <a href> and <td>type</td> are in the same row but the type cell
    # comes AFTER the link. We parse row-by-row.
    ex10_docs = []
    rows = re.findall(r"<tr[^>]*>(.*?)</tr>", html, re.IGNORECASE | re.DOTALL)
    for row in rows:
        # Extract all <td> contents in this row
        cells = re.findall(r"<td[^>]*>(.*?)</td>", row, re.IGNORECASE | re.DOTALL)
        if len(cells) < 3:
            continue

        # Look for a cell containing an /Archives/ link
        link_match = None
        for cell in cells:
            m = re.search(r'href="(/Archives/edgar/data/[^"]+)"', cell, re.IGNORECASE)
            if m:
                link_match = m.group(1)
                break

        if not link_match:
            continue

        # The type is in another cell — strip tags and check
        cell_texts = [re.sub(r"<[^>]+>", "", c).strip() for c in cells]
        exhibit_type = ""
        for ct in cell_texts:
            if EX10_PATTERN.match(ct):
                exhibit_type = ct
                break

        if exhibit_type:
            doc_url = f"https://www.sec.gov{link_match}"
            ex10_docs.append({"exhibit_type": exhibit_type, "doc_url": doc_url})

    return ex10_docs


def fetch_document_text(session, doc_url: str) -> str | None:
    """
    Fetch the text of an EX-10 document.
    Returns None on failure. Never raises.
    NOTE (Contract §4): returned text must NOT be written to logs.
    """
    try:
        resp = session.get(
            doc_url,
            headers={**_headers("www.sec.gov"), "Host": "www.sec.gov"},
            timeout=60,
        )
        if resp.ok and len(resp.content) > 500:
            return resp.text
        return None
    except Exception as exc:
        print(f"[ingest_edgar]   Fetch failed {doc_url}: {exc}", file=sys.stderr)
        return None


def ingest_edgar(target: int = EDGAR_TARGET_COUNT, dry_run: bool = False) -> dict:
    """
    Main ingestion function.

    Returns
    -------
    dict with manifest_count, fetched_count, failed_count.
    """
    try:
        import requests
    except ImportError as exc:
        raise ImportError("requests not installed.") from exc

    EDGAR_RAW_DIR.mkdir(parents=True, exist_ok=True)

    session = requests.Session()
    session.headers.update(_headers())

    print(f"[ingest_edgar] Starting SEC EDGAR fetch (target={target}, dry_run={dry_run})")
    print(f"[ingest_edgar] User-Agent: {EDGAR_USER_AGENT}")
    print(f"[ingest_edgar] Date range: {EDGAR_DATE_START} to {EDGAR_DATE_END}")
    print(f"[ingest_edgar] Strategy: EFTS 10-K search -> filing index -> EX-10.x extraction")
    print(f"[ingest_edgar] NOTE: forms=EX-10.1 returns 0 hits from EFTS (confirmed by probe).")

    # Step 1: Get pool of 10-K filings
    candidates = search_10k_filings(session, target)

    manifest_entries: list[dict] = []
    fetched = 0
    failed = 0
    skipped_no_ex10 = 0

    # Step 2: For each candidate, look for EX-10 exhibits
    for filing in candidates:
        if fetched >= target:
            break

        adsh = filing["adsh"]
        cik = filing["cik"]
        _sleep()

        ex10_docs = get_ex10_docs_from_filing(session, adsh, cik)
        if not ex10_docs:
            skipped_no_ex10 += 1
            continue

        print(f"[ingest_edgar] {adsh} -> {len(ex10_docs)} EX-10 doc(s) | {filing['display_name'][:50]}")

        for doc_info in ex10_docs:
            if fetched >= target:
                break

            doc_url = doc_info["doc_url"]
            exhibit_type = doc_info["exhibit_type"]

            entry = {
                "accession_no": adsh,
                "cik": cik,
                "entity_name": filing["display_name"],
                "form_type": filing["form"],
                "exhibit_type": exhibit_type,
                "file_date": filing["file_date"],
                "retrieval_timestamp": datetime.now(timezone.utc).isoformat(),
                "source_url": doc_url,
                "status": "pending",
            }

            if not dry_run:
                _sleep()
                text = fetch_document_text(session, doc_url)
                if text and len(text) > 500:
                    safe_name = adsh.replace("-", "_")
                    out_path = EDGAR_RAW_DIR / f"{safe_name}_{exhibit_type.replace('.','_')}.txt"
                    # Contract §4: text to git-ignored file only, never to logs
                    out_path.write_text(text, encoding="utf-8", errors="replace")
                    entry["status"] = "fetched"
                    entry["local_path"] = str(out_path)
                    entry["char_length"] = len(text)
                    fetched += 1
                    print(f"[ingest_edgar]   [OK] fetched {exhibit_type} ({len(text):,} chars)")
                else:
                    entry["status"] = "fetch_failed_or_empty"
                    failed += 1
                    print(f"[ingest_edgar]   [FAIL] empty/failed {doc_url[:60]}")
            else:
                entry["status"] = "dry_run"
                fetched += 1

            manifest_entries.append(entry)

    if not dry_run:
        EDGAR_MANIFEST.parent.mkdir(parents=True, exist_ok=True)
        with open(EDGAR_MANIFEST, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                    "strategy": "EFTS 10-K search → filing index HTML → EX-10.x extraction",
                    "efts_note": "forms=EX-10.1 returns 0 hits; 10-K search used instead (probed 2026-08-23)",
                    "target_count": target,
                    "candidates_checked": len(candidates),
                    "skipped_no_ex10": skipped_no_ex10,
                    "manifest_count": len(manifest_entries),
                    "fetched_count": fetched,
                    "failed_count": failed,
                    "entries": manifest_entries,
                },
                f,
                indent=2,
            )
        print(f"[ingest_edgar] Manifest -> {EDGAR_MANIFEST}")

    result = {
        "manifest_count": len(manifest_entries),
        "fetched_count": fetched,
        "failed_count": failed,
        "skipped_no_ex10": skipped_no_ex10,
    }
    print(f"[ingest_edgar] Done: {result}")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest SEC EDGAR EX-10 contracts")
    parser.add_argument("--target", type=int, default=EDGAR_TARGET_COUNT,
                        help=f"Number of EX-10 documents to fetch (default: {EDGAR_TARGET_COUNT})")
    parser.add_argument("--dry-run", action="store_true",
                        help="Collect metadata only; do not fetch or write files")
    args = parser.parse_args()

    result = ingest_edgar(target=args.target, dry_run=args.dry_run)
    print(json.dumps({"status": "ok", "result": result}, indent=2))


if __name__ == "__main__":
    main()
