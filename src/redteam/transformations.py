"""
src/redteam/transformations.py — Deterministic, pure, copy-on-write contract perturbation library.
Generates controlled variations without mutating original ClauseRecord objects or documents.
"""
import copy
import re
import hashlib
from typing import List, Dict, Tuple, Any, Optional
from src.config import ClauseRecord


def compute_clauses_checksum(clauses: List[ClauseRecord]) -> str:
    """Computes SHA-256 hash across full concatenated text of clauses in sequence."""
    h = hashlib.sha256()
    for c in clauses:
        h.update(f"{c.sequence_idx}:{c.clause_id}:{c.text}\n".encode("utf-8"))
    return h.hexdigest()


def _reindex_clauses(clauses: List[ClauseRecord]) -> List[ClauseRecord]:
    """Re-indexes sequence_idx monotonically from 0 to N-1 and preserves all other fields."""
    reindexed = []
    current_char = 0
    for idx, c in enumerate(clauses):
        text_len = len(c.text)
        reindexed.append(ClauseRecord(
            clause_id=c.clause_id,
            doc_id=c.doc_id,
            sequence_idx=idx,
            text=c.text,
            label=c.label,
            char_start=current_char,
            char_end=current_char + text_len,
            source=c.source,
            split=c.split
        ))
        current_char += text_len + 1
    return reindexed


# P1: Clause Displacement
def apply_clause_displacement(
    clauses: List[ClauseRecord],
    source_slot: int,
    target_slot: int
) -> Tuple[List[ClauseRecord], Dict[str, Any]]:
    """
    Moves clause from source_slot to target_slot.
    Preserves all text and clause IDs.
    """
    n = len(clauses)
    if not (0 <= source_slot < n) or not (0 <= target_slot < n):
        raise ValueError(f"Slots out of bounds: source={source_slot}, target={target_slot}, n={n}")
    if source_slot == target_slot:
        raise ValueError("Displacement source and target must be distinct slots (no-op prohibited).")

    target_clause = clauses[source_slot]
    remaining = [c for i, c in enumerate(clauses) if i != source_slot]
    new_perm = remaining[:target_slot] + [target_clause] + remaining[target_slot:]
    reindexed = _reindex_clauses(new_perm)

    metadata = {
        "perturbation_type": "P1_DISPLACEMENT",
        "moved_clause_id": target_clause.clause_id,
        "original_slot": source_slot,
        "displaced_slot": target_slot,
        "displacement_distance": abs(target_slot - source_slot),
        "affected_clause_ids": [target_clause.clause_id],
        "original_checksum": compute_clauses_checksum(clauses),
        "perturbed_checksum": compute_clauses_checksum(reindexed)
    }
    return reindexed, metadata


# P2: Clause Swapping
def apply_clause_swap(
    clauses: List[ClauseRecord],
    slot_a: int,
    slot_b: int
) -> Tuple[List[ClauseRecord], Dict[str, Any]]:
    """
    Swaps clauses between slot_a and slot_b.
    """
    n = len(clauses)
    if not (0 <= slot_a < n) or not (0 <= slot_b < n):
        raise ValueError(f"Slots out of bounds: slot_a={slot_a}, slot_b={slot_b}, n={n}")
    if slot_a == slot_b:
        raise ValueError("Swap slots must be distinct.")

    new_perm = list(clauses)
    new_perm[slot_a], new_perm[slot_b] = new_perm[slot_b], new_perm[slot_a]
    reindexed = _reindex_clauses(new_perm)

    metadata = {
        "perturbation_type": "P2_SWAP",
        "clause_a_id": clauses[slot_a].clause_id,
        "clause_b_id": clauses[slot_b].clause_id,
        "slot_a": slot_a,
        "slot_b": slot_b,
        "swap_distance": abs(slot_b - slot_a),
        "affected_clause_ids": [clauses[slot_a].clause_id, clauses[slot_b].clause_id],
        "original_checksum": compute_clauses_checksum(clauses),
        "perturbed_checksum": compute_clauses_checksum(reindexed)
    }
    return reindexed, metadata


