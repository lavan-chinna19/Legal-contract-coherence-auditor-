"""
demo_rules.py — Demonstration of Rule-Based Cross-Reference Resolution, Date-Logic Validation,
and Unified Auditor Pipeline (Prompt 13).
Runs on:
1. Real SEC EDGAR clean contracts (checking for crashes and structural parsing).
2. Deliberately broken reference test cases (dangling sections, exhibits, definitions).
3. Deliberately illogical date test cases (inverted effective/termination, retroactive payment, intra-clause inverted ranges).
4. Full unified pipeline producing integrated ML + Rule flags in one unified report.
"""
from pathlib import Path
import json

from src.config import EDGAR_RAW_DIR, ClauseRecord
from src.segmentation.factory import get_segmenter
from src.rules.reference_checker import CrossReferenceChecker
from src.rules.date_checker import DateLogicChecker
from src.rules.unified_pipeline import UnifiedAuditor, format_unified_audit_report


def build_test_cases():
    """Constructs the 4 deliberately broken test documents."""
    
    # Doc 1: Broken Reference (Section 8.4 and Exhibit C)
    doc_ref_1 = [
        ClauseRecord(
            clause_id="ref1_0",
            doc_id="doc_broken_ref_1",
            text="Section 1.01. Definitions. 'Confidential Information' means proprietary trade secrets.",
            label="Definitions",
            sequence_idx=0,
            char_start=0,
            char_end=88,
            source="test"
        ),
        ClauseRecord(
            clause_id="ref1_1",
            doc_id="doc_broken_ref_1",
            text="Section 1.02. Payment. Buyer shall remit payment pursuant to Section 8.4 of this Agreement.",
            label="Payment",
            sequence_idx=1,
            char_start=89,
            char_end=181,
            source="test"
        ),
        ClauseRecord(
            clause_id="ref1_2",
            doc_id="doc_broken_ref_1",
            text="Section 1.03. Scope of Work. Technical specifications are set forth in Exhibit C attached hereto.",
            label="Scope",
            sequence_idx=2,
            char_start=182,
            char_end=278,
            source="test"
        )
    ]

    # Doc 2: Broken Reference (Dangling definition in Section 14.1, missing Article IV)
    doc_ref_2 = [
        ClauseRecord(
            clause_id="ref2_0",
            doc_id="doc_broken_ref_2",
            text="ARTICLE I - RECITALS. The parties desire to enter into this consulting relationship.",
            label="Recitals",
            sequence_idx=0,
            char_start=0,
            char_end=84,
            source="test"
        ),
        ClauseRecord(
            clause_id="ref2_1",
            doc_id="doc_broken_ref_2",
            text="ARTICLE II - OBLIGATIONS. Consultant shall perform services as defined in Section 14.1 and Article IV.",
            label="Obligations",
            sequence_idx=1,
            char_start=85,
            char_end=189,
            source="test"
        )
    ]

    # Doc 3: Illogical Date (Effective Nov 15, 2025 > Termination Feb 1, 2024)
    doc_date_1 = [
        ClauseRecord(
            clause_id="date1_0",
            doc_id="doc_broken_date_1",
            text="Section 1. Term. This Agreement is effective as of November 15, 2025 (the 'Effective Date').",
            label="Term",
            sequence_idx=0,
            char_start=0,
            char_end=92,
            source="test"
        ),
        ClauseRecord(
            clause_id="date1_1",
            doc_id="doc_broken_date_1",
            text="Section 2. Expiration. Unless renewed, this Agreement shall terminate on February 1, 2024.",
            label="Termination",
            sequence_idx=1,
            char_start=93,
            char_end=183,
            source="test"
        )
    ]

    # Doc 4: Illogical Date (Payment before effective date, intra-clause inverted span)
    doc_date_2 = [
        ClauseRecord(
            clause_id="date2_0",
            doc_id="doc_broken_date_2",
            text="Section 1. Engagement. This Agreement commences on January 1, 2025 and ends on December 31, 2025.",
            label="Engagement",
            sequence_idx=0,
            char_start=0,
            char_end=98,
            source="test"
        ),
        ClauseRecord(
            clause_id="date2_1",
            doc_id="doc_broken_date_2",
            text="Section 2. Invoicing. First milestone payment due on March 1, 2022 by wire transfer.",
            label="Payment",
            sequence_idx=1,
            char_start=99,
            char_end=184,
            source="test"
        ),
        ClauseRecord(
            clause_id="date2_2",
            doc_id="doc_broken_date_2",
            text="Section 3. Warranty. Maintenance services run from October 1, 2025 to January 1, 2024.",
            label="Warranty",
            sequence_idx=2,
            char_start=185,
            char_end=271,
            source="test"
        )
    ]

    return [
        ("Deliberately Broken Reference Doc 1", doc_ref_1),
        ("Deliberately Broken Reference Doc 2", doc_ref_2),
        ("Deliberately Illogical Date Doc 3", doc_date_1),
        ("Deliberately Illogical Date Doc 4", doc_date_2),
    ]


