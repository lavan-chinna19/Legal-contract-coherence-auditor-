"""
src/config.py — Central configuration for Legal Contract Coherence Auditor.

RESEARCH/DEMO PROJECT — not production-ready.

All paths, model names, and thresholds are defined here.
No hardcoded absolute paths appear anywhere else in the codebase.
"""

from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

# ---------------------------------------------------------------------------
# Repository root (always relative — never hardcoded absolute paths)
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Data directories (git-ignored; never committed)
# ---------------------------------------------------------------------------
DATA_DIR = REPO_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

LEDGAR_RAW_DIR = RAW_DIR / "ledgar"
EDGAR_RAW_DIR = RAW_DIR / "sec_edgar"
CUAD_RAW_DIR = RAW_DIR / "cuad"
CASE_STUDY_DIR = RAW_DIR / "case_studies"

LEDGAR_PROCESSED = PROCESSED_DIR / "ledgar"
EDGAR_PROCESSED = PROCESSED_DIR / "sec_edgar"
CUAD_PROCESSED = PROCESSED_DIR / "cuad"

# ---------------------------------------------------------------------------
# Manifest / metadata files
# ---------------------------------------------------------------------------
EDGAR_MANIFEST = EDGAR_RAW_DIR / "edgar_manifest.json"
CUAD_ORDER_REPORT = CUAD_PROCESSED / "clause_order_verification.json"

# ---------------------------------------------------------------------------
# Fixtures directory (small synthetic test files — may be committed)
# ---------------------------------------------------------------------------
FIXTURES_DIR = REPO_ROOT / "fixtures"

# ---------------------------------------------------------------------------
# Model configuration
# TARGET (not yet measured) — fine-tuning paths are placeholders for Prompt 4+
# ---------------------------------------------------------------------------
MODEL_DIR = REPO_ROOT / "models"

LEGAL_BERT_MODEL = "nlpaueb/legal-bert-base-uncased"   # HuggingFace model ID; free, Apache-2.0
ZERO_SHOT_NLI_MODEL = "facebook/bart-large-mnli"        # HuggingFace model ID; free, MIT
SENTENCE_EMBEDDING_MODEL = "nlpaueb/legal-bert-base-uncased"

# Fine-tuned model paths (populated by Prompts 4 and 5)
COHERENCE_CHECKPOINT_PATH: Path = MODEL_DIR / "coherence_classifier.pt"
COHERENCE_TRAINING_CURVES_PATH: Path = FIXTURES_DIR / "coherence_training_curves.json"
FINE_TUNED_COHERENCE_MODEL: Optional[Path] = COHERENCE_CHECKPOINT_PATH
FINE_TUNED_EMBEDDINGS_MODEL: Optional[Path] = None

# Active Coherence Model Configuration ("fine_tuned" or "zero_shot")
ACTIVE_COHERENCE_MODEL = "fine_tuned"

# Active Segmenter Configuration (v1 or v2)
ACTIVE_SEGMENTER = "v1"

# ---------------------------------------------------------------------------
# Embeddings Configuration
# ---------------------------------------------------------------------------
EMBEDDINGS_CACHE_DIR = PROCESSED_DIR / "embeddings_cache"
EMBEDDINGS_CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Active Embedding Source Configuration ("frozen" or "fine_tuned")
ACTIVE_EMBEDDING_SOURCE = "frozen"

# ---------------------------------------------------------------------------
# Clause schema
# Canonical representation for a single extracted clause.
# ---------------------------------------------------------------------------
@dataclass
class ClauseRecord:
    """
    Standard clause schema used across all ingestion and modelling stages.

    Fields
    ------
    clause_id     : str  — globally unique identifier (<doc_id>_<sequence_idx>)
    doc_id        : str  — source document identifier
    text          : str  — verbatim clause text (never logged; see Contract §4)
    label         : str  — clause type label (e.g. "Definitions", "Payment Terms")
    sequence_idx  : int  — 0-based position in original document
    char_start    : int  — character offset of clause start in source document
    char_end      : int  — character offset of clause end in source document
    source        : str  — dataset origin: "ledgar" | "sec_edgar" | "cuad"
    split         : str  — "train" | "val" | "test" | "none"
    """
    clause_id: str
    doc_id: str
    text: str
    label: str
    sequence_idx: int
    char_start: int
    char_end: int
    source: str
    split: str = "none"

    def to_dict(self) -> dict:
        return {
            "clause_id": self.clause_id,
            "doc_id": self.doc_id,
            # NOTE: 'text' is intentionally included for local processing
            # but must NEVER be written to application logs (Contract §4).
            "text": self.text,
            "label": self.label,
            "sequence_idx": self.sequence_idx,
            "char_start": self.char_start,
            "char_end": self.char_end,
            "source": self.source,
            "split": self.split,
        }


# ---------------------------------------------------------------------------
# Dataset parameters
# ---------------------------------------------------------------------------
LEDGAR_HF_DATASET = "lex_glue"          # HuggingFace dataset name
LEDGAR_HF_CONFIG = "ledgar"              # subset name within lex_glue
LEDGAR_LABEL_FIELD = "label"
LEDGAR_TEXT_FIELD = "text"

# Train/val/test split ratios for datasets without pre-defined splits
TRAIN_RATIO = 0.80
VAL_RATIO = 0.10
TEST_RATIO = 0.10

# SEC EDGAR fetch settings
EDGAR_USER_AGENT = "LegalCoherenceAuditor research@example.com"  # REQUIRED by SEC
EDGAR_BASE_URL = "https://efts.sec.gov/LATEST/search-index"
EDGAR_FULL_TEXT_URL = "https://efts.sec.gov/LATEST/search-index"
EDGAR_TARGET_COUNT = 50          # Target number of contracts to fetch
EDGAR_RATE_LIMIT_SEC = 0.15      # 6–7 req/s, safely within SEC's 10 req/s limit
EDGAR_FORM_TYPES = ["10-K"]      # Form types to search; Exhibit 10 extracted from these
EDGAR_DATE_START = "2022-01-01"
EDGAR_DATE_END = "2023-12-31"

# CUAD settings
CUAD_HF_DATASET = "theatticusproject/cuad"         # HuggingFace dataset name

# ---------------------------------------------------------------------------
# Scoring thresholds — TARGET (not yet measured; to be set by Prompt 6+)
# ---------------------------------------------------------------------------
CHANNEL_A_OOD_THRESHOLD: float = 0.5    # TARGET: semantic OOD distance
CHANNEL_B_COHERENCE_THRESHOLD: float = 0.5  # TARGET: coherence transition score
ENSEMBLE_ALPHA: float = 0.5             # TARGET: weighting between channels
SEVERITY_HIGH_THRESHOLD: float = 0.75   # TARGET
SEVERITY_MED_THRESHOLD: float = 0.50    # TARGET

# ---------------------------------------------------------------------------
# Logging — text content must NEVER appear in logs (Contract §4)
# ---------------------------------------------------------------------------
LOG_LEVEL = "INFO"
LOG_DIR = REPO_ROOT / "logs"
# LOG_DIR is in .gitignore; do not store contract plaintext here.
