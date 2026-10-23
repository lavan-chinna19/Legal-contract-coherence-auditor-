"""Run the local API with explicit configuration or clearly labelled demo settings."""
import argparse
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
optional_dependencies = REPO_ROOT / ".release-deps"
if optional_dependencies.exists():
    sys.path.append(str(optional_dependencies))

from dotenv import load_dotenv


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--demo", action="store_true", help="Use public demo credentials on loopback only")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    load_dotenv(REPO_ROOT / ".env", override=False)
    if args.demo:
        os.environ.setdefault("API_KEY", "dev_auditor_key_12345")
        os.environ.setdefault("API_KEYS", "dev_auditor_key_12345,client_b_key_67890")
        os.environ.setdefault("ADMIN_API_KEY", "admin_secret_key_99999")
        os.environ.setdefault("STORAGE_ENCRYPTION_KEY", "HLcuRrkQVbecq-Kqt_z23Vm_mDsFCdmjFdPICZKEYKU=")
        os.environ.setdefault("RATE_LIMIT_REQUESTS", "200")
        print("DEMO configuration: public test credentials. Use synthetic documents only. Local model inference is real.")
    elif not (os.environ.get("API_KEY") or os.environ.get("API_KEYS")) or not os.environ.get("STORAGE_ENCRYPTION_KEY"):
        parser.error("Configure API_KEY/API_KEYS and STORAGE_ENCRYPTION_KEY in .env, or explicitly use --demo.")
    os.environ.setdefault("OMP_NUM_THREADS", "2")
    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
    os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")
    from cryptography.fernet import Fernet
    Fernet(os.environ["STORAGE_ENCRYPTION_KEY"].encode())
    import uvicorn
    uvicorn.run("src.api.main:app", host="127.0.0.1", port=args.port, workers=1,
                access_log=False, log_level=os.environ.get("LOG_LEVEL", "info").lower())


if __name__ == "__main__":
    main()
