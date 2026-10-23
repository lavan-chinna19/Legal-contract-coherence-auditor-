"""Bounded, read-only Docker/WSL diagnostics. Never resets or prunes data."""
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "tmp" / "docker-validation"
OUT.mkdir(parents=True, exist_ok=True)


def run(args, timeout=20):
    started = datetime.now(timezone.utc).isoformat()
    try:
        result = subprocess.run(args, cwd=ROOT, capture_output=True, timeout=timeout)
        data = {"command": args, "started_utc": started, "exit_code": result.returncode,
                "stdout": decode(result.stdout), "stderr": decode(result.stderr)}
    except subprocess.TimeoutExpired as exc:
        data = {"command": args, "started_utc": started, "exit_code": None, "timeout_seconds": timeout,
                "stdout": decode(exc.stdout or b""), "stderr": decode(exc.stderr or b"")}
    except OSError as exc:
        data = {"command": args, "started_utc": started, "exit_code": None, "error": str(exc)}
    print(json.dumps(data, ensure_ascii=True), flush=True)
    return data


def decode(value):
    if isinstance(value, str):
        return value
    return value.decode("utf-16" if b"\x00" in value else "utf-8", errors="replace").strip()


def main():
    compose = ["docker", "compose"]
    if (ROOT / ".env.docker.local").exists():
        compose += ["--env-file", str(ROOT / ".env.docker.local"), "-p", "lexaudit-release"]
    commands = [
        (["wsl.exe", "--status"], 20),
        (["wsl.exe", "--list", "--verbose"], 20),
        (["wsl.exe", "--version"], 20),
        (["docker", "version"], 20),
        (["docker", "info"], 20),
        (["docker", "context", "ls"], 15),
        (["docker", "desktop", "status"], 15),
        (["docker", "compose", "version"], 15),
        (compose + ["config", "--quiet"], 15),
    ]
    results = []
    for args, timeout in commands:
        results.append(run(args, timeout))
        (OUT / "host-diagnostics.json").write_text(json.dumps(results, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
