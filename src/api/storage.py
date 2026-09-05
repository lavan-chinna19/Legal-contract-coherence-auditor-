"""
src/api/storage.py — Encrypted Storage at Rest (Prompt 16 Work Package C)

Implements authenticated encryption (Fernet: AES-128-CBC + HMAC-SHA256) for uploaded contracts:
- Raw files on disk NEVER contain plaintext contract content
- Ciphertext stored in data/uploads/{doc_id}.enc
- Plaintext exists only in memory during upload ingestion and pipeline analysis
- Encryption key sourced from environment (STORAGE_ENCRYPTION_KEY)
- Key is NEVER logged, committed, or exposed through API endpoints
"""
import os
import json
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from cryptography.fernet import Fernet

from src.config import REPO_ROOT

logger = logging.getLogger("api")

UPLOAD_DIR = REPO_ROOT / "data" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# In-memory cached Fernet instance
_FERNET_INSTANCE: Optional[Fernet] = None


def get_fernet() -> Fernet:
    """
    Returns cached Fernet instance using key from STORAGE_ENCRYPTION_KEY environment variable.
    If no key is configured in environment, generates an ephemeral in-memory key for local dev/testing.
    """
    global _FERNET_INSTANCE
    if _FERNET_INSTANCE is not None:
        return _FERNET_INSTANCE

    raw_key = os.environ.get("STORAGE_ENCRYPTION_KEY", "").strip()
    if raw_key:
        try:
            _FERNET_INSTANCE = Fernet(raw_key.encode("utf-8"))
            return _FERNET_INSTANCE
        except Exception as e:
            logger.error(f"Invalid STORAGE_ENCRYPTION_KEY provided: {e}")
            raise ValueError("Invalid STORAGE_ENCRYPTION_KEY format. Must be 32 url-safe base64-encoded bytes.") from e

    # Fallback to ephemeral in-memory key for local development/testing
    logger.warning("STORAGE_ENCRYPTION_KEY not set in environment; generating ephemeral key for session.")
    ephemeral_key = Fernet.generate_key()
    _FERNET_INSTANCE = Fernet(ephemeral_key)
    return _FERNET_INSTANCE


def reset_fernet():
    """Resets cached Fernet instance (useful when testing different keys)."""
    global _FERNET_INSTANCE
    _FERNET_INSTANCE = None


def save_encrypted_document(doc_id: str, document_text: str, client_id: str = "unknown") -> Path:
    """
    Encrypts document text and writes binary ciphertext to disk.
    Plaintext is never written to persistent disk storage.
    """
    fernet = get_fernet()
    ciphertext = fernet.encrypt(document_text.encode("utf-8"))
    
    enc_path = UPLOAD_DIR / f"{doc_id}.enc"
    with open(enc_path, "wb") as f:
        f.write(ciphertext)
        
    # Write safe non-sensitive metadata alongside
    meta = {
        "doc_id": doc_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "created_timestamp": datetime.now(timezone.utc).timestamp(),
        "client_id": client_id,
        "size_bytes": len(ciphertext)
    }
    meta_path = UPLOAD_DIR / f"{doc_id}.meta.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f)
        
    return enc_path


def load_and_decrypt_document(doc_id: str) -> str:
    """
    Reads ciphertext from disk and decrypts it directly into memory.
    Raises FileNotFoundError if file does not exist.
    """
    enc_path = UPLOAD_DIR / f"{doc_id}.enc"
    if not enc_path.exists():
        # Fallback check for legacy .txt during migration test
        txt_path = UPLOAD_DIR / f"{doc_id}.txt"
        if txt_path.exists():
            with open(txt_path, "r", encoding="utf-8") as f:
                return f.read()
        raise FileNotFoundError(f"Encrypted document {doc_id} not found.")

    with open(enc_path, "rb") as f:
        ciphertext = f.read()
        
    fernet = get_fernet()
    plaintext_bytes = fernet.decrypt(ciphertext)
    return plaintext_bytes.decode("utf-8")


def get_document_metadata(doc_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves metadata for an uploaded document."""
    meta_path = UPLOAD_DIR / f"{doc_id}.meta.json"
    if not meta_path.exists():
        return None
    with open(meta_path, "r", encoding="utf-8") as f:
        return json.load(f)


def document_exists(doc_id: str) -> bool:
    """Checks if encrypted document exists on disk."""
    return (UPLOAD_DIR / f"{doc_id}.enc").exists() or (UPLOAD_DIR / f"{doc_id}.txt").exists()


def delete_document_files(doc_id: str) -> bool:
    """Deletes all disk artifacts (.enc, .meta.json, legacy .txt) for a given document."""
    deleted = False
    for ext in [".enc", ".meta.json", ".txt"]:
        target = UPLOAD_DIR / f"{doc_id}{ext}"
        if target.exists():
            try:
                target.unlink()
                deleted = True
            except OSError:
                pass
    return deleted
