"""
src/research/structural_coherence/features.py — Contextual Structural Feature Extractor.
Phase 4D-B Research Extension.
"""
import re
from typing import List, Tuple, Dict, Optional
import numpy as np

from src.config import ClauseRecord
from src.coherence.base import CoherenceModelInterface
from src.embeddings.factory import get_embedder


# Canonical Contract Discourse Lifecycle Hierarchy (Stages 0 to 6)
LIFECYCLE_STAGE_KEYWORDS = {
    0: ["preamble", "parties", "recital", "witnesseth", "whereas"],
    1: ["scope of services", "services", "statement of work", "grant of license", "license grant", "deliverable"],
    2: ["payment", "fee", "compensation", "invoice", "uptime", "service level", "term and termination", "term"],
    3: ["intellectual property", "confidentiality", "proprietary", "data protection", "audit"],
    4: ["indemnification", "indemnity", "limitation of liability", "liability", "warranty", "disclaimer"],
    5: ["governing law", "jurisdiction", "dispute resolution", "severability", "entire agreement", "miscellaneous", "notice"],
    6: ["exhibit", "schedule", "appendix", "signature", "in witness whereof", "execution"]
}


def infer_clause_lifecycle_stage(clause: ClauseRecord) -> int:
    """
    Infers the canonical contract lifecycle stage (0-6) from clause heading and label.
    Checks heading/title first to avoid body text false positives.
    """
    # Use label and heading (first 80 chars)
    header = ((clause.label or "") + " " + clause.text[:80]).lower()

    # Stage 6: Closing & Exhibits (Exhibit, Schedule, Signatures, Execution)
    if any(k in header for k in ["exhibit", "schedule", "appendix", "signature", "in witness whereof", "execution"]):
        return 6
    # Stage 0: Preamble / Parties / Recitals
    if any(k in header for k in ["preamble", "parties", "recital", "witnesseth", "whereas"]):
        return 0
    # Stage 1: Scope & Substantive Grant
    if any(k in header for k in ["scope", "services", "deliverable", "grant of license", "license grant"]):
        return 1
    # Stage 2: Payment & Term
    if any(k in header for k in ["payment", "fee", "compensation", "invoice", "service level", "uptime", "term and termination", "term."]):
        return 2
    # Stage 3: Operational Covenants (IP, Confidentiality, Audit)
    if any(k in header for k in ["intellectual property", "confidentiality", "proprietary", "audit", "data protection"]):
        return 3
    # Stage 4: Risk Allocation & Remedies (Indemnification, Liability, Warranties)
    if any(k in header for k in ["indemnif", "liability", "warranty", "disclaimer", "remed"]):
        return 4
    # Stage 5: General Boilerplate (Governing Law, Entire Agreement, Miscellaneous, Dispute)
    if any(k in header for k in ["governing law", "jurisdiction", "dispute", "severability", "entire agreement", "miscellaneous", "notice"]):
        return 5

    return 3  # Neutral operational middle


def extract_contextual_window_distances(
    embeddings: np.ndarray,
    window_size: int = 2
) -> np.ndarray:
    """
    Calculates cosine distance between each clause embedding and the mean of its local surrounding context.

    Args:
        embeddings: (N, D) array of L2-normalized clause vectors.
        window_size: Number of neighbors on each side to include in local context.

    Returns:
        (N,) array of contextual distance scores in [0.0, 1.0].
    """
    n, d = embeddings.shape
    if n <= 1:
        return np.zeros(n, dtype=np.float32)

    distances = np.zeros(n, dtype=np.float32)
    for i in range(n):
        # Window indices excluding i
        start_idx = max(0, i - window_size)
        end_idx = min(n, i + window_size + 1)
        neighbor_indices = [j for j in range(start_idx, end_idx) if j != i]

        if not neighbor_indices:
            distances[i] = 0.0
            continue

        ctx_centroid = np.mean(embeddings[neighbor_indices], axis=0)
        norm_centroid = ctx_centroid / (np.linalg.norm(ctx_centroid) + 1e-9)
        e_i = embeddings[i] / (np.linalg.norm(embeddings[i]) + 1e-9)

        # Cosine distance in [0, 2], scaled to [0, 1]
        cos_dist = float(max(0.0, 1.0 - np.dot(e_i, norm_centroid)))
        distances[i] = cos_dist

    return distances


def extract_progression_discordance(clauses: List[ClauseRecord]) -> np.ndarray:
    """
    Calculates lifecycle progression discordance for each clause in sequence.
    Detects severe backward lifecycle shifts (e.g. Scope or Preamble placed after Exhibits).

    Returns:
        (N,) array of normalized discordance scores in [0.0, 1.0].
    """
    n = len(clauses)
    if n <= 1:
        return np.zeros(n, dtype=np.float32)

    stages = np.array([infer_clause_lifecycle_stage(c) for c in clauses], dtype=np.int32)
    discordance = np.zeros(n, dtype=np.float32)

    # Opening rule: First clause must not be an operational/remedy/boilerplate clause (stage >= 2)
    if stages[0] >= 2:
        discordance[0] = min(1.0, (stages[0] - 1) / 3.0)

    max_so_far = stages[0]
    for i in range(1, n):
        curr_stage = stages[i]

        # Opening inversion: Preamble (Stage 0) appearing after substantive covenants
        if curr_stage == 0 and max_so_far >= 1:
            discordance[i] = 1.0
        else:
            # Backward regression: current stage significantly lower than max seen so far
            shift = max_so_far - curr_stage
            if shift >= 2:
                # Major backward regression: e.g. Stage 5/6 followed by Stage 1/2
                discordance[i] = min(1.0, (shift - 1) / 3.0)

        max_so_far = max(max_so_far, curr_stage)

    return discordance


def extract_boundary_contrast(
    coherence_probs: List[float]
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Calculates local contrast and z-scores for adjacent transition anomalies.

    Args:
        coherence_probs: List of P(c_i -> c_{i+1}) from Channel B.

    Returns:
        Tuple of (contrasts, z_scores) for each transition.
    """
    if not coherence_probs:
        return np.array([]), np.array([])

    anomalies = np.array([1.0 - p for p in coherence_probs], dtype=np.float32)
    mean_anom = np.mean(anomalies)
    std_anom = np.std(anomalies) + 1e-6

    contrasts = anomalies - mean_anom
    z_scores = contrasts / std_anom
    return contrasts, z_scores
