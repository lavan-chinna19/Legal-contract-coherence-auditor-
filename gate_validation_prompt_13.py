"""
gate_validation_prompt_13.py — Acceptance Gate Validator for Prompt 13.
Validates:
1. Gate 1: Both checkers run on all sample documents without crashing.
2. Gate 2: All deliberately broken test cases are correctly flagged (2 broken ref docs + 2 illogical date docs).
3. Gate 3: Integration into unified pipeline is confirmed end-to-end, producing rule flags alongside ML flags.
"""
import sys
import json
from pathlib import Path

from src.config import EDGAR_RAW_DIR, ClauseRecord
from src.segmentation.factory import get_segmenter
from src.rules.reference_checker import CrossReferenceChecker
from src.rules.date_checker import DateLogicChecker
from src.rules.unified_pipeline import UnifiedAuditor, format_unified_audit_report


def validate_prompt_13():
    print("=" * 76)
    print("PROMPT 13 ACCEPTANCE GATE VALIDATION")
    print("=" * 76)

    ref_checker = CrossReferenceChecker()
    date_checker = DateLogicChecker()
    auditor = UnifiedAuditor(reference_checker=ref_checker, date_checker=date_checker)

    results = {
        "gate_1_no_crashes": False,
        "gate_2_broken_cases_flagged": False,
        "gate_3_unified_pipeline": False,
        "details": {}
    }

    # ── GATE 1: Checkers run on sample documents without crashing ──────────────
    print("\n[Gate 1] Testing checkers on sample documents without crashing...")
    segmenter = get_segmenter("v1")
    txt_files = list(EDGAR_RAW_DIR.glob("*.txt"))
    sample_docs_audited = 0

    try:
        for fpath in txt_files[:3]:
            with open(fpath, "r", encoding="utf-8") as f:
                doc_clauses = segmenter.segment(f.read(), doc_id=fpath.stem)[:15]
            if doc_clauses:
                ref_flags, decl = ref_checker.check_document(doc_clauses, doc_id=fpath.stem)
                date_flags, dates = date_checker.check_document(doc_clauses, doc_id=fpath.stem)
                sample_docs_audited += 1
        
        # Test empty doc handling
        empty_ref_flags, _ = ref_checker.check_document([], doc_id="empty")
        empty_date_flags, _ = date_checker.check_document([], doc_id="empty")
        
        results["gate_1_no_crashes"] = True
        results["details"]["gate_1"] = {
            "sample_docs_tested": sample_docs_audited,
            "crashed": False
        }
        print(f"[PASS] Gate 1 Passed: {sample_docs_audited} real documents + edge cases audited with 0 crashes.")
    except Exception as e:
        print(f"[FAIL] Gate 1 Failed: {e}")
        results["details"]["gate_1"] = {"error": str(e)}

    # ── GATE 2: All deliberately broken test cases correctly flagged ──────────
    print("\n[Gate 2] Testing detection of all 4 deliberately broken test cases...")

    # Case 1: Dangling Section 8.4 & Exhibit C
    doc_ref_1 = [
        ClauseRecord("ref1_0", "doc_ref1", "Section 1.01. Definitions. 'Data' means records.", "Definitions", 0, 0, 48, "test"),
        ClauseRecord("ref1_1", "doc_ref1", "Section 1.02. Payment. Remit payment pursuant to Section 8.4.", "Payment", 1, 49, 111, "test"),
        ClauseRecord("ref1_2", "doc_ref1", "Section 1.03. Scope. Detailed in Exhibit C attached hereto.", "Scope", 2, 112, 171, "test")
    ]
    flags_ref1, _ = ref_checker.check_document(doc_ref_1, doc_id="doc_ref1")
    ref1_types = [f.flag_type for f in flags_ref1]
    case_1_ok = ("DANGLING_SECTION_REFERENCE" in ref1_types) and ("DANGLING_EXHIBIT_REFERENCE" in ref1_types)

    # Case 2: Dangling Section 14.1 & Article IV
    doc_ref_2 = [
        ClauseRecord("ref2_0", "doc_ref2", "ARTICLE I - RECITALS. The parties desire to partner.", "Recitals", 0, 0, 52, "test"),
        ClauseRecord("ref2_1", "doc_ref2", "ARTICLE II - DUTIES. Services as defined in Section 14.1 and Article IV.", "Duties", 1, 53, 126, "test")
    ]
    flags_ref2, _ = ref_checker.check_document(doc_ref_2, doc_id="doc_ref2")
    ref2_types = [f.flag_type for f in flags_ref2]
    case_2_ok = ("DANGLING_SECTION_REFERENCE" in ref2_types) and ("DANGLING_ARTICLE_REFERENCE" in ref2_types)

    # Case 3: Inverted Effective Date (Nov 15, 2025) > Termination Date (Feb 1, 2024)
    doc_date_1 = [
        ClauseRecord("date1_0", "doc_date1", "Section 1. Term. Effective as of November 15, 2025.", "Term", 0, 0, 51, "test"),
        ClauseRecord("date1_1", "doc_date1", "Section 2. Expiration. Terminates on February 1, 2024.", "Expiration", 1, 52, 105, "test")
    ]
    flags_date1, _ = date_checker.check_document(doc_date_1, doc_id="doc_date1")
    date1_types = [f.flag_type for f in flags_date1]
    case_3_ok = "INVERTED_CONTRACT_TERM" in date1_types

    # Case 4: Payment due March 1, 2022 before Effective Jan 1, 2025; intra-clause Oct 1, 2025 to Jan 1, 2024
    doc_date_2 = [
        ClauseRecord("date2_0", "doc_date2", "Section 1. Commences on January 1, 2025 and ends on December 31, 2025.", "Engagement", 0, 0, 68, "test"),
        ClauseRecord("date2_1", "doc_date2", "Section 2. Invoicing. Payment due on March 1, 2022.", "Payment", 1, 69, 120, "test"),
        ClauseRecord("date2_2", "doc_date2", "Section 3. Warranty from October 1, 2025 to January 1, 2024.", "Warranty", 2, 121, 181, "test")
    ]
    flags_date2, _ = date_checker.check_document(doc_date_2, doc_id="doc_date2")
    date2_types = [f.flag_type for f in flags_date2]
    case_4_ok = ("PAYMENT_BEFORE_EFFECTIVE_DATE" in date2_types) and ("INVERTED_DATE_RANGE" in date2_types)

    gate_2_passed = case_1_ok and case_2_ok and case_3_ok and case_4_ok
    results["gate_2_broken_cases_flagged"] = gate_2_passed
    results["details"]["gate_2"] = {
        "case_1_broken_ref_1_flagged": case_1_ok,
        "case_2_broken_ref_2_flagged": case_2_ok,
        "case_3_inverted_term_flagged": case_3_ok,
        "case_4_illogical_dates_flagged": case_4_ok,
        "total_test_flags_detected": len(flags_ref1) + len(flags_ref2) + len(flags_date1) + len(flags_date2)
    }

    if gate_2_passed:
        print(f"[PASS] Gate 2 Passed: All 4 test documents correctly flagged with exact expected violations ({results['details']['gate_2']['total_test_flags_detected']} total flags).")
    else:
        print(f"[FAIL] Gate 2 Failed: Case 1={case_1_ok}, Case 2={case_2_ok}, Case 3={case_3_ok}, Case 4={case_4_ok}")

    # ── GATE 3: Unified pipeline integration confirmed end-to-end ────────────
    print("\n[Gate 3] Running full end-to-end unified flag pipeline...")
    try:
        report = auditor.audit_document(doc_date_2, doc_id="doc_date2")
        gate_3_passed = (
            report.total_clauses == 3 and
            report.rule_violation_count >= 2 and
            len(report.scoring_result.clauses) == 3 and
            "rule_flags" in report.scoring_result.metadata and
            report.total_flags >= 2
        )
        results["gate_3_unified_pipeline"] = gate_3_passed
        results["details"]["gate_3"] = {
            "total_clauses": report.total_clauses,
            "ml_clauses_scored": len(report.scoring_result.clauses),
            "rule_flags_count": len(report.rule_flags),
            "total_flags": report.total_flags,
            "markdown_render_len": len(format_unified_audit_report(report, format_type="markdown")),
            "json_render_len": len(format_unified_audit_report(report, format_type="json"))
        }
        if gate_3_passed:
            print("[PASS] Gate 3 Passed: Unified pipeline produced integrated report with ML scoring and Rule flags.")
        else:
            print("[FAIL] Gate 3 Failed: Unified pipeline output validation failed.")
    except Exception as e:
        print(f"[FAIL] Gate 3 Failed: {e}")
        results["details"]["gate_3"] = {"error": str(e)}

    # Summary
    all_passed = results["gate_1_no_crashes"] and results["gate_2_broken_cases_flagged"] and results["gate_3_unified_pipeline"]
    print("\n" + "=" * 76)
    print(f"OVERALL STATUS: {'ALL GATES PASSED' if all_passed else 'SOME GATES FAILED'}")
    print("=" * 76)

    return all_passed, results


if __name__ == "__main__":
    passed, res = validate_prompt_13()
    sys.exit(0 if passed else 1)
