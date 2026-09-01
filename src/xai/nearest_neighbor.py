"""
src/xai/nearest_neighbor.py — Nearest-Neighbor Evidence Retrieval.
"""
import json
import uuid
import datetime
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional

from src.config import ClauseRecord, PROCESSED_DIR
from src.embeddings.base import EmbeddingInterface
from src.embeddings.factory import get_embedder
from src.xai.schema import ExplanationResult, NearestNeighborEvidence, ClaimScope


class NearestNeighborRetriever:
    """
    Retrieves the top-k nearest clauses from a reference corpus 
    using embedding cosine similarity.
    """
    def __init__(self, embedder: Optional[EmbeddingInterface] = None, corpus_path: Optional[Path] = None):
        self.embedder = embedder or get_embedder("frozen")
        # Default to a subset of the LEDGAR test split for speed in this demo/layer
        self.corpus_path = corpus_path or (PROCESSED_DIR / "ledgar" / "train.jsonl")
        
        self.corpus_clauses: List[ClauseRecord] = []
        self.corpus_embeddings: Optional[np.ndarray] = None
        self._load_corpus()

    def _load_corpus(self, limit: int = 500):
        """Loads and embeds a local corpus for retrieval."""
        if not self.corpus_path.exists():
            return
            
        clauses = []
        with open(self.corpus_path, "r", encoding="utf-8") as f:
            for i, line in enumerate(f):
                if i >= limit:
                    break
                data = json.loads(line)
                clauses.append(ClauseRecord(
                    doc_id=data.get("doc_id", "unknown"),
                    clause_id=data.get("clause_id", f"c_{i}"),
                    text=data["text"],
                    sequence_idx=data.get("sequence_idx", 0),
                    label=data.get("label"),
                    char_start=0,
                    char_end=len(data["text"]),
                    source="corpus"
                ))
        
        if clauses:
            self.corpus_clauses = clauses
            _, embs = self.embedder.embed_clauses(clauses)
            # Normalize for cosine similarity
            norms = np.linalg.norm(embs, axis=1, keepdims=True) + 1e-9
            self.corpus_embeddings = embs / norms

    def explain(self, target_clause: ClauseRecord, k: int = 3) -> ExplanationResult:
        """
        Retrieves the top-k most similar clauses from the corpus.
        """
        if self.corpus_embeddings is None or len(self.corpus_clauses) == 0:
            return self._empty_explanation(target_clause)

        # Embed target clause
        _, target_emb = self.embedder.embed_clauses([target_clause])
        target_emb = target_emb[0]
        target_emb = target_emb / (np.linalg.norm(target_emb) + 1e-9)

        # Compute cosine similarity
        similarities = np.dot(self.corpus_embeddings, target_emb)

        # Get top indices (excluding exact self-matches if present)
        # Sort descending
        top_indices = np.argsort(similarities)[::-1]
        
        results: List[NearestNeighborEvidence] = []
        for idx in top_indices:
            idx = int(idx)
            candidate = self.corpus_clauses[idx]
            
            # Avoid self-matching by ID or exact text match
            if candidate.clause_id == target_clause.clause_id or candidate.text == target_clause.text:
                continue
                
            sim_score = round(float(similarities[idx]), 4)
            
            results.append(NearestNeighborEvidence(
                neighbor_clause_id=candidate.clause_id,
                source_document=candidate.doc_id,
                similarity=sim_score,
                label=candidate.label
            ))
            
            if len(results) >= k:
                break

        claim_scope = ClaimScope(
            what_this_shows="Nearest-neighbor retrieval shows clauses with similar semantic embeddings from the training/reference corpus.",
            what_this_does_not_show="It does not establish that the retrieved clauses are legally correct, identical in legal effect, or represent an absolute standard."
        )

        return ExplanationResult(
            explanation_id=str(uuid.uuid4()),
            doc_id=target_clause.doc_id,
            clause_id=target_clause.clause_id,
            explanation_type="NEAREST_NEIGHBOR",
            model_version=self.embedder.model_name,
            timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            claim_scope=claim_scope,
            nn_payload=results
        )

    def _empty_explanation(self, target_clause: ClauseRecord) -> ExplanationResult:
        claim_scope = ClaimScope(
            what_this_shows="Nearest-neighbor retrieval shows clauses with similar semantic embeddings.",
            what_this_does_not_show="It does not establish legal equivalence."
        )
        return ExplanationResult(
            explanation_id=str(uuid.uuid4()),
            doc_id=target_clause.doc_id,
            clause_id=target_clause.clause_id,
            explanation_type="NEAREST_NEIGHBOR",
            model_version=self.embedder.model_name,
            timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            claim_scope=claim_scope,
            nn_payload=[]
        )
