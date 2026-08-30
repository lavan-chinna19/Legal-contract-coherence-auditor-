"""
src/scoring/channel_b.py — Channel B: Discourse / Coherence Transition Anomaly Scorer.
Evaluates transition likelihood between consecutive clause pairs using the coherence model.
"""
from typing import List, Tuple, Optional
from src.config import ClauseRecord, CHANNEL_B_COHERENCE_THRESHOLD
from src.coherence.factory import get_coherence_model
from src.coherence.base import CoherenceModelInterface
from src.scoring.schema import ChannelBEvidence


class ChannelBScorer:
    """
    Channel B Scorer: Quantifies structural transition anomalies between consecutive clauses.
    Higher scores indicate higher likelihood of an incoherent structural jump or displaced clause.
    """

    def __init__(
        self,
        coherence_model: Optional[CoherenceModelInterface] = None,
        coherence_threshold: float = CHANNEL_B_COHERENCE_THRESHOLD
    ):
        self.coherence_model = coherence_model or get_coherence_model()
        self.coherence_threshold = coherence_threshold

    def score_document_clauses(self, clauses: List[ClauseRecord]) -> List[Tuple[float, ChannelBEvidence]]:
        """
        Computes per-clause transition anomaly scores for all clauses in a document.
        
        Args:
            clauses: List of ClauseRecord objects ordered by sequence_idx.
            
        Returns:
            List[Tuple[float, ChannelBEvidence]]: List of (anomaly_score, evidence) per clause.
        """
        n = len(clauses)
        if n == 0:
            return []
        if n == 1:
            # Single clause has no transitions
            return [(0.0, ChannelBEvidence(
                incoming_prob=1.0,
                outgoing_prob=1.0,
                incoming_anomaly=0.0,
                outgoing_anomaly=0.0
            ))]

        # 1. Construct consecutive pairs (c_i, c_{i+1})
        pairs = [(clauses[i], clauses[i + 1]) for i in range(n - 1)]

        # 2. Batch score all transitions
        coherence_probs = self.coherence_model.score_pairs(pairs)

        # Transition anomalies: A_i = 1.0 - P(c_i -> c_{i+1})
        transition_anomalies = [1.0 - p for p in coherence_probs]

        results: List[Tuple[float, ChannelBEvidence]] = []

        # 3. Assign per-clause transition anomaly
        for i in range(n):
            if i == 0:
                # First clause: only outgoing transition (c_0 -> c_1)
                out_prob = coherence_probs[0]
                out_anom = transition_anomalies[0]
                in_prob = None
                in_anom = None
                clause_score = out_anom
                prev_id = None
                next_id = clauses[1].clause_id
            elif i == n - 1:
                # Last clause: only incoming transition (c_{n-2} -> c_{n-1})
                in_prob = coherence_probs[-1]
                in_anom = transition_anomalies[-1]
                out_prob = None
                out_anom = None
                clause_score = in_anom
                prev_id = clauses[n - 2].clause_id
                next_id = None
            else:
                # Middle clause: has both incoming (c_{i-1} -> c_i) and outgoing (c_i -> c_{i+1})
                in_prob = coherence_probs[i - 1]
                in_anom = transition_anomalies[i - 1]
                out_prob = coherence_probs[i]
                out_anom = transition_anomalies[i]
                # Combined clause transition anomaly: max of incoming or outgoing discontinuity
                clause_score = max(in_anom, out_anom)
                prev_id = clauses[i - 1].clause_id
                next_id = clauses[i + 1].clause_id

            evidence = ChannelBEvidence(
                incoming_prob=round(float(in_prob), 4) if in_prob is not None else None,
                outgoing_prob=round(float(out_prob), 4) if out_prob is not None else None,
                incoming_anomaly=round(float(in_anom), 4) if in_anom is not None else None,
                outgoing_anomaly=round(float(out_anom), 4) if out_anom is not None else None,
                prev_clause_id=prev_id,
                next_clause_id=next_id
            )

            results.append((round(float(clause_score), 4), evidence))

        return results
