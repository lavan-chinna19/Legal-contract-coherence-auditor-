"""Frozen, offline development evaluation. Never modifies production detector code or assets."""
from pathlib import Path
from collections import defaultdict, Counter
from io import BytesIO
from datetime import datetime, timezone
import argparse, csv, hashlib, importlib.metadata, json, os, platform, subprocess, sys, time, traceback

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
MECH = 'MECHANICALLY_VERIFIABLE_SYNTHETIC'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def dump(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, default=str)+'\n', encoding='utf-8')

def frozen_files():
    files = [BASE/'corpus.json', BASE/'PROTOCOL.md', BASE/'build_dataset.py', Path(__file__)]
    files += sorted((BASE/'cases').glob('*.txt'))
    files += sorted(p for p in (ROOT/'src').rglob('*.py') if '__pycache__' not in p.parts)
    files += [ROOT/p for p in ['models/coherence_classifier.pt', 'fixtures/ledgar_centroids.npz',
                              'fixtures/conformal_calibration_fixture.json']]
    if (ROOT/'models/thresholds.json').exists(): files.append(ROOT/'models/thresholds.json')
    return {str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in files}

def verify_manifest():
    expected=json.loads((BASE/'frozen_manifest.json').read_text(encoding='utf-8'))['files']
    actual=frozen_files()
    if actual != expected: raise RuntimeError('Frozen inputs/source hash mismatch; do not overwrite this baseline.')

def confusion(gold, prediction):
    if type(gold) is not bool or type(prediction) is not bool: return None
    return ('TP' if prediction else 'FN') if gold else ('FP' if prediction else 'TN')

def metrics(outcomes):
    counts=Counter(outcomes)
    tp,fp,fn,tn=[counts[k] for k in ['TP','FP','FN','TN']]
    ratio=lambda n,d: n/d if d else None
    return dict(n=tp+fp+fn+tn,TP=tp,FP=fp,FN=fn,TN=tn,
                precision=ratio(tp,tp+fp),recall=ratio(tp,tp+fn),F1=ratio(2*tp,2*tp+fp+fn),
                false_positive_rate=ratio(fp,fp+tn))

def write_csv(path, rows):
    if not rows:return
    with path.open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)

def summarize(records):
    decisions=[]; groups=defaultdict(list); clauses=[]
    for r in records:
        if r['status']!='OK':continue
        case=r['case']; report=r['audit']; graph=r['graph']; scores=report['scoring_result']['clauses']
        predictions={'reference_presence':bool(report['metadata']['ref_flags_count']),
            'directional_position':bool(graph['findings']),
            'date_chronology':bool(report['metadata']['date_flags_count']),
            'order_proxy_channel_a':any(c['channel_a_evidence']['is_ood'] for c in scores),
            'order_proxy_channel_b':any(c['channel_b_score']>=r['b_diagnostic_threshold'] for c in scores),
            'order_proxy_ensemble':any(c['is_anomaly'] for c in scores)}
        for task,gold in case['task_labels'].items():
            tasks=['order_proxy_channel_a','order_proxy_channel_b','order_proxy_ensemble'] if task=='order_changed_proxy' else [task]
            for name in tasks:
                if name not in predictions or case['label_provenance']!=MECH:continue
                pred=predictions[name];outcome=confusion(gold,pred)
                row=dict(case_id=case['case_id'],mode=r['mode'],task=name,stratum=case['stratum'],
                    provenance=case['label_provenance'],gold=gold,prediction=pred,outcome=outcome,
                    graph_status=graph['status'],graph_review_count=len(graph['reviews']),
                    source_document=case['source_document'])
                decisions.append(row)
                groups[(r['mode'],name,'all_predefined')].append(outcome)
                groups[(r['mode'],name,case['stratum'])].append(outcome)
        for c,source in zip(scores,r['segments']):
            clauses.append(dict(case_id=case['case_id'],mode=r['mode'],clause_id=c['clause_id'],
                source_document=case['source_document'],text=source['text'],char_start=source['char_start'],
                char_end=source['char_end'],channel_a=c['channel_a_score'],
                raw_centroid_distance=c['channel_a_evidence']['centroid_distance'],
                is_ood=c['channel_a_evidence']['is_ood'],channel_b=c['channel_b_score'],
                incoming_probability=c['channel_b_evidence']['incoming_prob'],outgoing_probability=c['channel_b_evidence']['outgoing_prob'],
                combined=c['combined_score'],severity=c['severity'],ml_flag=c['is_anomaly']))
    result={'metrics':[dict(mode=m,task=t,stratum=s,**metrics(v)) for (m,t,s),v in sorted(groups.items())],
        'analyses':len(records),'successful_analyses':sum(r['status']=='OK' for r in records),
        'failures':[dict(case_id=r['case']['case_id'],mode=r['mode'],error=r.get('error')) for r in records if r['status']!='OK'],
        'segmentation_mismatches':[dict(case_id=r['case']['case_id'],mode=r['mode'],**r['segmentation']) for r in records
            if r['status']=='OK' and r['mode']!='authored' and not r['segmentation']['authored_units_match']],
        'offset_failures':[dict(case_id=r['case']['case_id'],mode=r['mode']) for r in records
            if r['status']=='OK' and not r['segmentation']['offsets_valid']],
        'graph_review_policy':[dict(case_id=r['case']['case_id'],mode=r['mode'],
            expected=True,observed=bool(r['graph']['reviews']),status=r['graph']['status']) for r in records
            if r['status']=='OK' and r['case']['expected_graph_review'] is True],
        'errors':[d for d in decisions if d['outcome'] in ('FP','FN')],
        'provisional_cases':[dict(case_id=r['case']['case_id'],mode=r['mode'],ml_flags=r['audit']['ml_anomaly_count'],
             rule_flags=[f['flag_type'] for f in r['audit']['rule_flags']],graph_status=r['graph']['status'])
             for r in records if r['status']=='OK' and r['case']['label_provenance']!=MECH]}
    return result,decisions,clauses

