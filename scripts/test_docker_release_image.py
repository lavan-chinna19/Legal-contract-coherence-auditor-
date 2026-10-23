"""Run the release acceptance suite inside the built Linux image, offline."""
import json
import subprocess
from pathlib import Path
from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "tmp/docker-validation"


def main():
    settings = dotenv_values(ROOT / ".env.docker.local")
    compose = ["docker", "compose", "--env-file", str(ROOT / ".env.docker.local"), "-p", "lexaudit-release"]
    image = subprocess.run(compose + ["images", "-q", "backend"], capture_output=True, text=True, check=True, timeout=30).stdout.strip()
    if not image:
        raise SystemExit("Build and start the backend image before running its acceptance suite.")
    args = ["docker", "run", "--rm", "--network", "none", "--cpus", "2", "--memory", "4g",
            "--mount", f"type=bind,src={(ROOT / 'tests').as_posix()},dst=/app/tests,readonly",
            "--mount", "type=volume,src=lexaudit-release_model_cache,dst=/opt/hf/hub,readonly",
            "--env", "PYTEST_DISABLE_PLUGIN_AUTOLOAD=1", "--env", "PYTHONDONTWRITEBYTECODE=1",
            "--entrypoint", "python", image, "-m", "pytest", "tests/test_final_release.py", "-q", "--tb=short", "-p", "no:cacheprovider"]
    result = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300)
    (OUT / "image-release-tests.log").write_text(result.stdout + result.stderr, encoding="utf-8")
    (OUT / "image-release-tests.json").write_text(json.dumps({"argv": args, "exit_code": result.returncode, "status": "PASS" if result.returncode == 0 else "FAIL"}, indent=2), encoding="utf-8")
    print(result.stdout[-3500:])
    print("IMAGE_RELEASE_TESTS_EXIT=" + str(result.returncode))
    raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
