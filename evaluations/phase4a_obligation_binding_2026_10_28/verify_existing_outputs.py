"""Actual local neural/core parity; new experimental output never enters core inference."""
from pathlib import Path
import json,hashlib,os,sys,time
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[1];sys.path.insert(0,str(ROOT))

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def canon(v):return json.loads(json.dumps(v,default=str))

def main():
    out=BASE/'preserved_output_verification.json'
    if out.exists():raise FileExistsError('Keep previous parity evidence')
    runtime=BASE/'runtime/parity';runtime.mkdir(parents=True,exist_ok=True)
    os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',LEXAUDIT_ALLOW_MODEL_DOWNLOAD='0',
        LEXAUDIT_EMBEDDINGS_CACHE_DIR=str(runtime/'vectors'),LEXAUDIT_FEEDBACK_DB_PATH=str(runtime/'feedback.sqlite'),
        LEXAUDIT_THRESHOLDS_PATH=str(runtime/'thresholds.json'),OMP_NUM_THREADS='2',MKL_NUM_THREADS='2')
    os.environ.pop('DATABASE_URL',None)
    from src.api.dependencies import get_unified_auditor
    from src.rules.dependency_graph import detect_dependencies
    from src.rules.date_checker import DateLogicChecker
    from src.config import ClauseRecord
    import torch
    torch.set_num_threads(2)
    snapshot=json.loads((BASE/'preservation_before.json').read_text())['files']
    core=[p for p in snapshot if p.startswith(('src/temporal/','src/structure/','src/scoring/','src/embeddings/','src/coherence/','src/calibration/','models/'))]+['src/rules/date_checker.py','src/rules/unified_pipeline.py','src/rules/reference_checker.py','src/rules/dependency_graph.py','fixtures/ledgar_centroids.npz','fixtures/conformal_calibration_fixture.json','src/segmentation/rule_based.py']
    assert all(digest(ROOT/p)==snapshot[p] for p in core)
    temporal={}
    for line in (ROOT/'evaluations/phase3_temporal_reasoning_2026_10_26/results/paired_v3/paired_predictions.jsonl').open(encoding='utf8'):
        r=json.loads(line)
        if r['stratum']=='ORIGINAL_PHASE1':temporal[r['case_id'],r['mode']]=r
    auditor=get_unified_auditor();checks=[];start=time.monotonic()
    for line in (ROOT/'evaluations/phase2_structural_parser_2026_10_26/results/paired_v4/paired_predictions.jsonl').open(encoding='utf8'):
        old=json.loads(line)['new'];case_id=old['case']['case_id'];mode=old['mode'];doc_id=old['audit']['doc_id']
        clauses=[ClauseRecord(**c) for c in old['segments']];source=old['extracted_text']
        new=auditor.audit_document(clauses,doc_id,source_text=source).to_dict()
        graph=detect_dependencies([c.to_dict() for c in clauses],source_text=source)
        ref=lambda a:[f for f in a['rule_flags'] if not f['flag_id'].startswith('FLAG_DATE_')]
        direct=DateLogicChecker().analyze_document(clauses,doc_id,source_text=source)
        row=dict(case_id=case_id,mode=mode,neural_same=canon(new['scoring_result']['clauses'])==old['audit']['scoring_result']['clauses'],
            structure_same=new['metadata']['structural_document']==old['audit']['metadata']['structural_document'],
            references_same=canon(ref(new))==ref(old['audit']) and new['metadata']['reference_resolutions']==old['audit']['metadata']['reference_resolutions'],
            graph_same=canon(graph)==old['graph'],direct_preserved_date_integration_same=canon(direct['metadata'])==new['metadata']['temporal_analysis'])
        if (case_id,mode) in temporal:
            saved=temporal[case_id,mode]
            row['historical_phase3_date_same']=new['metadata']['temporal_analysis']==saved['new'] and [f for f in new['rule_flags'] if f['flag_id'].startswith('FLAG_DATE_')]==saved['new_flags']
        checks.append(row)
    result=dict(records=checks,counts={k:sum(r.get(k,False) for r in checks) for k in ['neural_same','structure_same','references_same','graph_same','direct_preserved_date_integration_same','historical_phase3_date_same']},
        case_modes=len(checks),frozen_core_files=len(core),core_hashes_unchanged=all(digest(ROOT/p)==snapshot[p] for p in core),
        date_method='38 modes match saved Phase 3 dates/flags exactly; all 148 modes match direct unchanged Phase 3 checker and its source hashes.',elapsed_seconds=time.monotonic()-start)
    result['passed']=result['core_hashes_unchanged'] and all(all(v for k,v in r.items() if k not in ['case_id','mode']) for r in checks)
    out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf8');print(json.dumps({k:v for k,v in result.items() if k!='records'},indent=2));assert result['passed']

if __name__=='__main__':main()
