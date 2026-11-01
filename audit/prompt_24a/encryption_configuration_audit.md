# Encryption Configuration Audit — Prompt 24A

**Author:** Principal Security Reviewer & Release Engineer  
**Audit Phase:** Prompt 24A (Final Release Corrections & Verification)  
**Date:** October 10, 2026  

---

## 1. Overview & Canonical Configuration

The Legal Contract Coherence Auditor uses Fernet authenticated encryption (`AES-128-CBC` with `HMAC-SHA256`) to protect uploaded contract text at rest (`data/uploads/`).

### Canonical Environment Variable
The canonical configuration variable is:
```text
STORAGE_ENCRYPTION_KEY
```

Legacy configurations previously referenced `ENCRYPTION_KEY`. In `src/api/storage.py`, backward compatibility is maintained via a fallback:
```python
raw_key = os.environ.get("STORAGE_ENCRYPTION_KEY", "").strip()
if not raw_key:
    # Fallback for migration from older deployments using ENCRYPTION_KEY
    raw_key = os.environ.get("ENCRYPTION_KEY", "").strip()
    if raw_key:
        logger.warning("Using legacy ENCRYPTION_KEY. Please migrate to STORAGE_ENCRYPTION_KEY.")
```

However, all demonstration scripts, setup guides, and `README.md` documentation have been updated to exclusively specify the canonical variable: `STORAGE_ENCRYPTION_KEY`.

---

## 2. Key Generation & Management Instructions

### Local Generation Command
Operators setting up the system should generate a random, 32-byte URL-safe base64-encoded Fernet key locally:

**Windows PowerShell:**
```powershell
$env:STORAGE_ENCRYPTION_KEY = python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

**Linux / macOS Bash:**
```bash
export STORAGE_ENCRYPTION_KEY=$(python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
```

### Critical Operational Requirements
1. **Secret Hygiene:** Never commit or hardcode actual encryption keys into Git, documentation, shell scripts, or commit messages. The hardcoded mock key `YWJj...` has been removed from all documentation.
2. **Key Stability Across Restarts:** If previously encrypted contract documents in `data/uploads/` need to be read or audited across application restarts, the operator **MUST supply the exact same key**. Generating a new ephemeral key on each restart will render previously stored ciphertext undecryptable (`InvalidToken`).
3. **Out-of-Git Storage:** In persistent or staging deployments, store the key in a local `.env` file (which is gitignored) or an external secrets manager.

---

## 3. Security Boundary & Failure Verification

The implementation in `src/api/storage.py` was audited against edge cases:
- **Production Mode Missing Key:** When `ENV=production` or `NODE_ENV=production` and `STORAGE_ENCRYPTION_KEY` is empty, the application fails closed with:
  `ValueError: STORAGE_ENCRYPTION_KEY is required in production environments.`
- **Invalid Key Format:** If an improperly padded or non-base64 key is provided, Fernet initialization raises:
  `ValueError: Invalid STORAGE_ENCRYPTION_KEY format. Must be 32 url-safe base64-encoded bytes.`
- **Development Fallback:** In development mode (`ENV=development`), if no key is configured, an ephemeral in-memory key is generated with a visible warning log, preventing unencrypted plaintext writes to disk.
- **Automated Retention:** Regardless of encryption state, all temporary upload blobs are purged after 24 hours (`RETENTION_TTL_SECONDS=86400`).
