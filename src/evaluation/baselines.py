"""
src/evaluation/baselines.py — Baseline Estimators for Anomaly and Coherence Evaluation (Work Package E).
Implements:
1. Majority-Vote Baseline (Classifies everything as negative/clean)
2. Logistic Regression Baseline (Trained on pairwise embedding differences / cosine similarities)
"""
from typing import List, Tuple, Dict, Any, Optional
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.dummy import DummyClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

from src.config import ClauseRecord
from src.evaluation.bootstrap import bootstrap_ci, bootstrap_kendall_tau


class MajorityVoteBaseline:
    """
    Baseline model that unconditionally predicts the dominant majority class ('CLEAN' / non-anomaly).
    """

    def __init__(self):
        self.dummy = DummyClassifier(strategy="most_frequent")
        self.is_fitted = False

    def fit(self, X: np.ndarray, y: np.ndarray):
        self.dummy.fit(X, y)
        self.is_fitted = True

    def predict(self, X: np.ndarray) -> np.ndarray:
        if not self.is_fitted:
            return np.zeros(len(X), dtype=int)
        return self.dummy.predict(X)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        if not self.is_fitted:
            probs = np.zeros((len(X), 2))
            probs[:, 0] = 1.0
            return probs
        return self.dummy.predict_proba(X)

    def score_document(self, clauses: List[ClauseRecord]) -> List[float]:
        """Returns constant 0.0 anomaly score for all clauses."""
        return [0.0 for _ in clauses]


class LogisticRegressionBaseline:
    """
    Linear logistic regression baseline operating on sentence embeddings and cosine similarities.
    Trained to predict whether a transition pair is coherent (1) or incoherent/shuffled (0).
    """

    def __init__(self, penalty: str = "l2", C: float = 1.0, random_state: int = 42):
        self.model = LogisticRegression(
            penalty=penalty,
            C=C,
            random_state=random_state,
            max_iter=1000
        )
        self.is_fitted = False

    def _extract_pair_features(self, emb_u: np.ndarray, emb_v: np.ndarray) -> np.ndarray:
        """
        Constructs standard feature representation for embedding pairs:
        [u, v, |u - v|, u * v, cosine_similarity]
        """
        diff = np.abs(emb_u - emb_v)
        prod = emb_u * emb_v
        
        # Cosine similarity
        norm_u = np.linalg.norm(emb_u, axis=-1, keepdims=True) + 1e-9
        norm_v = np.linalg.norm(emb_v, axis=-1, keepdims=True) + 1e-9
        cos_sim = np.sum(prod, axis=-1, keepdims=True) / (norm_u * norm_v)

        return np.hstack([emb_u, emb_v, diff, prod, cos_sim])

    def fit_from_embeddings(self, pairs_u: np.ndarray, pairs_v: np.ndarray, labels: np.ndarray):
        """
        Fits logistic regression model on coherent vs shuffled transition pairs.
        """
        X = self._extract_pair_features(pairs_u, pairs_v)
        self.model.fit(X, labels)
        self.is_fitted = True

    def predict_coherence_proba(self, emb_u: np.ndarray, emb_v: np.ndarray) -> np.ndarray:
        """
        Returns probability of coherence [0.0, 1.0].
        """
        if not self.is_fitted:
            # Heuristic cosine similarity fallback if not fitted
            norm_u = np.linalg.norm(emb_u, axis=-1, keepdims=True) + 1e-9
            norm_v = np.linalg.norm(emb_v, axis=-1, keepdims=True) + 1e-9
            cos = np.sum(emb_u * emb_v, axis=-1) / (norm_u.squeeze() * norm_v.squeeze())
            return np.clip((cos + 1.0) / 2.0, 0.0, 1.0)

        X = self._extract_pair_features(emb_u, emb_v)
        probs = self.model.predict_proba(X)
        return probs[:, 1] if probs.shape[1] > 1 else probs[:, 0]

    def score_document(self, clause_embeddings: np.ndarray) -> List[float]:
        """
        Scores clause transition anomalies along document sequence using linear model.
        """
        n = len(clause_embeddings)
        if n <= 1:
            return [0.0] * n

        u = clause_embeddings[:-1]
        v = clause_embeddings[1:]
        coherence_probs = self.predict_coherence_proba(u, v)
        anomaly_scores = [float(1.0 - p) for p in coherence_probs]

        clause_scores = []
        clause_scores.append(anomaly_scores[0])
        for i in range(1, n - 1):
            clause_scores.append(max(anomaly_scores[i - 1], anomaly_scores[i]))
        clause_scores.append(anomaly_scores[-1])

        return clause_scores
