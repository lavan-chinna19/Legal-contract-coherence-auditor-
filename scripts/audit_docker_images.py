"""Inspect built image contents and running mounts without exposing secrets."""
import hashlib
import json
import subprocess
from pathlib import Path
from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "tmp/docker-validation"
COMPOSE = ["docker", "compose", "--env-file", str(ROOT / ".env.docker.local"), "-p", "lexaudit-release"]


def main():
    settings = dotenv_values(ROOT / ".env.docker.local")
    private = [v for k, v in settings.items() if v and ("KEY" in k or "PASSWORD" in k)]
    private.extend((settings.get("API_KEYS") or "").split(","))
    data = {"status": "IN_PROGRESS", "commands": [], "checks": []}

    def save():
        (OUT / "image-audit.json").write_text(json.dumps(data, indent=2), encoding="utf-8")

    def command(args):
        result = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)
        data["commands"].append({"argv": args, "exit_code": result.returncode})
        save()
        if result.returncode:
            raise RuntimeError("Image audit command failed; output deliberately not printed to avoid possible secrets")
        return result.stdout

    def check(name, condition, evidence=None):
        data["checks"].append({"name": name, "status": "PASS" if condition else "FAIL", "evidence": evidence})
        save()
        print(("PASS " if condition else "FAIL ") + name, flush=True)
        if not condition:
            raise AssertionError(name)

    try:
        for service in ("backend", "frontend"):
            container_id = command(COMPOSE + ["ps", "-q", service]).strip()
            image_id = command(["docker", "inspect", "--format", "{{.Image}}", container_id]).strip()
            image = json.loads(command(["docker", "image", "inspect", image_id]))[0]
            config = image["Config"]
            check(service + " image runs as non-root", config["User"] not in ("", "root", "0"), {"user": config["User"], "image_id": image_id})
            env = "\n".join(config.get("Env") or [])
            check(service + " private runtime keys absent from image config", all(secret not in env for secret in private if secret))
            history = command(["docker", "history", "--no-trunc", "--format", "{{.CreatedBy}}", image_id])
            check(service + " private runtime keys absent from image layers", all(secret not in history for secret in private if secret))
            if service == "backend":
                script = '''import json,hashlib,os
from pathlib import Path
paths=["models/coherence_classifier.pt","fixtures/ledgar_centroids.npz","fixtures/conformal_calibration_fixture.json"]
print(json.dumps({"uid":os.getuid(),"assets":{p:hashlib.sha256((Path("/app")/p).read_bytes()).hexdigest() for p in paths},"fixture_files":sorted(p.name for p in Path("/app/fixtures").iterdir()),"data_files":[str(p) for p in Path("/app/data").rglob("*") if p.is_file()],"public_model_cache_files":[str(p) for p in Path("/opt/hf/hub").rglob("*") if p.is_file()],"env_files":[str(p) for p in Path("/app").rglob(".env*")],"has_tmp":Path("/app/tmp").exists(),"has_research_dataset":Path("/app/research").exists()}))'''
                inspected = json.loads(command(["docker", "run", "--rm", "--network", "none", "--entrypoint", "python", image_id, "-c", script]))
                expected = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in inspected["assets"]}
                check("frozen runtime assets exactly preserved", inspected["assets"] == expected, expected)
                check("only required calibration and centroid fixtures in image", inspected["fixture_files"] == ["conformal_calibration_fixture.json", "ledgar_centroids.npz"])
                check("no uploaded contracts, saved analyses or databases baked into image", not inspected["data_files"] and not inspected["has_tmp"] and not inspected["has_research_dataset"])
                check("public Legal-BERT is mounted, not baked into image", not inspected["public_model_cache_files"])
                check("backend environment files excluded", not inspected["env_files"])
            else:
                script = 'const fs=require("fs"); console.log(JSON.stringify({envFiles:fs.readdirSync("/app").filter(x=>x.startsWith(".env")),hasSource:fs.existsSync("/app/src"),uid:process.getuid(),roots:fs.readdirSync("/app")}));'
                inspected = json.loads(command(["docker", "run", "--rm", "--network", "none", "--entrypoint", "node", image_id, "-e", script]))
                check("frontend runtime excludes environment files and source checkout", not inspected["envFiles"] and not inspected["hasSource"], inspected)
        networks = json.loads(command(["docker", "network", "inspect", "lexaudit-release_auditor_network"]))
        check("application network blocks external routing", networks[0]["Internal"] is True)
        sample = json.loads((OUT / "acceptance.json").read_text(encoding="utf-8"))["snapshots"][0]
        runtime = '''import json
from pathlib import Path
from src.api.storage import UPLOAD_DIR,load_and_decrypt_document
doc_id=__import__("sys").argv[1]
files=[UPLOAD_DIR/(doc_id+s) for s in (".enc",".analysis.enc",".name.enc")]
print(json.dumps({"encrypted_files_exist":all(p.is_file() for p in files),"no_plaintext_marker":all(b"Section 3. Payment" not in p.read_bytes() for p in files),"decrypts_in_memory":load_and_decrypt_document(doc_id).startswith("Section 3. Payment"),"no_plaintext_upload":not (UPLOAD_DIR/(doc_id+".txt")).exists()}))'''
        encrypted = json.loads(command(COMPOSE + ["exec", "-T", "backend", "python", "-c", runtime, sample["doc_id"]]))
        check("persistent document artifacts encrypted and reopenable", all(encrypted.values()), encrypted)
        data["status"] = "PASS"
        save()
        print(f"PASS: {len(data['checks'])} image/storage checks", flush=True)
    except Exception:
        data["status"] = "FAIL"
        save()
        raise


if __name__ == "__main__":
    main()
