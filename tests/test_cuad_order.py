"""
tests/test_cuad_order.py — Automated test for CUAD clause-order preservation.

RESEARCH/DEMO PROJECT.

This test uses EITHER:
  (a) The live CUAD dataset if HuggingFace access is available and the processed
      order report already exists (ingest_cuad.py must have been run first), OR
  (b) A small synthetic fixture that mimics the CUAD QA structure to verify the
      order-checking logic itself.

Run:
    pytest tests/test_cuad_order.py -v

If the order report does not yet exist (ingest_cuad.py not run), the live-data
tests are skipped and only the fixture-based logic test runs.
"""

import json
import sys
from pathlib import Path
from collections import defaultdict

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.config import CUAD_ORDER_REPORT
from src.data.ingest_cuad import verify_clause_order


# ---------------------------------------------------------------------------
# Fixture-based logic tests (always run — no network needed)
# ---------------------------------------------------------------------------

class _FakeDataset:
    """Minimal dict-like mock that mimics the HuggingFace dataset API."""

    def __init__(self, rows):
        self._rows = rows

    def __len__(self):
        return len(self._rows)

    def __getitem__(self, idx):
        return self._rows[idx]

    def get(self, key, default=None):
        # Mimic dataset.get("train") returning a split
        if key == "train":
            return self
        return default


def _make_fake_dataset(rows) -> dict:
    """Wrap rows in a dict that verify_clause_order expects."""
    return {"train": _FakeDataset(rows)}


def _make_row(title, starts, texts=None):
    if texts is None:
        texts = [f"text_{s}" for s in starts]
    return {
        "title": title,
        "context": "placeholder context",
        "question": "Does this contain X?",
        "answers": {"answer_start": starts, "text": texts},
    }


# --- Synthetic test data (clearly labeled SYNTHETIC) ---

SYNTHETIC_MONOTONE_ROWS = [
    # SYNTHETIC TEST DATA — offsets increase within doc_A
    _make_row("doc_A", [10]),
    _make_row("doc_A", [50]),
    _make_row("doc_A", [120]),
    _make_row("doc_B", [5]),
    _make_row("doc_B", [80]),
]

SYNTHETIC_NON_MONOTONE_ROWS = [
    # SYNTHETIC TEST DATA — doc_C has a decreasing offset (out-of-order)
    _make_row("doc_C", [100]),
    _make_row("doc_C", [40]),   # 40 < 100 → non-monotone
    _make_row("doc_D", [10]),
    _make_row("doc_D", [200]),
]

SYNTHETIC_EMPTY_ANSWERS = [
    # SYNTHETIC TEST DATA — rows with no answers (should be ignored)
    {"title": "doc_E", "context": "", "question": "Q?", "answers": {"answer_start": [], "text": []}},
    _make_row("doc_E", [50]),
]


def test_synthetic_monotone_dataset():
    """
    SYNTHETIC TEST DATA: all answer spans within each document increase in offset.
    Expected: order_preserved = True.
    """
    fake = _make_fake_dataset(SYNTHETIC_MONOTONE_ROWS)
    result = verify_clause_order(fake)
    assert result["order_preserved"] is True, (
        f"Expected monotone dataset to pass. Got verdict: {result.get('verdict')}"
    )
    assert result["documents_non_monotone"] == 0
    assert result["documents_monotone_ordered"] >= 2  # doc_A and doc_B


def test_synthetic_non_monotone_dataset():
    """
    SYNTHETIC TEST DATA: doc_C has spans out of order.
    Expected: order_preserved = False.
    """
    fake = _make_fake_dataset(SYNTHETIC_NON_MONOTONE_ROWS)
    result = verify_clause_order(fake)
    assert result["order_preserved"] is False, (
        f"Expected non-monotone dataset to fail. Got verdict: {result.get('verdict')}"
    )
    assert result["documents_non_monotone"] >= 1


def test_synthetic_empty_answers_ignored():
    """
    SYNTHETIC TEST DATA: rows with no answers should not crash and should be counted.
    """
    fake = _make_fake_dataset(SYNTHETIC_EMPTY_ANSWERS)
    result = verify_clause_order(fake)
    assert "rows_without_answers" in result
    assert result["rows_without_answers"] >= 1


def test_verification_report_keys():
    """
    Verify the order report always returns the expected schema keys.
    """
    fake = _make_fake_dataset(SYNTHETIC_MONOTONE_ROWS)
    result = verify_clause_order(fake)
    required_keys = [
        "verification_method", "total_rows", "rows_with_answers",
        "rows_without_answers", "unique_documents", "documents_checked",
        "documents_monotone_ordered", "documents_non_monotone",
        "pct_documents_monotone", "order_preserved", "verdict",
    ]
    for key in required_keys:
        assert key in result, f"Missing key in order report: {key}"


# ---------------------------------------------------------------------------
# Live-data tests (skipped if order report not yet generated)
# ---------------------------------------------------------------------------

@pytest.mark.skipif(
    not CUAD_ORDER_REPORT.exists(),
    reason=(
        "CUAD order report not yet generated. "
        "Run: python -m src.data.ingest_cuad first."
    ),
)
def test_live_cuad_order_report_exists():
    """Checks that the order report file is valid JSON with the required schema."""
    with open(CUAD_ORDER_REPORT, encoding="utf-8") as f:
        report = json.load(f)
    required = ["order_preserved", "verdict", "total_rows", "unique_documents"]
    for key in required:
        assert key in report, f"Live order report missing key: {key}"


@pytest.mark.skipif(
    not CUAD_ORDER_REPORT.exists(),
    reason="CUAD order report not yet generated.",
)
def test_live_cuad_report_has_verdict():
    """Ensures the live report explicitly states whether order is preserved."""
    with open(CUAD_ORDER_REPORT, encoding="utf-8") as f:
        report = json.load(f)
    # order_preserved must be a bool — not None, not missing
    assert isinstance(report["order_preserved"], bool), (
        "order_preserved must be a boolean in the live report."
    )
    assert len(report["verdict"]) > 20, "verdict string is suspiciously short"
