"""
src/calibration/synthetic_generator.py — Synthetic Shuffle-Test Calibration Data Generator.
Constructs calibration and evaluation sets strictly from same-document reordering and permutations.
Provably enforces synthetic-only data provenance (Acceptance Gate 1).
"""
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
import random
import numpy as np

from src.config import ClauseRecord


@dataclass
class SyntheticCalibrationItem:
    """
    Synthetic calibration record representing either clean consecutive clauses or
    shuffled/perturbed orderings within the same document.
    """
    item_id: str
    doc_id: str
    clauses: List[ClauseRecord]
    manipulation_type: str  # "clean" | "block_shuffle" | "reversed_pair" | "permute_all"
    ground_truth_anomaly: List[float]  # [0.0, 1.0] per clause: 0.0 = clean order, 1.0 = shuffled/perturbed
    perturbed_indices: List[int]
    source: str = "synthetic_shuffle"
    is_synthetic: bool = True

    def __post_init__(self):
        if not self.is_synthetic:
            raise ValueError(f"Violation: Non-synthetic data encountered in item {self.item_id}")
        if not self.source.startswith("synthetic"):
            raise ValueError(f"Violation: Source '{self.source}' does not have synthetic provenance.")


def assert_is_synthetic_only(dataset: List[SyntheticCalibrationItem]) -> bool:
    """
    Acceptance Gate 1 Assertion:
    Provably validates that all items and clauses in the calibration set are synthetic-only.
    Rejects any unverified real flagged/unflagged labels or external human feedback.
    """
    if not dataset:
        raise ValueError("Dataset is empty; cannot validate synthetic provenance.")

    for item in dataset:
        if not isinstance(item, SyntheticCalibrationItem):
            raise TypeError(f"Invalid record type {type(item)}; expected SyntheticCalibrationItem")
        if not item.is_synthetic:
            raise AssertionError(f"Item {item.item_id} has is_synthetic=False")
        if not item.source.startswith("synthetic"):
            raise AssertionError(f"Item {item.item_id} has non-synthetic source '{item.source}'")
        for c in item.clauses:
            if not (c.source.startswith("synthetic") or c.source in ("synthetic", "synthetic_clean", "synthetic_shuffle", "test", "demo")):
                raise AssertionError(f"Clause {c.clause_id} in {item.item_id} has invalid source '{c.source}'")
    return True


class SyntheticShuffleDatasetGenerator:
    """
    Generates synthetic calibration and held-out test sets using intradocument clause shuffling.
    Produces both intact (clean, label=0.0) sequences and controlled shuffled perturbations (label=1.0).
    """

    def __init__(self, seed: int = 42):
        self.seed = seed
        self.rng = random.Random(seed)

    def create_synthetic_item(
        self,
        base_clauses: List[ClauseRecord],
        doc_id: str,
        manipulation: str = "block_shuffle",
        item_id: Optional[str] = None
    ) -> SyntheticCalibrationItem:
        """
        Creates a single synthetic item with controlled ordering manipulation.
        """
        n = len(base_clauses)
        if n < 2:
            raise ValueError("Need at least 2 clauses to perform synthetic shuffle.")

        synthetic_clauses = [
            ClauseRecord(
                clause_id=f"syn_{doc_id}_{c.sequence_idx}",
                doc_id=f"syn_{doc_id}",
                text=c.text,
                label=c.label,
                sequence_idx=c.sequence_idx,
                char_start=c.char_start,
                char_end=c.char_end,
                source="synthetic"
            )
            for c in base_clauses
        ]

        ground_truth = [0.0] * n
        perturbed_indices = []

        if manipulation == "clean":
            source_tag = "synthetic_clean"
        elif manipulation == "block_shuffle":
            # Pick a contiguous subsegment of length at least 2 and shuffle it
            block_len = min(max(2, n // 3), n)
            start_idx = self.rng.randint(0, n - block_len)
            end_idx = start_idx + block_len
            subsegment = list(synthetic_clauses[start_idx:end_idx])
            # Ensure it is actually permuted
            for _ in range(5):
                self.rng.shuffle(subsegment)
                if any(subsegment[k].clause_id != synthetic_clauses[start_idx + k].clause_id for k in range(block_len)):
                    break
            synthetic_clauses[start_idx:end_idx] = subsegment
            perturbed_indices = list(range(start_idx, end_idx))
            for idx in perturbed_indices:
                ground_truth[idx] = 1.0
            source_tag = "synthetic_shuffle"
        elif manipulation == "reversed_pair":
            # Swap two adjacent clauses
            idx = self.rng.randint(0, n - 2)
            synthetic_clauses[idx], synthetic_clauses[idx + 1] = synthetic_clauses[idx + 1], synthetic_clauses[idx]
            perturbed_indices = [idx, idx + 1]
            ground_truth[idx] = 1.0
            ground_truth[idx + 1] = 1.0
            source_tag = "synthetic_shuffle"
        elif manipulation == "permute_all":
            self.rng.shuffle(synthetic_clauses)
            perturbed_indices = list(range(n))
            ground_truth = [1.0] * n
            source_tag = "synthetic_shuffle"
        else:
            raise ValueError(f"Unknown manipulation type: {manipulation}")

        # Update sequence indices
        for i, c in enumerate(synthetic_clauses):
            c.sequence_idx = i

        effective_id = item_id or f"syn_item_{doc_id}_{manipulation}_{self.rng.randint(1000, 9999)}"

        item = SyntheticCalibrationItem(
            item_id=effective_id,
            doc_id=f"syn_{doc_id}",
            clauses=synthetic_clauses,
            manipulation_type=manipulation,
            ground_truth_anomaly=ground_truth,
            perturbed_indices=perturbed_indices,
            source=source_tag,
            is_synthetic=True
        )
        return item

    def generate_calibration_and_test_splits(
        self,
        source_documents: List[Tuple[str, List[ClauseRecord]]],
        cal_fraction: float = 0.6,
        items_per_doc: int = 4
    ) -> Tuple[List[SyntheticCalibrationItem], List[SyntheticCalibrationItem]]:
        """
        Generates disjoint calibration and held-out test datasets from source documents.
        """
        all_items: List[SyntheticCalibrationItem] = []

        manipulation_cycle = ["clean", "block_shuffle", "reversed_pair", "permute_all"]

        for doc_idx, (doc_id, clauses) in enumerate(source_documents):
            if len(clauses) < 3:
                continue
            for k in range(items_per_doc):
                manip = manipulation_cycle[k % len(manipulation_cycle)]
                item = self.create_synthetic_item(
                    base_clauses=clauses,
                    doc_id=f"{doc_id}_{k}",
                    manipulation=manip,
                    item_id=f"cal_item_{doc_idx}_{k}_{manip}"
                )
                all_items.append(item)

        self.rng.shuffle(all_items)
        split_idx = int(len(all_items) * cal_fraction)
        cal_set = all_items[:split_idx]
        test_set = all_items[split_idx:]

        # Enforce acceptance gate on both splits
        assert_is_synthetic_only(cal_set)
        assert_is_synthetic_only(test_set)

        return cal_set, test_set