# P3: Exact Clause Duplication
def apply_exact_duplication(
    clauses: List[ClauseRecord],
    source_slot: int,
    insert_slot: int,
    new_clause_id: Optional[str] = None
) -> Tuple[List[ClauseRecord], Dict[str, Any]]:
    """
    Duplicates clause at source_slot and inserts an identical copy at insert_slot with a unique ID.
    """
    n = len(clauses)
    if not (0 <= source_slot < n):
        raise ValueError(f"Source slot out of bounds: {source_slot}")
    if not (0 <= insert_slot <= n):
        raise ValueError(f"Insert slot out of bounds: {insert_slot}")

    orig_clause = clauses[source_slot]
    dup_id = new_clause_id or f"{orig_clause.clause_id}_dup_{insert_slot}"

    dup_clause = ClauseRecord(
        clause_id=dup_id,
        doc_id=orig_clause.doc_id,
        sequence_idx=insert_slot,
        text=orig_clause.text,
        label=orig_clause.label,
        char_start=0,
        char_end=len(orig_clause.text),
        source="SYNTHETIC_DUPLICATION",
        split=orig_clause.split
    )

    new_perm = list(clauses)
    new_perm.insert(insert_slot, dup_clause)
    reindexed = _reindex_clauses(new_perm)

    metadata = {
        "perturbation_type": "P3_EXACT_DUPLICATION",
        "source_clause_id": orig_clause.clause_id,
        "duplicate_clause_id": dup_id,
        "source_slot": source_slot,
        "insert_slot": insert_slot,
        "affected_clause_ids": [orig_clause.clause_id, dup_id],
        "original_checksum": compute_clauses_checksum(clauses),
        "perturbed_checksum": compute_clauses_checksum(reindexed)
    }
    return reindexed, metadata


# P4: Near-Duplicate Clause
def apply_near_duplication(
    clauses: List[ClauseRecord],
    source_slot: int,
    insert_slot: int,
    substitution_mode: str = "SYNONYM_REPLACEMENT",
    new_clause_id: Optional[str] = None
) -> Tuple[List[ClauseRecord], Dict[str, Any]]:
    """
    Inserts a semantically near-identical variant of the source clause at insert_slot.
    Uses deterministic lexical substitutions.
    """
    n = len(clauses)
    if not (0 <= source_slot < n):
        raise ValueError(f"Source slot out of bounds: {source_slot}")

    orig_clause = clauses[source_slot]
    text = orig_clause.text

    # Deterministic legal synonym mapping
    substitutions = [
        (r"\bVendor\b", "Supplier"),
        (r"\bCustomer\b", "Client"),
        (r"\bshall\b", "agrees to"),
        (r"\bpromptly\b", "without undue delay"),
        (r"\bAgreement\b", "Contract"),
        (r"\bcommence\b", "begin"),
        (r"\bforthwith\b", "immediately")
    ]

    var_text = text
    applied_subs = []
    for pat, rep in substitutions:
        if re.search(pat, var_text):
            var_text = re.sub(pat, rep, var_text, count=2)
            applied_subs.append(f"{pat}->{rep}")

    if var_text == text:
        # Fallback cosmetic phrasing modification if no keywords matched
        var_text = text.replace(".", ", provided that all covenants herein are respected.")

    dup_id = new_clause_id or f"{orig_clause.clause_id}_neardup_{insert_slot}"
    variant_clause = ClauseRecord(
        clause_id=dup_id,
        doc_id=orig_clause.doc_id,
        sequence_idx=insert_slot,
        text=var_text,
        label=orig_clause.label,
        char_start=0,
        char_end=len(var_text),
        source="SYNTHETIC_NEAR_DUPLICATION",
        split=orig_clause.split
    )

    new_perm = list(clauses)
    new_perm.insert(insert_slot, variant_clause)
    reindexed = _reindex_clauses(new_perm)

    metadata = {
        "perturbation_type": "P4_NEAR_DUPLICATION",
        "source_clause_id": orig_clause.clause_id,
        "variant_clause_id": dup_id,
        "source_slot": source_slot,
        "insert_slot": insert_slot,
        "applied_substitutions": applied_subs,
        "affected_clause_ids": [orig_clause.clause_id, dup_id],
        "original_checksum": compute_clauses_checksum(clauses),
        "perturbed_checksum": compute_clauses_checksum(reindexed)
    }
    return reindexed, metadata


