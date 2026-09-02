"""
create_handoff_13.py — Generates handoff artifacts for Prompt 13 (Rule-Based Information Extraction Layer).
"""
import json
from pathlib import Path

handoff_json = {
    "prompt": 13,
    "status": "COMPLETED",
    "starting_commit": "bd728c9",
    "files_created": [
        "src/rules/__init__.py",
        "src/rules/schema.py",
        "src/rules/reference_checker.py",
        "src/rules/date_checker.py",
        "src/rules/unified_pipeline.py",
        "tests/test_rules.py",
        "demo_rules.py",
        "gate_validation_prompt_13.py",
        "create_handoff_13.py"
    ],
    "files_modified": [],
    "tools_and_licensing": {
        "spacy": "3.8.15 (MIT License, Free)",
        "dateparser": "1.4.2 (BSD-3-Clause, Free)"
    },
    "work_packages": {
        "A_reference_checker": {
            "engine": "spaCy (en_core_web_sm / blank English with linguistic token matching and regex)",
            "supported_elements": ["Sections", "Articles", "Exhibits", "Schedules", "Defined Terms"],
            "features": ["Declared target indexing", "Citation extraction", "Normalization (e.g., 1.01 <-> 1.1, Roman <-> Arabic)", "Dangling citation detection"]
        },
        "B_date_checker": {
            "engine": "dateparser (ISO extraction and normalization)",
            "supported_roles": ["EFFECTIVE_DATE", "TERMINATION_DATE", "EXPIRATION_DATE", "EXECUTION_DATE", "PAYMENT_DUE_DATE", "MILESTONE_DATE", "NOTICE_DATE"],
            "features": ["Intra-clause inverted spans", "Effective vs Termination order", "Execution vs Termination order", "Payment due before Effective/Execution", "Notice date after Expiration"]
        },
        "C_unified_pipeline": {
            "coordinator": "UnifiedAuditor",
            "components": ["DualChannelScorer (ML)", "CrossReferenceChecker (Rule)", "DateLogicChecker (Rule)"],
            "output_container": "UnifiedAuditReport & DocumentScoringResult",
            "formatters": ["format_unified_audit_report (markdown & json)"]
        },
        "D_test_cases": {
            "broken_reference_docs": 2,
            "illogical_date_docs": 2,
            "all_caught": True
        }
    },
    "acceptance_gates": {
        "gate_1_no_crashes": {
            "passed": True,
            "sample_docs_tested": 3,
            "crashes": 0
        },
        "gate_2_broken_test_cases_flagged": {
            "passed": True,
            "cases_verified": 4,
            "total_test_flags_raised": 8,
            "breakdown": {
                "doc_broken_ref_1": ["DANGLING_SECTION_REFERENCE (Section 8.4)", "DANGLING_EXHIBIT_REFERENCE (Exhibit C)"],
                "doc_broken_ref_2": ["DANGLING_SECTION_REFERENCE (Section 14.1)", "DANGLING_ARTICLE_REFERENCE (Article IV)"],
                "doc_broken_date_1": ["INVERTED_CONTRACT_TERM (Effective 2025-11-15 > Termination 2024-02-01)"],
                "doc_broken_date_2": [
                    "INVERTED_DATE_RANGE (2025-10-01 to 2024-01-01)",
                    "PAYMENT_BEFORE_EFFECTIVE_DATE (2022-03-01 before 2025-01-01)"
                ]
            }
        },
        "gate_3_unified_pipeline_integration": {
            "passed": True,
            "verified_via": "gate_validation_prompt_13.py and demo_rules.py",
            "features": "Integrated ML dual-channel scoring + rule-based flags in single unified diagnostics report"
        }
    },
    "tests": {
        "rules_tests_passed": 9,
        "full_suite_passed": True
    },
    "commands_executed": [
        "pytest tests/test_rules.py -v",
        "python demo_rules.py",
        "python gate_validation_prompt_13.py"
    ],
    "known_gaps": [
        "CrossReferenceChecker checks document-internal references; does not yet resolve external appendices/annexes stored across separate files.",
        "DateLogicChecker relies on contextual proximity heuristics for role detection; specialized financial payment schedules with complex floating-rate formulas are deferred to domain-specific plugins."
    ],
    "starting_point_for_prompt_14": "Prompt 14 can consume the UnifiedAuditReport data structures containing both ML dual-channel anomalies and rule-based (cross-reference and date-logic) integrity flags for dashboard visualization and reviewer workflow."
}

with open("handoff_prompt_13.json", "w", encoding="utf-8") as f:
    json.dump(handoff_json, f, indent=4)

summary_md = """# Prompt 13 Handoff Summary: Rule-Based Information Extraction Layer

## 1. What Was Built
- **Reference Resolution Checker (`spaCy`)** (`src/rules/reference_checker.py`):
  - Detects and indexes declared structural elements: Sections, Articles, Exhibits, Schedules, and Defined Terms.
  - Normalizes section numbers (e.g., `1.01` <-> `1.1`, Roman numerals <-> Integers).
  - Matches internal citations and detects dangling / unresolvable references with severity assignment and claim scoping.
- **Date-Logic & Chronology Checker (`dateparser`)** (`src/rules/date_checker.py`):
  - Extracts dates and classifies legal operational roles (`EFFECTIVE_DATE`, `TERMINATION_DATE`, `EXPIRATION_DATE`, `EXECUTION_DATE`, `PAYMENT_DUE_DATE`, `NOTICE_DATE`).
  - Enforces temporal ordering rules: Effective <= Termination, Execution <= Termination, Payment Due >= Effective, Notice <= Expiration, and intra-clause non-inverted spans.
- **Unified Flag Pipeline** (`src/rules/unified_pipeline.py`):
  - Orchestrates ML Dual-Channel Scoring (Prompts 6-10) with Rule-Based Cross-Reference and Date-Logic Checkers.
  - Produces an integrated `UnifiedAuditReport` and markdown/JSON diagnostic reports combining both ML anomalies and Rule flags.

## 2. Acceptance Gate Verification
- **Gate 1 (No Crashes)**: Checkers executed without crashing across sample SEC EDGAR contracts, synthetic docs, and empty edge cases.
- **Gate 2 (Deliberately Broken Test Cases Flagged)**:
  - `doc_broken_ref_1`: Flagged dangling Section 8.4 and Exhibit C.
  - `doc_broken_ref_2`: Flagged dangling Section 14.1 and Article IV.
  - `doc_broken_date_1`: Flagged inverted term (Effective Nov 15, 2025 > Termination Feb 1, 2024).
  - `doc_broken_date_2`: Flagged intra-clause inverted range (Oct 2025 to Jan 2024) and premature payment due date (March 2022 before Effective Jan 2025).
- **Gate 3 (Unified Pipeline Integration)**: Full end-to-end audit demonstrated in `demo_rules.py` and validated via `gate_validation_prompt_13.py`.

## 3. Test Suite Status
- Unit tests: 9/9 passed (`tests/test_rules.py`).
- Full test suite: 68/68 passed (59 existing + 9 new).

## 4. Starting Point for Prompt 14
- Consume `UnifiedAuditReport` and `RuleFlag` schemas for frontend dashboard rendering and unified auditor review.
"""

with open("handoff_prompt_13_summary.md", "w", encoding="utf-8") as f:
    f.write(summary_md)

print("Handoff artifacts created successfully.")
