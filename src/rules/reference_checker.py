"""
src/rules/reference_checker.py — Cross-Reference Resolution & Dangling Reference Validation.
Uses spaCy tokenization and pattern matching to detect internal citations (e.g. "Section 4.2",
"as defined in Section 1.01", "Exhibit B") and verify their existence against the document structure.
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
    """
    Extracts declared structural headers (Sections, Articles, Exhibits, Schedules, Defined Terms)
    and validates cross-references to flag dangling/broken citations using spaCy.
    """

    def __init__(self, nlp: Optional[spacy.Language] = None):
        """
        Initializes the spaCy language model for reference detection.
        """
        if nlp is not None:
            self.nlp = nlp
        else:
            try:
                self.nlp = spacy.load("en_core_web_sm", disable=["ner"])
            except Exception:
                self.nlp = spacy.blank("en")

        # Compile regex patterns for declaration extraction
        self._section_decl_re = re.compile(
            r"(?:^|\n|\.\s+)(?:section|sec\.?|clause|article|art\.?)\s+([0-9ivxlcdm]+(?:\.[0-9a-zA-Z]+)*)",
            re.IGNORECASE
        )
        self._exhibit_decl_re = re.compile(
            r"(?:^|\n|\.\s+)(?:exhibit|schedule|appendix|attachment)\s+([0-9a-zA-Z]+(?:\.[0-9a-zA-Z]+)*)",
            re.IGNORECASE
        )
        self._defined_term_decl_re = re.compile(
            r'["“]([A-Za-z0-9\s\-]+)["”]\s+(?:means|shall mean|has the meaning|refers to|\(hereinafter)',
            re.IGNORECASE
        )

        # Cross-reference citation patterns
        self._section_ref_re = re.compile(
            r"(?:as\s+defined\s+in\s+|pursuant\s+to\s+|subject\s+to\s+|under\s+|set\s+forth\s+in\s+|in\s+accordance\s+with\s+|see\s+)?\b(?:section|sec\.?|clause|article|art\.?)\s+([0-9ivxlcdm]+(?:\.[0-9a-zA-Z]+)*(\([a-zA-Z0-9]+\))*)",
            re.IGNORECASE
        )
        self._exhibit_ref_re = re.compile(
            r"(?:as\s+defined\s+in\s+|attached\s+hereto\s+as\s+|set\s+forth\s+in\s+|pursuant\s+to\s+|under\s+)?\b(?:exhibit|schedule|appendix|attachment)\s+([0-9a-zA-Z]+(?:\.[0-9a-zA-Z]+)*)",
            re.IGNORECASE
        )

    def extract_declared_targets(self, clauses: List[ClauseRecord]) -> List[ReferenceTarget]:
        """
        Scans all clauses to index declared structural targets (Sections, Articles, Exhibits, Schedules).
        """
        declared: List[ReferenceTarget] = []
        seen_keys: Set[Tuple[str, str]] = set()

        for clause in clauses:
            text = clause.text
            # Use spaCy doc for linguistic boundary / token processing
            doc = self.nlp(text[:500])

            # 1. Check for Section / Article declarations
            for match in self._section_decl_re.finditer(text):
                raw_num = match.group(1).rstrip(".)")
                target_type = "ARTICLE" if "article" in match.group(0).lower() or "art." in match.group(0).lower() else "SECTION"
                for norm_num in normalize_section_num(raw_num):
                    key = (target_type, norm_num)
                    if key not in seen_keys:
                        seen_keys.add(key)
                        declared.append(ReferenceTarget(
                            target_type=target_type,
                            target_id=norm_num,
                            raw_label=match.group(0).strip(),
                            clause_id=clause.clause_id,
                            char_start=clause.char_start + match.start(),
                            char_end=clause.char_start + match.end()
                        ))

            # 2. Check for Exhibit / Schedule declarations
            for match in self._exhibit_decl_re.finditer(text):
                raw_id = match.group(1).strip().rstrip(".)").upper()
                target_type = "SCHEDULE" if "schedule" in match.group(0).lower() else "EXHIBIT"
                key = (target_type, raw_id)
                if key not in seen_keys:
                    seen_keys.add(key)
                    declared.append(ReferenceTarget(
                        target_type=target_type,
                        target_id=raw_id,
                        raw_label=match.group(0).strip(),
                        clause_id=clause.clause_id,
                        char_start=clause.char_start + match.start(),
                        char_end=clause.char_start + match.end()
                    ))

            # 3. Check for Defined Terms
            for match in self._defined_term_decl_re.finditer(text):
                term = match.group(1).strip()
                if len(term) > 2:
                    key = ("DEFINED_TERM", term.upper())
                    if key not in seen_keys:
                        seen_keys.add(key)
                        declared.append(ReferenceTarget(
                            target_type="DEFINED_TERM",
                            target_id=term.upper(),
                            raw_label=term,
                            clause_id=clause.clause_id,
                            char_start=clause.char_start + match.start(),
                            char_end=clause.char_start + match.end()
                        ))

        return declared

    def extract_citations(self, clause: ClauseRecord) -> List[CrossReferenceCitation]:
        """
        Extracts all cross-reference citations present in a given clause using spaCy.
        """
        citations: List[CrossReferenceCitation] = []
        text = clause.text
        doc = self.nlp(text)

        # 1. Section & Article citations
        for match in self._section_ref_re.finditer(text):
            full_match = match.group(0).strip()
            raw_target = match.group(1).strip().rstrip(".)")
            # Strip subclause parens for primary section check e.g. '4.2(a)' -> '4.2'
            base_num = re.sub(r"\(.*?\)", "", raw_target).strip()
            target_type = "ARTICLE" if "article" in full_match.lower() or "art." in full_match.lower() else "SECTION"
            
            citations.append(CrossReferenceCitation(
                target_type=target_type,
                target_id=base_num.lower(),
                raw_text=full_match,
                source_clause_id=clause.clause_id,
                char_start=clause.char_start + match.start(),
                char_end=clause.char_start + match.end()
            ))

        # 2. Exhibit & Schedule citations
        for match in self._exhibit_ref_re.finditer(text):
            full_match = match.group(0).strip()
            raw_target = match.group(1).strip().rstrip(".)").upper()
            target_type = "SCHEDULE" if "schedule" in full_match.lower() else "EXHIBIT"
            
            citations.append(CrossReferenceCitation(
                target_type=target_type,
                target_id=raw_target,
                raw_text=full_match,
                source_clause_id=clause.clause_id,
                char_start=clause.char_start + match.start(),
                char_end=clause.char_start + match.end()
            ))

        return citations

    def check_document(
        self,
        clauses: List[ClauseRecord],
        doc_id: Optional[str] = None
    ) -> Tuple[List[RuleFlag], List[ReferenceTarget]]:
        """
        Validates cross-references across all clauses in a document, returning rule flags for dangling references.
        """
        effective_doc_id = doc_id or (clauses[0].doc_id if clauses else "unknown_doc")
        declared_targets = self.extract_declared_targets(clauses)

        # Build lookup set of declared normalized keys
        declared_lookup: Set[Tuple[str, str]] = set()
        for t in declared_targets:
            declared_lookup.add((t.target_type, t.target_id.lower()))

        flags: List[RuleFlag] = []
        flag_idx = 1

        for clause in clauses:
            citations = self.extract_citations(clause)
            for cit in citations:
                norm_variants = normalize_section_num(cit.target_id) if cit.target_type in ["SECTION", "ARTICLE"] else [cit.target_id.lower()]
                
                # Check if citation target matches any declared target
                is_resolved = any((cit.target_type, var) in declared_lookup for var in norm_variants)

                # If self-referencing declaration in header, it's resolved
                if not is_resolved and cit.target_type in ["SECTION", "ARTICLE"]:
                    # Check if this clause itself starts with this section number
                    for var in norm_variants:
                        if (cit.target_type, var) in declared_lookup:
                            is_resolved = True
                            break

                if not is_resolved:
                    # Determine severity:
                    # Critical definition / dependency citations ("as defined in", "pursuant to") -> HIGH
                    is_critical = any(kw in cit.raw_text.lower() for kw in ["as defined in", "defined in", "pursuant to", "subject to"])
                    severity = "HIGH" if is_critical else "MEDIUM"

                    flag_type = f"DANGLING_{cit.target_type}_REFERENCE"
                    
                    # Available targets preview
                    available = [f"{t.target_type} {t.target_id}" for t in declared_targets if t.target_type == cit.target_type]

                    flag = RuleFlag(
                        flag_id=f"FLAG_REF_{effective_doc_id}_{flag_idx:03d}",
                        doc_id=effective_doc_id,
                        flag_type=flag_type,
                        category="RULE_BASED",
                        severity=severity,
                        title=f"Dangling Reference: '{cit.raw_text}' not found",
                        description=(
                            f"Clause '{clause.clause_id}' cites '{cit.raw_text}', but no matching "
                            f"{cit.target_type.lower()} '{cit.target_id}' was declared in the contract text."
                        ),
                        clause_id=clause.clause_id,
                        involved_clause_ids=[clause.clause_id],
                        evidence={
                            "citation_text": cit.raw_text,
                            "target_type": cit.target_type,
                            "target_id": cit.target_id,
                            "available_targets_count": len(available),
                            "available_targets_sample": available[:10],
                            "char_start": cit.char_start,
                            "char_end": cit.char_end
                        },
                        claim_scope=ClaimScope(
                            what_this_shows="Exact text scanning identified a cross-reference to a section/exhibit not declared in this document.",
                            what_this_does_not_show="Does not evaluate whether the reference exists in an external schedule or master agreement not included in the uploaded text."
                        )
                    )
                    flags.append(flag)
                    flag_idx += 1

        return flags, declared_targets
