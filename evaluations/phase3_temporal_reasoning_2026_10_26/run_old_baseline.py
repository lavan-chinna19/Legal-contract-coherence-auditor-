"""Run the unmodified legacy temporal checker before Phase 3 implementation."""
from pathlib import Path
import importlib.util,json,sys,hashlib
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[1];sys.path.insert(0,str(ROOT))
def main():
    out=BASE/'old_baseline';out.mkdir(exist_ok=False)
    path=BASE/'legacy_snapshot/date_checker.py'
    spec=importlib.util.spec_from_file_location('legacy_phase3_dates',path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    from src.api.ingestion import parse_document
    from src.segmentation.rule_based import RuleBasedSegmenter
    from src.config import ClauseRecord
    helper_path=ROOT/'evaluations/phase1_detection_baseline_2026_10_26/run_baseline.py'
    spec=importlib.util.spec_from_file_location('baseline_helpers',helper_path);h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
    phase1=helper_path.parent;cases=json.loads((phase1/'corpus.json').read_text(encoding='utf8'))['cases']
    records=[]
    for case in cases:
        if not case['case_id'].startswith('T'):continue
        for mode in ['authored','txt']+(['pdf','docx'] if case['case_id'] in ['T02','T13'] else []):
            doc_id=f"baseline_{case['case_id']}_{mode}"
            if mode=='authored':
                clauses=[];offset=0
                for i,text in enumerate(case['clauses']):
                    clauses.append(ClauseRecord(f'{doc_id}_{i}',doc_id,text,'controlled_unit',i,offset,offset+len(text),'synthetic_development'));offset+=len(text)+2
            else:
                parsed=parse_document(h.encoded_document(case,mode),case['case_id']+'.'+mode)
                clauses=RuleBasedSegmenter().segment(parsed,doc_id)
            flags,dates=m.DateLogicChecker().check_document(clauses,doc_id)
            records.append(dict(case=case,mode=mode,flags=[f.to_dict() for f in flags],dates=[d.to_dict() for d in dates]))
    (out/'predictions.json').write_text(json.dumps(records,indent=2)+'\n',encoding='utf8')
    from collections import Counter
    outcomes=[]
    for r in records:
        if r['mode']=='txt' and 'date_chronology' in r['case']['task_labels']:
            g=r['case']['task_labels']['date_chronology'];p=bool(r['flags']);outcomes.append(('TP' if p else 'FN') if g else ('FP' if p else 'TN'))
    result=dict(executed_before_new_temporal_code=True,analyses=len(records),legacy_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),txt_confusion=dict(Counter(outcomes)))
    (out/'verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8');print(json.dumps(result))
if __name__=='__main__':main()
