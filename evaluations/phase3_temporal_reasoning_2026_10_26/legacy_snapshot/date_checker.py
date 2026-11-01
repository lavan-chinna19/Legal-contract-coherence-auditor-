"""
src/rules/date_checker.py — Date-Logic Extraction and Chronological Consistency Validator.
Uses dateparser to parse dates from contract clauses and verifies operational timeline logic
(e.g., Effective Date <= Termination Date, Execution Date <= Expiration Date, Payment Date >= Effective Date).
"""
import re
from datetime import datetime, date
from typing import List, Dict, Tuple, Optional, Any
import dateparser

from src.config import ClauseRecord
from src.rules.schema import (
    DateEntity,
    RuleFlag,
    ClaimScope
)


# Common date regex patterns for legal contracts
MONTHS_PATTERN = r"(?:January|February|March|April|May|June|July|August|September|October|November|December|Jan\.?|Feb\.?|Mar\.?|Apr\.?|Jun\.?|Jul\.?|Aug\.?|Sep\.?|Sept\.?|Oct\.?|Nov\.?|Dec\.?)"

DATE_PATTERNS = [
    # "October 15, 2024" or "Oct 15, 2024" or "October 15 2024"
    re.compile(rf"\b({MONTHS_PATTERN}\s+\d{{1,2}}(?:st|nd|rd|th)?,?\s+\d{{4}})\b", re.IGNORECASE),
    # "15th day of October, 2024" or "15 October 2024"
    re.compile(rf"\b(\d{{1,2}}(?:st|nd|rd|th)?(?:\s+day\s+of)?\s+{MONTHS_PATTERN},?\s+\d{{4}})\b", re.IGNORECASE),
    # "2024-10-15" or "2024/10/15"
    re.compile(r"\b(\d{4}[-/]\d{1,2}[-/]\d{1,2})\b"),
    # "10/15/2024" or "10-15-2024"
    re.compile(r"\b(\d{1,2}[-/]\d{1,2}[-/]\d{4})\b")
]

# Role keyword patterns
ROLE_PATTERNS = [
    ("EFFECTIVE_DATE", re.compile(r"(?:effective\s+(?:as\s+of|date|from|on)|commenc(?:es?|ing|ement)\s+(?:on|as\s+of|date)|start\s+date)", re.IGNORECASE)),
    ("TERMINATION_DATE", re.compile(r"(?:terminat(?:es?|ion|ed)\s+(?:on|as\s+of|date)|end\s+date|closing\s+date\b)", re.IGNORECASE)),
    ("EXPIRATION_DATE", re.compile(r"(?:expir(?:es?|ation|y)\s+(?:on|as\s+of|date))", re.IGNORECASE)),
    ("EXECUTION_DATE", re.compile(r"(?:executed\s+(?:on|as\s+of)|dated\s+as\s+of|entered\s+into\s+(?:on|as\s+of)|signed\s+(?:on|as\s+of))", re.IGNORECASE)),
    ("PAYMENT_DUE_DATE", re.compile(r"(?:payment\s+(?:due|payable|shall\s+be\s+made)\s+(?:on|by|no\s+later\s+than|before)|invoice\s+due|payable\s+on)", re.IGNORECASE)),
    ("MILESTONE_DATE", re.compile(r"(?:milestone|deliver(?:y|able)\s+(?:date|due|by)|phase\s+\d+\s+completion)", re.IGNORECASE)),
    ("NOTICE_DATE", re.compile(r"(?:notice\s+(?:date|given\s+by|required\s+by|prior\s+to))", re.IGNORECASE))
]