def run_demo():
    print("=" * 76)
    print("DEMO: Prompt 13 — Rule-Based Information Extraction & Unified Pipeline")
    print("=" * 76)

    ref_checker = CrossReferenceChecker()
    date_checker = DateLogicChecker()
    auditor = UnifiedAuditor(reference_checker=ref_checker, date_checker=date_checker)

    # 1. Gate 1: Check real SEC EDGAR contracts without crashing
    segmenter = get_segmenter("v1")
    txt_files = list(EDGAR_RAW_DIR.glob("*.txt"))
    if txt_files:
        print("\n" + "-" * 76)
        print("GATE 1 VERIFICATION: Running checkers on real SEC EDGAR contracts")
        print("-" * 76)
        for i, fpath in enumerate(txt_files[:2]):
            with open(fpath, "r", encoding="utf-8") as f:
                doc_clauses = segmenter.segment(f.read(), doc_id=fpath.stem)[:20]
            
            ref_flags, declared = ref_checker.check_document(doc_clauses, doc_id=fpath.stem)
            date_flags, dates = date_checker.check_document(doc_clauses, doc_id=fpath.stem)
            
            print(f"  [EDGAR Contract {i+1}] `{fpath.name}` ({len(doc_clauses)} clauses)")
            print(f"    - Declared Sections/Exhibits indexed: {len(declared)}")
            print(f"    - Dates parsed: {len(dates)}")
            print(f"    - Reference flags: {len(ref_flags)}, Date logic flags: {len(date_flags)}")

    # 2. Gate 2: Verify all 4 deliberately broken test cases
    test_cases = build_test_cases()
    print("\n" + "=" * 76)
    print("GATE 2 VERIFICATION: Deliberately Broken Test Cases")
    print("=" * 76)

    for name, clauses in test_cases:
        doc_id = clauses[0].doc_id
        ref_flags, declared = ref_checker.check_document(clauses, doc_id=doc_id)
        date_flags, dates = date_checker.check_document(clauses, doc_id=doc_id)
        total_rule_flags = ref_flags + date_flags

        print(f"\n--- Test Document: {name} (`{doc_id}`) ---")
        print(f"  Clauses: {len(clauses)} | Rule Flags Raised: {len(total_rule_flags)}")
        for f in total_rule_flags:
            print(f"    - [{f.severity}] {f.flag_type}: {f.title}")
            print(f"      Description: {f.description}")

    # 3. Gate 3: Full End-to-End Unified Pipeline Run
    print("\n" + "=" * 76)
    print("GATE 3 VERIFICATION: Full Unified Pipeline Run (ML + Rule-Based Flags)")
    print("=" * 76)

    # Run on broken date doc 2 which has ML clauses + date flags
    target_doc = test_cases[3][1]
    unified_report = auditor.audit_document(target_doc, doc_id="doc_broken_date_2")

    print(f"Unified Report for `{unified_report.doc_id}`:")
    print(f"  Total Clauses:        {unified_report.total_clauses}")
    print(f"  Total Flags:          {unified_report.total_flags}")
    print(f"  ML Anomaly Count:     {unified_report.ml_anomaly_count}")
    print(f"  Rule Violation Count: {unified_report.rule_violation_count}")
    print(f"  High Severity Count:  {unified_report.high_severity_count}")
    print(f"  Medium Severity:      {unified_report.medium_severity_count}")

    print("\n" + "-" * 76)
    print("UNIFIED AUDIT MARKDOWN REPORT SAMPLE:")
    print("-" * 76)
    md_output = format_unified_audit_report(unified_report, format_type="markdown")
    print(md_output)

    return unified_report


if __name__ == "__main__":
    run_demo()
