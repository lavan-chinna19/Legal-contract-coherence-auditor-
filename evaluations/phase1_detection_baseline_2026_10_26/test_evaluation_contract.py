"""Evaluation arithmetic and provenance checks; does not assert known detector errors away."""
import importlib.util
import json
from pathlib import Path
import pytest

BASE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('phase1_runner',BASE/'run_baseline.py')
runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)

def test_confusion_truth_table():
    assert [runner.confusion(a,b) for a,b in [(True,True),(False,True),(True,False),(False,False)]]==['TP','FP','FN','TN']

def test_unlabelled_is_not_true_negative():
    assert runner.confusion(None,False) is None
    assert runner.confusion('provisional',False) is None
    assert runner.confusion(False,None) is None

def test_metric_denominators():
    m=runner.metrics(['TP','TP','FP','FN','TN','TN','TN'])
    assert m['precision']==pytest.approx(2/3)
    assert m['recall']==pytest.approx(2/3)
    assert m['F1']==pytest.approx(2/3)
    assert m['false_positive_rate']==pytest.approx(1/4)
    assert m['n']==7

def test_undefined_metrics_remain_null():
    m=runner.metrics(['TN'])
    assert m['precision'] is None and m['recall'] is None and m['F1'] is None
    assert runner.metrics([])['false_positive_rate'] is None

def test_corpus_provenance_and_case_ids():
    corpus=json.loads((BASE/'corpus.json').read_text(encoding='utf-8'));cases=corpus['cases']
    assert len(cases)==70 and len({c['case_id'] for c in cases})==70
    assert sum(c['label_provenance']==runner.MECH for c in cases)==59
    assert all(not c['independently_adjudicated'] and c['split']=='EXPOSED_DEVELOPMENT' for c in cases)

def test_source_documents_match_authored_units():
    cases=json.loads((BASE/'corpus.json').read_text(encoding='utf-8'))['cases']
    for case in cases:
        assert (BASE/case['source_document']).read_text(encoding='utf-8')=='\n\n'.join(case['clauses'])

def test_provisional_examples_have_no_binary_legal_labels():
    cases=json.loads((BASE/'corpus.json').read_text(encoding='utf-8'))['cases']
    assert all(not c['task_labels'] for c in cases if c['label_provenance']!=runner.MECH)

def test_proxy_labels_describe_operations_only():
    cases=json.loads((BASE/'corpus.json').read_text(encoding='utf-8'))['cases']
    order=[c for c in cases if c['case_id'].startswith('O')]
    assert len(order)==12 and sum(c['task_labels']['order_changed_proxy'] for c in order)==9
    assert all(set(c['task_labels'])=={'order_changed_proxy'} for c in order)

def test_ambiguous_references_not_direction_negatives():
    cases=json.loads((BASE/'corpus.json').read_text(encoding='utf-8'))['cases']
    for c in cases:
        if c['case_id'] in ['R10','R11','R12','R13','R14','R18','R19','R25']:
            assert 'directional_position' not in c['task_labels']

def test_frozen_manifest():
    runner.verify_manifest()

def test_repeatability_comparison_normalizes_only_evidence_sets():
    analysis_spec=importlib.util.spec_from_file_location('phase1_analysis',BASE/'analyze_results.py')
    analysis=importlib.util.module_from_spec(analysis_spec);analysis_spec.loader.exec_module(analysis)
    a={'declared_targets':[{'target_id':'i'},{'target_id':'1'}],'scores':[.1,.2],'timestamp':'first'}
    b={'declared_targets':[{'target_id':'1'},{'target_id':'i'}],'scores':[.1,.2],'timestamp':'second'}
    assert analysis.stable(a)==analysis.stable(b)
    b['scores']=[.2,.1]
    assert analysis.stable(a)!=analysis.stable(b)

def test_saved_runs_have_full_case_mode_coverage():
    for run in ['frozen_primary','frozen_replication']:
        records=[json.loads(line) for line in (BASE/'results'/run/'predictions.jsonl').read_text(encoding='utf-8').splitlines()]
        assert len(records)==148 and len({(r['case']['case_id'],r['mode']) for r in records})==148
        assert all(r['status']=='OK' for r in records)
        assert sum(r['mode']=='authored' for r in records)==70
        assert sum(r['mode']=='txt' for r in records)==70
