"""Award Docker completion only from passing recorded real workflow evidence."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "tmp/docker-validation"
DOCS = ROOT / "docs"


def evidence(name):
    return json.loads((OUT / name).read_text(encoding="utf-8"))


def main():
    acceptance = evidence("acceptance.json")
    images = evidence("image-audit.json")
    browser = evidence("browser-acceptance.json")
    linux_tests = evidence("image-release-tests.json")
    build = evidence("build-result.json")
    assert build["exit_code"] == 0
    assert acceptance["status"] == images["status"] == browser["status"] == linux_tests["status"] == "PASS"
    assert linux_tests["exit_code"] == 0 and "20 passed" in (OUT / "image-release-tests.log").read_text(encoding="utf-8")
    for result in (acceptance, images, browser):
        assert result["checks"] and all(c["status"] == "PASS" for c in result["checks"])
    names = {c["name"] for c in acceptance["checks"]}
    assert {"new application containers created", "feedback survives database restart and app recreation", "runtime external network is isolated"} <= names
    assert all(c["exit_code"] == 0 for c in acceptance["commands"] + images["commands"])
    counts = {"http_runtime": len(acceptance["checks"]), "image_storage": len(images["checks"]), "browser": len(browser["checks"]), "linux_release_tests": 20}
    tracker_path = DOCS / "FINAL_COMPLETION_TRACKER.md"
    tracker = tracker_path.read_text(encoding="utf-8")
    tracker = tracker.replace("Updated 2026-10-23.", "Updated 2026-10-24.")
    tracker = tracker.replace("**23/24 COMPLETE = 2300/24 = 95.833333.../100 (95.83/100 displayed)**", "**24/24 COMPLETE = 100/100**")
    lines = tracker.splitlines()
    lines = [f"| Docker container runtime | COMPLETE | Real Compose build, four healthy services, {counts['http_runtime']} runtime checks, {counts['image_storage']} image/storage checks, browser workflow, 20 Linux release tests; restart/recreation persistence verified |" if line.startswith("| Docker container runtime |") else line for line in lines]
    lines = ["- **COMPLETE - Docker runtime:** recovered engine; actual build, health, auth, all formats, local inference, reports, encrypted history, PostgreSQL feedback and persistence verified. See DOCKER_VALIDATION_REPORT.md." if line.startswith("- **IN PROGRESS - Docker runtime:") else line for line in lines]
    tracker = "\n".join(lines) + "\n"
    tracker = tracker.replace("No staging, commit, push, deployment or destructive Git operation was performed.", "No staging, commit, push, external deployment or destructive Git operation was performed. The user-authorized local Docker deployment was verified separately below.")
    tracker += f"\n## Final Docker milestone - COMPLETE\n\nActual build exit 0; backend/frontend/gateway/PostgreSQL healthy; {counts['http_runtime']} runtime checks, {counts['image_storage']} image/storage checks, {counts['browser']} browser assertions and 20 Linux release tests passed. Original private configuration and research data were not included in images. Runtime internet egress is blocked; public Legal-BERT is mounted read-only and CPU inference is real. Stable encryption keys and named volumes preserve exact snapshots across restart and fresh application containers. The scoring denominator remains 24; all rows now earn COMPLETE. External scientific/legal/security validation remains BLOCKED and is not implied by this application score.\n"
    assert sum("| COMPLETE |" in line for line in tracker.splitlines() if line.startswith("| ")) == 24
    tracker_path.write_text(tracker, encoding="utf-8")
    report = f"""# Docker validation and final application completion

**Application completion: 24/24 COMPLETE = 100/100. Demo classification: DEMO_READY_WITH_LIMITATIONS. Production scientific/legal/security readiness: not independently validated.**

This result follows actual Dockerized acceptance; it is not awarded for writing container files. The native full regression previously passed 244 tests with two documented optional-CUAD skips. The Linux image separately passed the 20 release acceptance tests; these counts overlap and are not added together.

