"""Read-only preservation/test audit; emits a new final evidence file, never rewrites history."""
from pathlib import Path
import hashlib,json,subprocess,xml.etree.ElementTree as ET
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[1]

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    target=BASE/'final_verification_2026_10_28.json'
    if target.exists():raise FileExistsError('Preserve the existing verification; use a new artifact name for a new session')
    snapshot=json.loads((BASE/'preservation_before.json').read_text(encoding='utf8'))
    allowed={'src/api/jobs.py','src/api/reports.py','src/rules/date_checker.py','src/rules/unified_pipeline.py',
        'tests/test_final_release.py','docs/FINAL_COMPLETION_TRACKER.md'}
    missing=[p for p in snapshot['files'] if not (ROOT/p).exists()]
    changed=[p for p,h in snapshot['files'].items() if (ROOT/p).exists() and digest(ROOT/p)!=h]
    manifest=json.loads((BASE/'results/paired_v3/source_manifest_before_predictions.json').read_text(encoding='utf8'))
    encoder=json.loads((ROOT/'evaluations/phase1_detection_baseline_2026_10_26/results/legalbert_cache_fingerprint.json').read_text(encoding='utf8'))
    cache=Path.home()/'.cache/huggingface/hub/models--nlpaueb--legal-bert-base-uncased/snapshots'/encoder['cached_main_revision']
    cached={name:digest(cache/name)==entry['sha256'] for name,entry in encoder['files'].items()}
    tests=[]
    for name in ['initial_regression.xml','affected_v1.xml','full_native_v1.xml','affected_v2.xml','full_native_v2.xml']:
        xml=ET.parse(BASE/name).getroot();suites=list(xml.iter('testsuite'))
        row=dict(file=name,tests=sum(int(s.attrib['tests']) for s in suites),
            failures=sum(int(s.attrib['failures']) for s in suites),errors=sum(int(s.attrib['errors']) for s in suites),
            skipped=sum(int(s.attrib['skipped']) for s in suites),
            skips=[dict(test=t.attrib['name'],reason=t.find('skipped').attrib.get('message')) for t in xml.iter('testcase') if t.find('skipped') is not None])
        row['passed']=row['tests']-row['failures']-row['errors']-row['skipped'];tests.append(row)
    raw=json.loads((ROOT/'evaluations/phase1_detection_baseline_2026_10_26/preservation_before.json').read_text(encoding='utf8'))
    raw={p:h for p,h in raw['files'].items() if p.startswith('data/raw/')}
    raw_changed=[p for p,h in raw.items() if not (ROOT/p).exists() or digest(ROOT/p)!=h]
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    result=dict(snapshot_existing_files=len(snapshot['files']),changed_existing_files=changed,missing_existing_files=missing,
        unexpected_existing_changes=sorted(set(changed)-allowed),
        preserved_phase1_files=sum(p.startswith('evaluations/phase1_') for p in snapshot['files']),
        preserved_phase2_files=sum(p.startswith('evaluations/phase2_') for p in snapshot['files']),
        preserved_frontend_files=sum(p.startswith('frontend/') for p in snapshot['files']),
        raw_research_files_checked=len(raw),changed_raw_research_files=raw_changed,
        local_legalbert_cache=cached,
        legacy_source_matches_original=digest(BASE/'legacy_snapshot/date_checker.py')==snapshot['files']['src/rules/date_checker.py'],
        new_dataset_matches_authored_hash=digest(BASE/'new_cases.json')==(BASE/'new_cases.sha256').read_text().strip(),
        final_evaluated_source_manifest_matches=all(digest(ROOT/p)==h for p,h in manifest.items()),
        git_head_at_original_oct26_snapshot=snapshot['head'],
        git_head_at_resumed_session='e5436ea4da3fcaeb7f000a0c06a95a3a125514b8',git_head_after=head,
        git_history_note='Existing Phase 2 commit was already present when resumed. No Git mutation in this implementation session.',
        test_runs=tests,
        paired_verification=json.loads((BASE/'results/paired_v3/verification.json').read_text(encoding='utf8')))
    result['passed']=not missing and not result['unexpected_existing_changes'] and not raw_changed and all(cached.values()) and result['legacy_source_matches_original'] and result['new_dataset_matches_authored_hash'] and result['final_evaluated_source_manifest_matches'] and head==result['git_head_at_resumed_session']
    target.write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    print(json.dumps(result,indent=2));assert result['passed']

if __name__=='__main__':main()
