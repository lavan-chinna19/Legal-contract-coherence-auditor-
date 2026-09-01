"""
src/xai/ig.py — Integrated Gradients for Channel A.
"""
import uuid
import datetime
import torch
import torch.nn as nn
import numpy as np
from typing import List, Optional

try:
    from captum.attr import LayerIntegratedGradients
except ImportError:
    LayerIntegratedGradients = None

from src.config import ClauseRecord
from src.scoring.channel_a import ChannelAScorer
from src.xai.schema import ExplanationResult, IntegratedGradientsExplanation, ClaimScope


class ChannelAWrapper(nn.Module):
    """
    Differentiable PyTorch wrapper around the frozen Legal-BERT model
    to enable gradient-based attribution to the nearest centroid distance.
    """
    def __init__(self, embedder, centroid_matrix):
        super().__init__()
        self.embedder = embedder
        # Extract the underlying HuggingFace auto_model from the SentenceTransformer
        self.transformer = embedder._model[0].auto_model
        # Move centroids to same device as transformer
        self.centroids = torch.tensor(centroid_matrix, dtype=torch.float32, device=self.transformer.device)

    def forward(self, input_ids, attention_mask):
        out = self.transformer(input_ids=input_ids, attention_mask=attention_mask)
        token_embeddings = out[0]
        # Mean pooling
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, 1)
        sum_mask = torch.clamp(input_mask_expanded.sum(1), min=1e-9)
        sentence_embeddings = sum_embeddings / sum_mask
        # Normalize
        sentence_embeddings = torch.nn.functional.normalize(sentence_embeddings, p=2, dim=1)
        # Cosine distance
        cos_sim = torch.matmul(sentence_embeddings, self.centroids.T)
        cos_dist = 1.0 - cos_sim
        # Distance to nearest centroid
        min_dist, _ = torch.min(cos_dist, dim=1)
        return min_dist


class IntegratedGradientsExplainer:
    def __init__(self, channel_a_scorer: ChannelAScorer):
        self.scorer = channel_a_scorer
        if LayerIntegratedGradients is None:
            raise ImportError("captum is required for Integrated Gradients.")

        if not self.scorer.embedder or getattr(self.scorer.embedder, "_model", None) is None:
            self.scorer.embedder._load_model()
            
        self.wrapper = ChannelAWrapper(
            self.scorer.embedder, 
            self.scorer.centroid_matrix
        )
        self.wrapper.eval()
        
        # Word embeddings layer
        word_emb_layer = self.wrapper.transformer.embeddings.word_embeddings
        self.lig = LayerIntegratedGradients(self.wrapper, word_emb_layer)

    def explain(self, clause: ClauseRecord, steps: int = 50) -> ExplanationResult:
        tokenizer = self.scorer.embedder._model.tokenizer
        
        inputs = tokenizer(
            clause.text, 
            return_tensors="pt", 
            truncation=True, 
            max_length=512
        )
        input_ids = inputs["input_ids"].to(self.wrapper.transformer.device)
        attention_mask = inputs["attention_mask"].to(self.wrapper.transformer.device)

        # Compute baseline distance
        with torch.no_grad():
            target_dist = self.wrapper(input_ids, attention_mask).item()

        # Attribute
        # Baseline is 0 (PAD) tokens by default in NLP IG
        baseline_ids = torch.zeros_like(input_ids)
        with torch.no_grad():
            baseline_dist = self.wrapper(baseline_ids, attention_mask).item()
            
        attributions, delta = self.lig.attribute(
            inputs=input_ids,
            baselines=baseline_ids,
            additional_forward_args=(attention_mask,),
            n_steps=steps,
            return_convergence_delta=True
        )

        # Sum attributions over embedding dimensions to get token-level attribution
        token_attributions = attributions.sum(dim=-1).squeeze(0).cpu().detach().numpy()
        
        # Get tokens
        tokens = tokenizer.convert_ids_to_tokens(input_ids.squeeze(0).cpu().numpy())

        # Build schema
        ig_payload = IntegratedGradientsExplanation(
            tokens=tokens,
            attributions=[round(float(x), 4) for x in token_attributions],
            target_score=round(float(target_dist), 4),
            baseline_score=round(float(baseline_dist), 4)
        )

        claim_scope = ClaimScope(
            what_this_shows="Integrated Gradients indicates which input tokens/features contributed most to the Channel A semantic distance anomaly score.",
            what_this_does_not_show="It does not prove that those tokens are legally significant, causally responsible for a contract defect, or that the model's prediction is correct."
        )

        return ExplanationResult(
            explanation_id=str(uuid.uuid4()),
            doc_id=clause.doc_id,
            clause_id=clause.clause_id,
            explanation_type="INTEGRATED_GRADIENTS",
            model_version=self.scorer.embedder.model_name,
            timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            claim_scope=claim_scope,
            ig_payload=ig_payload
        )
