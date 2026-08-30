"""
src/scoring/channel_a.py — Channel A: Semantic OOD Distance to Type Centroids.
Uses 768-dim Legal-BERT embeddings and LEDGAR-derived clause-type centroids.
"""
import os
import json
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import numpy as np

from src.config import (
    ClauseRecord,
    LEDGAR_CENTROIDS_PATH,
    CHANNEL_A_OOD_THRESHOLD,
    FIXTURES_DIR
)
from src.embeddings.factory import get_embedder
from src.scoring.schema import ChannelAEvidence


class ChannelAScorer:
    """
    Channel A Scorer: Quantifies semantic Out-Of-Distribution (OOD) distance
    between a clause embedding and reference clause-type centroids.
    """

    def __init__(
        self,
        centroids_path: Optional[Path] = None,
        embedder=None,
        ood_threshold: float = CHANNEL_A_OOD_THRESHOLD
    ):
        self.centroids_path = Path(centroids_path or LEDGAR_CENTROIDS_PATH)
        self.embedder = embedder or get_embedder("frozen")
        self.ood_threshold = ood_threshold
        self.centroids: Dict[str, np.ndarray] = {}
        self.centroid_names: List[str] = []
        self.centroid_matrix: Optional[np.ndarray] = None
        
        self._load_or_init_centroids()

    def _load_or_init_centroids(self):
        if self.centroids_path.exists():
            data = np.load(self.centroids_path)
            self.centroid_names = list(data.files)
            self.centroids = {k: data[k] for k in self.centroid_names}
            self.centroid_matrix = np.vstack([self.centroids[k] for k in self.centroid_names])
            # Normalize centroids to unit length for fast cosine distance
            norms = np.linalg.norm(self.centroid_matrix, axis=1, keepdims=True) + 1e-9
            self.centroid_matrix = self.centroid_matrix / norms

    @staticmethod
    def compute_and_save_centroids(
        labeled_clauses: List[ClauseRecord],
        embedder=None,
        output_path: Optional[Path] = None
    ) -> "ChannelAScorer":
        """
        Computes clause type centroids from a collection of labeled clauses and saves to disk.
        """
        if embedder is None:
            embedder = get_embedder("frozen")

        output_path = Path(output_path or LEDGAR_CENTROIDS_PATH)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Group clauses by label
        label_map: Dict[str, List[ClauseRecord]] = {}
        for c in labeled_clauses:
            if c.label:
                label_map.setdefault(str(c.label), []).append(c)

        # Filter categories with at least 5 examples for robust centroids
        valid_labels = {k: v for k, v in label_map.items() if len(v) >= 3}
        if not valid_labels:
            # Fallback if few labels
            valid_labels = label_map

        # Embed clauses per label
        centroid_dict = {}
        for label, group in valid_labels.items():
            _, embs = embedder.embed_clauses(group)
            mean_vector = np.mean(embs, axis=0)
            unit_vector = mean_vector / (np.linalg.norm(mean_vector) + 1e-9)
            # Sanitize label for npz key
            safe_label = f"type_{label}".replace(" ", "_").replace("/", "_")
            centroid_dict[safe_label] = unit_vector.astype(np.float32)

        np.savez_compressed(output_path, **centroid_dict)
        return ChannelAScorer(centroids_path=output_path, embedder=embedder)

    def score_clauses(self, clauses: List[ClauseRecord]) -> List[Tuple[float, ChannelAEvidence]]:
        """
        Calculates semantic OOD anomaly scores and diagnostic evidence for each clause.
        
        Returns:
            List[Tuple[score, ChannelAEvidence]]: Normalized anomaly score in [0.0, 1.0] and evidence.
        """
        if not clauses:
            return []

        if self.centroid_matrix is None or len(self.centroid_names) == 0:
            # If no centroids loaded, return baseline neutral distance
            return [(0.5, ChannelAEvidence(
                nearest_centroid_label="UNKNOWN",
                centroid_distance=0.5,
                is_ood=False,
                top_k_distances={"UNKNOWN": 0.5}
            )) for _ in clauses]

        # Embed input clauses
        _, clause_embs = self.embedder.embed_clauses(clauses)
        
        # Normalize embeddings
        norms = np.linalg.norm(clause_embs, axis=1, keepdims=True) + 1e-9
        clause_embs_norm = clause_embs / norms

        # Cosine similarity matrix: (N_clauses, N_centroids)
        # Cosine distance = 1.0 - Cosine similarity
        cos_sim = np.dot(clause_embs_norm, self.centroid_matrix.T)  # in [-1.0, 1.0]
        cos_dist = 1.0 - cos_sim  # in [0.0, 2.0]

        results: List[Tuple[float, ChannelAEvidence]] = []

        for i, c in enumerate(clauses):
            dists = cos_dist[i]
            nearest_idx = int(np.argmin(dists))
            min_dist = float(dists[nearest_idx])
            nearest_label = self.centroid_names[nearest_idx]

            # Top-3 nearest centroids for evidence
            top_k_indices = np.argsort(dists)[:min(3, len(self.centroid_names))]
            top_k_map = {self.centroid_names[idx]: round(float(dists[idx]), 4) for idx in top_k_indices}

            # Normalize distance to [0.0, 1.0] anomaly score
            # In typical BERT embedding spaces, cosine distance ranges from 0.15 (exact match) to 0.85 (OOD)
            # Calibrate: distance > ood_threshold indicates anomaly
            norm_anomaly_score = float(np.clip((min_dist - 0.20) / (0.80 - 0.20), 0.0, 1.0))
            is_ood = min_dist >= self.ood_threshold

            evidence = ChannelAEvidence(
                nearest_centroid_label=nearest_label,
                centroid_distance=round(min_dist, 4),
                is_ood=is_ood,
                top_k_distances=top_k_map
            )
            results.append((round(norm_anomaly_score, 4), evidence))

        return results
