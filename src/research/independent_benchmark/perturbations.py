"""
src/research/independent_benchmark/perturbations.py
Controlled, Copy-on-Write Benchmark Transformations for Structural Coherence.
"""
import copy
import hashlib
import re
from typing import List, Tuple, Optional, Dict, Any

from src.config import ClauseRecord
from src.research.independent_benchmark.schema import (
    BenchmarkCase,
    PerturbationRecord,
    SourceDocumentRecord
)
from src.research.independent_benchmark.oracle import (
    IndependentGroundTruthOracle,
    BACKWARD_DISCOURSE_PATTERNS
)


def make_clause_copy(clause: ClauseRecord, new_idx: Optional[int] = None) -> ClauseRecord:
    """Create a clean copy-on-write clone of a ClauseRecord."""
    return ClauseRecord(
        clause_id=clause.clause_id,
        doc_id=clause.doc_id,
        text=clause.text,
        label=getattr(clause, "label", "General Provision"),
        sequence_idx=new_idx if new_idx is not None else clause.sequence_idx,
        char_start=getattr(clause, "char_start", 0),
        char_end=getattr(clause, "char_end", len(clause.text)),
        source=getattr(clause, "source", "sec_edgar"),
        split=getattr(clause, "split", "none")
    )


def reindex_clauses(clauses: List[ClauseRecord]) -> List[ClauseRecord]:
    """Reindex sequence_idx for all clauses after reordering."""
    reindexed = []
    for i, c in enumerate(clauses):
        reindexed.append(make_clause_copy(c, new_idx=i))
    return reindexed


def find_clause_with_backward_discourse(clauses: List[ClauseRecord], min_idx: int = 1) -> Optional[int]:
    """Find the first clause index with an explicit backward discourse marker."""
    for i in range(min_idx, len(clauses)):
        hits = IndependentGroundTruthOracle.inspect_discourse_dependency(clauses[i].text)
        if hits:
            return i
    return None


def find_independent_covenant_pair(clauses: List[ClauseRecord]) -> Optional[Tuple[int, int]]:
    """
    Find two independent boilerplate covenants (e.g., governing law, notices,
    counterparts, severability) that do not reference each other.
    """
    kw_covenants = ["governing law", "notices", "counterparts", "severability", "entire agreement", "amendment", "waiver"]
    candidates = []
    for i, c in enumerate(clauses):
        text_lower = c.text.lower()
        if any(kw in text_lower for kw in kw_covenants):
            # Ensure no backward discourse marker
            if not IndependentGroundTruthOracle.inspect_discourse_dependency(c.text):
                candidates.append(i)

    if len(candidates) >= 2:
        return candidates[0], candidates[1]

    # Fallback: two middle clauses without markers
    mid = len(clauses) // 2
    for i in range(mid, len(clauses) - 2):
        if not IndependentGroundTruthOracle.inspect_discourse_dependency(clauses[i].text) and \
           not IndependentGroundTruthOracle.inspect_discourse_dependency(clauses[i+1].text):
            return i, i + 1
    return None


def find_dispute_or_arbitration_clause(clauses: List[ClauseRecord]) -> Optional[int]:
    """Find a dispute resolution, arbitration, or governing law clause for front-loading."""
    keywords = ["arbitration", "dispute resolution", "governing law", "jurisdiction", "venue"]
    for i in range(2, len(clauses)):
        t_low = clauses[i].text.lower()
        if any(kw in t_low for kw in keywords):
            return i
    return None


def find_definitions_clause(clauses: List[ClauseRecord]) -> Optional[int]:
    """Find a definitions or interpretation clause."""
    keywords = ["definitions", "defined terms", "certain definitions", "interpretation"]
    for i in range(1, len(clauses)):
        t_low = clauses[i].text.lower()
        if any(kw in t_low for kw in keywords):
            return i
    return None


