"""Final focused preservation/evidence checks; never updates historical evidence."""
from pathlib import Path
from collections import Counter
import hashlib,json,subprocess,xml.etree.ElementTree as ET
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[1]

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    target=BASE/'final_verification.json'
    if target.exists():raise FileExistsError('Keep final evidence; choose a new artifact for another session')
    before=json.loads((BASE/'preservation_before.json').read_text(encoding='utf8'));changed=[];missing=[]
    for p,h in before['files'].items():
        path=ROOT/p
        if not path.exists():missing.append(p)
        elif digest(path)!=h:changed.append(p)
    allowed={'src/obligations/binding.py','src/api/reports.py','docs/FINAL_COMPLETION_TRACKER.md'}
    manifest=json.loads((BASE/'results/comparison_v2/source_manifest_before_predictions.json').read_text())
    focused=json.loads((BASE/'focused_input_manifest.json').read_text())
    original=json.loads((ROOT/'evaluations/phase4a_obligation_binding_2026_10_28/implementation_frozen.json').read_text())
    tests=[]
    for name in ['affected_v1.xml','affected_v2.xml','full_native_v1.xml']:
        root=ET.parse(BASE/name).getroot();suites=list(root.iter('testsuite'))
        row=dict(file=name,tests=sum(int(s.attrib['tests']) for s in suites),failures=sum(int(s.attrib['failures']) for s in suites),errors=sum(int(s.attrib['errors']) for s in suites),skipped=sum(int(s.attrib['skipped']) for s in suites),
            skips=[dict(test=t.attrib['name'],reason=t.find('skipped').attrib.get('message')) for t in root.iter('testcase') if t.find('skipped') is not None])
        row['passed']=row['tests']-row['failures']-row['errors']-row['skipped'];tests.append(row)
    metrics=[]
    rows=[json.loads(l) for l in (BASE/'results/comparison_v2/paired_synthetic.jsonl').open(encoding='utf8')]
    saved=json.loads((BASE/'results/comparison_v2/summary.json').read_text());labelled_errors=[]
    for stratum in sorted(set(r['stratum'] for r in rows)):
        cases=[r for r in rows if r['stratum']==stratum];values={}
        for side in ['old','new']:
            c=Counter()
            for r in cases:
                if r['case']['gold_match'] is None:continue
                p=r[side]['selected']['status']=='MATCHED';c[('TP' if p else 'FN') if r['case']['gold_match'] else ('FP' if p else 'TN')]+=1
            value={k:c[k] for k in ['TP','FP','FN','TN']};values[side]=value
            assert all(v==saved[stratum][side]['binary'][k] for k,v in value.items())
        metrics.append(dict(stratum=stratum,counts=values,documents=len(cases)))
        labelled_errors.extend(r['case']['case_id'] for r in cases if r['case']['gold_state'] is not None and r['new']['selected']['status']!=r['case']['gold_state'])
    fingerprint=json.loads((ROOT/'evaluations/phase1_detection_baseline_2026_10_26/results/legalbert_cache_fingerprint.json').read_text())
    cache=Path.home()/'.cache/huggingface/hub/models--nlpaueb--legal-bert-base-uncased/snapshots'/fingerprint['cached_main_revision']
    cache_checks={name:digest(cache/name)==entry['sha256'] for name,entry in fingerprint['files'].items()}
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    public=json.loads((BASE/'public_applicability_audit.json').read_text(encoding='utf8'))['observations'];normalized=[r for r in public if r['mode']=='existing_legacy_html_extraction']
    result=dict(existing_snapshot_files=len(before['files']),changed_existing_files=changed,missing_existing_files=missing,unexpected_existing_changes=sorted(set(changed)-allowed),
        preserved_frontend_files=sum(p.startswith('frontend/') for p in before['files']),
        preserved_historical_files=sum(p.startswith(('evaluations/phase1_','evaluations/phase2_','evaluations/phase3_','evaluations/phase4a_','data/raw/','research/')) for p in before['files']),
        original_baseline_sha256=digest(BASE/'baseline_snapshot/binding.py'),baseline_hash_matches=digest(BASE/'baseline_snapshot/binding.py')==original['files']['src/obligations/binding.py'],
        baseline_reproduced=json.loads((BASE/'results/baseline_v1/verification.json').read_text())['original_results_reproduced'],
        final_source_manifest_unchanged=all(digest(ROOT/p)==h for p,h in manifest.items()),focused_inputs_unchanged=all(digest(BASE/p)==h for p,h in focused['files'].items()),
        legalbert_cache_checks=cache_checks,core_parity_passed=json.loads((BASE/'preserved_output_verification.json').read_text())['passed'],
        git_head_before=before['head'],git_head_after=head,test_runs=tests,metrics=metrics,remaining_labelled_synthetic_state_errors=labelled_errors,
        public_normalized=dict(documents=len(normalized),pairs=sum(sum(r['new_pair_counts'].values()) for r in normalized),supported_pairs=sum(sum(v for k,v in r['new_pair_counts'].items() if k in ['MATCHED','DIFFERENT']) for r in normalized),
            modal_cues=sum(r['modal_cues'] for r in normalized),skipped_inline_modal_cues=sum(r['inline_heading_cues_skipped'] for r in normalized)),
        readiness='NO-GO for narrow authentic-contract contradiction detection demonstration; no Phase4B')
    result['passed']=not missing and not result['unexpected_existing_changes'] and result['baseline_hash_matches'] and result['baseline_reproduced']==58 and result['final_source_manifest_unchanged'] and result['focused_inputs_unchanged'] and all(cache_checks.values()) and result['core_parity_passed'] and head==before['head'] and tests[-1]['passed']==468 and not tests[-1]['failures'] and not tests[-1]['errors'] and not labelled_errors
    target.write_text(json.dumps(result,indent=2)+'\n',encoding='utf8');print(json.dumps(result,indent=2));assert result['passed']

if __name__=='__main__':main()
