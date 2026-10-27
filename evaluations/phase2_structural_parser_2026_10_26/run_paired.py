"""Re-execute exact legacy modules and new rules with the same frozen neural scorer.

Phase 1 corpus/results are read-only. Case-specific logic is confined to measurement strata
and the already-defined format probe selection, never production parsing or prediction.
"""
from pathlib import Path
from collections import Counter
import argparse, hashlib, importlib.util, json, os, sys, time
BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[1]
PHASE1=ROOT/'evaluations/phase1_detection_baseline_2026_10_26'

def load_module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def dump(path,value):path.write_text(json.dumps(value,indent=2,ensure_ascii=False,default=str)+'\n',encoding='utf8')

def main(run_id):
    out=BASE/'results'/run_id;out.mkdir(parents=True,exist_ok=False)
    runtime=BASE/'runtime'/run_id;runtime.mkdir(parents=True,exist_ok=False)
    os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',LEXAUDIT_ALLOW_MODEL_DOWNLOAD='0',
        LEXAUDIT_EMBEDDINGS_CACHE_DIR=str(runtime/'vectors'),LEXAUDIT_FEEDBACK_DB_PATH=str(runtime/'feedback.sqlite'),
        OMP_NUM_THREADS='2',MKL_NUM_THREADS='2',TOKENIZERS_PARALLELISM='false')
    os.environ.pop('DATABASE_URL',None);sys.path.insert(0,str(ROOT))
    previous=json.loads((BASE/'preservation_before.json').read_text(encoding='utf8'))['files']
    immutable=[p for p in previous if p.startswith(('src/embeddings/','src/coherence/','src/scoring/','src/calibration/','models/','evaluations/phase1_'))]
    immutable += ['src/config.py','src/segmentation/rule_based.py','src/api/ingestion.py','src/rules/date_checker.py','fixtures/ledgar_centroids.npz','fixtures/conformal_calibration_fixture.json']
    assert all(digest(ROOT/p)==previous[p] for p in immutable),'Frozen asset/Phase 1/scoring input code changed'
    files=[*sorted((ROOT/'src').rglob('*.py')),Path(__file__),BASE/'PROTOCOL.md',*sorted((BASE/'legacy_snapshot').glob('*.py'))]
    manifest={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in files}
    dump(out/'source_manifest_before_predictions.json',manifest)
    helper=load_module('phase1_evaluation_helpers',PHASE1/'run_baseline.py')
    old_reference=load_module('legacy_reference',BASE/'legacy_snapshot/reference_checker.py')
    old_pipeline=load_module('legacy_pipeline',BASE/'legacy_snapshot/unified_pipeline.py')
    old_graph=load_module('legacy_graph',BASE/'legacy_snapshot/dependency_graph.py')
    legacy_seg=load_module('src.segmentation._phase2_legacy_rule_based',BASE/'legacy_snapshot/rule_based.py')
    old_ingest=load_module('legacy_ingestion',BASE/'legacy_snapshot/ingestion.py')
    from src.api.dependencies import get_dual_channel_scorer,get_ml_segmenter,get_unified_auditor
    from src.api.ingestion import parse_document
    from src.rules.dependency_graph import detect_dependencies
    from src.structure import parse_contract,resolve_references
    from src.config import ClauseRecord
    import torch
    torch.set_num_threads(2)
    scorer=get_dual_channel_scorer();new_auditor=get_unified_auditor()
    old_auditor=old_pipeline.UnifiedAuditor(scorer=scorer,reference_checker=old_reference.CrossReferenceChecker())
    old_segmenter=legacy_seg.RuleBasedSegmenter();new_segmenter=get_ml_segmenter()
    assert scorer is new_auditor.scorer and scorer.channel_a.centroid_matrix is not None
    cases=json.loads((PHASE1/'corpus.json').read_text(encoding='utf8'))['cases']
    original={(r['case']['case_id'],r['mode']):r for r in [json.loads(x) for x in (PHASE1/'results/frozen_primary/predictions.jsonl').read_text(encoding='utf8').splitlines()]}
    old_records=[];new_records=[];parity=[];start=time.monotonic()
    with (out/'paired_predictions.jsonl').open('w',encoding='utf8') as stream:
        for case in cases:
            for mode in ['authored','txt']+(['pdf','docx'] if case['case_id'] in ['R02','T02','T13','S04'] else []):
                doc_id=f"baseline_{case['case_id']}_{mode}";source='\n\n'.join(case['clauses'])
                if mode=='authored':
                    segments=[];offset=0;parsed=source
                    for i,text in enumerate(case['clauses']):
                        segments.append(ClauseRecord(f'{doc_id}_{i}',doc_id,text,'controlled_unit',i,offset,offset+len(text),'synthetic_development'));offset+=len(text)+2
                    old_segments=segments
                else:
                    content=helper.encoded_document(case,mode)
                    parsed=parse_document(content,f"{case['case_id']}.{mode}")
                    assert parsed==old_ingest.parse_document(content,f"{case['case_id']}.{mode}")
                    segments=new_segmenter.segment(parsed,doc_id);old_segments=old_segmenter.segment(parsed,doc_id)
                assert [c.to_dict() for c in segments]==[c.to_dict() for c in old_segments]
                old=old_auditor.audit_document(old_segments,doc_id).to_dict()
                new=new_auditor.audit_document(segments,doc_id,source_text=parsed).to_dict()
                structure=parse_contract(segments,doc_id,source_text=parsed)
                old_g=old_graph.detect_dependencies([c.to_dict() for c in old_segments])
                new_g=detect_dependencies([c.to_dict() for c in segments],structure=structure)
                normalization=new_segmenter._clean_html(parsed) if mode!='authored' else parsed
                common=dict(case=case,mode=mode,status='OK',segments=[c.to_dict() for c in segments],extracted_text=parsed,
                    normalized_text=normalization,b_diagnostic_threshold=scorer.severity_ranker.med_single_threshold,
                    segmentation=dict(expected=len(case['clauses']),observed=len(segments),
                        authored_units_match=[c.text for c in segments]==case['clauses'],
                        offsets_valid=all(normalization[c.char_start:c.char_end]==c.text for c in segments),normalization_changed_text=normalization!=parsed))
                old_r=dict(common,audit=old,graph=old_g);new_r=dict(common,audit=new,graph=new_g)
                old_records.append(old_r);new_records.append(new_r)
                old_scores=old['scoring_result']['clauses'];new_scores=new['scoring_result']['clauses']
                phase1=original[(case['case_id'],mode)]
                old_ref_signature=lambda report: sorted((f['flag_type'],f['clause_id'],f['evidence'].get('target_id')) for f in report['rule_flags'])
                # Saved JSON represents confidence-interval tuples as arrays. Normalize that
                # serialization distinction without dropping or rounding numerical evidence.
                phase1_equal=json.loads(json.dumps(old_scores))==phase1['audit']['scoring_result']['clauses'] and old_ref_signature(old)==old_ref_signature(phase1['audit']) and old_g==phase1['graph']
                date_signature=lambda report:[f for f in report['rule_flags'] if f['flag_type'] not in [x['flag_type'] for x in report['rule_flags'] if x['flag_type'].startswith('DANGLING_')]]
                date_clean=lambda report:[{k:v for k,v in f.items() if k!='flag_id'} for f in date_signature(report)]
                offsets_ok=all(parsed[r['char_start']:r['char_end']]==r['text'] for r in structure.references)
                offsets_ok &= all(parsed[s['heading_start']:s['heading_end']]==s['heading_text'] and parsed[s['identifier_start']:s['identifier_end']]==s['raw_identifier'] for s in structure.sections)
                parity.append(dict(case_id=case['case_id'],mode=mode,neural_clause_results_identical=old_scores==new_scores,
                    phase1_prediction_reproduced=phase1_equal,date_flags_identical=date_clean(old)==date_clean(new),
                    exact_source_preserved=structure.source_text==parsed and ''.join(u['text'] for u in structure.units)==parsed,
                    exact_structural_offsets=offsets_ok))
                stream.write(json.dumps(dict(case_id=case['case_id'],mode=mode,old=old_r,new=new_r,parity=parity[-1]),ensure_ascii=False)+'\n');stream.flush()
            print(case['case_id'],f'{time.monotonic()-start:.1f}s',flush=True)
    old_summary,old_decisions,old_clause_rows=helper.summarize(old_records)
    new_summary,new_decisions,new_clause_rows=helper.summarize(new_records)
    dump(out/'old_summary.json',old_summary);dump(out/'new_summary.json',new_summary)
    helper.write_csv(out/'old_decisions.csv',old_decisions);helper.write_csv(out/'new_decisions.csv',new_decisions)
    helper.write_csv(out/'new_clause_predictions.csv',new_clause_rows)
    changes=[]
    old_map={(r['case_id'],r['mode'],r['task']):r for r in old_decisions}
    for new in new_decisions:
        old=old_map[(new['case_id'],new['mode'],new['task'])]
        changed=old['prediction']!=new['prediction'];old_error=old['outcome'] in ['FP','FN'];new_error=new['outcome'] in ['FP','FN']
        entry=dict(case_id=new['case_id'],mode=new['mode'],task=new['task'],ground_truth=new['gold'],provenance=new['provenance'],
            original_prediction=old['prediction'],new_prediction=new['prediction'],prediction_changed=changed,
            original_outcome=old['outcome'],new_outcome=new['outcome'],corrected_error=old_error and not new_error,
            introduced_regression=not old_error and new_error)
        record=next(r for r in new_records if r['case']['case_id']==new['case_id'] and r['mode']==new['mode'])
        if changed:
            evidence=record['audit']['metadata']['reference_resolutions'] if new['task']=='reference_presence' else record['graph']['findings']
            entry['why_changed']='Shared exact-identity source-backed declarations/citations replace legacy regex/normalization; see per-reference status, source spans and target evidence.'
            entry['supporting_evidence']=evidence
        else:entry['why_changed']='Document-level prediction unchanged; structural/resolver evidence may still differ.'
        changes.append(entry)
    dump(out/'comparison.json',changes);dump(out/'parity.json',parity)
    coverage=[]
    for r in new_records:
        meta=r['audit']['metadata'];res=meta['reference_resolutions']
        coverage.append(dict(case_id=r['case']['case_id'],mode=r['mode'],provenance=r['case']['label_provenance'],
            sections=len(meta['structural_document']['sections']),references=len(res),
            statuses=dict(Counter(x['resolution_status'] for x in res)),reference_reviews=meta['reference_review_count'],
            graph_reviews=len(r['graph']['reviews']),graph_status=r['graph']['status']))
    dump(out/'coverage.json',coverage)
    summary=dict(analyses_per_implementation=len(parity),unique_development_documents=len(cases),
        neural_parity=sum(p['neural_clause_results_identical'] for p in parity),
        phase1_reproduced=sum(p['phase1_prediction_reproduced'] for p in parity),
        date_parity=sum(p['date_flags_identical'] for p in parity),
        exact_source_preservation=sum(p['exact_source_preserved'] for p in parity),
        exact_offset_preservation=sum(p['exact_structural_offsets'] for p in parity),
        corrected_decisions=sum(c['corrected_error'] for c in changes),introduced_regressions=sum(c['introduced_regression'] for c in changes),
        elapsed_seconds=time.monotonic()-start,all_inputs_exposed_development=True,independently_adjudicated=0,
        immutable_file_hashes_verified=len(set(immutable)),source_manifest_unchanged=manifest=={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in files})
    dump(out/'verification.json',summary);print(json.dumps(summary,indent=2))
    return 0 if all(all(p[k] for k in ['neural_clause_results_identical','phase1_prediction_reproduced','date_flags_identical','exact_source_preserved','exact_structural_offsets']) for p in parity) and summary['source_manifest_unchanged'] else 1

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--run-id',required=True);args=ap.parse_args()
    if Path(args.run_id).name!=args.run_id or args.run_id in ['.','..']:ap.error('Use a new simple run ID')
    raise SystemExit(main(args.run_id))
