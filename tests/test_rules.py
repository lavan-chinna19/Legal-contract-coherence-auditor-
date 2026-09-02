"""
tests/test_rules.py — Comprehensive Unit Tests for Rule-Based Checkers and Unified Pipeline.
Tests spaCy cross-reference validation, dateparser date-logic validation,
and unified multi-paradigm pipeline integration.
"""
import pytest
from datetime import datetime

from src.config import ClauseRecord
from src.rules.schema import (
    RuleFlag,
    UnifiedAuditReport,
    ReferenceTarget,
    DateEntity,
    ClaimScope
)
from src.rules.reference_checker import CrossReferenceChecker, normalize_section_num
from src.rules.date_checker import DateLogicChecker
from src.rules.unified_pipeline import UnifiedAuditor, format_unified_audit_report
from src.scoring.pipeline import DualChannelScorer


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures for Broken References and Illogical Dates (Work Package D)
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def doc_broken_ref_1():
    """Document 1 with deliberately broken Section 8.4 and Exhibit C references."""
    return [
        ClauseRecord(
            clause_id="doc_ref1_0",
            doc_id="doc_broken_ref_1",
            text="Section 1.01. Definitions. As used herein, 'Confidential Information' means proprietary data.",
            label="Definitions",
            sequence_idx=0,
            char_start=0,
            char_end=95,
            source="test"
        ),
        ClauseRecord(
            clause_id="doc_ref1_1",
            doc_id="doc_broken_ref_1",
            text="Section 1.02. Payment Terms. Buyer shall remit payment pursuant to Section 8.4 of this Agreement.",
            label="Payment",
            sequence_idx=1,
            char_start=96,
            char_end=198,
            source="test"
        ),
        ClauseRecord(
            clause_id="doc_ref1_2",
            doc_id="doc_broken_ref_1",
            text="Section 1.03. Deliverables. Specifications are set forth in Exhibit C attached hereto.",
            label="Deliverables",
            sequence_idx=2,
            char_start=199,
            char_end=285,
            source="test"
        )
    ]


@pytest.fixture
def doc_broken_ref_2():
    """Document 2 with dangling definition reference in Section 14.1 and missing Article IV."""
    return [
        ClauseRecord(
            clause_id="doc_ref2_0",
            doc_id="doc_broken_ref_2",
            text="ARTICLE I - RECITALS. The parties desire to enter into this consulting relationship.",
            label="Recitals",
            sequence_idx=0,
            char_start=0,
            char_end=84,
            source="test"
        ),
        ClauseRecord(
            clause_id="doc_ref2_1",
            doc_id="doc_broken_ref_2",
            text="ARTICLE II - OBLIGATIONS. Consultant shall perform services as defined in Section 14.1 and Article IV.",
            label="Obligations",
            sequence_idx=1,
            char_start=85,
            char_end=189,
            source="test"
        )
    ]


@pytest.fixture
def doc_broken_date_1():
    """Document 3 with inverted term: Effective Date (Nov 15, 2025) is after Termination Date (Feb 1, 2024)."""
    return [
        ClauseRecord(
            clause_id="doc_date1_0",
            doc_id="doc_broken_date_1",
            text="Section 1. Term. This Agreement is effective as of November 15, 2025 (the 'Effective Date').",
            label="Term",
            sequence_idx=0,
            char_start=0,
            char_end=92,
            source="test"
        ),
        ClauseRecord(
            clause_id="doc_date1_1",
            doc_id="doc_broken_date_1",
            text="Section 2. Expiration. Unless renewed, this Agreement shall terminate on February 1, 2024.",
            label="Termination",
            sequence_idx=1,
            char_start=93,
            char_end=183,
            source="test"
        )
    ]


