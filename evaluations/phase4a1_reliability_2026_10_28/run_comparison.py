"""Actual frozen Phase 4A baseline and repaired matcher on exposed focused evidence."""
from pathlib import Path
from collections import Counter
import argparse,hashlib,importlib.util,json,sys,time
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[1];OLD=ROOT/'evaluations/phase4a_obligation_binding_2026_10_28'
sys.path.insert(0,str(ROOT))

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
def old_module():
    path=BASE/'baseline_snapshot/binding.py'
    manifest=json.loads((OLD/'implementation_frozen.json').read_text())
    assert digest(path)==manifest['files']['src/obligations/binding.py']
    spec=importlib.util.spec_from_file_location('frozen_phase4a_binding',path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def cases():
    rows=[]
    for split,run in [('development','development_v1'),('evaluation','evaluation_first_pass')]:
        saved={r['case_id']:r for r in [json.loads(l) for l in (OLD/'results'/run/'predictions.jsonl').open(encoding='utf8')]}
        for c in json.loads((OLD/(split+'.json')).read_text())['cases']:rows.append(dict(case=c,stratum='EXPOSED_ORIGINAL_'+split.upper(),saved=saved[c['case_id']]['result']))
    for c in json.loads((BASE/'focused_cases.json').read_text())['cases']:rows.append(dict(case=c,stratum='FOCUSED_AUTHORED_DEVELOPMENT',saved=None))
    return rows

def selected(result,c):
    def find(side):
        return [r for r in result['records'] if r['section_identity']==c.get(side+'_section','1' if side=='left' else '2')][c.get(side+'_index',0)]
    try:
        a,b=find('left'),find('right')
        pair=next(p for p in result['pairs'] if {p['left_id'],p['right_id']}=={a['record_id'],b['record_id']})
        return pair
    except (IndexError,StopIteration):return dict(status='UNSUPPORTED',reasons=['NO_EXTRACTED_TARGET_PAIR'])

def synthetic(analyze):
    result=[]
    for entry in cases():
        c=entry['case'];r=analyze(source_text=c['text'],doc_id=c['case_id'])
        for record in r['records']:
            assert c['text'][record['char_start']:record['char_end']]==record['raw_text']
            for spans in record['evidence'].values():
                for span in spans:assert c['text'][span['char_start']:span['char_end']]==span['text']
        result.append(dict(case=c,stratum=entry['stratum'],selected=selected(r,c),result=r,
            original_archived_result_reproduced=None if entry['saved'] is None else r==entry['saved']))
    return result

def public(analyze):
    from src.segmentation.rule_based import RuleBasedSegmenter
    manifest=json.loads((ROOT/'data/raw/sec_edgar/edgar_manifest.json').read_text())
    lookup={Path(e['local_path']).name:e for e in manifest['entries']}
    prior=json.loads((OLD/'public_substantive_smoke.json').read_text());paths=list(dict.fromkeys(r['path'] for r in prior['observations']))
    records=[]
    for rel in paths:
        path=ROOT/rel;raw=path.read_bytes();text=raw.decode('utf8');source=lookup[path.name]
        for mode,input_text in [('raw_source',text),('existing_legacy_html_extraction',RuleBasedSegmenter()._clean_html(text))]:
            out=analyze(source_text=input_text,doc_id=path.stem+'_'+mode)
            assert all(input_text[r['char_start']:r['char_end']]==r['raw_text'] for r in out['records'])
            records.append(dict(path=rel,source_url=source['source_url'],entity_name=source['entity_name'],accession=source['accession_no'],exhibit=source['exhibit_type'],filing_date=source['file_date'],
                mode=mode,raw_sha256=digest(path),input_sha256=hashlib.sha256(input_text.encode('utf8')).hexdigest(),input_text=input_text,
                coordinate_note='Spans index this identified extraction view, not original HTML bytes or PDF geometry.',result=out,ground_truth=None))
    return records

def write_rows(p,rows):
    with p.open('w',encoding='utf8') as stream:
        for row in rows:stream.write(json.dumps(row,ensure_ascii=False)+'\n')

def metrics(rows,side):
    count=Counter()
    for r in rows:
        gold=r['case']['gold_match']
        if gold is None:continue
        pred=r[side]['selected']['status']=='MATCHED';count[('TP' if pred else 'FN') if gold else ('FP' if pred else 'TN')]+=1
    tp,fp,fn,tn=[count[k] for k in ['TP','FP','FN','TN']];d=lambda a,b:a/b if b else None
    return dict(n=tp+fp+fn+tn,TP=tp,FP=fp,FN=fn,TN=tn,precision=d(tp,tp+fp),recall=d(tp,tp+fn),F1=d(2*tp,2*tp+fp+fn),FPR=d(fp,fp+tn),FNR=d(fn,tp+fn))

def main(baseline,run_id):
    frozen=json.loads((BASE/'focused_input_manifest.json').read_text())
    assert all(digest(BASE/p)==h for p,h in frozen['files'].items())
    out=BASE/'results'/run_id;out.mkdir(parents=True,exist_ok=False)
    if baseline:
        m=old_module();syn=synthetic(m.analyze_bindings);pub=public(m.analyze_bindings)
        write_rows(out/'synthetic.jsonl',syn);write_rows(out/'public.jsonl',pub)
        check=dict(original_results_reproduced=sum(r['original_archived_result_reproduced'] is True for r in syn),original_cases=58,focused_cases=20,public_observations=len(pub),baseline_sha256=digest(BASE/'baseline_snapshot/binding.py'))
        dump(out/'verification.json',check);print(json.dumps(check,indent=2));assert check['original_results_reproduced']==58;return
    from src.obligations import analyze_bindings
    files=[*sorted((ROOT/'src/obligations').glob('*.py')),ROOT/'src/api/reports.py',Path(__file__)]
    source_manifest={p.relative_to(ROOT).as_posix():digest(p) for p in files};dump(out/'source_manifest_before_predictions.json',source_manifest)
    prior=BASE/'results/baseline_v1'
    old_syn=[json.loads(l) for l in (prior/'synthetic.jsonl').open(encoding='utf8')];new_syn=synthetic(analyze_bindings)
    paired=[dict(case=a['case'],stratum=a['stratum'],old=a,new=b) for a,b in zip(old_syn,new_syn)]
    write_rows(out/'paired_synthetic.jsonl',paired)
    old_pub=[json.loads(l) for l in (prior/'public.jsonl').open(encoding='utf8')];new_pub=public(analyze_bindings)
    public_paired=[dict(old=a,new=b) for a,b in zip(old_pub,new_pub)];write_rows(out/'paired_public.jsonl',public_paired)
    summary={};changes=[]
    for stratum in sorted(set(r['stratum'] for r in paired)):
        rows=[r for r in paired if r['stratum']==stratum];s={}
        for side in ['old','new']:
            decided=sum(r[side]['selected']['status'] in ['MATCHED','DIFFERENT'] for r in rows)
            all_pairs=sum(len(r[side]['result']['pairs']) for r in rows)
            pair_decided=sum(p['status'] in ['MATCHED','DIFFERENT'] for r in rows for p in r[side]['result']['pairs'])
            s[side]=dict(binary=metrics(rows,side),selected_pair_statuses=dict(Counter(r[side]['selected']['status'] for r in rows)),
                selected_decided=decided,documents=len(rows),selected_abstained=len(rows)-decided,
                emitted_pairs=all_pairs,emitted_decided_pairs=pair_decided,emitted_abstained_pairs=all_pairs-pair_decided,
                documents_with_any_supported_pair=sum(any(p['status'] in ['MATCHED','DIFFERENT'] for p in r[side]['result']['pairs']) for r in rows))
        summary[stratum]=s
        for r in rows:
            gold=r['case']['gold_state']
            if gold is not None:
                a=r['old']['selected']['status'];b=r['new']['selected']['status']
                if a!=b:changes.append(dict(case_id=r['case']['case_id'],stratum=stratum,gold=gold,before=a,after=b,corrected=a!=gold and b==gold,introduced=a==gold and b!=gold))
    dump(out/'summary.json',summary);dump(out/'changes.json',changes)
    dump(out/'verification.json',dict(source_manifest_unchanged=all(digest(ROOT/p)==h for p,h in source_manifest.items()),synthetic_observations=len(paired),public_observations=len(public_paired),parser_exceptions=0))
    print(json.dumps(summary,indent=2));print('Changed decisions',json.dumps(changes));assert all(digest(ROOT/p)==h for p,h in source_manifest.items())

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--baseline',action='store_true');p.add_argument('--run-id',required=True);a=p.parse_args();main(a.baseline,a.run_id)
