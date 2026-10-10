import os
import pytest
from cryptography.fernet import Fernet
from src.api.storage import get_fernet, reset_fernet

def test_storage_encryption_key_canonical():
    """Verify STORAGE_ENCRYPTION_KEY is used when provided."""
    reset_fernet()
    valid_key = Fernet.generate_key().decode()
    os.environ["STORAGE_ENCRYPTION_KEY"] = valid_key
    f = get_fernet()
    assert f is not None
    # Verify it encrypts/decrypts
    ct = f.encrypt(b"test")
    assert f.decrypt(ct) == b"test"
    
    # Process restart persistence simulation
    reset_fernet()
    f2 = get_fernet()
    assert f2.decrypt(ct) == b"test"
    del os.environ["STORAGE_ENCRYPTION_KEY"]

def test_legacy_encryption_key_migration():
    """Verify legacy ENCRYPTION_KEY still works if STORAGE_ENCRYPTION_KEY is missing."""
    reset_fernet()
    valid_key = Fernet.generate_key().decode()
    os.environ["ENCRYPTION_KEY"] = valid_key
    f = get_fernet()
    assert f is not None
    ct = f.encrypt(b"legacy")
    assert f.decrypt(ct) == b"legacy"
    del os.environ["ENCRYPTION_KEY"]

def test_ephemeral_key_generation():
    """Verify ephemeral key is generated in local env if no keys are provided."""
    reset_fernet()
    if "STORAGE_ENCRYPTION_KEY" in os.environ: del os.environ["STORAGE_ENCRYPTION_KEY"]
    if "ENCRYPTION_KEY" in os.environ: del os.environ["ENCRYPTION_KEY"]
    os.environ["ENV"] = "development"
    
    f1 = get_fernet()
    assert f1 is not None
    reset_fernet()
    f2 = get_fernet()
    # Since they are ephemeral, f2 shouldn't decrypt f1's ciphertext
    ct = f1.encrypt(b"test")
    with pytest.raises(Exception):
        f2.decrypt(ct)

def test_production_fails_closed_missing_key():
    """Verify production fails if no persistent key is provided."""
    reset_fernet()
    if "STORAGE_ENCRYPTION_KEY" in os.environ: del os.environ["STORAGE_ENCRYPTION_KEY"]
    if "ENCRYPTION_KEY" in os.environ: del os.environ["ENCRYPTION_KEY"]
    os.environ["ENV"] = "production"
    
    with pytest.raises(ValueError, match="required in production"):
        get_fernet()
    del os.environ["ENV"]