# P5: Broken Internal Cross-Reference
def apply_broken_reference(
    clauses: List[ClauseRecord],
    target_clause_id: str,
    old_target_sec: str,
    new_nonexistent_sec: str = "Section 99"
) -> Tuple[List[ClauseRecord], Dict[str, Any]]:
    """
    Mutates a valid internal cross-reference citation in target_clause to cite an undeclared section.
    """
    idx = next((i for i, c in enumerate(clauses) if c.clause_id == target_clause_id), -1)
    if idx == -1:
        raise ValueError(f"Clause {target_clause_id} not found.")

    target_clause = clauses[idx]
    orig_text = target_clause.text

    # Search for reference to old_target_sec (e.g. "Section 4" or "Section 4.1")
    pattern = re.compile(rf"\b(Section|Clause|Article)\s+{re.escape(old_target_sec)}\b", re.IGNORECASE)
    if not pattern.search(orig_text):
        # Fallback replace any Section mention
        gen_pattern = re.compile(r"\b(Section|Clause|Article)\s+\d+(?:\.\d+)?\b", re.IGNORECASE)
        if not gen_pattern.search(orig_text):
            raise ValueError(f"Target citation '{old_target_sec}' not found in clause '{target_clause_id}'.")
        mutated_text = gen_pattern.sub(new_nonexistent_sec, orig_text, count=1)
    else:
        mutated_text = pattern.sub(new_nonexistent_sec, orig_text, count=1)

    new_clauses = list(clauses)
    new_clauses[idx] = ClauseRecord(
        clause_id=target_clause.clause_id,
        doc_id=target_clause.doc_id,
        sequence_idx=target_clause.sequence_idx,
        text=mutated_text,
        label=target_clause.label,
        char_start=target_clause.char_start,
        char_end=target_clause.char_start + len(mutated_text),
        source="SYNTHETIC_BROKEN_REF",
        split=target_clause.split
    )
    reindexed = _reindex_clauses(new_clauses)

    metadata = {
        "perturbation_type": "P5_BROKEN_REFERENCE",
        "clause_id": target_clause_id,
        "old_citation": old_target_sec,
        "new_citation": new_nonexistent_sec,
        "affected_clause_ids": [target_clause_id],
        "original_checksum": compute_clauses_checksum(clauses),
        "perturbed_checksum": compute_clauses_checksum(reindexed)
    }
    return reindexed, metadata