class BenchmarkPerturbationEngine:
    """
    Constructs scientifically controlled, copy-on-write contract variants.
    """

    @classmethod
    def create_n1_clean_case(cls, doc: SourceDocumentRecord, clauses: List[ClauseRecord]) -> BenchmarkCase:
        """Create clean canonical control (N1)."""
        case_id = f"{doc.parent_document_id}_N1_CLEAN"
        orig = reindex_clauses(clauses)
        perturbed = reindex_clauses(clauses)

        source_hash = doc.raw_sha256
        perturbed_hash = doc.raw_sha256

        annotation = IndependentGroundTruthOracle.evaluate_transformation(
            original_clauses=orig,
            perturbed_clauses=perturbed,
            transformation_type="N1_CLEAN_CONTRACT",
            displaced_idx=0,
            target_idx=0,
            case_id=case_id,
            parent_id=doc.parent_document_id,
            family_id=doc.document_family_id,
            split=doc.split_assignment,
            source_hash=source_hash,
            perturbed_hash=perturbed_hash
        )

        perturbation = PerturbationRecord(
            case_id=case_id,
            parent_document_id=doc.parent_document_id,
            document_family_id=doc.document_family_id,
            split=doc.split_assignment,
            category_code="N1",
            transformation_name="Clean Canonical Contract",
            is_positive=False,
            is_hard_negative=False,
            is_ambiguous=False,
            source_clause_count=len(orig),
            perturbed_clause_count=len(perturbed),
            displaced_clause_indices=[],
            target_clause_indices=[],
            transformation_valid=True,
            deterministic_seed=42,
            description="Original unmodified SEC EDGAR contract"
        )

        return BenchmarkCase(annotation=annotation, perturbation=perturbation, original_clauses=orig, perturbed_clauses=perturbed)

    @classmethod
    def create_p1_discourse_inversion_case(cls, doc: SourceDocumentRecord, clauses: List[ClauseRecord]) -> Optional[BenchmarkCase]:
        """Create discourse dependency inversion (P1)."""
        idx = find_clause_with_backward_discourse(clauses, min_idx=1)
        if idx is None:
            return None

        case_id = f"{doc.parent_document_id}_P1_DISC_INV"
        orig = reindex_clauses(clauses)

        # Swap clause idx with clause idx - 1 (inverting discourse referent)
        perturbed_list = list(orig)
        perturbed_list[idx - 1], perturbed_list[idx] = perturbed_list[idx], perturbed_list[idx - 1]
        perturbed = reindex_clauses(perturbed_list)

        source_hash = doc.raw_sha256
        perturbed_text = "\n\n".join(c.text for c in perturbed)
        perturbed_hash = hashlib.sha256(perturbed_text.encode("utf-8")).hexdigest()

        annotation = IndependentGroundTruthOracle.evaluate_transformation(
            original_clauses=orig,
            perturbed_clauses=perturbed,
            transformation_type="P1_DISCOURSE_DEPENDENCY_INVERSION",
            displaced_idx=idx,
            target_idx=idx - 1,
            case_id=case_id,
            parent_id=doc.parent_document_id,
            family_id=doc.document_family_id,
            split=doc.split_assignment,
            source_hash=source_hash,
            perturbed_hash=perturbed_hash
        )

        perturbation = PerturbationRecord(
            case_id=case_id,
            parent_document_id=doc.parent_document_id,
            document_family_id=doc.document_family_id,
            split=doc.split_assignment,
            category_code="P1",
            transformation_name="Discourse Dependency Inversion",
            is_positive=True,
            is_hard_negative=False,
            is_ambiguous=False,
            source_clause_count=len(orig),
            perturbed_clause_count=len(perturbed),
            displaced_clause_indices=[idx],
            target_clause_indices=[idx - 1],
            transformation_valid=True,
            deterministic_seed=42,
            description=f"Inverted clause {idx} containing backward discourse referent with preceding clause {idx - 1}."
        )

        return BenchmarkCase(annotation=annotation, perturbation=perturbation, original_clauses=orig, perturbed_clauses=perturbed)

    @classmethod
    def create_p2_discourse_displacement_case(cls, doc: SourceDocumentRecord, clauses: List[ClauseRecord]) -> Optional[BenchmarkCase]:
        """Create discourse referent displacement to document start (P2)."""
        idx = find_clause_with_backward_discourse(clauses, min_idx=2)
        if idx is None:
            return None

        case_id = f"{doc.parent_document_id}_P2_DISC_DISP"
        orig = reindex_clauses(clauses)

        # Displace clause idx to position 0 (start of agreement)
        perturbed_list = list(orig)
        clause_to_move = perturbed_list.pop(idx)
        perturbed_list.insert(0, clause_to_move)
        perturbed = reindex_clauses(perturbed_list)

        source_hash = doc.raw_sha256
        perturbed_text = "\n\n".join(c.text for c in perturbed)
        perturbed_hash = hashlib.sha256(perturbed_text.encode("utf-8")).hexdigest()

        annotation = IndependentGroundTruthOracle.evaluate_transformation(
            original_clauses=orig,
            perturbed_clauses=perturbed,
            transformation_type="P2_DISCOURSE_REFERENT_DISPLACEMENT",
            displaced_idx=idx,
            target_idx=0,
            case_id=case_id,
            parent_id=doc.parent_document_id,
            family_id=doc.document_family_id,
            split=doc.split_assignment,
            source_hash=source_hash,
            perturbed_hash=perturbed_hash
        )

        perturbation = PerturbationRecord(
            case_id=case_id,
            parent_document_id=doc.parent_document_id,
            document_family_id=doc.document_family_id,
            split=doc.split_assignment,
            category_code="P2",
            transformation_name="Discourse Referent Long-Range Displacement",
            is_positive=True,
            is_hard_negative=False,
            is_ambiguous=False,
            source_clause_count=len(orig),
            perturbed_clause_count=len(perturbed),
            displaced_clause_indices=[idx],
            target_clause_indices=[0],
            transformation_valid=True,
            deterministic_seed=42,
            description=f"Relocated clause {idx} containing backward discourse referent to position 0."
        )

        return BenchmarkCase(annotation=annotation, perturbation=perturbation, original_clauses=orig, perturbed_clauses=perturbed)

    @classmethod
    def create_n2_covenant_swap_case(cls, doc: SourceDocumentRecord, clauses: List[ClauseRecord]) -> Optional[BenchmarkCase]:
        """Create valid commutative covenant swap (N2)."""
        pair = find_independent_covenant_pair(clauses)
        if pair is None:
            return None
        i, j = pair

        case_id = f"{doc.parent_document_id}_N2_COV_SWAP"
        orig = reindex_clauses(clauses)

        perturbed_list = list(orig)
        perturbed_list[i], perturbed_list[j] = perturbed_list[j], perturbed_list[i]
        perturbed = reindex_clauses(perturbed_list)

        source_hash = doc.raw_sha256
        perturbed_text = "\n\n".join(c.text for c in perturbed)
        perturbed_hash = hashlib.sha256(perturbed_text.encode("utf-8")).hexdigest()

        annotation = IndependentGroundTruthOracle.evaluate_transformation(
            original_clauses=orig,
            perturbed_clauses=perturbed,
            transformation_type="N2_INDEPENDENT_COVENANT_SWAP",
            displaced_idx=i,
            target_idx=j,
            case_id=case_id,
            parent_id=doc.parent_document_id,
            family_id=doc.document_family_id,
            split=doc.split_assignment,
            source_hash=source_hash,
            perturbed_hash=perturbed_hash
        )

        perturbation = PerturbationRecord(
            case_id=case_id,
            parent_document_id=doc.parent_document_id,
            document_family_id=doc.document_family_id,
            split=doc.split_assignment,
            category_code="N2",
            transformation_name="Independent Covenant Swap",
            is_positive=False,
            is_hard_negative=False,
            is_ambiguous=False,
            source_clause_count=len(orig),
            perturbed_clause_count=len(perturbed),
            displaced_clause_indices=[i, j],
            target_clause_indices=[j, i],
            transformation_valid=True,
            deterministic_seed=42,
            description=f"Swapped independent covenants {i} and {j} with zero discourse links."
        )

        return BenchmarkCase(annotation=annotation, perturbation=perturbation, original_clauses=orig, perturbed_clauses=perturbed)

    @classmethod
    def create_n3_hard_negative_dispute_case(cls, doc: SourceDocumentRecord, clauses: List[ClauseRecord]) -> Optional[BenchmarkCase]:
        """Create hard negative: front-loaded dispute resolution / arbitration notice (N3)."""
        idx = find_dispute_or_arbitration_clause(clauses)
        if idx is None:
            return None

        case_id = f"{doc.parent_document_id}_N3_FRONT_DISPUTE"
        orig = reindex_clauses(clauses)

        # Move dispute clause to index 1 (right after preamble)
        perturbed_list = list(orig)
        clause_to_move = perturbed_list.pop(idx)
        perturbed_list.insert(1, clause_to_move)
        perturbed = reindex_clauses(perturbed_list)

        source_hash = doc.raw_sha256
        perturbed_text = "\n\n".join(c.text for c in perturbed)
        perturbed_hash = hashlib.sha256(perturbed_text.encode("utf-8")).hexdigest()

        annotation = IndependentGroundTruthOracle.evaluate_transformation(
            original_clauses=orig,
            perturbed_clauses=perturbed,
            transformation_type="N3_FRONTLOADED_DISPUTE_NOTICE",
            displaced_idx=idx,
            target_idx=1,
            case_id=case_id,
            parent_id=doc.parent_document_id,
            family_id=doc.document_family_id,
            split=doc.split_assignment,
            source_hash=source_hash,
            perturbed_hash=perturbed_hash
        )

        perturbation = PerturbationRecord(
            case_id=case_id,
            parent_document_id=doc.parent_document_id,
            document_family_id=doc.document_family_id,
            split=doc.split_assignment,
            category_code="N3",
            transformation_name="Hard Negative: Front-Loaded Dispute Resolution",
            is_positive=False,
            is_hard_negative=True,
            is_ambiguous=False,
            source_clause_count=len(orig),
            perturbed_clause_count=len(perturbed),
            displaced_clause_indices=[idx],
            target_clause_indices=[1],
            transformation_valid=True,
            deterministic_seed=42,
            description=f"Front-loaded dispute resolution clause {idx} to index 1 (valid commercial drafting practice)."
        )

        return BenchmarkCase(annotation=annotation, perturbation=perturbation, original_clauses=orig, perturbed_clauses=perturbed)

    @classmethod
    def create_n4_hard_negative_definitions_case(cls, doc: SourceDocumentRecord, clauses: List[ClauseRecord]) -> Optional[BenchmarkCase]:
        """Create hard negative: front-loaded definitions / master schedule (N4)."""
        idx = find_definitions_clause(clauses)
        if idx is None or idx == 1:
            return None

        case_id = f"{doc.parent_document_id}_N4_FRONT_DEFS"
        orig = reindex_clauses(clauses)

        perturbed_list = list(orig)
        clause_to_move = perturbed_list.pop(idx)
        perturbed_list.insert(1, clause_to_move)
        perturbed = reindex_clauses(perturbed_list)

        source_hash = doc.raw_sha256
        perturbed_text = "\n\n".join(c.text for c in perturbed)
        perturbed_hash = hashlib.sha256(perturbed_text.encode("utf-8")).hexdigest()

        annotation = IndependentGroundTruthOracle.evaluate_transformation(
            original_clauses=orig,
            perturbed_clauses=perturbed,
            transformation_type="N4_FRONTLOADED_DEFINITIONS",
            displaced_idx=idx,
            target_idx=1,
            case_id=case_id,
            parent_id=doc.parent_document_id,
            family_id=doc.document_family_id,
            split=doc.split_assignment,
            source_hash=source_hash,
            perturbed_hash=perturbed_hash
        )

        perturbation = PerturbationRecord(
            case_id=case_id,
            parent_document_id=doc.parent_document_id,
            document_family_id=doc.document_family_id,
            split=doc.split_assignment,
            category_code="N4",
            transformation_name="Hard Negative: Front-Loaded Definitions",
            is_positive=False,
            is_hard_negative=True,
            is_ambiguous=False,
            source_clause_count=len(orig),
            perturbed_clause_count=len(perturbed),
            displaced_clause_indices=[idx],
            target_clause_indices=[1],
            transformation_valid=True,
            deterministic_seed=42,
            description=f"Front-loaded definitions clause {idx} to index 1."
        )

        return BenchmarkCase(annotation=annotation, perturbation=perturbation, original_clauses=orig, perturbed_clauses=perturbed)

    @classmethod
    def create_a1_ambiguous_case(cls, doc: SourceDocumentRecord, clauses: List[ClauseRecord]) -> Optional[BenchmarkCase]:
        """Create ambiguous case: middle non-discourse clause swap with unclear legal defect."""
        if len(clauses) < 8:
            return None
        i = len(clauses) // 3
        j = 2 * len(clauses) // 3

        case_id = f"{doc.parent_document_id}_A1_AMBIG_SWAP"
        orig = reindex_clauses(clauses)

        perturbed_list = list(orig)
        perturbed_list[i], perturbed_list[j] = perturbed_list[j], perturbed_list[i]
        perturbed = reindex_clauses(perturbed_list)

        source_hash = doc.raw_sha256
        perturbed_text = "\n\n".join(c.text for c in perturbed)
        perturbed_hash = hashlib.sha256(perturbed_text.encode("utf-8")).hexdigest()

        annotation = IndependentGroundTruthOracle.evaluate_transformation(
            original_clauses=orig,
            perturbed_clauses=perturbed,
            transformation_type="A1_AMBIGUOUS_REORDERING",
            displaced_idx=i,
            target_idx=j,
            case_id=case_id,
            parent_id=doc.parent_document_id,
            family_id=doc.document_family_id,
            split=doc.split_assignment,
            source_hash=source_hash,
            perturbed_hash=perturbed_hash
        )

        perturbation = PerturbationRecord(
            case_id=case_id,
            parent_document_id=doc.parent_document_id,
            document_family_id=doc.document_family_id,
            split=doc.split_assignment,
            category_code="A1",
            transformation_name="Ambiguous Non-Canonical Order",
            is_positive=False,
            is_hard_negative=False,
            is_ambiguous=True,
            source_clause_count=len(orig),
            perturbed_clause_count=len(perturbed),
            displaced_clause_indices=[i, j],
            target_clause_indices=[j, i],
            transformation_valid=True,
            deterministic_seed=42,
            description="Operational provisions reordered with indeterminate legal discourse impact."
        )

        return BenchmarkCase(annotation=annotation, perturbation=perturbation, original_clauses=orig, perturbed_clauses=perturbed)