def encoded_document(case, mode):
    text='\n\n'.join(case['clauses'])
    if mode=='txt':return text.encode('utf-8')
    if mode=='docx':
        from docx import Document
        doc=Document()
        for line in text.splitlines():doc.add_paragraph(line)
        stream=BytesIO();doc.save(stream);return stream.getvalue()
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    from xml.sax.saxutils import escape
    stream=BytesIO();styles=getSampleStyleSheet();story=[]
    for line in text.splitlines():story.append(Paragraph(escape(line),styles['Normal']) if line else Spacer(1,10))
    SimpleDocTemplate(stream).build(story);return stream.getvalue()

def execute(run_id, selected=None):
    verify_manifest()
    run_dir=BASE/'results'/run_id
    run_dir.mkdir(parents=True,exist_ok=False)
    runtime=BASE/'runtime'/run_id;runtime.mkdir(parents=True,exist_ok=False)
    os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',LEXAUDIT_ALLOW_MODEL_DOWNLOAD='0',
        LEXAUDIT_EMBEDDINGS_CACHE_DIR=str(runtime/'vectors'),LEXAUDIT_FEEDBACK_DB_PATH=str(runtime/'feedback.sqlite'),
        OMP_NUM_THREADS='2',MKL_NUM_THREADS='2',TOKENIZERS_PARALLELISM='false')
    sys.path.insert(0,str(ROOT))
    from src.api.dependencies import get_unified_auditor,get_ml_segmenter
    from src.api.ingestion import parse_document
    from src.rules.dependency_graph import detect_dependencies
    from src.config import ClauseRecord, THRESHOLDS_PATH
    import torch
    torch.set_num_threads(2)
    auditor=get_unified_auditor();segmenter=get_ml_segmenter();scorer=auditor.scorer
    assert scorer.channel_a.centroid_matrix is not None,'Missing actual centroid matrix'
    assert scorer.calibrator and scorer.calibrator.is_fitted,'Actual calibration state unavailable'
    corpus=json.loads((BASE/'corpus.json').read_text(encoding='utf-8'))
    cases=[c for c in corpus['cases'] if not selected or c['case_id'] in selected]
    assert cases and (not selected or len(cases)==len(selected))
    versions={}
    for name in ['torch','numpy','sentence-transformers','transformers','spacy','dateparser','crepes','pdfplumber','python-docx','reportlab']:
        try:versions[name]=importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:versions[name]=None
    nlp=getattr(auditor.reference_checker,'nlp',None)
    metadata=dict(started_utc=datetime.now(timezone.utc).isoformat(),python=sys.version,platform=platform.platform(),
        git_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),versions=versions,
        selected_case_ids=selected,manifest_sha256=sha(BASE/'frozen_manifest.json'),
        model_name=scorer.channel_a.embedder.model_name,centroid_count=len(scorer.channel_a.centroid_names),
        checkpoint=scorer.channel_b.coherence_model.checkpoint_path,alpha=scorer.alpha,
        ranker=vars(scorer.severity_ranker),ood_raw_distance_threshold=scorer.channel_a.ood_threshold,
        unused_b_coherence_threshold=scorer.channel_b.coherence_threshold,
        threshold_file=str(THRESHOLDS_PATH),threshold_file_exists=THRESHOLDS_PATH.exists(),
        calibration=dict(target_coverage=scorer.calibrator.target_coverage,n=scorer.calibrator.n_calibration_samples,
            quantile=scorer.calibrator.conformal_quantile,source=scorer.calibrator.calibration_source),
        spacy_meta=nlp.meta if nlp else None,thread_count=torch.get_num_threads(),offline=True)
    dump(run_dir/'metadata.json',metadata)
    records=[];start=time.monotonic()
    with (run_dir/'predictions.jsonl').open('w',encoding='utf-8') as output:
        for case in cases:
            modes=['authored','txt']+(['pdf','docx'] if case['case_id'] in ['R02','T02','T13','S04'] else [])
            for mode in modes:
                r=dict(case=case,mode=mode,status='FAILED',b_diagnostic_threshold=scorer.severity_ranker.med_single_threshold)
                try:
                    doc_id=f"baseline_{case['case_id']}_{mode}"
                    source='\n\n'.join(case['clauses'])
                    if mode=='authored':
                        parsed=source;normalized=source;segments=[];offset=0
                        for i,text in enumerate(case['clauses']):
                            segments.append(ClauseRecord(f'{doc_id}_{i}',doc_id,text,'controlled_unit',i,offset,offset+len(text),'synthetic_development'))
                            offset+=len(text)+2
                    else:
                        content=encoded_document(case,mode)
                        if mode!='txt':
                            (run_dir/'transport_inputs').mkdir(exist_ok=True)
                            (run_dir/'transport_inputs'/f"{case['case_id']}.{mode}").write_bytes(content)
                        parsed=parse_document(content,f"{case['case_id']}.{mode}")
                        normalized=segmenter._clean_html(parsed);segments=segmenter.segment(parsed,doc_id=doc_id)
                    r.update(extracted_text=parsed,normalized_text=normalized,segments=[c.to_dict() for c in segments],
                        segmentation=dict(expected=len(case['clauses']),observed=len(segments),
                            authored_units_match=[c.text for c in segments]==case['clauses'],
                            offsets_valid=all(normalized[c.char_start:c.char_end]==c.text for c in segments),
                            normalization_changed_text=parsed!=normalized))
                    r['audit']=auditor.audit_document(segments,doc_id=doc_id).to_dict()
                    r['graph']=detect_dependencies([c.to_dict() for c in segments]);r['status']='OK'
                except Exception as e:r.update(error=f'{type(e).__name__}: {e}',traceback=traceback.format_exc())
                output.write(json.dumps(r,ensure_ascii=False,default=str)+'\n');output.flush();records.append(r)
            print(f"{case['case_id']}: {', '.join(x['mode']+'='+x['status'] for x in records if x['case']['case_id']==case['case_id'])} ({time.monotonic()-start:.1f}s)",flush=True)
    probes=[]
    from fastapi import HTTPException
    from reportlab.pdfgen.canvas import Canvas
    blank=BytesIO();canvas=Canvas(blank);canvas.showPage();canvas.save()
    for name,content in [('invalid.txt',b'\xff\xfe'),('damaged.pdf',b'%PDF-invalid'),('damaged.docx',b'invalid'),('blank.pdf',blank.getvalue())]:
        try:parse_document(content,name);probes.append(dict(name=name,expected_status=400,observed_status=200,passed=False))
        except HTTPException as e:probes.append(dict(name=name,expected_status=400,observed_status=e.status_code,passed=e.status_code==400,detail=e.detail))
    dump(run_dir/'parser_probes.json',probes)
    summary,decisions,clause_rows=summarize(records)
    dump(run_dir/'summary.json',summary);write_csv(run_dir/'decisions.csv',decisions);write_csv(run_dir/'clause_predictions.csv',clause_rows)
    model=scorer.channel_a.embedder._model
    metadata.update(completed_utc=datetime.now(timezone.utc).isoformat(),elapsed_seconds=time.monotonic()-start,
        actual_max_sequence_length=model.max_seq_length if model else None,
        actual_embedding_dimension=model.get_sentence_embedding_dimension() if model else None,
        parameters_frozen=all(not p.requires_grad for p in model.parameters()) if model else None,
        bert_training_mode=model.training if model else None,head_training_mode=scorer.channel_b.coherence_model._model.training)
    dump(run_dir/'metadata.json',metadata)
    verify_manifest()
    print(json.dumps(dict(analyses=summary['analyses'],successful=summary['successful_analyses'],failures=summary['failures'],parser_probes=probes),indent=2),flush=True)
    return 1 if summary['failures'] or not all(p['passed'] for p in probes) else 0

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--freeze',action='store_true');ap.add_argument('--run-id');ap.add_argument('--case-ids',nargs='*');args=ap.parse_args()
    if args.freeze:
        target=BASE/'frozen_manifest.json'
        if target.exists():raise FileExistsError('Manifest already frozen')
        dump(target,dict(frozen_before_predictions=True,files=frozen_files()))
        print('Input/source manifest frozen; no detector executed.')
    else:
        if not args.run_id:ap.error('--run-id required')
        if Path(args.run_id).name!=args.run_id or args.run_id in ('.','..'):ap.error('Use a simple new run directory name')
        sys.exit(execute(args.run_id,args.case_ids))