@pytest.fixture
def doc_broken_date_2():
    """Document 4 with payment due date preceding effective date and intra-clause inverted range."""
    return [
        ClauseRecord(
            clause_id="doc_date2_0",
            doc_id="doc_broken_date_2",
            text="Section 1. Engagement. This Agreement commences on January 1, 2025 and ends on December 31, 2025.",
            label="Engagement",
            sequence_idx=0,
            char_start=0,
            char_end=98,
            source="test"
        ),
        ClauseRecord(
            clause_id="doc_date2_1",
            doc_id="doc_broken_date_2",
            text="Section 2. Invoicing. First milestone payment due on March 1, 2022 by wire transfer.",
            label="Payment",
            sequence_idx=1,
            char_start=99,
            char_end=184,
            source="test"
        ),
        ClauseRecord(
            clause_id="doc_date2_2",
            doc_id="doc_broken_date_2",
            text="Section 3. Warranty Period. Maintenance services run from October 1, 2025 to January 1, 2024.",
            label="Warranty",
            sequence_idx=2,
            char_start=185,
            char_end=280,
            source="test"
        )
    ]


@pytest.fixture
def doc_clean_sample():
    """Clean document with valid cross-references and consistent chronology."""
    return [
        ClauseRecord(
            clause_id="clean_0",
            doc_id="doc_clean",
            text="Section 1.01. Definitions. 'Services' means the engineering tasks described in Exhibit A.",
            label="Definitions",
            sequence_idx=0,
            char_start=0,
            char_end=90,
            source="test"
        ),
        ClauseRecord(
            clause_id="clean_1",
            doc_id="doc_clean",
            text="Section 1.02. Term. This Agreement is effective as of January 1, 2024 and terminates on December 31, 2024.",
            label="Term",
            sequence_idx=1,
            char_start=91,
            char_end=198,
            source="test"
        ),
        ClauseRecord(
            clause_id="clean_2",
            doc_id="doc_clean",
            text="Section 1.03. Payment. Subject to Section 1.01, payment is due on June 1, 2024.",
            label="Payment",
            sequence_idx=2,
            char_start=199,
            char_end=278,
            source="test"
        ),
        ClauseRecord(
            clause_id="clean_3",
            doc_id="doc_clean",
            text="Exhibit A. Statement of Work. Detailed technical deliverables.",
            label="Exhibit",
            sequence_idx=3,
            char_start=279,
            char_end=341,
            source="test"
        )
    ]


# ─────────────────────────────────────────────────────────────────────────────
# Work Package A Tests: Cross-Reference Resolution (spaCy)
# ─────────────────────────────────────────────────────────────────────────────

def test_normalize_section_num():
    assert "1.01" in normalize_section_num("1.01")
    assert "1.1" in normalize_section_num("1.01")
    assert "4" in normalize_section_num("iv")
    assert "iv" in normalize_section_num("4")


def test_reference_checker_clean_document(doc_clean_sample):
    checker = CrossReferenceChecker()
    flags, declared = checker.check_document(doc_clean_sample)

    assert len(declared) >= 3  # Section 1.01, Section 1.02, Section 1.03, Exhibit A
    assert len(flags) == 0     # Clean document should have 0 dangling flags


def test_reference_checker_broken_ref_doc_1(doc_broken_ref_1):
    """Confirm broken Section 8.4 and Exhibit C are caught in doc 1."""
    checker = CrossReferenceChecker()
    flags, declared = checker.check_document(doc_broken_ref_1)

    assert len(flags) == 2
    flag_types = [f.flag_type for f in flags]
    assert "DANGLING_SECTION_REFERENCE" in flag_types
    assert "DANGLING_EXHIBIT_REFERENCE" in flag_types

    # Section 8.4 citation in clause 1 is critical ("pursuant to") -> HIGH severity
    sec_flag = next(f for f in flags if f.flag_type == "DANGLING_SECTION_REFERENCE")
    assert sec_flag.severity == "HIGH"
    assert "Section 8.4" in sec_flag.evidence["citation_text"]
    assert sec_flag.clause_id == "doc_ref1_1"


