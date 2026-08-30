"""
src/coherence/model.py — PyTorch Neural Coherence Scorer Head.
Takes clause embeddings (u, v) and predicts transition coherence probability.
"""
import torch
import torch.nn as nn
import numpy as np
from typing import Union


class CoherenceScorerHead(nn.Module):
    """
    Lightweight classification head over pair embeddings (u, v).
    
    Given embedding u for clause A and v for clause B (dim D),
    constructs feature vector [u, v, |u - v|, u * v] of dimension 4*D,
    and classifies whether transition A -> B is coherent (1) or incoherent (0).
    """

    def __init__(self, embedding_dim: int = 768, hidden_dim1: int = 256, hidden_dim2: int = 64, dropout_rate: float = 0.2):
        super().__init__()
        self.embedding_dim = embedding_dim
        input_dim = embedding_dim * 4  # [u, v, |u - v|, u * v]

        self.classifier = nn.Sequential(
            nn.Linear(input_dim, hidden_dim1),
            nn.LayerNorm(hidden_dim1),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(hidden_dim1, hidden_dim2),
            nn.ReLU(),
            nn.Dropout(dropout_rate * 0.5),
            nn.Linear(hidden_dim2, 1)
        )

    def extract_features(self, u: torch.Tensor, v: torch.Tensor) -> torch.Tensor:
        """
        Constructs rich pair representation: [u, v, |u - v|, u * v].
        """
        diff = torch.abs(u - v)
        prod = u * v
        return torch.cat([u, v, diff, prod], dim=-1)

    def forward(self, u: torch.Tensor, v: torch.Tensor) -> torch.Tensor:
        """
        Returns raw logits of shape (batch_size, 1).
        """
        features = self.extract_features(u, v)
        logits = self.classifier(features)
        return logits

    def predict_proba(self, u: Union[torch.Tensor, np.ndarray], v: Union[torch.Tensor, np.ndarray]) -> np.ndarray:
        """
        Inference helper returning coherence probabilities in [0.0, 1.0].
        Accepts numpy arrays or torch tensors.
        """
        self.eval()
        with torch.no_grad():
            if isinstance(u, np.ndarray):
                u_t = torch.from_numpy(u).float()
            else:
                u_t = u.float()

            if isinstance(v, np.ndarray):
                v_t = torch.from_numpy(v).float()
            else:
                v_t = v.float()

            if u_t.ndim == 1:
                u_t = u_t.unsqueeze(0)
            if v_t.ndim == 1:
                v_t = v_t.unsqueeze(0)

            logits = self.forward(u_t, v_t)
            probs = torch.sigmoid(logits).squeeze(-1).cpu().numpy()
            return probs