# P6: Missing Exhibit Reference
def apply_missing_exhibit(
    clauses: List[ClauseRecord],
    target_clause_id: str,
    old_exhibit_ref: Optional[str] = None,
    new_nonexistent_exhibit: str = "Exhibit Z"
) -> Tuple[List[ClauseRecord], Dict[str, Any]]:
    """
    Mutates an exhibit reference or injects an undeclared exhibit citation.
    """
    idx = next((i for i, c in enumerate(clauses) if c.clause_id == target_clause_id), -1)
    if idx == -1:
        raise ValueError(f"Clause {target_clause_id} not found.")

    target_clause = clauses[idx]
    orig_text = target_clause.text

    if old_exhibit_ref and re.search(rf"\bExhibit\s+{re.escape(old_exhibit_ref)}\b", orig_text, re.I):
        mutated_text = re.sub(rf"\bExhibit\s+{re.escape(old_exhibit_ref)}\b", new_nonexistent_exhibit, orig_text, count=1, flags=re.I)
    elif re.search(r"\bExhibit\s+[A-Za-z0-9]+\b", orig_text, re.I):
        mutated_text = re.sub(r"\bExhibit\s+[A-Za-z0-9]+\b", new_nonexistent_exhibit, orig_text, count=1, flags=re.I)
    else:
        # Append an explicit undeclared exhibit citation
        mutated_text = orig_text.rstrip(".") + f", as set forth in {new_nonexistent_exhibit} attached hereto."

    new_clauses = list(clauses)
    new_clauses[idx] = ClauseRecord(
        clause_id=target_clause.clause_id,
        doc_id=target_clause.doc_id,
        sequence_idx=target_clause.sequence_idx,
        text=mutated_text,
        label=target_clause.label,
        char_start=target_clause.char_start,
        char_end=target_clause.char_start + len(mutated_text),
        source="SYNTHETIC_MISSING_EXHIBIT",
        split=target_clause.split
    )
    reindexed = _reindex_clauses(new_clauses)

    metadata = {
        "perturbation_type": "P6_MISSING_EXHIBIT",
        "clause_id": target_clause_id,
        "new_exhibit": new_nonexistent_exhibit,
        "affected_clause_ids": [target_clause_id],
        "original_checksum": compute_clauses_checksum(clauses),
        "perturbed_checksum": compute_clauses_checksum(reindexed)
    }
    return reindexed, metadata


# P7: Date Chronology Inversion
def apply_date_inversion(
    clauses: List[ClauseRecord],
    target_clause_id: str,
    inversion_type: str = "INVERTED_CONTRACT_TERM",
    new_date_str: str = "December 31, 2020"
) -> Tuple[List[ClauseRecord], Dict[str, Any]]:
    """
    Injects a chronological contradiction (e.g. changing Termination Date to occur before Effective Date).
    """
    idx = next((i for i, c in enumerate(clauses) if c.clause_id == target_clause_id), -1)
    if idx == -1:
        raise ValueError(f"Clause {target_clause_id} not found.")

    target_clause = clauses[idx]
    orig_text = target_clause.text

    # Search for date pattern and replace based on inversion role
    date_regex = re.compile(
        r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b",
        re.IGNORECASE
    )

    if inversion_type == "INVERTED_CONTRACT_TERM":
        term_pat = re.compile(
            r"(terminat(?:es?|ion)\s+(?:date|on|as\s+of)?\s*(?:is|shall\s+be)?\s*)"
            r"(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}",
            re.I
        )
        if term_pat.search(orig_text):
            mutated_text = term_pat.sub(rf"\g<1>{new_date_str}", orig_text)
        else:
            matches = list(date_regex.finditer(orig_text))
            if len(matches) >= 2:
                last_m = matches[-1]
                mutated_text = orig_text[:last_m.start()] + new_date_str + orig_text[last_m.end():]
            elif matches:
                mutated_text = date_regex.sub(new_date_str, orig_text, count=1)
            else:
                mutated_text = orig_text + f" The Agreement termination date shall be {new_date_str}."
    elif inversion_type in ("INVALID_PAYMENT_TIMELINE", "PAYMENT_BEFORE_EFFECTIVE_DATE"):
        mutated_text = orig_text.rstrip(".") + f". Payment due on {new_date_str}."
    else:
        if date_regex.search(orig_text):
            mutated_text = date_regex.sub(new_date_str, orig_text, count=1)
        else:
            mutated_text = orig_text + f" Relevant date is {new_date_str}."

    new_clauses = list(clauses)
    new_clauses[idx] = ClauseRecord(
        clause_id=target_clause.clause_id,
        doc_id=target_clause.doc_id,
        sequence_idx=target_clause.sequence_idx,
        text=mutated_text,
        label=target_clause.label,
        char_start=target_clause.char_start,
        char_end=target_clause.char_start + len(mutated_text),
        source="SYNTHETIC_DATE_INVERSION",
        split=target_clause.split
    )
    reindexed = _reindex_clauses(new_clauses)

    metadata = {
        "perturbation_type": "P7_DATE_INVERSION",
        "clause_id": target_clause_id,
        "inversion_type": inversion_type,
        "injected_date": new_date_str,
        "affected_clause_ids": [target_clause_id],
        "original_checksum": compute_clauses_checksum(clauses),
        "perturbed_checksum": compute_clauses_checksum(reindexed)
    }
    return reindexed, metadata