def test_reference_checker_broken_ref_doc_2(doc_broken_ref_2):
    """Confirm dangling definition reference to Section 14.1 and missing Article IV in doc 2."""
    checker = CrossReferenceChecker()
    flags, declared = checker.check_document(doc_broken_ref_2)

    assert len(flags) >= 2
    flag_targets = [f.evidence.get("target_id") for f in flags]
    assert "14.1" in flag_targets
    assert "iv" in flag_targets or "4" in flag_targets


# ─────────────────────────────────────────────────────────────────────────────
# Work Package B Tests: Date Logic Validation (dateparser)
# ─────────────────────────────────────────────────────────────────────────────

def test_date_checker_clean_document(doc_clean_sample):
    checker = DateLogicChecker()
    flags, dates = checker.check_document(doc_clean_sample)

    assert len(dates) >= 3
    assert len(flags) == 0  # Chronologically consistent


def test_date_checker_inverted_term_doc_3(doc_broken_date_1):
    """Confirm inverted Effective Date (Nov 2025) > Termination Date (Feb 2024) is caught."""
    checker = DateLogicChecker()
    flags, dates = checker.check_document(doc_broken_date_1)

    assert len(flags) >= 1
    flag = flags[0]
    assert flag.flag_type == "INVERTED_CONTRACT_TERM"
    assert flag.severity == "HIGH"
    assert "Effective Date" in flag.title
    assert flag.evidence["effective_date"] == "2025-11-15"
    assert flag.evidence["termination_date"] == "2024-02-01"
    assert flag.evidence["delta_days"] < 0


def test_date_checker_broken_date_doc_4(doc_broken_date_2):
    """Confirm payment before effective date and intra-clause inverted date range are caught."""
    checker = DateLogicChecker()
    flags, dates = checker.check_document(doc_broken_date_2)

    assert len(flags) >= 2
    flag_types = [f.flag_type for f in flags]
    assert "PAYMENT_BEFORE_EFFECTIVE_DATE" in flag_types
    assert "INVERTED_DATE_RANGE" in flag_types

    # Check intra-clause inversion flag details
    intra_flag = next(f for f in flags if f.flag_type == "INVERTED_DATE_RANGE")
    assert intra_flag.severity == "HIGH"
    assert intra_flag.evidence["start_date"] == "2025-10-01"
    assert intra_flag.evidence["end_date"] == "2024-01-01"


# ─────────────────────────────────────────────────────────────────────────────
# Work Package C & Acceptance Gate 3 Tests: Unified Pipeline Integration
# ─────────────────────────────────────────────────────────────────────────────

def test_unified_auditor_end_to_end(doc_broken_ref_1, doc_broken_date_2):
    """Verify UnifiedAuditor coordinates ML scorer and rule checkers into unified report."""
    auditor = UnifiedAuditor()

    # Test doc 1 (Broken references)
    report1 = auditor.audit_document(doc_broken_ref_1, doc_id="doc_broken_ref_1")
    assert isinstance(report1, UnifiedAuditReport)
    assert report1.doc_id == "doc_broken_ref_1"
    assert report1.total_clauses == 3
    assert report1.rule_violation_count == 2
    assert report1.total_flags >= 2
    assert report1.high_severity_count >= 1

    # Check markdown formatter
    md1 = format_unified_audit_report(report1, format_type="markdown")
    assert "# Unified Contract Integrity & Coherence Audit" in md1
    assert "Rule-Based Integrity Violations" in md1
    assert "DANGLING_SECTION_REFERENCE" in md1
    assert "ML Dual-Channel Coherence Table" in md1

    # Check JSON serialization
    json1 = format_unified_audit_report(report1, format_type="json")
    assert '"doc_id": "doc_broken_ref_1"' in json1
    assert '"rule_flags"' in json1


def test_unified_auditor_empty_doc():
    """Verify UnifiedAuditor handles empty document gracefully."""
    auditor = UnifiedAuditor()
    report = auditor.audit_document([])
    assert report.total_clauses == 0
    assert report.total_flags == 0
    assert report.rule_violation_count == 0
