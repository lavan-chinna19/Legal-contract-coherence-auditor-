"""
src/__init__.py — Legal Contract Coherence Auditor core package.
"""
import os

# Set these before any Hugging Face module imports: local_files_only alone
# does not stop some versions from checking conversion/model metadata online.
if os.environ.get("LEXAUDIT_ALLOW_MODEL_DOWNLOAD", "0") != "1":
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")
