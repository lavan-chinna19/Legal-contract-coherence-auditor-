"""
src/research/independent_benchmark/deduplication.py
Duplicate Detection, Near-Duplicate Candidate Identification and Cross-Family Audit.
"""
from typing import List, Tuple, Dict, Any
import itertools
import re

from src.research.independent_benchmark.schema import SourceDocumentRecord, DuplicateAuditRecord


def calculate_jaccard_similarity(text_a: str, text_b: str, shingle_size: int = 3) -> float:
    """Compute token-shingle Jaccard similarity between two texts."""
    tokens_a = re.findall(r"\b\w+\b", text_a.lower())
    tokens_b = re.findall(r"\b\w+\b", text_b.lower())
    if not tokens_a or not tokens_b:
        return 0.0

    shingles_a = set(" ".join(tokens_a[i:i+shingle_size]) for i in range(max(1, len(tokens_a) - shingle_size + 1)))
    shingles_b = set(" ".join(tokens_b[i:i+shingle_size]) for i in range(max(1, len(tokens_b) - shingle_size + 1)))

    intersection = len(shingles_a & shingles_b)
    union = len(shingles_a | shingles_b)
    if union == 0:
        return 0.0
    return round(intersection / union, 4)


def run_corpus_deduplication_audit(
    docs: List[SourceDocumentRecord],
    near_duplicate_threshold: float = 0.85
) -> List[DuplicateAuditRecord]:
    """
    Exhaustively audit all pairs of candidate parent contracts for:
    1. Exact raw byte duplicates
    2. Normalized text duplicates
    3. High-overlap near duplicates
    4. Cross-family boilerplate leakage
    """
    audit_records: List[DuplicateAuditRecord] = []

    # Map text content by doc id
    texts = {}
    for d in docs:
        with open(d.file_path, "r", encoding="utf-8", errors="ignore") as f:
            texts[d.parent_document_id] = f.read()

    for doc_a, doc_b in itertools.combinations(docs, 2):
        is_exact = doc_a.raw_sha256 == doc_b.raw_sha256
        is_norm = doc_a.normalized_text_sha256 == doc_b.normalized_text_sha256

        # Only compute Jaccard if lengths are somewhat comparable or same family
        len_ratio = min(len(texts[doc_a.parent_document_id]), len(texts[doc_b.parent_document_id])) / max(len(texts[doc_a.parent_document_id]), len(texts[doc_b.parent_document_id]))
        if len_ratio > 0.4:
            jaccard = calculate_jaccard_similarity(texts[doc_a.parent_document_id], texts[doc_b.parent_document_id])
        else:
            jaccard = 0.0

        if is_exact or is_norm:
            if doc_a.document_family_id == doc_b.document_family_id:
                verdict = "EXACT_DUPLICATE_SAME_FAMILY"
            else:
                verdict = "CROSS_FAMILY_COLLISION"
            notes = "Identical text detected."
        elif jaccard >= near_duplicate_threshold:
            if doc_a.document_family_id == doc_b.document_family_id:
                verdict = "NEAR_DUPLICATE_SAME_FAMILY"
            else:
                verdict = "CROSS_FAMILY_COLLISION"
            notes = f"High shingle overlap (Jaccard={jaccard})."
        else:
            verdict = "DISTINCT_INDEPENDENT"
            notes = "Documents distinct and independent."

        record = DuplicateAuditRecord(
            doc_id_a=doc_a.parent_document_id,
            doc_id_b=doc_b.parent_document_id,
            family_id_a=doc_a.document_family_id,
            family_id_b=doc_b.document_family_id,
            is_exact_byte_duplicate=is_exact,
            is_normalized_duplicate=is_norm,
            jaccard_similarity=jaccard,
            audit_verdict=verdict,
            notes=notes
        )
        audit_records.append(record)

    return audit_records
