"""
src/coherence/pair_sampler.py — Consecutive-clause training pair constructor with
easy (cross-document) and hard (same-document shuffle/distance) negative sampling.
"""
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
import random
from collections import defaultdict
from src.config import ClauseRecord


@dataclass
class CoherencePair:
    """
    Data structure representing a labeled pair of clauses for coherence training/eval.
    
    Fields:
        clause_a: Antecedent clause
        clause_b: Subsequent clause
        label: 1.0 for coherent (consecutive), 0.0 for incoherent (negative)
        pair_type: "positive" | "easy_negative" | "hard_negative"
        doc_id_a: Source document for clause_a
        doc_id_b: Source document for clause_b
    """
    clause_a: ClauseRecord
    clause_b: ClauseRecord
    label: float
    pair_type: str
    doc_id_a: str
    doc_id_b: str

    def to_dict(self) -> dict:
        return {
            "clause_id_a": self.clause_a.clause_id,
            "clause_id_b": self.clause_b.clause_id,
            "label": self.label,
            "pair_type": self.pair_type,
            "doc_id_a": self.doc_id_a,
            "doc_id_b": self.doc_id_b,
        }


class CoherencePairSampler:
    """
    Constructs training and evaluation pairs from structured clause documents.
    
    Exact Sampling Strategy & Ratios:
    ---------------------------------
    1. Positive Pairs (label=1.0):
       - Exactly consecutive clauses within the same document: (clause_i, clause_{i+1}).
       - Represents genuine sequential discourse flow.
       - Base count: P = N - 1 pairs per document (for N clauses).
       
    2. Easy Negatives (label=0.0):
       - Clauses drawn from different documents: (clause_i^{Doc_A}, clause_j^{Doc_B}) with Doc_A != Doc_B.
       - Tests semantic domain and context mismatch.
       - Ratio: `easy_neg_ratio` * P (default: 1.0 -> 1 easy negative per positive).
       
    3. Hard Negatives (label=0.0):
       - Clauses from the same document that violate consecutive progression:
         (a) Reversed consecutive pairs: (clause_{i+1}, clause_i)
         (b) Long-range forward jumps: (clause_i, clause_j) where j >= i + 2
         (c) Backward jumps: (clause_j, clause_i) where j > i + 1
       - Tests subtle intradocument structural order and discourse transitions.
       - Ratio: `hard_neg_ratio` * P (default: 1.0 -> 1 hard negative per positive).
    """

    def __init__(
        self,
        easy_neg_ratio: float = 1.0,
        hard_neg_ratio: float = 1.0,
        seed: int = 42
    ):
        self.easy_neg_ratio = easy_neg_ratio
        self.hard_neg_ratio = hard_neg_ratio
        self.seed = seed
        self.rng = random.Random(seed)

    def sample_document_pairs(
        self,
        doc_clauses: List[ClauseRecord],
        all_docs_clauses: Optional[Dict[str, List[ClauseRecord]]] = None
    ) -> List[CoherencePair]:
        """
        Samples positive, hard negative, and (optionally) easy negative pairs for a single document.
        
        Args:
            doc_clauses: List of ClauseRecord objects from one document, ordered by sequence_idx.
            all_docs_clauses: Optional dictionary of doc_id -> List[ClauseRecord] for cross-doc easy negatives.
            
        Returns:
            List[CoherencePair]: Generated dataset of labeled pairs.
        """
        # Ensure ordered by sequence_idx
        sorted_clauses = sorted(doc_clauses, key=lambda c: c.sequence_idx)
        n = len(sorted_clauses)
        if n < 2:
            return []

        doc_id = sorted_clauses[0].doc_id
        pairs: List[CoherencePair] = []

        # 1. Positives: Consecutive pairs (c_i, c_{i+1})
        positive_pairs = []
        for i in range(n - 1):
            pair = CoherencePair(
                clause_a=sorted_clauses[i],
                clause_b=sorted_clauses[i + 1],
                label=1.0,
                pair_type="positive",
                doc_id_a=doc_id,
                doc_id_b=doc_id
            )
            positive_pairs.append(pair)
        pairs.extend(positive_pairs)
        num_positives = len(positive_pairs)

        # 2. Hard Negatives: Same document, non-consecutive or reversed
        # Candidate hard negatives
        hard_candidates = []
        # (a) Reversed consecutive pairs: (c_{i+1}, c_i)
        for i in range(n - 1):
            hard_candidates.append((sorted_clauses[i + 1], sorted_clauses[i]))
            
        # (b) Jumps with distance >= 2: (c_i, c_{i+k}) and (c_{i+k}, c_i)
        for i in range(n):
            for j in range(n):
                if abs(i - j) >= 2:
                    hard_candidates.append((sorted_clauses[i], sorted_clauses[j]))

        target_hard = int(round(num_positives * self.hard_neg_ratio))
        if hard_candidates:
            self.rng.shuffle(hard_candidates)
            selected_hard = hard_candidates[:target_hard]
            for ca, cb in selected_hard:
                pairs.append(CoherencePair(
                    clause_a=ca,
                    clause_b=cb,
                    label=0.0,
                    pair_type="hard_negative",
                    doc_id_a=doc_id,
                    doc_id_b=doc_id
                ))

        # 3. Easy Negatives: Cross-document pairs
        if all_docs_clauses and len(all_docs_clauses) > 1:
            other_doc_ids = [d for d in all_docs_clauses.keys() if d != doc_id and len(all_docs_clauses[d]) > 0]
            if other_doc_ids:
                target_easy = int(round(num_positives * self.easy_neg_ratio))
                for _ in range(target_easy):
                    ca = self.rng.choice(sorted_clauses)
                    other_doc = self.rng.choice(other_doc_ids)
                    cb = self.rng.choice(all_docs_clauses[other_doc])
                    pairs.append(CoherencePair(
                        clause_a=ca,
                        clause_b=cb,
                        label=0.0,
                        pair_type="easy_negative",
                        doc_id_a=doc_id,
                        doc_id_b=other_doc
                    ))

        return pairs

    def sample_dataset(self, clauses: List[ClauseRecord]) -> List[CoherencePair]:
        """
        Samples a full balanced dataset across all documents in clauses.
        
        Args:
            clauses: List of ClauseRecord objects across one or more documents.
            
        Returns:
            List[CoherencePair]: Shuffled list of all generated pairs.
        """
        docs_map: Dict[str, List[ClauseRecord]] = defaultdict(list)
        for c in clauses:
            docs_map[c.doc_id].append(c)

        all_pairs: List[CoherencePair] = []
        for doc_id, doc_clauses in docs_map.items():
            doc_pairs = self.sample_document_pairs(doc_clauses, all_docs_clauses=docs_map)
            all_pairs.extend(doc_pairs)

        self.rng.shuffle(all_pairs)
        return all_pairs