| Verification | Actual result |
| --- | --- |
| Docker host recovery | Engine 29.6.1 responds after reversible runtime-socket quarantine |
| Compose build and configuration | Exit 0 |
| Backend/frontend/gateway/PostgreSQL | All healthy |
| Real HTTP/runtime checks | {counts['http_runtime']} PASS |
| Image/storage checks | {counts['image_storage']} PASS |
| Browser assertions | {counts['browser']} PASS |
| Release tests inside offline Linux image | 20 passed, exit 0 |
| Authentication and owner isolation | Missing/invalid keys rejected; other owner preview/export denied |
| TXT/PDF/DOCX | Actual upload, preview, local inference and exports passed |
| History and persistence | Exact saved scores/evidence survive restart and fresh application-container recreation |
| PostgreSQL feedback | Actual synthetic feedback survives database restart and application recreation |
| PDF/DOCX reports | Packages reopen; required factual content and protected-download headers verified before/after restart/recreation |
| Local inference/privacy | CPU Torch; offline settings; blocked external routing; read-only public model mount |
| Image contents | Frozen checksums match; no uploaded documents, saved databases, private env files or cache baked into images |

## Host issue and safe recovery

Docker Desktop 4.82.0 failed before LexAudit ran: inaccessible zero-byte AF_UNIX reparse points at `Docker/run/dockerInference`, then `docker-secrets-engine/engine.sock`. The logs show the Inference manager error predating this release. WSL checks passed. With Docker stopped, only these runtime directories were renamed to timestamped sibling backups. A clean start restored the engine. No factory reset, WSL unregister, volume removal, prune or software upgrade occurred. Backups are retained as documented in DOCKER_RUN_AND_VALIDATION.md.

## Deployment corrections

Required Dockerfiles exist and the canonical frontend/backend images actually built. Image contexts are allowlisted. The backend copies only source and three frozen runtime assets; user data is never copied. Frontend uses Node 24.13.1, receives the public API URL during build and runs as a non-root user. The backend runs as UID 10001, one CPU worker, with bounded resources and readiness-based health checks. API/database/encryption keys are generated in Git-ignored `.env.docker.local`; retain that file for history. A read-only named volume exposes only the seeded public Legal-BERT cache; the one-shot setup copies from a read-only host mount without downloads. Named volumes retain encrypted uploads/snapshots, vectors, file-based configuration and PostgreSQL data. MinIO is preserved as an optional legacy profile and is not used by the API or claimed as verified.

## Exact launch and verification commands

```powershell
python scripts/initialize_docker_env.py
docker compose --env-file .env.docker.local -p lexaudit-release config --quiet
docker compose --env-file .env.docker.local -p lexaudit-release --progress plain build
docker compose --env-file .env.docker.local -p lexaudit-release --profile tools run --rm --no-deps model-setup
docker compose --env-file .env.docker.local -p lexaudit-release up -d --wait --wait-timeout 300
python scripts/validate_docker_release.py
python scripts/audit_docker_images.py
python scripts/test_docker_release_image.py
```

Frontend: `http://127.0.0.1:3001`; backend: `http://127.0.0.1:8011`. Copy your private API_KEY from `.env.docker.local` into Connection. Existing native services on 3000/8010 were not replaced. The Compose project is `lexaudit-release`; no pre-existing project volumes were present when validation began. Use the documented installed Python environment for the scripts.

## Evidence and limits

`tmp/docker-validation` retains initial/recovered host diagnostics, reversible recovery records, real build output, actual command arguments/exit codes, service health, redacted logs, acceptance JSON, report packages, image audit and Linux test output. The first PyTorch download experienced network/TLS interruptions, then resumed with certificate verification intact; no TLS bypass was used.

