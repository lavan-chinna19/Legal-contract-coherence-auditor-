"""
src/research/independent_benchmark/provenance.py
Data Provenance and Source Manifest Audit for SEC EDGAR Contract Corpus.
"""
import hashlib
import json
import os
import re
from typing import List, Dict, Any, Optional

from src.research.independent_benchmark.schema import SourceDocumentRecord
from src.segmentation.rule_based import RuleBasedSegmenter


def compute_normalized_text(raw_text: str) -> str:
    """Normalize text by collapsing whitespace and lowercasing."""
    return re.sub(r"\s+", " ", raw_text).strip().lower()


def compute_sha256(text: str) -> str:
    """Compute SHA-256 hash of a string."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def compute_content_fingerprint(text: str) -> str:
    """
    Compute a 64-bit SimHash hexadecimal fingerprint over word 3-grams
    for fast near-duplicate identification.
    """
    words = re.findall(r"\b\w+\b", text.lower())
    if not words:
        return "0" * 16
    shingles = [" ".join(words[i:i+3]) for i in range(max(1, len(words) - 2))]
    if not shingles:
        shingles = words

    v = [0] * 64
    for shingle in shingles:
        h = int(hashlib.md5(shingle.encode("utf-8")).hexdigest(), 16)
        for i in range(64):
            bit = (h >> i) & 1
            if bit == 1:
                v[i] += 1
            else:
                v[i] -= 1

    fingerprint = 0
    for i in range(64):
        if v[i] > 0:
            fingerprint |= (1 << i)
    return f"{fingerprint:016x}"


def infer_contract_type(text_sample: str, exhibit_type: str) -> str:
    """Infer high-level commercial contract type from text and exhibit metadata."""
    sample = text_sample[:2000].lower()
    if "employment agreement" in sample or "executive employment" in sample:
        return "Executive Employment Agreement"
    elif "credit agreement" in sample or "loan agreement" in sample or "revolving credit" in sample:
        return "Credit and Financing Agreement"
    elif "license agreement" in sample or "intellectual property" in sample:
        return "Intellectual Property License"
    elif "supply agreement" in sample or "manufacturing agreement" in sample:
        return "Commercial Supply Agreement"
    elif "lease agreement" in sample or "sublease" in sample:
        return "Commercial Real Estate Lease"
    elif "service agreement" in sample or "services agreement" in sample:
        return "Master Services Agreement"
    elif "stock purchase" in sample or "asset purchase" in sample:
        return "Purchase and Sale Agreement"
    elif "severance agreement" in sample or "separation agreement" in sample:
        return "Executive Separation Agreement"
    elif "incentive plan" in sample or "award agreement" in sample or "stock award" in sample:
        return "Equity Incentive Award Agreement"
    elif "indemnification agreement" in sample:
        return "Director Indemnification Agreement"
    else:
        return f"Material Contract Exhibit ({exhibit_type})"


def load_edgar_source_corpus(
    manifest_path: str = "data/raw/sec_edgar/edgar_manifest.json",
    min_clauses: int = 10,
    max_clauses: int = 125
) -> List[SourceDocumentRecord]:
    """
    Load raw SEC EDGAR contracts, segment clauses, compute cryptographic hashes
    and provenance records. Filters to pilot candidates within clause bounds.
    """
    if not os.path.exists(manifest_path):
        raise FileNotFoundError(f"EDGAR manifest not found at {manifest_path}")

    with open(manifest_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    entries = data.get("entries", [])
    segmenter = RuleBasedSegmenter()
    records: List[SourceDocumentRecord] = []

    for entry in entries:
        path = entry.get("local_path", "")
        if not os.path.exists(path):
            continue

        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            raw_text = f.read()

        norm_text = compute_normalized_text(raw_text)
        raw_hash = compute_sha256(raw_text)
        norm_hash = compute_sha256(norm_text)
        fingerprint = compute_content_fingerprint(norm_text)

        clauses = segmenter.segment(raw_text)
        clause_count = len(clauses)

        if not (min_clauses <= clause_count <= max_clauses):
            continue

        cik = entry.get("cik", "UNKNOWN")
        exhibit = entry.get("exhibit_type", "EX-10")
        clean_exhibit = re.sub(r"[^a-zA-Z0-9]", "_", exhibit)
        parent_doc_id = f"SEC_CIK{cik}_{clean_exhibit}"
        family_id = f"FAM_CIK_{cik}"
        contract_type = infer_contract_type(raw_text, exhibit)

        record = SourceDocumentRecord(
            parent_document_id=parent_doc_id,
            document_family_id=family_id,
            source_uri_or_reference=entry.get("source_url", "https://www.sec.gov/edgar"),
            source_type="SEC_EDGAR_EXHIBIT_10",
            contract_type=contract_type,
            source_organization=entry.get("entity_name", "UNKNOWN"),
            acquisition_date=entry.get("file_date", entry.get("retrieval_timestamp", "2023-12-31")),
            license_status="PUBLIC_DOMAIN_US_FEDERAL_FILING",
            raw_sha256=raw_hash,
            normalized_text_sha256=norm_hash,
            content_fingerprint=fingerprint,
            parser_version="RuleBasedSegmenter_v1.0",
            clause_segmentation_version="ClauseRecord_v1.0",
            split_assignment="UNASSIGNED",
            provenance_confidence="HIGH_OFFICIAL_FILING",
            clause_count=clause_count,
            char_length=len(raw_text),
            file_path=path
        )
        records.append(record)

    return records
