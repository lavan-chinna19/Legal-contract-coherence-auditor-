"""Create private local Compose settings without replacing existing keys."""
import os
import secrets
from pathlib import Path
from cryptography.fernet import Fernet

ROOT = Path(__file__).resolve().parent.parent
DESTINATION = ROOT / ".env.docker.local"


def main():
    if DESTINATION.exists():
        print("Existing .env.docker.local preserved. Reuse it to retain encrypted history.")
        return
    hub = Path(os.environ.get("HF_HUB_CACHE", str(Path.home() / ".cache/huggingface/hub")))
    model = hub / "models--nlpaueb--legal-bert-base-uncased"
    if not (model / "snapshots").is_dir():
        raise SystemExit("Public Legal-BERT cache missing. Prepare the documented model cache first.")
    primary, secondary = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
    values = {
        "API_KEY": primary,
        "API_KEYS": primary + "," + secondary,
        "ADMIN_API_KEY": secrets.token_urlsafe(32),
        "STORAGE_ENCRYPTION_KEY": Fernet.generate_key().decode(),
        "POSTGRES_USER": "auditor_user",
        "POSTGRES_DB": "legal_auditor",
        "POSTGRES_PASSWORD": secrets.token_urlsafe(32),
        "LEXAUDIT_LEGALBERT_DIR": model.resolve().as_posix(),
        "LEXAUDIT_BACKEND_PORT": "8011",
        "LEXAUDIT_FRONTEND_PORT": "3001",
        "RATE_LIMIT_REQUESTS": "200",
        "RETENTION_TTL_SECONDS": "86400",
    }
    # Exclusive creation prevents accidental encryption-key replacement.
    with DESTINATION.open("x", encoding="utf-8") as stream:
        stream.write("# Private local Compose configuration. Preserve this encryption key.\n")
        for key, value in values.items():
            stream.write(f"{key}={value}\n")
    print("Created .env.docker.local with private keys; no credentials printed.")


if __name__ == "__main__":
    main()
