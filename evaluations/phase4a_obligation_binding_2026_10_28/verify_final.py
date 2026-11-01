"""Final preservation and evidence audit. Does not change existing or frozen artifacts."""
from pathlib import Path
from collections import Counter
import hashlib,json,subprocess,xml.etree.ElementTree as ET
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[1]

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    target=BASE/'final_verification.json'
    if target.exists():raise FileExistsError('Keep final verification; use a new artifact for another session')
    before=json.loads((BASE/'preservation_before.json').read_text(encoding='utf8'))
    changed=[];missing=[]
    for p,h in before['files'].items():
        path=ROOT/p
        if not path.exists():missing.append(p)
        elif digest(path)!=h:changed.append(p)
    allowed={'src/api/release_routes.py','src/api/reports.py','docs/FINAL_COMPLETION_TRACKER.md'}
    frozen=json.loads((BASE/'implementation_frozen.json').read_text())
    benchmark=json.loads((BASE/'benchmark_frozen_manifest.json').read_text())
    tests=[]
    for name in ['development_v1.xml','integration_v1.xml','integration_v2.xml','full_native_v1.xml']:
        root=ET.parse(BASE/name).getroot();suites=list(root.iter('testsuite'))
        row=dict(file=name,tests=sum(int(s.attrib['tests']) for s in suites),failures=sum(int(s.attrib['failures']) for s in suites),
            errors=sum(int(s.attrib['errors']) for s in suites),skipped=sum(int(s.attrib['skipped']) for s in suites),
            skips=[dict(test=t.attrib['name'],reason=t.find('skipped').attrib.get('message')) for t in root.iter('testcase') if t.find('skipped') is not None])
        row['passed']=row['tests']-row['failures']-row['errors']-row['skipped'];tests.append(row)
    encoder=json.loads((ROOT/'evaluations/phase1_detection_baseline_2026_10_26/results/legalbert_cache_fingerprint.json').read_text())
    cache=Path.home()/'.cache/huggingface/hub/models--nlpaueb--legal-bert-base-uncased/snapshots'/encoder['cached_main_revision']
    cache_checks={name:digest(cache/name)==v['sha256'] for name,v in encoder['files'].items()}
    summary=[]
    for name in ['development_v1','evaluation_first_pass']:
        path=BASE/'results'/name;rows=[json.loads(l) for l in (path/'predictions.jsonl').open(encoding='utf8')]
        s=json.loads((path/'summary.json').read_text());outcomes=Counter()
        for r in rows:
            if r['gold_match'] is None:continue
            p=r['prediction']=='MATCHED';outcomes[('TP' if p else 'FN') if r['gold_match'] else ('FP' if p else 'TN')]+=1
        binary={k:outcomes[k] for k in ['TP','FP','FN','TN']}
        states=dict(Counter(r['prediction'] for r in rows));covered=states.get('MATCHED',0)+states.get('DIFFERENT',0)
        summary.append(dict(run=name,binary=binary,predicted_state_counts=states,covered=covered,denominator=len(rows),
            matches=all(v==s['full_binary_screen'][k] for k,v in binary.items()) and covered==s['coverage_numerator']))
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    result=dict(existing_snapshot_files=len(before['files']),changed_existing_files=changed,missing_existing_files=missing,
        unexpected_existing_changes=sorted(set(changed)-allowed),
        preserved_history_files=sum(p.startswith(('evaluations/phase1_','evaluations/phase2_','evaluations/phase3_','research/','data/raw/')) for p in before['files']),
        preserved_frontend_files=sum(p.startswith('frontend/') for p in before['files']),
        frozen_source_still_matches=all(digest(ROOT/p)==h for p,h in frozen['files'].items()),
        frozen_benchmark_still_matches=all(digest(BASE/p)==h for p,h in benchmark['files'].items()),
        legalbert_cache_checks=cache_checks,
        model_checkpoint_sha256=digest(ROOT/'models/coherence_classifier.pt'),
        centroids_sha256=digest(ROOT/'fixtures/ledgar_centroids.npz'),
        git_head_before=before['head'],git_head_after=head,
        tests=tests,metric_recalculation=summary,
        archived_reproduction=json.loads((BASE/'results/exposed_reproduction_v1/reproduction.json').read_text()),
        preserved_output_check=json.loads((BASE/'preserved_output_verification.json').read_text())['passed'],
        known_open_limitations=['Joint subject actor extraction fails reserved example','Passive positive unsupported and counted FN','Recurring event field gold defect: two cells per split; raw metrics qualified','Public-source probes lack labels and supported pairs','Docker engine unavailable','Independent legal/natural-family/security validation pending'],
        readiness='Experimental native research prototype; NO-GO for Phase4B automatic distant-clause contradiction detection')
    result['passed']=not missing and not result['unexpected_existing_changes'] and result['frozen_source_still_matches'] and result['frozen_benchmark_still_matches'] and all(cache_checks.values()) and head==before['head'] and all(s['matches'] for s in summary) and result['preserved_output_check'] and result['archived_reproduction']['identical']==58 and tests[-1]['passed']==440 and not tests[-1]['failures'] and not tests[-1]['errors']
    target.write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    print(json.dumps({k:v for k,v in result.items() if k!='archived_reproduction'},indent=2));assert result['passed']

if __name__=='__main__':main()
