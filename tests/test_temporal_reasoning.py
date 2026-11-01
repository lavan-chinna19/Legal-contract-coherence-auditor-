"""Temporal arithmetic is a textual development task, not expert legal adjudication."""
import json
from pathlib import Path
import pytest
from src.temporal import analyze_temporal
from src.temporal.extraction import parse_date

BASE=Path(__file__).resolve().parents[1]/'evaluations/phase3_temporal_reasoning_2026_10_26'
CASES=[c for name in ['new_cases.json','challenge_cases.json']
       for c in json.loads((BASE/name).read_text(encoding='utf8'))['cases']]

@pytest.mark.parametrize('case',CASES,ids=lambda c:c['case_id'])
def test_exposed_mechanical_examples_and_exact_source(case):
    source=case['text'];result=analyze_temporal(source_text=source,doc_id='unit')
    meta=result['metadata']
    if case['confirmed_conflict_gold'] is not None:
        assert bool(meta['confirmed_conflict_count'])==case['confirmed_conflict_gold']
    for s in meta['statements']:
        assert source[s['char_start']:s['char_end']]==s['raw_text']
        if s['raw_date']:assert source[s['date_start']:s['date_end']]==s['raw_date']
        assert s['coordinate_space']=='original_extracted_text'
    for flag in result['flags']:
        assert flag.evidence['decision_category'] in ['CONFIRMED_TEMPORAL_CONFLICT','POTENTIAL_INCONSISTENCY']

@pytest.mark.parametrize('raw,iso,error',[
    ('2024-02-29','2024-02-29',None),('2026-02-30',None,'INVALID_CALENDAR_DATE'),
    ('03/04/2026',None,'AMBIGUOUS_NUMERIC_DATE'),('13/04/2026','2026-04-13',None),
    ('January 1st, 2026','2026-01-01',None),('1 day of Jan 2026','2026-01-01',None)])
def test_explicit_date_parsing(raw,iso,error):assert parse_date(raw)==(iso,error)

def test_no_calendar_or_trigger_is_invented():
    result=analyze_temporal(source_text='Buyer shall pay Invoice Alpha within 10 business days after receipt of Invoice Alpha.')
    assert not result['flags']
    s=result['metadata']['statements'][0]
    assert s['absolute_date'] is None and s['parsing_status']=='UNSUPPORTED'
    assert 'BUSINESS_CALENDAR_UNPROVIDED' in s['uncertainty']

def test_overlap_is_potential_not_confirmed():
    source=('Invoice Alpha is received on 2026-01-01. '
        'Buyer shall pay Invoice Alpha within 10 calendar days after receipt of Invoice Alpha. '
        'Buyer shall pay Invoice Alpha within 20 calendar days after receipt of Invoice Alpha.')
    result=analyze_temporal(source_text=source)
    assert result['metadata']['potential_inconsistency_count']>0
    assert result['metadata']['confirmed_conflict_count']==0
    assert any(d['details'].get('feasible_upper')==10 for d in result['decisions'])

def test_source_section_and_party_are_retained():
    result=analyze_temporal(source_text='Section 7. Event\nFor Buyer, Event Completion occurs on 2026-06-01.')
    s=result['metadata']['statements'][0]
    assert s['section_identity']=='7' and s['section_uid']
    assert s['party_context']=='buyer' and s['actor'] is None

@pytest.mark.parametrize('quantity,value',[('twenty-one',21),('seventy nine',79),('ninety-nine',99),('thirteen',13),('90',90)])
def test_compound_duration(quantity,value):
    r=analyze_temporal(source_text=f'Buyer shall pay Invoice Alpha within {quantity} calendar days after receipt of Invoice Alpha.')
    s=next(s for s in r['statements'] if s.kind=='DURATION')
    assert s.duration_value==value and s.upper_offset==value

def test_limit_abstains_and_never_emits_partial_conflicts():
    source=' '.join(f'Event Completion occurs on 2026-06-{1+i%20:02d}.' for i in range(501))
    result=analyze_temporal(source_text=source)
    assert not result['flags'] and result['metadata']['status']=='UNSUPPORTED'

def test_unicode_crlf_preserved():
    source='Section 1. Term\r\nCafé: Effective Date is 2026-12-01.\r\nSection 2. Term\r\nExpiration Date is 2026-01-01.'
    r=analyze_temporal(source_text=source)
    assert r['metadata']['confirmed_conflict_count']==1
    assert all(source[s.char_start:s.char_end]==s.raw_text for s in r['statements'])

@pytest.mark.parametrize('source',[
    'Service does not run from 2026-06-10 to 2026-06-01.',
    'Effective Date is either 2026-06-01 or 2026-07-01.',
    'Effective Date is before 2026-07-01. Expiration Date is 2026-06-01.',
    'If approved, Milestone Alpha occurs on 2026-07-01. Milestone Beta occurs on 2026-06-01. Milestone Alpha must occur before Milestone Beta.',
])
def test_no_unconditional_confirmation_from_incomplete_constraints(source):
    r=analyze_temporal(source_text=source)
    assert not r['metadata']['confirmed_conflict_count']
    assert r['metadata']['review_count']+r['metadata']['unsupported_count']>0

def test_modal_term_endpoint_is_not_responsible_party():
    source='The effective date of this Agreement is January 1, 2025 and the termination date shall be December 31, 2025.'
    r=analyze_temporal(source_text=source)
    assert not r['flags']
    assert {s.event for s in r['statements']}=={'effective date','termination date'}
    assert all(s.actor is None for s in r['statements'])

def test_existing_msa_has_no_false_conflicts_but_preserves_uncertainty():
    from src.redteam.fixtures import SYNTHETIC_FIXTURE_REGISTRY
    source='\n'.join(c.text for c in SYNTHETIC_FIXTURE_REGISTRY['SYNTH_DOC_01_MSA']())
    r=analyze_temporal(source_text=source)
    assert not r['flags'] and not r['metadata']['confirmed_conflict_count']
    assert r['metadata']['review_count']+r['metadata']['unsupported_count']>0
