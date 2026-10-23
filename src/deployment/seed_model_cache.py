"""Copy only the explicitly mounted public Legal-BERT cache into a local volume."""
import json
import shutil
from pathlib import Path


def main():
    source = Path("/seed")
    target = Path("/opt/hf/hub/models--nlpaueb--legal-bert-base-uncased")
    reference = (source / "refs/main").read_text().strip()
    marker = target / ".lexaudit-seeded.json"
    if marker.exists() and json.loads(marker.read_text()).get("reference") == reference:
        print("Existing seeded public model cache preserved.")
        return
    # Both locations are explicit mounts. No private data directory is read.
    shutil.copytree(source, target, dirs_exist_ok=True, symlinks=True)
    (target / ".lexaudit-seeded.json").write_text(json.dumps({"reference": reference, "source": "local public Legal-BERT cache"}))
    print("Public Legal-BERT cache copied to persistent Linux volume. No downloads.")


if __name__ == "__main__":
    main()
