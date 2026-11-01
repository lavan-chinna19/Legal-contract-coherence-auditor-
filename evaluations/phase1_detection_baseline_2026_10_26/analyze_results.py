"""Derive reviewable evidence from saved predictions; never reruns or tunes detectors."""
from pathlib import Path
import json
from collections import Counter
BASE=Path(__file__).resolve().parent

def load(run):
    return [json.loads(line) for line in (BASE/'results'/run/'predictions.jsonl').read_text(encoding='utf-8').splitlines()]

def stable(value, key='', canonicalize_sets=True):
    # UUID flag IDs and wall-clock timestamps are deliberately not scientific predictions.
    if isinstance(value,dict):return {k:stable(v,k,canonicalize_sets) for k,v in value.items() if k not in ['flag_id','timestamp']}
    if isinstance(value,list):
        result=[stable(v,'',canonicalize_sets) for v in value]
        # These fields are semantically sets assembled from Python sets in the frozen code.
        # Clause order, scores, reference positions and predictions are never reordered/ignored.
        return sorted(result,key=lambda x:json.dumps(x,sort_keys=True)) if canonicalize_sets and key in ['declared_targets','available_targets_sample','involved_clause_ids'] else result
    return value

def analyze():
    records=load('frozen_primary');evidence=[]
    for r in records:
        scores=r['audit']['scoring_result']['clauses']
        evidence.append(dict(case_id=r['case']['case_id'],mode=r['mode'],
            family=r['case']['family'],provenance=r['case']['label_provenance'],
            gold=r['case']['task_labels'],rule_flags=r['audit']['rule_flags'],
            declared_targets=r['audit']['declared_targets'],dates=r['audit']['extracted_dates'],
            graph=r['graph'],segments=r['segments'],segmentation=r['segmentation'],
            ml_flags=r['audit']['ml_anomaly_count'],
            mean_A=sum(c['channel_a_score'] for c in scores)/len(scores),
            max_A=max(c['channel_a_score'] for c in scores),
            mean_B=sum(c['channel_b_score'] for c in scores)/len(scores),
            max_B=max(c['channel_b_score'] for c in scores),
            max_ensemble=max(c['combined_score'] for c in scores),
            mean_interval_width=sum(c['interval_width'] for c in scores)/len(scores)))
    (BASE/'results'/'evidence_index.json').write_text(json.dumps(evidence,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    for r in evidence:
        if r['mode']=='txt':
            print(r['case_id'],r['gold'],'rules='+str([f['flag_type'] for f in r['rule_flags']]),
                'graph='+r['graph']['status'],f"A={r['max_A']:.4f} B={r['max_B']:.4f} E={r['max_ensemble']:.4f} MLflags={r['ml_flags']}")
    replication=BASE/'results'/'frozen_replication'/'predictions.jsonl'
    if replication.exists() and (replication.parent/'summary.json').exists():
        second=load('frozen_replication')
        differences=[dict(case_id=a['case']['case_id'],mode=a['mode']) for a,b in zip(records,second) if stable(a)!=stable(b)]
        result=dict(primary_records=len(records),replication_records=len(second),
            ignored_non_predictive_fields=['flag_id','timestamp'],
            canonicalized_unordered_fields=['declared_targets','available_targets_sample','involved_clause_ids'],
            raw_order_equal_records=sum(stable(a,canonicalize_sets=False)==stable(b,canonicalize_sets=False) for a,b in zip(records,second)),
            stable_prediction_records=sum(stable(a)==stable(b) for a,b in zip(records,second)),
            differences=differences,passed=len(records)==len(second) and not differences)
        (BASE/'results'/'repeatability.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
        print('REPEATABILITY',result)

if __name__=='__main__':analyze()
