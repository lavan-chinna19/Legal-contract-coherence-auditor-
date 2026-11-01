"""Reuse historical core parity code with new output destination; historical files stay read-only."""
from pathlib import Path
import hashlib,importlib.util,json
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[1]

def main():
    path=ROOT/'evaluations/phase4a_obligation_binding_2026_10_28/verify_existing_outputs.py'
    before=json.loads((BASE/'preservation_before.json').read_text(encoding='utf8'))
    assert hashlib.sha256(path.read_bytes()).hexdigest()==before['files'][path.relative_to(ROOT).as_posix()]
    spec=importlib.util.spec_from_file_location('release_core_verifier',path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    m.BASE=BASE;m.main()

if __name__=='__main__':main()
