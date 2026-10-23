"""
src/redteam/fixtures.py — Nonconfidential synthetic contract fixtures for reproducible red-team evaluation.
"""
from typing import List, Dict
from src.config import ClauseRecord


def get_synthetic_msa_clauses() -> List[ClauseRecord]:
    """
    10-clause Master Services Agreement with unambiguous structure, valid cross-references,
    and verified chronological dates. Clean negative control baseline.
    """
    doc_id = "SYNTH_DOC_01_MSA"
    raw_clauses = [
        ("Section 1. Preamble and Parties. This Master Services Agreement is entered into as of January 1, 2025 by and between Client Inc. and Provider LLC.", "Preamble"),
        ("Section 2. Scope of Services. Provider agrees to provide software development and consulting services as described in Exhibit A attached hereto.", "Services"),
        ("Section 3. Payment Terms. Invoices shall be payable within thirty (30) days of receipt. Payment due date shall be on or after the Effective Date.", "Payment"),
        ("Section 4. Intellectual Property. All work product developed pursuant to Section 2 shall be deemed work made for hire owned by Client.", "Intellectual Property"),
        ("Section 5. Confidentiality. Each party agrees to maintain in strict confidence all proprietary information disclosed under this Agreement.", "Confidentiality"),
        ("Section 6. Term and Termination. The effective date of this Agreement is January 1, 2025 and the termination date shall be December 31, 2025.", "Term"),
        ("Section 7. Indemnification. Provider shall defend and indemnify Client against any third-party claims arising from a breach of Section 5.", "Indemnification"),
        ("Section 8. Limitation of Liability. Neither party shall be liable for indirect or consequential damages arising under this Agreement.", "Liability"),
        ("Section 9. Governing Law. This Agreement shall be governed by and construed in accordance with the laws of the State of Delaware.", "Governing Law"),
        ("Section 10. Miscellaneous. This Agreement, including Exhibit A, constitutes the entire understanding between the parties.", "Miscellaneous"),
        ("Exhibit A. Statement of Work. Scope details, technical deliverables, and milestone specifications.", "Exhibit")
    ]

    clauses = []
    char_offset = 0
    for idx, (text, label) in enumerate(raw_clauses):
        clauses.append(ClauseRecord(
            clause_id=f"{doc_id}_c{idx:02d}",
            doc_id=doc_id,
            sequence_idx=idx,
            text=text,
            label=label,
            char_start=char_offset,
            char_end=char_offset + len(text),
            source="SYNTHETIC_REDTEAM_FIXTURE",
            split="evaluation"
        ))
        char_offset += len(text) + 2
    return clauses


def get_synthetic_sla_clauses() -> List[ClauseRecord]:
    """
    8-clause Software License Agreement.
    """
    doc_id = "SYNTH_DOC_02_SLA"
    raw_clauses = [
        ("Section 1. Grant of License. Licensor grants Licensee a non-exclusive, non-transferable license to use the Software.", "License Grant"),
        ("Section 2. Permitted Users. Use of the Software is limited to authorized employees pursuant to Section 1.", "Users"),
        ("Section 3. Fees and Taxes. Licensee shall pay the annual subscription fees set forth in Section 4.", "Fees"),
        ("Section 4. Schedule of Fees. Annual subscription fee shall be $50,000 payable upon execution.", "Fee Schedule"),
        ("Section 5. Warranty Disclaimer. Licensor disclaims all implied warranties of merchantability and fitness for a particular purpose.", "Warranty"),
        ("Section 6. Audit Rights. Licensor may audit Licensee's software deployment once annually upon reasonable notice.", "Audit"),
        ("Section 7. Term. The initial term begins on March 1, 2025 and expires on February 28, 2026.", "Term"),
        ("Section 8. Dispute Resolution. Any dispute under this Agreement shall be resolved through binding arbitration.", "Dispute")
    ]

    clauses = []
    char_offset = 0
    for idx, (text, label) in enumerate(raw_clauses):
        clauses.append(ClauseRecord(
            clause_id=f"{doc_id}_c{idx:02d}",
            doc_id=doc_id,
            sequence_idx=idx,
            text=text,
            label=label,
            char_start=char_offset,
            char_end=char_offset + len(text),
            source="SYNTHETIC_REDTEAM_FIXTURE",
            split="evaluation"
        ))
        char_offset += len(text) + 2
    return clauses


SYNTHETIC_FIXTURE_REGISTRY = {
    "SYNTH_DOC_01_MSA": get_synthetic_msa_clauses,
    "SYNTH_DOC_02_SLA": get_synthetic_sla_clauses
}