# P8: Clause Deletion
def apply_clause_deletion(
    clauses: List[ClauseRecord],
    target_slot: int
) -> Tuple[List[ClauseRecord], Dict[str, Any]]:
    """
    Deletes the clause at target_slot, re-indexing remaining clauses.
    """
    n = len(clauses)
    if not (0 <= target_slot < n):
        raise ValueError(f"Target slot out of bounds: {target_slot}")

    deleted_clause = clauses[target_slot]
    remaining = [c for i, c in enumerate(clauses) if i != target_slot]
    reindexed = _reindex_clauses(remaining)

    metadata = {
        "perturbation_type": "P8_DELETION",
        "deleted_clause_id": deleted_clause.clause_id,
        "deleted_slot": target_slot,
        "deleted_clause_text": deleted_clause.text[:100],
        "affected_clause_ids": [deleted_clause.clause_id],
        "original_checksum": compute_clauses_checksum(clauses),
        "perturbed_checksum": compute_clauses_checksum(reindexed)
    }
    return reindexed, metadata


# P9: Clean Negative Control
def apply_negative_control(
    clauses: List[ClauseRecord]
) -> Tuple[List[ClauseRecord], Dict[str, Any]]:
    """
    Returns an untouched, identical copy of the document (negative control baseline).
    """
    reindexed = _reindex_clauses(list(clauses))
    metadata = {
        "perturbation_type": "P9_NEGATIVE_CONTROL",
        "affected_clause_ids": [],
        "original_checksum": compute_clauses_checksum(clauses),
        "perturbed_checksum": compute_clauses_checksum(reindexed)
    }
    return reindexed, metadata


# P10: Combined Perturbations
def apply_combined_perturbation(
    clauses: List[ClauseRecord],
    perturbation_steps: List[Dict[str, Any]]
) -> Tuple[List[ClauseRecord], Dict[str, Any]]:
    """
    Applies multiple sequential perturbations in a controlled pipeline.
    """
    current_clauses = list(clauses)
    all_affected = []
    step_summaries = []

    for step in perturbation_steps:
        ptype = step["type"]
        if ptype == "P1_DISPLACEMENT":
            current_clauses, meta = apply_clause_displacement(
                current_clauses, step["source_slot"], step["target_slot"]
            )
        elif ptype == "P2_SWAP":
            current_clauses, meta = apply_clause_swap(
                current_clauses, step["slot_a"], step["slot_b"]
            )
        elif ptype == "P3_EXACT_DUPLICATION":
            current_clauses, meta = apply_exact_duplication(
                current_clauses, step["source_slot"], step["insert_slot"]
            )
        elif ptype == "P5_BROKEN_REFERENCE":
            current_clauses, meta = apply_broken_reference(
                current_clauses, step["target_clause_id"], step["old_target_sec"], step.get("new_sec", "Section 99")
            )
        elif ptype == "P7_DATE_INVERSION":
            current_clauses, meta = apply_date_inversion(
                current_clauses, step["target_clause_id"], new_date_str=step.get("date_str", "December 31, 2020")
            )
        elif ptype == "P8_DELETION":
            current_clauses, meta = apply_clause_deletion(
                current_clauses, step["target_slot"]
            )
        else:
            raise ValueError(f"Unsupported combined step type: {ptype}")

        all_affected.extend(meta.get("affected_clause_ids", []))
        step_summaries.append(meta)

    metadata = {
        "perturbation_type": "P10_COMBINED",
        "step_count": len(perturbation_steps),
        "step_summaries": step_summaries,
        "affected_clause_ids": list(set(all_affected)),
        "original_checksum": compute_clauses_checksum(clauses),
        "perturbed_checksum": compute_clauses_checksum(current_clauses)
    }
    return current_clauses, metadata
