import re
import html
from typing import List
from src.config import ClauseRecord
from .base import SegmenterInterface

class RuleBasedSegmenter(SegmenterInterface):
    """
    V1 Deterministic Rule-Based Segmenter.
    Uses regex patterns common in legal contracts to identify clause boundaries.
    """
    def __init__(self):
        # Matches patterns like:
        # "1.", "1.1", "1.1.1", "(a)", "(i)", "Section 1.", "Article I.", "1)"
        self.clause_pattern = re.compile(
            r'^\s*(?:'
            r'(?:(?:Article|Section)\s+[IVXLCDM\d]+[.:]*\s*)'
            r'|(?:\d+(?:\.\d+)*[.:]*\s*)'
            r'|(?:\([a-z\divxlcdm]+\)\s*)'
            r')', 
            re.MULTILINE | re.IGNORECASE
        )
        
        # Matches all-caps headings on a single line or short lines
        self.heading_pattern = re.compile(r'^\s*([A-Z][A-Z\s,.-]{2,100})$', re.MULTILINE)

    def _clean_html(self, raw_text: str) -> str:
        """Removes HTML tags and unescapes HTML entities to yield plain text."""
        # Replace block tags with newlines to preserve visual structure
        text = re.sub(r'<(div|p|br|hr|tr|td|table|h[1-6])[^>]*>', '\n', raw_text, flags=re.IGNORECASE)
        # Strip all other tags
        text = re.sub(r'<[^>]+>', ' ', text)
        # Unescape entities (e.g. &nbsp; -> space)
        text = html.unescape(text)
        # Clean up excessive newlines
        text = re.sub(r'\n\s*\n', '\n\n', text)
        return text

    def segment(self, text: str, doc_id: str = "unknown") -> List[ClauseRecord]:
        text = self._clean_html(text)
        
        if not text.strip():
            return []

        # Find all split points (both numbered clauses and headings)
        splits = []
        
        for m in self.clause_pattern.finditer(text):
            splits.append((m.start(), "Numbered Clause"))
            
        for m in self.heading_pattern.finditer(text):
            splits.append((m.start(), "Heading"))
            
        # Deduplicate and sort by offset
        splits = sorted(list({s[0]: s for s in splits}.values()), key=lambda x: x[0])
        
        if not splits or splits[0][0] != 0:
            # If the document doesn't start with a matched pattern, treat the preamble as a clause
            splits.insert(0, (0, "Preamble"))
            
        clauses = []
        num_splits = len(splits)
        
        for i, (start_idx, label) in enumerate(splits):
            end_idx = splits[i+1][0] if i + 1 < num_splits else len(text)
            
            clause_text = text[start_idx:end_idx].strip()
            
            if not clause_text:
                continue
                
            # Create a ClauseRecord
            record = ClauseRecord(
                clause_id=f"{doc_id}_{len(clauses)}",
                doc_id=doc_id,
                text=clause_text,
                label=label,
                sequence_idx=len(clauses),
                char_start=start_idx,
                char_end=start_idx + len(clause_text),
                source="sec_edgar",
                split="none"
            )
            clauses.append(record)
            
        return clauses
