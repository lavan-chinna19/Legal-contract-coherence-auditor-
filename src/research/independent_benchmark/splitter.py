"""
src/research/independent_benchmark/splitter.py
Source-Family Isolation and Splitter with Zero-Leakage Verification.
"""
from typing import List, Dict, Set, Tuple, Any
from collections import defaultdict

from src.research.independent_benchmark.schema import (
    SourceDocumentRecord,
    SplitAssignmentRecord,
    SplitPartition
)


def partition_source_families(
    docs: List[SourceDocumentRecord],
    dev_ratio: float = 0.60,
    val_ratio: float = 0.20,
    test_ratio: float = 0.20,
    deterministic_seed: int = 42
) -> Tuple[List[SourceDocumentRecord], List[SplitAssignmentRecord]]:
    """
    Partitions parent contracts strictly at the source-family (CIK) level
    BEFORE any transformations or perturbations are applied.

    Guarantees:
    - Zero parent-contract cross-split leakage
    - Zero corporate-entity family overlap between train, validation, and test
    """
    # Group parent documents by family
    family_to_docs = defaultdict(list)
    for doc in docs:
        family_to_docs[doc.document_family_id].append(doc)

    sorted_families = sorted(family_to_docs.keys())
    total_families = len(sorted_families)

    if total_families < 3:
        raise ValueError(f"Need at least 3 distinct families to create disjoint splits, got {total_families}")

    # Deterministic partition assignment
    # Target ~60% dev, ~20% val, ~20% test
    val_count = max(1, round(total_families * val_ratio))
    test_count = max(1, round(total_families * test_ratio))
    dev_count = total_families - val_count - test_count

    # To ensure balance across document counts, assign families deterministically
    dev_families: Set[str] = set()
    val_families: Set[str] = set()
    test_families: Set[str] = set()

    # Deterministic assignment using fixed indices
    # We assign:
    # Test: last test_count families
    # Val: preceding val_count families
    # Dev: remaining families
    for i, fam_id in enumerate(sorted_families):
        if i < dev_count:
            dev_families.add(fam_id)
        elif i < dev_count + val_count:
            val_families.add(fam_id)
        else:
            test_families.add(fam_id)

    # STRICT ASSERTIONS: Zero Leakage
    assert len(dev_families & val_families) == 0, "Leakage: dev and val families overlap!"
    assert len(dev_families & test_families) == 0, "Leakage: dev and test families overlap!"
    assert len(val_families & test_families) == 0, "Leakage: val and test families overlap!"
    assert len(dev_families | val_families | test_families) == total_families, "Unassigned family found!"

    split_records: List[SplitAssignmentRecord] = []
    updated_docs: List[SourceDocumentRecord] = []

    for fam_id, fam_docs in family_to_docs.items():
        if fam_id in dev_families:
            split = SplitPartition.DEVELOPMENT
        elif fam_id in val_families:
            split = SplitPartition.VALIDATION
        else:
            split = SplitPartition.SEALED_TEST

        org = fam_docs[0].source_organization
        parent_ids = [d.parent_document_id for d in fam_docs]

        split_records.append(SplitAssignmentRecord(
            document_family_id=fam_id,
            source_organization=org,
            split_assignment=split,
            parent_contract_count=len(fam_docs),
            parent_document_ids=parent_ids
        ))

        for d in fam_docs:
            d.split_assignment = split.value
            updated_docs.append(d)

    # Verify that no document has mismatched family split
    for d in updated_docs:
        expected_split = (
            SplitPartition.DEVELOPMENT.value if d.document_family_id in dev_families
            else SplitPartition.VALIDATION.value if d.document_family_id in val_families
            else SplitPartition.SEALED_TEST.value
        )
        assert d.split_assignment == expected_split, f"Doc {d.parent_document_id} split mismatch!"

    return updated_docs, split_records


def verify_split_disjointness(
    dev_docs: List[SourceDocumentRecord],
    val_docs: List[SourceDocumentRecord],
    test_docs: List[SourceDocumentRecord]
) -> Dict[str, Any]:
    """Verification assertions for split integrity."""
    dev_fams = set(d.document_family_id for d in dev_docs)
    val_fams = set(d.document_family_id for d in val_docs)
    test_fams = set(d.document_family_id for d in test_docs)

    dev_parents = set(d.parent_document_id for d in dev_docs)
    val_parents = set(d.parent_document_id for d in val_docs)
    test_parents = set(d.parent_document_id for d in test_docs)

    dev_val_overlap = dev_fams & val_fams
    dev_test_overlap = dev_fams & test_fams
    val_test_overlap = val_fams & test_fams

    parent_overlap = (dev_parents & val_parents) | (dev_parents & test_parents) | (val_parents & test_parents)

    is_clean = (
        len(dev_val_overlap) == 0 and
        len(dev_test_overlap) == 0 and
        len(val_test_overlap) == 0 and
        len(parent_overlap) == 0
    )

    return {
        "is_disjoint": is_clean,
        "dev_family_count": len(dev_fams),
        "val_family_count": len(val_fams),
        "test_family_count": len(test_fams),
        "dev_parent_count": len(dev_parents),
        "val_parent_count": len(val_parents),
        "test_parent_count": len(test_parents),
        "dev_val_family_overlap": list(dev_val_overlap),
        "dev_test_family_overlap": list(dev_test_overlap),
        "val_test_family_overlap": list(val_test_overlap),
        "parent_overlap": list(parent_overlap)
    }
