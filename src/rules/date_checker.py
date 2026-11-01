"""Compatibility facade for context-aware, source-backed temporal analysis.

Legacy flag names/priorities are retained where appropriate. Decision categories in evidence
separate supported contradictions from arithmetic candidates, uncertainty and unsupported syntax.
"""
from src.temporal.extraction import MONTHS as MONTHS_PATTERN,DATE_RE,ROLE_RE as ROLE_PATTERNS
DATE_PATTERNS=[DATE_RE]

class DateLogicChecker:
    def analyze_document(self,clauses,doc_id=None,*,source_text=None,structure=None):
        from src.temporal.analysis import analyze_temporal
        return analyze_temporal(clauses,doc_id,source_text=source_text,structure=structure)

    def check_document(self,clauses,doc_id=None,*,source_text=None):
        result=self.analyze_document(clauses,doc_id,source_text=source_text)
        return result['flags'],result['dates']

    def extract_dates_from_clause(self,clause):
        result=self.analyze_document([clause])
        for item in result['dates']:
            item.char_start+=clause.char_start;item.char_end+=clause.char_start
        return result['dates']
