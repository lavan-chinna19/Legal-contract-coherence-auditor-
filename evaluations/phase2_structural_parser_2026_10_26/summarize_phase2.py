"""Derive all-case comparisons and preservation evidence from final saved outputs."""
from pathlib import Path
from collections import Counter
import csv, hashlib, json, subprocess, xml.etree.ElementTree as ET
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[1];RUN=BASE/'results/paired_v4'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n',encoding='utf8')

def main():
    decisions=json.loads((RUN/'comparison.json').read_text(encoding='utf8'))
    paired=[json.loads(x) for x in (RUN/'paired_predictions.jsonl').read_text(encoding='utf8').splitlines()]
    cases=[]
    for r in paired:
        old=r['old'];new=r['new'];case=new['case']
        task_rows=[x for x in decisions if x['case_id']==r['case_id'] and x['mode']==r['mode']]
        def prediction(v):
            return dict(missing_target_flag=bool(v['audit']['metadata']['ref_flags_count']),
                directional_finding=bool(v['graph']['findings']),graph_status=v['graph']['status'],
                reference_flags=[dict(flag_type=f['flag_type'],target_id=f['evidence'].get('target_id'),
                    clause_id=f['clause_id']) for f in v['audit']['rule_flags'] if f['flag_type'].startswith('DANGLING_')])
        before=prediction(old);after=prediction(new)
        rows_changed=before!=after
        explanation=[]
        if before['missing_target_flag']!=after['missing_target_flag'] or before['reference_flags']!=after['reference_flags']:
            explanation.append('Exact full-identity heading/citation resolution on unchanged extraction replaces self-declaration, suffix truncation, plural omission and destructive-normalization inputs; per-reference evidence identifies actual changes.')
        if before['directional_finding']!=after['directional_finding']:
            explanation.append('Supported punctuation/preposed direction is retained and checked against exact target/source character positions.')
        if before['graph_status']!=after['graph_status']:
            explanation.append('Newly recognized unsupported/unresolved syntax is represented explicitly in graph review/finding state.')
        if not explanation:explanation.append('Document-level predictions unchanged; source structure and explicit review/coverage metadata are still recorded.')
        cases.append(dict(case_id=r['case_id'],mode=r['mode'],source_document=case['source_document'],
            ground_truth=case['task_labels'],provenance=case['label_provenance'],independently_adjudicated=False,
            original_prediction=before,new_prediction=after,prediction_changed=rows_changed,
            why_changed=explanation,task_outcomes=task_rows,
            corrected_tasks=[x['task'] for x in task_rows if x['corrected_error']],
            regressed_tasks=[x['task'] for x in task_rows if x['introduced_regression']],
            legal_correctness='NOT_ASSESSED_NO_ADJUDICATED_LEGAL_GROUND_TRUTH',
            supporting_evidence=new['audit']['metadata']['reference_resolutions'],
            parser_reviews=new['audit']['metadata']['reference_reviews'],parity=r['parity']))
    dump(RUN/'case_comparison.json',cases)
    with (RUN/'case_comparison.csv').open('w',encoding='utf8',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=['case_id','mode','provenance','ground_truth','original_prediction','new_prediction','prediction_changed','why_changed','corrected_tasks','regressed_tasks','legal_correctness'])
        writer.writeheader()
        for c in cases:writer.writerow({k:json.dumps(c[k],ensure_ascii=False) if isinstance(c[k],(dict,list)) else c[k] for k in writer.fieldnames})
    before=json.loads((BASE/'preservation_before.json').read_text(encoding='utf8'))
    allowed={'src/api/jobs.py','src/api/release_routes.py','src/api/reports.py','src/rules/dependency_graph.py','src/rules/reference_checker.py','src/rules/unified_pipeline.py','docs/FINAL_COMPLETION_TRACKER.md'}
    changed=[];missing=[]
    for name,value in before['files'].items():
        path=ROOT/name
        if not path.exists():missing.append(name)
        elif digest(path)!=value:changed.append(name)
    legacy={'reference_checker.py':'src/rules/reference_checker.py','dependency_graph.py':'src/rules/dependency_graph.py',
        'unified_pipeline.py':'src/rules/unified_pipeline.py','rule_based.py':'src/segmentation/rule_based.py','ingestion.py':'src/api/ingestion.py'}
    legacy_verified={name:digest(BASE/'legacy_snapshot'/name)==before['files'][source] for name,source in legacy.items()}
    manifest=json.loads((RUN/'source_manifest_before_predictions.json').read_text(encoding='utf8'))
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    preservation=dict(existing_snapshot_files=len(before['files']),unchanged_existing_files=len(before['files'])-len(changed)-len(missing),
        changed_existing_files=changed,authorized_existing_source_changes=sorted(allowed),missing_existing_files=missing,
        unexpected_changes=sorted(set(changed)-allowed),phase1_files_checked=sum(name.startswith('evaluations/phase1_') for name in before['files']),
        legacy_snapshots=legacy_verified,final_evaluated_source_hashes_match=all(digest(ROOT/name)==value for name,value in manifest.items()),
        git_head_before=before['head'],git_head_after=head,
        note='Existing test_api_integration.py was not in this original snapshot; its retained assertions now pass identical upload-decoded raw source and add three preservation assertions. New parser/integration tests and new docs/evaluation files are additions.')
    encoder=json.loads((ROOT/'evaluations/phase1_detection_baseline_2026_10_26/results/legalbert_cache_fingerprint.json').read_text(encoding='utf8'))
    cache=Path.home()/'.cache/huggingface/hub/models--nlpaueb--legal-bert-base-uncased/snapshots'/encoder['cached_main_revision']
    preservation['local_legalbert_files_unchanged']={name:digest(cache/name)==entry['sha256'] for name,entry in encoder['files'].items()}
    phase1_before=json.loads((ROOT/'evaluations/phase1_detection_baseline_2026_10_26/preservation_before.json').read_text(encoding='utf8'))
    raw_inputs={name:value for name,value in phase1_before['files'].items() if name.startswith('data/raw/')}
    preservation['raw_research_inputs_checked_against_phase1_snapshot']=len(raw_inputs)
    preservation['changed_or_missing_raw_research_inputs']=[name for name,value in raw_inputs.items() if not (ROOT/name).exists() or digest(ROOT/name)!=value]
    preservation['passed']=not missing and not preservation['unexpected_changes'] and all(legacy_verified.values()) and head==before['head'] and preservation['final_evaluated_source_hashes_match'] and all(preservation['local_legalbert_files_unchanged'].values()) and not preservation['changed_or_missing_raw_research_inputs']
    dump(BASE/'results/preservation_verification.json',preservation)
    tests=[]
    for name in ['parser_initial_tests.xml','parser_tests.xml','integration_tests.xml','full_native_tests.xml','full_native_final.xml','full_native_verified.xml']:
        root=ET.parse(BASE/name).getroot();suites=list(root.iter('testsuite'))
        tests.append(dict(file=name,tests=sum(int(s.attrib['tests']) for s in suites),failures=sum(int(s.attrib['failures']) for s in suites),
            errors=sum(int(s.attrib['errors']) for s in suites),skipped=sum(int(s.attrib['skipped']) for s in suites),
            skips=[dict(test=t.attrib['name'],reason=t.find('skipped').attrib.get('message')) for t in root.iter('testcase') if t.find('skipped') is not None]))
    dump(BASE/'results/test_runs.json',tests)
    coverage=json.loads((RUN/'coverage.json').read_text(encoding='utf8'))
    summary=dict(final_run='paired_v4',unique_documents=70,analyses_per_implementation=len(cases),
        txt_reference_resolution_statuses=dict(sum((Counter(r['statuses']) for r in coverage if r['mode']=='txt'),Counter())),
        corrected_txt_tasks=[dict(case_id=c['case_id'],tasks=c['corrected_tasks']) for c in cases if c['mode']=='txt' and c['corrected_tasks']],
        regressed_labelled_tasks=[dict(case_id=c['case_id'],mode=c['mode'],tasks=c['regressed_tasks']) for c in cases if c['regressed_tasks']],
        verification=json.loads((RUN/'verification.json').read_text(encoding='utf8')),preservation=preservation['passed'])
    dump(BASE/'results/final_summary.json',summary)
    print(json.dumps(summary,indent=2));print('Tests:',tests[-1])
    return 0 if preservation['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
