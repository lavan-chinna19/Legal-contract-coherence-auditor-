"""
src/coherence/fine_tuned.py — Fine-Tuned Discourse Coherence Model.
Evaluates clause pairs using the trained neural head over cached Legal-BERT embeddings.
"""
import os
from typing import List, Tuple, Optional
import numpy as np
import torch

from src.config import ClauseRecord, COHERENCE_CHECKPOINT_PATH
from src.embeddings.factory import get_embedder
from src.coherence.base import CoherenceModelInterface
from src.coherence.model import CoherenceScorerHead


class FineTunedCoherenceModel(CoherenceModelInterface):
    """
    Fine-tuned discourse coherence model.
    Utilizes frozen Legal-BERT embeddings with cached disk lookups and a trained PyTorch scoring head.
    """

    def __init__(self, checkpoint_path: Optional[str] = None, embedding_source: str = "frozen"):
        self.checkpoint_path = str(checkpoint_path or COHERENCE_CHECKPOINT_PATH)
        self.embedding_source = embedding_source
        self.embedder = get_embedder(embedding_source)
        self.embedding_dim = self.embedder.embedding_dim
        
        self._model = CoherenceScorerHead(embedding_dim=self.embedding_dim)
        self._load_weights()

    def _load_weights(self):
        if os.path.exists(self.checkpoint_path):
            state_dict = torch.load(self.checkpoint_path, map_location=torch.device("cpu"), weights_only=True)
            self._model.load_state_dict(state_dict)
            self._model.eval()
        else:
            # Model initialized with defaults if checkpoint not yet trained
            self._model.eval()

    @property
    def name(self) -> str:
        return f"fine_tuned_coherence_head (dim={self.embedding_dim})"

    def score_pair(self, clause_a: ClauseRecord, clause_b: ClauseRecord) -> float:
        """
        Computes coherence score for a single clause pair.
        """
        scores = self.score_pairs([(clause_a, clause_b)])
        return scores[0]

    def score_pairs(self, pairs: List[Tuple[ClauseRecord, ClauseRecord]]) -> List[float]:
        """
        Computes coherence scores for a batch of clause pairs.
        """
        if not pairs:
            return []

        # Collect unique clauses to embed efficiently
        unique_clauses = {}
        for ca, cb in pairs:
            unique_clauses[ca.clause_id] = ca
            unique_clauses[cb.clause_id] = cb

        clauses_list = list(unique_clauses.values())
        _, embs = self.embedder.embed_clauses(clauses_list)
        clause_map = {c.clause_id: embs[i] for i, c in enumerate(clauses_list)}

        u_arr = np.vstack([clause_map[ca.clause_id] for ca, _ in pairs])
        v_arr = np.vstack([clause_map[cb.clause_id] for _, cb in pairs])

        probs = self._model.predict_proba(u_arr, v_arr)
        if isinstance(probs, (np.floating, float)):
            return [float(probs)]
        return [float(p) for p in probs]
