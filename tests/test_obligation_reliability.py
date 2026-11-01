"""Focused Phase 4A.1 repairs, authored source-backed examples, no legal truth labels."""
from pathlib import Path
import json
import pytest
from src.obligations import analyze_bindings

BASE=Path(__file__).resolve().parents[1]/'evaluations/phase4a1_reliability_2026_10_28'
CASES=json.loads((BASE/'focused_cases.json').read_text())['cases']

@pytest.mark.parametrize('case',CASES,ids=lambda c:c['case_id'])
def test_focused_repairs(case):
    out=analyze_bindings(source_text=case['text'])
    assert len(out['records'])==2
    a,b=out['records'];pair=out['pairs'][0]
    assert pair['status']==case['gold_state']
    assert a['actors']==case['actors_left']
    assert b['actors']==case['actors_right']
    assert pair['actor_action_relationship']==case['expected_actor_action_relationship']
    if case['expected_instance']:
        assert a['event_instance']==b['event_instance']==case['expected_instance']
    if case['case_id'] in ['notification_type_only','generic_event_type','recurrence']:
        assert a['event_instance'] is b['event_instance'] is None
    for record in out['records']:
        assert case['text'][record['char_start']:record['char_end']]==record['raw_text']
        for spans in record['evidence'].values():
            for span in spans:assert case['text'][span['char_start']:span['char_end']]==span['text']

def test_joint_subject_does_not_consume_a_second_explicit_obligation():
    source='Section 1. Duty\nProvider and Subcontractor shall pay Invoice Alpha and Buyer shall deliver Report Bravo.'
    out=analyze_bindings(source_text=source)
    assert len(out['records'])==2
    assert out['records'][0]['actors']==['provider','subcontractor']
    assert out['records'][1]['actors']==['buyer']

def test_actor_order_is_not_identity_order():
    source='Section 1. Duty\nBuyer & Seller shall pay Invoice Alpha.\nSection 2. Duty\nInvoice Alpha must be paid by Seller and Buyer.'
    out=analyze_bindings(source_text=source)
    assert out['pairs'][0]['status']=='MATCHED'

def test_old_passive_and_joint_examples_are_repaired():
    old=BASE.parent/'phase4a_obligation_binding_2026_10_28'
    cases=json.loads((old/'evaluation.json').read_text())['cases']
    for c in cases:
        if c['case_id'].endswith('_passive_identity'):
            assert analyze_bindings(source_text=c['text'])['pairs'][0]['status']=='MATCHED'
        if c['case_id'].endswith('_coordinated_subject'):
            out=analyze_bindings(source_text=c['text'])
            assert out['records'][1]['actors']==['purchaser','vendor']
            assert out['pairs'][0]['status']=='DIFFERENT'

def test_trigger_instance_is_not_invented_as_notification_occurrence():
    source='Section 1. Duty\nProvider shall notify Customer after receipt of Invoice Alpha for occurrence 1.\nSection 2. Duty\nCustomer shall be notified by Provider after receipt of Invoice Alpha for occurrence 1.'
    out=analyze_bindings(source_text=source)
    assert all(r['event_instance'] is None and r['object'] is None for r in out['records'])
    assert out['pairs'][0]['status']=='UNCERTAIN'

def test_definition_conjunction_does_not_create_joint_responsible_parties():
    source='Capitalized terms used herein and not otherwise defined shall have the meanings ascribed in the Agreement.'
    out=analyze_bindings(source_text=source)
    assert all(r['actor'] is None and r['actors']==[] for r in out['records'])
