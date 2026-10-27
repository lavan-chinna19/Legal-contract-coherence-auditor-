"""
Source-backed cross-reference resolution and dangling-target validation.
The legacy normalization helper and two-value check_document interface remain available;
the exact resolver uses the shared structural inventory and explicit ambiguity reviews.
"""
import re
from typing import List, Dict, Set, Tuple, Optional, Any
import spacy
from spacy.tokens import Doc

from src.config import ClauseRecord
from src.rules.schema import (
    ReferenceTarget,
    CrossReferenceCitation,
    RuleFlag,
    ClaimScope
)


# Roman numeral conversion mapping
ROMAN_TO_INT = {
    "i": 1, "ii": 2, "iii": 3, "iv": 4, "v": 5, "vi": 6, "vii": 7, "viii": 8, "ix": 9, "x": 10,
    "xi": 11, "xii": 12, "xiii": 13, "xiv": 14, "xv": 15, "xvi": 16, "xvii": 17, "xviii": 18, "xix": 19, "xx": 20
}


def normalize_section_num(num_str: str) -> List[str]:
    """
    Produces normalized forms for section numbers (e.g., '1.01' -> ['1.01', '1.1', '1'], '4' -> ['4', '4.0']).
    """
    clean = num_str.strip().rstrip(".").lower()
    variants = [clean]
    
    # Handle roman numerals
    if clean in ROMAN_TO_INT:
        variants.append(str(ROMAN_TO_INT[clean]))
    elif clean.isdigit():
        int_val = int(clean)
        for rom, val in ROMAN_TO_INT.items():
            if val == int_val:
                variants.append(rom)
                break

    # Handle float-like section numbers like 1.01 vs 1.1
    if "." in clean:
        parts = clean.split(".")
        try:
            norm_parts = [str(int(p)) if p.isdigit() else p for p in parts]
            variants.append(".".join(norm_parts))
        except Exception:
            pass

    return list(set(variants))


class CrossReferenceChecker:
    """Source-backed reference validation; old two-value interface remains supported.

    normalize_section_num above is retained for import compatibility only. Exact resolution
    never aliases decimal identities or discards subclause suffixes. Reviews are separate
    from missing-target RuleFlags and do not count as confirmed missing references.
    """
    def __init__(self, nlp=None):
        self.nlp = nlp  # Compatibility injection; the structural grammar does not need NLP weights.

    @staticmethod
    def _targets(structure):
        return [ReferenceTarget(target_type=s['target_type'], target_id=s['identity'].lower(),
            raw_label=s['heading_text'], clause_id=s['clause_id'],
            char_start=s['identifier_start'], char_end=s['identifier_end']) for s in structure.sections]

    def extract_declared_targets(self, clauses):
        from src.structure import parse_contract
        return self._targets(parse_contract(clauses))

    def extract_citations(self, clause):
        from src.structure import parse_contract
        structure=parse_contract([clause])
        return [CrossReferenceCitation(target_type=r['target_type'], target_id=r['target_id'].lower(),
            raw_text=r['text'], source_clause_id=r['source_clause_id'],
            char_start=clause.char_start+r['char_start'], char_end=clause.char_start+r['char_end'])
            for r in structure.references]

    def analyze_document(self, clauses, doc_id=None, *, source_text=None, structure=None):
        from src.structure import parse_contract, resolve_references
        structure=structure or parse_contract(clauses,doc_id,source_text=source_text)
        resolutions=resolve_references(structure);declared=self._targets(structure);flags=[]
        source_hash=structure.to_dict()['source_sha256']
        for r in resolutions:
            if r['resolution_status']!='MISSING':continue
            critical=any(kw in r['text'].lower() for kw in ['as defined in','pursuant to','subject to'])
            available=[f"{s.target_type} {s.target_id}" for s in declared if s.target_type==r['target_type']]
            flags.append(RuleFlag(flag_id=f"FLAG_REF_{structure.doc_id}_{len(flags)+1:03d}",
                doc_id=structure.doc_id,flag_type=f"DANGLING_{r['target_type']}_REFERENCE",
                category='RULE_BASED',severity='HIGH' if critical else 'MEDIUM',
                title=f"Dangling Reference: '{r['text']}' not found",
                description=f"Clause '{r['source_clause_id']}' cites '{r['text']}', but no exact {r['target_type'].lower()} '{r['target_id']}' declaration exists in the supported extracted structure.",
                clause_id=r['source_clause_id'],involved_clause_ids=[r['source_clause_id']],
                evidence=dict(citation_text=r['text'],target_type=r['target_type'],target_id=r['target_id'].lower(),
                    available_targets_count=len(available),available_targets_sample=available[:10],
                    char_start=r['char_start'],char_end=r['char_end'],coordinate_space=structure.coordinate_space,
                    source_sha256=source_hash,reference_uid=r['reference_uid'],
                    resolution_status=r['resolution_status'],reason=r['reason']),
                claim_scope=ClaimScope(what_this_shows='An explicit reference target is absent from the supported extracted structure.',
                    what_this_does_not_show='Does not establish legal invalidity or absence from an external agreement or unprovided attachment.')))
        return dict(flags=flags,declared_targets=declared,structure=structure,resolutions=resolutions,
            reviews=[r for r in resolutions if r['status']=='REVIEW_REQUIRED']+structure.reviews)

    def check_document(self, clauses, doc_id=None, *, source_text=None):
        result=self.analyze_document(clauses,doc_id,source_text=source_text)
        return result['flags'],result['declared_targets']