Local functional completion does not establish legal correctness or model generalization. Independent annotation/adjudication, unseen-family confirmatory evaluation and external security validation remain external blockers. Two native optional research-artifact tests remain skipped. Font/layout coverage, hostile-parser security and operational reliability are bounded by the documented tests, not universally certified. No model retraining, dataset relabeling, frozen-result modification, Git commit/push or external deployment was performed.
"""
    (DOCS / "DOCKER_VALIDATION_REPORT.md").write_text(report, encoding="utf-8")
    for filename in ("FINAL_RELEASE_REPORT.md", "FINAL_RELEASE_TEST_RESULTS.md", "RELEASE_CHECKLIST.md", "KNOWN_LIMITATIONS.md", "INSTALL_AND_RUN.md"):
        path = DOCS / filename
        content = path.read_text(encoding="utf-8")
        if "<!-- docker-validation-final -->" not in content:
            title_end = content.find("\n")
            notice = "\n\n<!-- docker-validation-final -->\n**Updated 2026-10-24: 24/24 application components COMPLETE (100/100).** The user-authorized local Docker deployment and restart/recreation persistence passed. Independent scientific, legal and external security validation remains outstanding. See [DOCKER_VALIDATION_REPORT.md](DOCKER_VALIDATION_REPORT.md) and [DOCKER_RUN_AND_VALIDATION.md](DOCKER_RUN_AND_VALIDATION.md) for actual evidence and launch commands.\n"
            content = content[:title_end] + notice + content[title_end:]
            if filename == "FINAL_RELEASE_REPORT.md":
                start = content.find("The requested local application workflows")
                end = content.find("\n\n", start)
                if start >= 0:
                    content = content[:start] + "The requested local application workflows and Docker deployment are implemented and verified. The unchanged checklist denominator now has **24 COMPLETE items out of 24: 100/100**. Independent scientific and external security validation remain separate blockers and are not claimed as completed application features." + content[end:]
                content = content.replace("| Docker runtime | BLOCKED; Compose configuration validates, engine unavailable; no container deployment |", "| Docker runtime | PASS; real build, four healthy services, workflow acceptance, image audit and restart/recreation persistence |")
                content = content.replace("Docker runtime verification is the sole non-COMPLETE item in the counted 24-item release checklist.", "Docker runtime verification now passes; all 24 counted application items are COMPLETE.")
                content = content.replace("No staging, commit, push, destructive Git operation or deployment was performed.", "No staging, commit, push, destructive Git operation or external deployment was performed. The authorized local Docker deployment was subsequently verified.")
                content = content.replace("Both the optimized frontend on port 3000 and CPU API on port 8010 are running.", "The native frontend/API remain available on 3000/8010; the verified local Docker deployment uses 3001/8011.")
                content = content.replace("The 24th component remains BLOCKED.", "The socket-only directories were subsequently preserved and engine recovery succeeded. The 24th component is now COMPLETE, backed by the Docker validation report.")
            elif filename == "RELEASE_CHECKLIST.md":
                content = content.replace("23/24 COMPLETE = 95.833333...%", "24/24 COMPLETE = 100%")
                content = content.replace("the remaining item is explicitly blocked", "all counted application items are verified")
                content = content.replace("| Container runtime validation | BLOCKED | Docker Desktop Linux engine unavailable; Compose configuration validates but image/runtime not exercised |", "| Container runtime validation | COMPLETE | Actual Compose build, four healthy services, inference/exports/history, image audit, restart/recreation and 20 Linux release tests |")
            elif filename == "KNOWN_LIMITATIONS.md":
                content = "\n".join("- Docker host startup initially failed on stale runtime sockets; reversible recovery succeeded and the default container deployment is now verified. The historical optional MinIO profile is not used by the API and remains outside the verified application path." if line.startswith("- Docker Desktop's Linux engine is unavailable.") else line for line in content.splitlines()) + "\n"
            elif filename == "INSTALL_AND_RUN.md":
                content = content.replace("Docker Desktop's engine was unavailable during verification. The backend Docker recipe includes the release requirements and DejaVu fonts, but its image was not built or deployed.", "Docker was initially unavailable; subsequent safe host recovery, actual image builds and container workflow verification passed. Use DOCKER_RUN_AND_VALIDATION.md for the verified Compose deployment and private configuration.")
            else:
                content = content.replace("Container build/runtime remains BLOCKED, not a passing check; no factory reset or deployment occurred.", "This initial host failure was later recovered without data deletion. Container build/runtime, acceptance, image audits and restart/recreation checks now pass; no factory reset or external deployment occurred.")
                content += f"\n## Verified Docker follow-up\n\nCompose build/configuration and all command checks exited 0. Real acceptance: {counts['http_runtime']} passing HTTP/runtime assertions; image/storage audit: {counts['image_storage']} passes; Chromium: {counts['browser']} passing assertions; release tests inside the Linux image: 20 passed, exit 0. Docker health checks show backend/frontend/gateway/PostgreSQL healthy. Exact snapshots and PostgreSQL feedback survive restart and application-container recreation. Counts overlap prior native coverage and are not summed. The Docker validation report links the retained actual logs and evidence.\n"
            path.write_text(content, encoding="utf-8")
    (OUT / "final-completion.json").write_text(json.dumps({"complete": 24, "total": 24, "percentage": 100, "status": "PASS", "verified_counts": counts}, indent=2), encoding="utf-8")
    print("Verified evidence accepted: 24/24 COMPLETE = 100/100. External validation is separate.")


if __name__ == "__main__":
    main()
