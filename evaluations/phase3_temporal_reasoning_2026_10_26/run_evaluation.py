"""Paired exposed development evaluation; original artifacts are read-only.

Run from repository root with the existing clean Python. Each --run-id must be new.
No model fitting, threshold changes, network model access or user storage writes.
"""
from pathlib import Path
from collections import Counter
import argparse,hashlib,importlib.util,json,os,sys,time
BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[1]

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False,default=str)+'\n',encoding='utf8')
def canon(v):return json.loads(json.dumps(v,default=str))
def module(name,p):
    spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def metrics(rows,gold,prediction):
    counts=Counter()
    for r in rows:
        g=gold(r);p=prediction(r)
        if g is None:continue
        counts[('TP' if p else 'FN') if g else ('FP' if p else 'TN')]+=1
    tp,fp,fn,tn=[counts[k] for k in ['TP','FP','FN','TN']]
    div=lambda a,b:a/b if b else None
    return dict(n=tp+fp+fn+tn,TP=tp,FP=fp,FN=fn,TN=tn,precision=div(tp,tp+fp),recall=div(tp,tp+fn),
        F1=div(2*tp,2*tp+fp+fn),false_positive_rate=div(fp,fp+tn))

def main(run_id):
    out=BASE/'results'/run_id;out.mkdir(parents=True,exist_ok=False)
    runtime=BASE/'runtime'/run_id;runtime.mkdir(parents=True,exist_ok=False)
    os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',LEXAUDIT_ALLOW_MODEL_DOWNLOAD='0',
        LEXAUDIT_EMBEDDINGS_CACHE_DIR=str(runtime/'vectors'),LEXAUDIT_FEEDBACK_DB_PATH=str(runtime/'feedback.sqlite'),
        LEXAUDIT_THRESHOLDS_PATH=str(runtime/'thresholds.json'),OMP_NUM_THREADS='2',MKL_NUM_THREADS='2',TOKENIZERS_PARALLELISM='false')
    os.environ.pop('DATABASE_URL',None);sys.path.insert(0,str(ROOT))
    files=[*sorted((ROOT/'src').rglob('*.py')),*sorted(BASE.glob('*.py')),BASE/'PROTOCOL.md',
        BASE/'new_cases.json',BASE/'challenge_cases.json',BASE/'legacy_snapshot/date_checker.py']
    manifest={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in files}
    dump(out/'source_manifest_before_predictions.json',manifest)
    from src.temporal import analyze_temporal
    from src.api.dependencies import get_unified_auditor,get_ml_segmenter
    from src.api.ingestion import parse_document
    from src.config import ClauseRecord
    from src.rules.dependency_graph import detect_dependencies
    import torch
    torch.set_num_threads(2)
    old_checker=module('phase3_frozen_dates',BASE/'legacy_snapshot/date_checker.py').DateLogicChecker()
    segmenter=get_ml_segmenter();auditor=get_unified_auditor()
    phase2=ROOT/'evaluations/phase2_structural_parser_2026_10_26/results/paired_v4/paired_predictions.jsonl'
    records=[];parity=[];started=time.monotonic()
    with (out/'paired_predictions.jsonl').open('w',encoding='utf8') as stream:
        for line in phase2.open(encoding='utf8'):
            saved=json.loads(line)['new'];case=saved['case'];mode=saved['mode'];old=saved['audit']
            segments=[ClauseRecord(**c) for c in saved['segments']]
            text=saved['extracted_text'];doc_id=old['doc_id']
            new=auditor.audit_document(segments,doc_id,source_text=text).to_dict()
            graph=detect_dependencies([c.to_dict() for c in segments],structure=None,source_text=text)
            ref=lambda report:[f for f in report['rule_flags'] if not f['flag_id'].startswith('FLAG_DATE_')]
            checks=dict(case_id=case['case_id'],mode=mode,
                neural_identical=canon(old['scoring_result']['clauses'])==canon(new['scoring_result']['clauses']),
                structure_identical=old['metadata']['structural_document']==new['metadata']['structural_document'],
                references_identical=canon(ref(old))==canon(ref(new)) and old['metadata']['reference_resolutions']==new['metadata']['reference_resolutions'],
                graph_identical=canon(saved['graph'])==canon(graph))
            parity.append(checks)
            if case['case_id'].startswith('T'):
                flags,dates=old_checker.check_document(segments,doc_id)
                r=dict(stratum='ORIGINAL_PHASE1',case_id=case['case_id'],mode=mode,case=case,source_text=text,
                    gold=case['task_labels'].get('date_chronology'),label_task='original chronology candidate screen',
                    old_flags=[f.to_dict() for f in flags],old_dates=[d.to_dict() for d in dates],
                    new=new['metadata']['temporal_analysis'],new_flags=[f for f in new['rule_flags'] if f['flag_id'].startswith('FLAG_DATE_')])
                records.append(r);stream.write(json.dumps(r,ensure_ascii=False)+'\n');stream.flush()
        for filename in ['new_cases.json','challenge_cases.json']:
            for case in json.loads((BASE/filename).read_text(encoding='utf8'))['cases']:
                text=case['text'];doc_id='phase3_'+case['case_id'];segments=segmenter.segment(text,doc_id)
                flags,dates=old_checker.check_document(segments,doc_id)
                new=analyze_temporal(segments,doc_id,source_text=text)
                r=dict(stratum=case['provenance'],case_id=case['case_id'],mode='txt',case=case,source_text=text,
                    gold=case['confirmed_conflict_gold'],label_task='explicit constructed conflict',
                    old_flags=[f.to_dict() for f in flags],old_dates=[d.to_dict() for d in dates],
                    new=new['metadata'],new_flags=[f.to_dict() for f in new['flags']])
                records.append(r);stream.write(json.dumps(r,ensure_ascii=False)+'\n');stream.flush()
    for r in records:
        for s in r['new']['statements']:
            assert r['source_text'][s['char_start']:s['char_end']]==s['raw_text']
            if s['raw_date']:assert r['source_text'][s['date_start']:s['date_end']]==s['raw_date']
    original=[r for r in records if r['stratum']=='ORIGINAL_PHASE1' and r['mode']=='txt']
    summary={'original_chronology_screen':dict(old=metrics(original,lambda r:r['gold'],lambda r:bool(r['old_flags'])),
        new=metrics(original,lambda r:r['gold'],lambda r:bool(r['new_flags'])))}
    for stratum in sorted({r['stratum'] for r in records if r['stratum']!='ORIGINAL_PHASE1'}):
        rows=[r for r in records if r['stratum']==stratum]
        relational=lambda r:any(d['category'] in ['CONSISTENT','CONFIRMED_TEMPORAL_CONFLICT'] and len(d.get('statement_ids',[]))>=2 for d in r['new']['decisions'])
        summary[stratum]=dict(documents=len(rows),independently_adjudicated=0,
            legacy_alert_proxy=metrics(rows,lambda r:r['gold'],lambda r:bool(r['old_flags'])),
            new_confirmed_screen=metrics(rows,lambda r:r['gold'],lambda r:bool(r['new']['confirmed_conflict_count'])),
            selective_supported_relation=metrics([r for r in rows if relational(r)],lambda r:r['gold'],lambda r:bool(r['new']['confirmed_conflict_count'])),
            candidate_alert_documents=sum(bool(r['new_flags']) for r in rows),
            review_documents=sum(bool(r['new']['review_count']) for r in rows),
            unsupported_documents=sum(bool(r['new']['unsupported_count']) for r in rows),
            abstention_documents=sum(bool(r['new']['review_count']+r['new']['unsupported_count']) for r in rows),
            supported_relation_documents=sum(relational(r) for r in rows),
            recognized_statements=sum(len(r['new']['statements']) for r in rows),
            supported_statements=sum(s['parsing_status']=='EXPLICIT_SUPPORTED' for r in rows for s in r['new']['statements']),
            statuses=dict(Counter(r['new']['status'] for r in rows)))
    changes=[]
    for r in records:
        if r['mode']!='txt' or r['gold'] is None:continue
        before=bool(r['old_flags']);after=bool(r['new_flags']) if r['stratum']=='ORIGINAL_PHASE1' else bool(r['new']['confirmed_conflict_count'])
        changes.append(dict(case_id=r['case_id'],stratum=r['stratum'],gold=r['gold'],old_prediction=before,new_prediction=after,
            old_outcome=('TP' if before else 'FN') if r['gold'] else ('FP' if before else 'TN'),
            new_outcome=('TP' if after else 'FN') if r['gold'] else ('FP' if after else 'TN'),
            new_status=r['new']['status'],checks=[d.get('check') for d in r['new']['decisions']]))
    baseline=json.loads((BASE/'old_baseline/predictions.json').read_text(encoding='utf8'))
    oldmap={(r['case']['case_id'],r['mode']):r for r in baseline}
    # The legacy checker serializes a Python set of involved IDs as a list. Its
    # iteration order varies across processes. Normalize ONLY this unordered field.
    def stable_flags(flags):
        return [dict(f,involved_clause_ids=sorted(f['involved_clause_ids'])) for f in flags]
    reproduction=all(stable_flags(r['old_flags'])==stable_flags(oldmap[(r['case_id'],r['mode'])]['flags']) and r['old_dates']==oldmap[(r['case_id'],r['mode'])]['dates'] for r in records if r['stratum']=='ORIGINAL_PHASE1')
    verification=dict(analyses=len(records),neural_parity_cases=len(parity),old_baseline_reproduced=reproduction,
        parity_counts={k:sum(p[k] for p in parity) for k in ['neural_identical','structure_identical','references_identical','graph_identical']},
        exact_temporal_spans_verified=True,parser_exceptions=0,
        source_manifest_unchanged=all(digest(ROOT/p)==h for p,h in manifest.items()),elapsed_seconds=time.monotonic()-started)
    dump(out/'summary.json',summary);dump(out/'changes.json',changes);dump(out/'parity.json',parity);dump(out/'verification.json',verification)
    print(json.dumps(dict(summary=summary,verification=verification),indent=2),flush=True)
    assert reproduction and verification['source_manifest_unchanged']
    assert all(all(p[k] for k in ['neural_identical','structure_identical','references_identical','graph_identical']) for p in parity),'Preserved-channel regression'

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--run-id',required=True);main(parser.parse_args().run_id)
