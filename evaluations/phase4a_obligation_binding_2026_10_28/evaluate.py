"""Frozen split evaluation. No training, external model or hidden denominator exclusions."""
from pathlib import Path
from collections import Counter
import argparse,hashlib,json,sys,time
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[1];sys.path.insert(0,str(ROOT))
FIELDS=['actor','action','object','recipient','trigger','event_instance']

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
def source_files():return sorted([*(ROOT/'src/obligations').glob('*.py'),ROOT/'src/api/release_routes.py',ROOT/'src/api/reports.py',*(ROOT/'tests').glob('test_obligation*.py'),Path(__file__),BASE/'PROTOCOL.md'])
def freeze():
    path=BASE/'implementation_frozen.json'
    if path.exists():raise FileExistsError('Implementation is already frozen; never tune after reserved evaluation exposure')
    dump(path,dict(frozen_before_evaluation=True,files={p.relative_to(ROOT).as_posix():digest(p) for p in source_files()}))
    print('Implementation frozen before reserved split evaluation.')

def binary(rows,key):
    c=Counter()
    for r in rows:
        gold=r['gold_match']
        if gold is None:continue
        positive=r[key]=='MATCHED';c[('TP' if positive else 'FN') if gold else ('FP' if positive else 'TN')]+=1
    tp,fp,fn,tn=[c[k] for k in ['TP','FP','FN','TN']];div=lambda a,b:a/b if b else None
    return dict(n=tp+fp+fn+tn,TP=tp,FP=fp,FN=fn,TN=tn,precision=div(tp,tp+fp),recall=div(tp,tp+fn),F1=div(2*tp,2*tp+fp+fn),false_positive_rate=div(fp,fp+tn),false_negative_rate=div(fn,fn+tp))

