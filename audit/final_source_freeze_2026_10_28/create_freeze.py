"""Create a local non-Git source/evidence freeze and verify it. Never package private runtime data."""
from pathlib import Path
import difflib,hashlib,json,subprocess,zipfile,xml.etree.ElementTree as ET
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[1]

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,value):
    if p.exists():raise FileExistsError(f'Preserve existing freeze artifact: {p.name}')
    p.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n',encoding='utf8')

def main():
    manifest_path=BASE/'RESEARCH_FREEZE_MANIFEST.json';archive=BASE/'LexAudit-research-prototype-source.zip'
    if manifest_path.exists() or archive.exists() or (BASE/'final_verification.json').exists():raise FileExistsError('Freeze already exists; do not overwrite it')
    before=json.loads((BASE/'preservation_before.json').read_text(encoding='utf8'))
    changed=[];missing=[]
    for name,h in before['files'].items():
        p=ROOT/name
        if not p.exists():missing.append(name)
        elif digest(p)!=h:changed.append(name)
    allowed={'src/obligations/binding.py','docs/FINAL_COMPLETION_TRACKER.md'}
    root_before=json.loads((BASE/'root_files_before.json').read_text(encoding='utf8'))
    root_changed=[p for p,h in root_before.items() if digest(ROOT/p)!=h]
    assert not missing and not set(changed)-allowed and not set(root_changed)-{'README.md'},'Unexpected existing file change'
    old=(BASE/'baseline_binding.py').read_text(encoding='utf8').splitlines()
    new=(ROOT/'src/obligations/binding.py').read_text(encoding='utf8').splitlines()
    code=lambda lines:[s for s in lines if not s.lstrip().startswith('#')]
    expected=[s.replace("body_start=node['heading_end']", "body_start=node['identifier_end']") for s in code(old)]
    assert expected==code(new),'Runtime correction exceeds the documented single executable line'
    assert digest(BASE/'baseline_binding.py')==before['files']['src/obligations/binding.py']
    tests=[]
    for name in ['reproduction_before.xml','affected_after.xml','full_native_v1.xml']:
        root=ET.parse(BASE/name).getroot();suites=list(root.iter('testsuite'))
        row=dict(file=name,tests=sum(int(s.attrib['tests']) for s in suites),failures=sum(int(s.attrib['failures']) for s in suites),errors=sum(int(s.attrib['errors']) for s in suites),skipped=sum(int(s.attrib['skipped']) for s in suites),
            skips=[dict(test=t.attrib['name'],reason=t.find('skipped').attrib.get('message')) for t in root.iter('testcase') if t.find('skipped') is not None])
        row['passed']=row['tests']-row['failures']-row['errors']-row['skipped'];tests.append(row)
    assert tests[-1]['passed']==484 and not tests[-1]['failures'] and not tests[-1]['errors']
    core=json.loads((BASE/'preserved_output_verification.json').read_text(encoding='utf8'))
    public=json.loads((BASE/'public_source_verification.json').read_text(encoding='utf8'))
    frontend=json.loads((BASE/'frontend_results.json').read_text(encoding='utf8'))
    assert core['passed'] and public['skipped_normalized_modal_cues_after']==0 and all(x['exit_code']==0 for x in frontend)
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    branch=subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip()
    assert head==before['head'] and branch==before['branch']

    excluded_parts={'node_modules','.next','__pycache__','runtime','.git','.venv','venv','uploads','cache','caches'}
    excluded_suffixes={'.db','.sqlite','.sqlite3','.pt','.bin','.npz','.pkl','.safetensors','.zip','.pyc','.tsbuildinfo'}
    selected={}
    roots=['src','tests','frontend','docs','scripts','fixtures','evaluations',BASE.relative_to(ROOT).as_posix()]
    derived={'RESEARCH_FREEZE_MANIFEST.json','archive_receipt.json','final_verification.json','freeze_console.log'}
    for folder in roots:
        for p in (ROOT/folder).rglob('*'):
            if not p.is_file() or any(x in excluded_parts for x in p.relative_to(ROOT).parts):continue
            if p.name.startswith('.env') or p.suffix.lower() in excluded_suffixes or p.name in derived:continue
            selected[p.relative_to(ROOT).as_posix()]=p
    for p in ROOT.iterdir():
        if p.is_file() and (p.suffix=='.py' or p.name in {'README.md','CONTRIBUTORS.md','.gitignore','.dockerignore','docker-compose.yml','render.yaml','railway.json','pytest.ini','pyproject.toml','LICENSE','LICENSE.md'} or p.name.startswith(('requirements','Dockerfile'))):
            selected[p.name]=p
    files={name:dict(sha256=digest(p),bytes=p.stat().st_size) for name,p in sorted(selected.items())}
    assets={}
    for folder in ['models','data/raw']:
        for p in (ROOT/folder).rglob('*'):
            if p.is_file() and '__pycache__' not in p.parts:
                assets[p.relative_to(ROOT).as_posix()]=dict(sha256=digest(p),bytes=p.stat().st_size,included_in_source_archive=False)
    p=ROOT/'fixtures/ledgar_centroids.npz'
    assets[p.relative_to(ROOT).as_posix()]=dict(sha256=digest(p),bytes=p.stat().st_size,included_in_source_archive=False)
    fingerprint=json.loads((ROOT/'evaluations/phase1_detection_baseline_2026_10_26/results/legalbert_cache_fingerprint.json').read_text(encoding='utf8'))
    cache=Path.home()/'.cache/huggingface/hub/models--nlpaueb--legal-bert-base-uncased/snapshots'/fingerprint['cached_main_revision']
    cache_checks={name:digest(cache/name)==entry['sha256'] for name,entry in fingerprint['files'].items()}
    assert all(cache_checks.values())
    status=subprocess.check_output(['git','status','--porcelain=v1','--untracked-files=all'],cwd=ROOT,text=True)
    manifest=dict(freeze_label='LexAudit native research prototype, 2026-10-28',git_base_head=head,git_branch=branch,
        git_state='DIRTY: base commit alone is not the release identity; included file hashes identify the actual tested source',git_status_at_manifest_creation=status,
        files=files,required_local_assets=assets,legalbert_cache_fingerprint=fingerprint,
        excluded='Git objects, all private env files, user uploads/documents, databases, venv/node caches, model weights/cache and raw datasets; broader research assets remain in original workspace with preservation ledger.',
        prototype_scope='Source-consuming experimental application; no independent legal accuracy, Docker runtime or contradiction-readiness claim',
        implementation_change='One executable consumer offset: identifier_end instead of physical-line heading_end',
        paper_inventory='docs/FINAL_SOURCE_PARSING_AND_RESEARCH_FREEZE.md',preserved_existing_file_ledger='audit/final_source_freeze_2026_10_28/preservation_before.json')
    dump(manifest_path,manifest)
    with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for name,p in sorted(selected.items()):z.write(p,name)
        z.write(manifest_path,manifest_path.relative_to(ROOT).as_posix())
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        members=set(z.namelist());expected_members=set(files)|{manifest_path.relative_to(ROOT).as_posix()}
        assert members==expected_members
        assert all(hashlib.sha256(z.read(name)).hexdigest()==entry['sha256'] for name,entry in files.items())
    assert all(digest(ROOT/name)==entry['sha256'] for name,entry in files.items()),'Packaged source changed during freeze'
    receipt=dict(archive=archive.relative_to(ROOT).as_posix(),sha256=digest(archive),bytes=archive.stat().st_size,
        included_files=len(files)+1,manifest=manifest_path.relative_to(ROOT).as_posix(),manifest_sha256=digest(manifest_path),purpose='Local source/evidence freeze only; no Git commit, public publication or deployment')
    dump(BASE/'archive_receipt.json',receipt)
    verification=dict(passed=True,existing_snapshot_files=len(before['files']),changed_existing_files=changed,root_changed_files=root_changed,missing_existing_files=missing,unexpected_changes=[],
        preserved_frontend_files=sum(p.startswith('frontend/') for p in before['files']),
        preserved_historical_files=sum(p.startswith(('evaluations/','research/','data/raw/','audit/','design/')) for p in before['files']),
        single_executable_line_patch_verified=True,git_head_before=before['head'],git_head_after=head,git_branch=branch,
        legalbert_cache_checks=cache_checks,core_parity=core['counts'],test_runs=tests,public_verification=public,
        archive_receipt=receipt,source_manifest_matches=True,archive_members_and_hashes_verified=True,
        docker_runtime='UNVERIFIED: missing host engine pipe',final_classification='Frozen reproducible native research prototype with documented limitations; NO-GO for authentic-contract contradiction detection',implementation_stopped=True)
    dump(BASE/'final_verification.json',verification)
    print(json.dumps(dict(passed=True,archive=receipt,source_files=len(files),existing_files_preserved=len(before['files'])-len(changed),changed=changed,root_changed=root_changed,final_native_passed=484),indent=2))

if __name__=='__main__':main()
