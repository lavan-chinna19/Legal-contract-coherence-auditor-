"""Keep test fixtures, including legacy destructive feedback fixtures, off user data."""
import os
import tempfile
from pathlib import Path

_test_runtime = tempfile.TemporaryDirectory(prefix="lexaudit-tests-")
_root = Path(_test_runtime.name)
# Tests must never inherit a configured external feedback database.
os.environ.pop("DATABASE_URL", None)
os.environ["LEXAUDIT_FEEDBACK_DB_PATH"] = str(_root / "feedback.sqlite")
os.environ["LEXAUDIT_THRESHOLDS_PATH"] = str(_root / "thresholds.json")
os.environ["LEXAUDIT_EMBEDDINGS_CACHE_DIR"] = str(_root / "vectors")
os.environ["LEXAUDIT_UPLOAD_DIR"] = str(_root / "uploads")
# Keep all tests local. This does not substitute or mock any model.
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
