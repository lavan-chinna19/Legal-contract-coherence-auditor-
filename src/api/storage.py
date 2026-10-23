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
import re
import threading
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from cryptography.fernet import Fernet

from src.config import REPO_ROOT, EMBEDDINGS_CACHE_DIR

logger = logging.getLogger("api")

UPLOAD_DIR = Path(os.environ.get("LEXAUDIT_UPLOAD_DIR", str(REPO_ROOT / "data" / "uploads")))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# In-memory cached Fernet instance
_FERNET_INSTANCE: Optional[Fernet] = None
_SNAPSHOT_LOCK = threading.Lock()


def validate_document_id(doc_id: str):
    if not re.fullmatch(r"doc_[A-Za-z0-9_-]{1,100}", doc_id):
        from fastapi import HTTPException
        raise HTTPException(400, "Invalid document identifier.")


def get_fernet() -> Fernet:
    """
    Returns cached Fernet instance using key from STORAGE_ENCRYPTION_KEY environment variable.
    If no key is configured in environment, generates an ephemeral in-memory key for local dev/testing.
    """
    global _FERNET_INSTANCE
    if _FERNET_INSTANCE is not None:
        return _FERNET_INSTANCE

    raw_key = os.environ.get("STORAGE_ENCRYPTION_KEY", "").strip()
    if not raw_key:
        # Fallback for migration from older deployments using ENCRYPTION_KEY
        raw_key = os.environ.get("ENCRYPTION_KEY", "").strip()
        if raw_key:
            logger.warning("Using legacy ENCRYPTION_KEY. Please migrate to STORAGE_ENCRYPTION_KEY.")
            
    if raw_key:
        try:
            _FERNET_INSTANCE = Fernet(raw_key.encode("utf-8"))
            return _FERNET_INSTANCE
        except Exception as e:
            logger.error(f"Invalid STORAGE_ENCRYPTION_KEY provided: {e}")
            raise ValueError("Invalid STORAGE_ENCRYPTION_KEY format. Must be 32 url-safe base64-encoded bytes.") from e

    # Fail closed in production if no key is configured
    env = os.environ.get("ENV", os.environ.get("NODE_ENV", "development")).lower()
    if env in ("production", "prod"):
        raise ValueError("STORAGE_ENCRYPTION_KEY is required in production environments.")

    # Fallback to ephemeral in-memory key for local development/testing
    logger.warning("STORAGE_ENCRYPTION_KEY not set in environment; generating ephemeral key for session.")
    ephemeral_key = Fernet.generate_key()
    _FERNET_INSTANCE = Fernet(ephemeral_key)
    return _FERNET_INSTANCE


def reset_fernet():
    """Resets cached Fernet instance (useful when testing different keys)."""
    global _FERNET_INSTANCE
    _FERNET_INSTANCE = None


def save_encrypted_document(doc_id: str, document_text: str, client_id: str = "unknown", filename: str = "contract.txt") -> Path:
    """
    Encrypts document text and writes binary ciphertext to disk.
    Plaintext is never written to persistent disk storage.
    """
    validate_document_id(doc_id)
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

    # Keep potentially sensitive filenames inside encrypted storage too.
    (UPLOAD_DIR / f"{doc_id}.name.enc").write_bytes(fernet.encrypt(filename.encode("utf-8")))
        
    return enc_path


def load_and_decrypt_document(doc_id: str) -> str:
    """
    Reads ciphertext from disk and decrypts it directly into memory.
    Raises FileNotFoundError if file does not exist.
    """
    validate_document_id(doc_id)
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
    validate_document_id(doc_id)
    meta_path = UPLOAD_DIR / f"{doc_id}.meta.json"
    if not meta_path.exists():
        return None
    with open(meta_path, "r", encoding="utf-8") as f:
        return json.load(f)


def document_exists(doc_id: str) -> bool:
    """Checks if encrypted document exists on disk."""
    if not re.fullmatch(r"doc_[A-Za-z0-9_-]{1,100}", doc_id):
        return False
    return (UPLOAD_DIR / f"{doc_id}.enc").exists() or (UPLOAD_DIR / f"{doc_id}.txt").exists()


def delete_document_files(doc_id: str) -> bool:
    """Deletes all disk artifacts (.enc, .meta.json, legacy .txt) for a given document."""
    deleted = False
    validate_document_id(doc_id)
    for ext in [".enc", ".meta.json", ".txt", ".analysis.enc", ".analysis.tmp", ".name.enc"]:
        target = UPLOAD_DIR / f"{doc_id}{ext}"
        if target.exists():
            try:
                target.unlink()
                deleted = True
            except OSError:
                pass
    cache_root = EMBEDDINGS_CACHE_DIR.resolve()
    for suffix in (".npz", ".npz.lock"):
        for cached in EMBEDDINGS_CACHE_DIR.glob(f"*/{doc_id}{suffix}"):
            if cached.resolve().is_relative_to(cache_root):
                try:
                    cached.unlink()
                    deleted = True
                except OSError:
                    pass
    return deleted


def document_name(doc_id: str) -> str:
    validate_document_id(doc_id)
    path = UPLOAD_DIR / f"{doc_id}.name.enc"
    return get_fernet().decrypt(path.read_bytes()).decode("utf-8") if path.exists() else doc_id


def save_analysis_snapshot(job: dict):
    with _SNAPSHOT_LOCK:
        _save_analysis_snapshot(job)


def _save_analysis_snapshot(job: dict):
    doc_id = job["doc_id"]
    validate_document_id(doc_id)
    meta = get_document_metadata(doc_id)
    if not meta:
        raise FileNotFoundError("Document expired before analysis could be saved.")
    path = UPLOAD_DIR / f"{doc_id}.analysis.enc"
    temporary = path.with_suffix(".tmp")
    temporary.write_bytes(get_fernet().encrypt(json.dumps(job, ensure_ascii=False).encode("utf-8")))
    temporary.replace(path)
    if meta:
        meta["latest_job_id"] = job["job_id"]
        (UPLOAD_DIR / f"{doc_id}.meta.json").write_text(json.dumps(meta), encoding="utf-8")


def load_analysis_snapshot(doc_id: str) -> Optional[dict]:
    validate_document_id(doc_id)
    path = UPLOAD_DIR / f"{doc_id}.analysis.enc"
    if not path.exists():
        return None
    return json.loads(get_fernet().decrypt(path.read_bytes()))


def list_owned_documents(client_id: str) -> list:
    documents = []
    for path in UPLOAD_DIR.glob("doc_*.meta.json"):
        try:
            meta = json.loads(path.read_text(encoding="utf-8"))
            if meta.get("client_id") == client_id:
                documents.append({"doc_id": meta["doc_id"], "name": document_name(meta["doc_id"]),
                                  "created_at": meta["created_at"], "job_id": meta.get("latest_job_id")})
        except (ValueError, OSError, KeyError):
            continue
        except Exception:
            # An old ephemeral key may no longer decrypt a legacy upload.
            continue
    return sorted(documents, key=lambda d: d["created_at"], reverse=True)