class DateLogicChecker:
    """
    Extracts dates and associated legal timeline roles from contract clauses,
    validating temporal logic and flagging chronological contradictions.
    """

    def __init__(self):
        self._dateparser_settings = {
            "PREFER_DAY_OF_MONTH": "first",
            "REQUIRE_PARTS": ["year", "month"],
            "RETURN_AS_TIMEZONE_AWARE": False
        }

    def extract_dates_from_clause(self, clause: ClauseRecord) -> List[DateEntity]:
        """
        Scans clause text for dates and classifies their role based on surrounding context.
        """
        entities: List[DateEntity] = []
        text = clause.text
        seen_spans = set()

        for pat in DATE_PATTERNS:
            for match in pat.finditer(text):
                span = (match.start(), match.end())
                if any(s[0] <= span[0] and span[1] <= s[1] for s in seen_spans):
                    continue
                seen_spans.add(span)

                raw_date = match.group(1).strip()
                parsed = dateparser.parse(raw_date, settings=self._dateparser_settings)
                if parsed is None:
                    continue

                # Context window: check immediately preceding 60 chars or back to sentence/clause boundary
                start_ctx = max(0, span[0] - 60)
                preceding_text = text[start_ctx:span[0]]

                # Find the closest role pattern in preceding text
                role = "GENERAL_DATE"
                best_match_end = -1
                for role_name, role_re in ROLE_PATTERNS:
                    for m in role_re.finditer(preceding_text):
                        if m.end() > best_match_end:
                            best_match_end = m.end()
                            role = role_name

                # If no preceding role found, check following 40 chars
                if role == "GENERAL_DATE":
                    following_text = text[span[1]:min(len(text), span[1] + 40)]
                    for role_name, role_re in ROLE_PATTERNS:
                        if role_re.search(following_text):
                            role = role_name
                            break

                entities.append(DateEntity(
                    role=role,
                    raw_text=raw_date,
                    parsed_iso=parsed.strftime("%Y-%m-%d"),
                    clause_id=clause.clause_id,
                    char_start=clause.char_start + span[0],
                    char_end=clause.char_start + span[1]
                ))

        # Sort extracted entities by character position
        entities.sort(key=lambda d: d.char_start)
        return entities

    def check_document(
        self,
        clauses: List[ClauseRecord],
        doc_id: Optional[str] = None
    ) -> Tuple[List[RuleFlag], List[DateEntity]]:
        """
        Extracts all dates and validates global and intra-clause chronological consistency.
        """
        effective_doc_id = doc_id or (clauses[0].doc_id if clauses else "unknown_doc")
        all_dates: List[DateEntity] = []

        for clause in clauses:
            dates = self.extract_dates_from_clause(clause)
            all_dates.extend(dates)

        flags: List[RuleFlag] = []
        flag_idx = 1

        # 1. Intra-Clause Inversion Check (e.g., "from [date1] to [date2]" within same clause)
        for clause in clauses:
            clause_dates = [d for d in all_dates if d.clause_id == clause.clause_id]
            if len(clause_dates) >= 2:
                # Check if text connects them with 'to', 'until', 'through'
                for i in range(len(clause_dates) - 1):
                    d1 = clause_dates[i]
                    d2 = clause_dates[i + 1]
                    dt1 = datetime.strptime(d1.parsed_iso, "%Y-%m-%d").date()
                    dt2 = datetime.strptime(d2.parsed_iso, "%Y-%m-%d").date()

                    inter_text = clause.text[d1.char_end - clause.char_start : d2.char_start - clause.char_start].lower()
                    if any(conn in inter_text for conn in ["to", "through", "until", "ending on", "terminating on"]):
                        if dt1 > dt2:
                            delta_days = (dt1 - dt2).days
                            flags.append(RuleFlag(
                                flag_id=f"FLAG_DATE_{effective_doc_id}_{flag_idx:03d}",
                                doc_id=effective_doc_id,
                                flag_type="INVERTED_DATE_RANGE",
                                category="RULE_BASED",
                                severity="HIGH",
                                title="Inverted Date Span in Clause",
                                description=(
                                    f"Clause '{clause.clause_id}' specifies an inverted date range: "
                                    f"Start date '{d1.raw_text}' ({d1.parsed_iso}) occurs {delta_days} days after "
                                    f"end date '{d2.raw_text}' ({d2.parsed_iso})."
                                ),
                                clause_id=clause.clause_id,
                                involved_clause_ids=[clause.clause_id],
                                evidence={
                                    "start_date": d1.parsed_iso,
                                    "end_date": d2.parsed_iso,
                                    "delta_days": -delta_days,
                                    "start_raw": d1.raw_text,
                                    "end_raw": d2.raw_text
                                },
                                claim_scope=ClaimScope(
                                    what_this_shows="Chronological parsing identified that the stated start date occurs after the stated end date.",
                                    what_this_does_not_show="Does not determine whether this is a drafting typo or an intentional retrospective clause."
                                )
                            ))
                            flag_idx += 1

        # 2. Document-Level Role Checks
        effective_dates = [d for d in all_dates if d.role == "EFFECTIVE_DATE"]
        termination_dates = [d for d in all_dates if d.role in ["TERMINATION_DATE", "EXPIRATION_DATE"]]
        execution_dates = [d for d in all_dates if d.role == "EXECUTION_DATE"]
        payment_dates = [d for d in all_dates if d.role == "PAYMENT_DUE_DATE"]
        notice_dates = [d for d in all_dates if d.role == "NOTICE_DATE"]

        # Rule A: Effective Date <= Termination / Expiration Date
        for eff in effective_dates:
            eff_dt = datetime.strptime(eff.parsed_iso, "%Y-%m-%d").date()
            for term in termination_dates:
                term_dt = datetime.strptime(term.parsed_iso, "%Y-%m-%d").date()
                if eff_dt > term_dt:
                    delta_days = (eff_dt - term_dt).days
                    flags.append(RuleFlag(
                        flag_id=f"FLAG_DATE_{effective_doc_id}_{flag_idx:03d}",
                        doc_id=effective_doc_id,
                        flag_type="INVERTED_CONTRACT_TERM",
                        category="RULE_BASED",
                        severity="HIGH",
                        title=f"Illogical Term: Effective Date after {term.role.replace('_', ' ').title()}",
                        description=(
                            f"Effective Date '{eff.raw_text}' ({eff.parsed_iso}) in clause '{eff.clause_id}' "
                            f"is {delta_days} days after {term.role.replace('_', ' ').title()} '{term.raw_text}' "
                            f"({term.parsed_iso}) in clause '{term.clause_id}'."
                        ),
                        clause_id=eff.clause_id,
                        involved_clause_ids=list(set([eff.clause_id, term.clause_id])),
                        evidence={
                            "effective_date": eff.parsed_iso,
                            "termination_date": term.parsed_iso,
                            "effective_raw": eff.raw_text,
                            "termination_raw": term.raw_text,
                            "delta_days": -delta_days
                        },
                        claim_scope=ClaimScope(
                            what_this_shows="The parsed contract effective date is chronologically after the stated termination/expiration date.",
                            what_this_does_not_show="Does not evaluate if subsequent amendments or side letters extend the term."
                        )
                    ))
                    flag_idx += 1

        # Rule B: Execution Date <= Termination / Expiration Date
        for exe in execution_dates:
            exe_dt = datetime.strptime(exe.parsed_iso, "%Y-%m-%d").date()
            for term in termination_dates:
                term_dt = datetime.strptime(term.parsed_iso, "%Y-%m-%d").date()
                if exe_dt > term_dt:
                    delta_days = (exe_dt - term_dt).days
                    flags.append(RuleFlag(
                        flag_id=f"FLAG_DATE_{effective_doc_id}_{flag_idx:03d}",
                        doc_id=effective_doc_id,
                        flag_type="EXECUTION_AFTER_TERMINATION",
                        category="RULE_BASED",
                        severity="HIGH",
                        title="Execution Date Occurs After Termination",
                        description=(
                            f"Contract execution date '{exe.raw_text}' ({exe.parsed_iso}) in clause '{exe.clause_id}' "
                            f"is after stated termination date '{term.raw_text}' ({term.parsed_iso}) in clause '{term.clause_id}'."
                        ),
                        clause_id=exe.clause_id,
                        involved_clause_ids=list(set([exe.clause_id, term.clause_id])),
                        evidence={
                            "execution_date": exe.parsed_iso,
                            "termination_date": term.parsed_iso,
                            "delta_days": -delta_days
                        },
                        claim_scope=ClaimScope(
                            what_this_shows="Contract execution date is chronologically later than the termination date.",
                            what_this_does_not_show="Does not assess validity of retroactive ratification under contract law."
                        )
                    ))
                    flag_idx += 1

        # Rule C: Payment Due Date >= Effective Date / Execution Date
        for pay in payment_dates:
            pay_dt = datetime.strptime(pay.parsed_iso, "%Y-%m-%d").date()
            ref_dates = effective_dates or execution_dates
            for ref in ref_dates:
                ref_dt = datetime.strptime(ref.parsed_iso, "%Y-%m-%d").date()
                if pay_dt < ref_dt:
                    delta_days = (ref_dt - pay_dt).days
                    flags.append(RuleFlag(
                        flag_id=f"FLAG_DATE_{effective_doc_id}_{flag_idx:03d}",
                        doc_id=effective_doc_id,
                        flag_type="PAYMENT_BEFORE_EFFECTIVE_DATE",
                        category="RULE_BASED",
                        severity="HIGH",
                        title="Payment Due Before Contract Effective Date",
                        description=(
                            f"Payment due date '{pay.raw_text}' ({pay.parsed_iso}) in clause '{pay.clause_id}' "
                            f"falls {delta_days} days before contract {ref.role.replace('_', ' ').title()} '{ref.raw_text}' ({ref.parsed_iso})."
                        ),
                        clause_id=pay.clause_id,
                        involved_clause_ids=list(set([pay.clause_id, ref.clause_id])),
                        evidence={
                            "payment_due_date": pay.parsed_iso,
                            "reference_date": ref.parsed_iso,
                            "reference_role": ref.role,
                            "delta_days": delta_days
                        },
                        claim_scope=ClaimScope(
                            what_this_shows="Scheduled payment date precedes the operational effective or execution date.",
                            what_this_does_not_show="Does not verify whether pre-contractual deposit agreements exist."
                        )
                    ))
                    flag_idx += 1

        # Rule D: Notice Date <= Expiration / Termination Date
        for not_d in notice_dates:
            not_dt = datetime.strptime(not_d.parsed_iso, "%Y-%m-%d").date()
            for term in termination_dates:
                term_dt = datetime.strptime(term.parsed_iso, "%Y-%m-%d").date()
                if not_dt > term_dt:
                    delta_days = (not_dt - term_dt).days
                    flags.append(RuleFlag(
                        flag_id=f"FLAG_DATE_{effective_doc_id}_{flag_idx:03d}",
                        doc_id=effective_doc_id,
                        flag_type="NOTICE_AFTER_EXPIRATION",
                        category="RULE_BASED",
                        severity="MEDIUM",
                        title="Notice Deadline Falls After Contract Expiration",
                        description=(
                            f"Notice deadline '{not_d.raw_text}' ({not_d.parsed_iso}) in clause '{not_d.clause_id}' "
                            f"is {delta_days} days after contract expiration '{term.raw_text}' ({term.parsed_iso})."
                        ),
                        clause_id=not_d.clause_id,
                        involved_clause_ids=list(set([not_d.clause_id, term.clause_id])),
                        evidence={
                            "notice_date": not_d.parsed_iso,
                            "expiration_date": term.parsed_iso,
                            "delta_days": -delta_days
                        },
                        claim_scope=ClaimScope(
                            what_this_shows="Notice deadline is scheduled after the contract has already expired.",
                            what_this_does_not_show="Does not account for post-termination survival clauses."
                        )
                    ))
                    flag_idx += 1

        return flags, all_dates
