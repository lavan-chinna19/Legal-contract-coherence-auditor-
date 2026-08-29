import re
from typing import List
import spacy
from spacy.cli import download
from src.config import ClauseRecord
from .base import SegmenterInterface

class BIOTaggerSegmenter(SegmenterInterface):
    """
    V2 Stretch Path: Learned BIO Tagger.
    Uses a lightweight NLP model (spaCy en_core_web_sm) combined with 
    sequence BIO tagging to identify clause boundaries.
    """
    def __init__(self, model_path: str = "en_core_web_sm"):
        try:
            self.nlp = spacy.load(model_path)
        except OSError:
            # Fallback if spacy model isn't downloaded yet
            download(model_path)
            self.nlp = spacy.load(model_path)

    def _predict_bio_tags(self, text: str):
        """
        Predicts B-CLAUSE, I-CLAUSE, O tags for sentences.
        In a full implementation, this would be a trained sequence model (e.g. CRF or Transformer).
        For this stretch path without full training data, we approximate using linguistic features.
        """
        doc = self.nlp(text[:1000000])  # limit length to avoid memory issues
        tags = []
        for sent in doc.sents:
            # Heuristic approximation of a learned model for demonstration
            # In reality, this would be `model.predict(sent)`
            text_sent = sent.text.strip()
            
            # Simple feature: starts with a number or uppercase word implies B-CLAUSE
            is_start = False
            if re.match(r'^(?:(?:Article|Section)\s+[IVXLCDM\d]+[.:]*|\d+(?:\.\d+)*[.:]*|\([a-z\divxlcdm]+\)|[A-Z][A-Z\s,.-]{2,100})', text_sent, re.IGNORECASE):
                is_start = True
                
            if is_start:
                tags.append((sent, "B-CLAUSE"))
            else:
                tags.append((sent, "I-CLAUSE"))
                
        return tags

    def segment(self, text: str, doc_id: str = "unknown") -> List[ClauseRecord]:
        if not text.strip():
            return []

        tagged_sentences = self._predict_bio_tags(text)
        
        clauses = []
        current_clause_sents = []
        current_start_char = 0
        
        for sent, tag in tagged_sentences:
            if tag == "B-CLAUSE" and current_clause_sents:
                # Flush current clause
                clause_text = text[current_start_char:sent.start_char].strip()
                if clause_text:
                    record = ClauseRecord(
                        clause_id=f"{doc_id}_{len(clauses)}",
                        doc_id=doc_id,
                        text=clause_text,
                        label="Segment",
                        sequence_idx=len(clauses),
                        char_start=current_start_char,
                        char_end=current_start_char + len(clause_text),
                        source="sec_edgar",
                        split="none"
                    )
                    clauses.append(record)
                current_clause_sents = [sent]
                current_start_char = sent.start_char
            else:
                if not current_clause_sents:
                    current_start_char = sent.start_char
                current_clause_sents.append(sent)
                
        # Flush the last clause
        if current_clause_sents:
            end_char = current_clause_sents[-1].end_char
            clause_text = text[current_start_char:end_char].strip()
            if clause_text:
                record = ClauseRecord(
                    clause_id=f"{doc_id}_{len(clauses)}",
                    doc_id=doc_id,
                    text=clause_text,
                    label="Segment",
                    sequence_idx=len(clauses),
                    char_start=current_start_char,
                    char_end=current_start_char + len(clause_text),
                    source="sec_edgar",
                    split="none"
                )
                clauses.append(record)
                
        return clauses
