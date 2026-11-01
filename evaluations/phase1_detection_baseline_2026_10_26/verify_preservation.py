"""Read-only verification of pre-existing files and supplementary local model fingerprint."""
from pathlib import Path
import hashlib,json,subprocess
BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[1]
def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda:stream.read(4*1024*1024),b''):h.update(chunk)
    return h.hexdigest()
def verify():
    before=json.loads((BASE/'preservation_before.json').read_text(encoding='utf-8'))
    changed=[];missing=[]
    for name,digest in before['files'].items():
        path=ROOT/name
        if not path.exists():missing.append(name)
        elif sha(path)!=digest:changed.append(name)
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    result=dict(existing_files_checked=len(before['files']),changed_existing_files=changed,missing_existing_files=missing,
        head_before=before['head'],head_after=head,passed=not changed and not missing and head==before['head'],
        scope='Pre-existing source/frontend/models/fixtures/docs/research/design/audit/raw-data plus root configuration. New evaluation files and new baseline documentation are excluded.')
    (BASE/'results'/'preservation_verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    cache=Path.home()/'.cache/huggingface/hub/models--nlpaueb--legal-bert-base-uncased'
    revision=(cache/'refs/main').read_text().strip()
    snapshot=cache/'snapshots'/revision
    files={str(p.relative_to(snapshot)).replace('\\','/'):dict(sha256=sha(p),bytes=p.stat().st_size) for p in snapshot.rglob('*') if p.is_file()}
    fingerprint=dict(model='nlpaueb/legal-bert-base-uncased',cached_main_revision=revision,files=files,
        note='Supplementary post-run fingerprint of already local offline model. Production checkpoint and centroids were hashed before predictions in frozen_manifest.json. No model downloaded or modified.')
    (BASE/'results'/'legalbert_cache_fingerprint.json').write_text(json.dumps(fingerprint,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))
    return 0 if result['passed'] else 1
if __name__=='__main__':raise SystemExit(verify())