def run(split,run_id):
    benchmark=json.loads((BASE/'benchmark_frozen_manifest.json').read_text(encoding='utf8'))
    assert all(digest(BASE/p)==h for p,h in benchmark['files'].items()),'Frozen inputs/protocol changed'
    if split=='evaluation':
        manifest=json.loads((BASE/'implementation_frozen.json').read_text(encoding='utf8'))
        assert all(digest(ROOT/p)==h for p,h in manifest['files'].items()),'Production/test source changed after freeze'
        exposure=BASE/'evaluation_exposure.json'
        if exposure.exists():raise FileExistsError('Reserved split already exposed; no tuning/repeated initial evaluation')
        dump(exposure,dict(run_id=run_id,split='evaluation',source_frozen=True,policy='One initial reserved-split evaluation. Any later correction is exposed development, never an untouched score.'))
    out=BASE/'results'/run_id;out.mkdir(parents=True,exist_ok=False)
    manifest={p.relative_to(ROOT).as_posix():digest(p) for p in source_files()}
    dump(out/'source_manifest_before_predictions.json',manifest)
    from src.obligations import analyze_bindings
    cases=json.loads((BASE/(split+'.json')).read_text(encoding='utf8'))['cases'];rows=[];fields={f:Counter() for f in FIELDS};record_counts=Counter();start=time.monotonic()
    for case in cases:
        result=analyze_bindings(source_text=case['text'],doc_id=case['case_id'])
        for rec in result['records']:
            assert case['text'][rec['char_start']:rec['char_end']]==rec['raw_text']
            for spans in rec['evidence'].values():
                for span in spans:assert case['text'][span['char_start']:span['char_end']]==span['text']
        sides={s:[r for r in result['records'] if r['section_identity']==case[s+'_section']] for s in ['left','right']}
        try:
            left=sides['left'][case['left_index']];right=sides['right'][case['right_index']]
            pair=next(p for p in result['pairs'] if {p['left_id'],p['right_id']}=={left['record_id'],right['record_id']})
        except (IndexError,StopIteration):
            left=right=None;pair=dict(status='UNSUPPORTED',reasons=['NO_EXTRACTED_TARGET_PAIR'],evidence=[])
        # Explicit ablation, not a historical classifier: ignore trigger/conditions/scope etc.
        if left and right:
            values=[(left[f],right[f]) for f in ['actor','action','object']]
            ablation='UNCERTAIN' if any(a is None or b is None for a,b in values) else 'MATCHED' if all(a==b for a,b in values) else 'DIFFERENT'
        else:ablation='UNSUPPORTED'
        errors=[]
        if case['label_provenance']!='PROVISIONAL_INTERPRETATION':
            for side in ['left','right']:
                expected=case['expected_'+side];observed=sides[side]
                record_counts['expected']+=len(expected);record_counts['extracted']+=len(observed)
                record_counts['missing']+=max(0,len(expected)-len(observed));record_counts['extra']+=max(0,len(observed)-len(expected))
                for i,gold in enumerate(expected):
                    pred=observed[i] if i<len(observed) else {}
                    for field in FIELDS:
                        g,p=gold[field],pred.get(field);c=fields[field];c['denominator']+=1
                        if g==p:c['exact']+=1
                        if g is not None:c['gold_nonnull']+=1
                        if p is not None:c['predicted_nonnull']+=1
                        if g is not None and g==p:c['correct_nonnull']+=1
                        if g!=p:errors.append(dict(side=side,index=i,field=field,expected=g,predicted=p))
        rows.append(dict(case_id=case['case_id'],family_id=case['family_id'],gold_state=case['gold_state'],gold_match=case['gold_match'],
            prediction=pair['status'],ablation=ablation,selected_pair=pair,field_errors=errors,
            outcome_correct=None if case['gold_state'] is None else case['gold_state']==pair['status'],case=case,result=result))
    div=lambda a,b:a/b if b else None
    field_summary={f:dict(c,exact_rate=div(c['exact'],c['denominator']),nonnull_precision=div(c['correct_nonnull'],c['predicted_nonnull']),nonnull_recall=div(c['correct_nonnull'],c['gold_nonnull'])) for f,c in fields.items()}
    labelled=[r for r in rows if r['gold_state'] is not None];decided=[r for r in rows if r['prediction'] in ['MATCHED','DIFFERENT']]
    summary=dict(split=split,documents=len(rows),labelled_states=len(labelled),provisional_unscored=len(rows)-len(labelled),independent_annotation_count=0,
        full_binary_screen=binary(rows,'prediction'),selective_binary_screen=binary(decided,'prediction'),
        guard_ablation_binary=binary(rows,'ablation'),
        coverage_numerator=len(decided),coverage_denominator=len(rows),coverage=div(len(decided),len(rows)),
        abstention_numerator=len(rows)-len(decided),abstention_rate=div(len(rows)-len(decided),len(rows)),
        state_confusion=dict(Counter(r['gold_state']+' -> '+r['prediction'] for r in labelled)),
        correct_state_count=sum(r['outcome_correct'] for r in labelled),state_accuracy=div(sum(r['outcome_correct'] for r in labelled),len(labelled)),
        unsafe_confirmation_count=sum(r['gold_state'] in ['UNCERTAIN','UNSUPPORTED'] and r['prediction']=='MATCHED' for r in labelled),
        field_metrics=field_summary,record_counts=dict(record_counts),elapsed_seconds=time.monotonic()-start,
        label_scope='Mechanical explicit-field comparability only. Reserved synthetic families are author-controlled, not independent real-world legal validation.',
        parser_exceptions=0,source_manifest_unchanged=all(digest(ROOT/p)==h for p,h in manifest.items()))
    with (out/'predictions.jsonl').open('w',encoding='utf8') as stream:
        for r in rows:stream.write(json.dumps(r,ensure_ascii=False)+'\n')
    dump(out/'summary.json',summary)
    dump(out/'errors.json',[r for r in rows if r['outcome_correct'] is False or r['field_errors']])
    dump(out/'ablation_changes.json',[dict(case_id=r['case_id'],gold=r['gold_state'],without_guards=r['ablation'],with_guards=r['prediction']) for r in labelled if r['ablation']!=r['prediction']])
    print(json.dumps(summary,indent=2));assert summary['source_manifest_unchanged']

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--freeze',action='store_true');parser.add_argument('--split',choices=['development','evaluation']);parser.add_argument('--run-id');args=parser.parse_args()
    if args.freeze:freeze()
    else:
        if not args.split or not args.run_id:parser.error('Both --split and a new --run-id are required')
        run(args.split,args.run_id)
