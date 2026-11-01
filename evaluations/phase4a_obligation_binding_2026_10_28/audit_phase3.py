"""Recompute Phase 3 reported statistics from retained observations, not report prose."""
from pathlib import Path
from collections import Counter
import json,hashlib,math
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[1]

def confusion(rows,predict):
    c=Counter(('TP' if predict(r) else 'FN') if r['gold'] else ('FP' if predict(r) else 'TN') for r in rows if r['gold'] is not None)
    tp,fp,fn,tn=[c[k] for k in ['TP','FP','FN','TN']];divide=lambda a,b:a/b if b else None
    return dict(TP=tp,FP=fp,FN=fn,TN=tn,n=tp+fp+fn+tn,precision=divide(tp,tp+fp),recall=divide(tp,tp+fn),F1=divide(2*tp,2*tp+fp+fn),false_positive_rate=divide(fp,fp+tn))

def main():
    target=BASE/'phase3_audit_verified.json'
    if target.exists():raise FileExistsError('Preserve previous audit evidence')
    run=ROOT/'evaluations/phase3_temporal_reasoning_2026_10_26/results/paired_v3'
    rows=[json.loads(l) for l in (run/'paired_predictions.jsonl').open(encoding='utf8')]
    saved=json.loads((run/'summary.json').read_text());checks=[];coverage=[]
    supported=lambda r:any(d['category'] in ['CONSISTENT','CONFIRMED_TEMPORAL_CONFLICT'] and len(d.get('statement_ids',[]))>=2 for d in r['new']['decisions'])
    for stratum in sorted({r['stratum'] for r in rows}):
        rs=[r for r in rows if r['stratum']==stratum and r['mode']=='txt']
        if stratum=='ORIGINAL_PHASE1':
            tasks=[('old',rs,lambda r:bool(r['old_flags'])),('new',rs,lambda r:bool(r['new_flags']))];expected=saved['original_chronology_screen']
        else:
            tasks=[('legacy_alert_proxy',rs,lambda r:bool(r['old_flags'])),('new_confirmed_screen',rs,lambda r:bool(r['new']['confirmed_conflict_count'])),('selective_supported_relation',[r for r in rs if supported(r)],lambda r:bool(r['new']['confirmed_conflict_count']))];expected=saved[stratum]
        for name,subset,predict in tasks:
            value=confusion(subset,predict)
            checks.append(dict(stratum=stratum,task=name,recomputed=value,matches=all((v==expected[name][k]) if v is None else math.isclose(v,expected[name][k]) for k,v in value.items())))
        coverage.append(dict(stratum=stratum,documents=len(rs),supported_relational=sum(supported(r) for r in rs),
            review=sum(bool(r['new']['review_count']) for r in rs),unsupported=sum(bool(r['new']['unsupported_count']) for r in rs),
            review_unsupported_union=sum(bool(r['new']['review_count']+r['new']['unsupported_count']) for r in rs),
            supported_statements=sum(s['parsing_status']=='EXPLICIT_SUPPORTED' for r in rs for s in r['new']['statements']),
            recognized_statements=sum(len(r['new']['statements']) for r in rs)))
    result=dict(confusion_and_metric_checks=checks,coverage=coverage,
        report_errata=[dict(field='new mechanical review/unsupported union',reported='21/50 (42%)',actual='20/50 (40%)'),
            dict(field='new mechanical review documents',reported=16,actual=15),
            dict(field='new mechanical supported statements',reported='94/118 (79.66%)',actual='96/118 (81.36%)')],
        metric_semantics='Full screen denominator includes abstentions as no confirmation: positive abstention FN, negative abstention screen TN. Selective metrics must show coverage. Review union and supported-relational share can overlap; they are not complements.',
        original_audit_note='phase3_audit.json checked raw summary but its fixed interpretation incorrectly repeated 42%; this verified audit explicitly checks report discrepancies.',
        raw_summary_checks_pass=all(x['matches'] for x in checks))
    target.write_text(json.dumps(result,indent=2)+'\n',encoding='utf8');print(json.dumps(result,indent=2));assert result['raw_summary_checks_pass']

if __name__=='__main__':main()
