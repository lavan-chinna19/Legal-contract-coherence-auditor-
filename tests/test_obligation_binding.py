"""Pre-evaluation development/unit tests; never import the frozen evaluation split."""
from pathlib import Path
import json
import pytest
from src.obligations import analyze_bindings

BASE=Path(__file__).resolve().parents[1]/'evaluations/phase4a_obligation_binding_2026_10_28'
DEV=json.loads((BASE/'development.json').read_text(encoding='utf8'))['cases']

def selected(result,case):
    left=[r for r in result['records'] if r['section_identity']==case['left_section']][case['left_index']]
    right=[r for r in result['records'] if r['section_identity']==case['right_section']][case['right_index']]
    return next(p for p in result['pairs'] if {p['left_id'],p['right_id']}=={left['record_id'],right['record_id']})

@pytest.mark.parametrize('case',DEV,ids=lambda c:c['case_id'])
def test_development_pairs(case):
    result=analyze_bindings(source_text=case['text'],doc_id='development')
    if case['gold_state'] is not None:assert selected(result,case)['status']==case['gold_state']
    for record in result['records']:
        assert case['text'][record['char_start']:record['char_end']]==record['raw_text']
        for spans in record['evidence'].values():
            for span in spans:assert case['text'][span['char_start']:span['char_end']]==span['text']

@pytest.mark.parametrize('text',[
    'Buyer shall pay Invoice Alpha and deliver Report Bravo.',
    'Buyer shall pay Invoice Alpha and Invoice Bravo.',
    'It shall pay Invoice Alpha.',
    'Buyer shall pay the invoice.',
    'Buyer shall pay Invoice Alpha after receipt.',
    'Buyer shall pay Invoice Alpha to them.',
])
def test_incomplete_binding_never_becomes_match(text):
    source='Section 1. Duty\n'+text+'\nSection 2. Duty\nBuyer shall pay Invoice Alpha.'
    result=analyze_bindings(source_text=source)
    assert all(p['status']!='MATCHED' for p in result['pairs'])

def test_relative_timing_is_not_used_to_classify_conflicts():
    source='Section 1. Duty\nBuyer shall pay Invoice Alpha within 10 calendar days.\nSection 2. Duty\nBuyer must remit Invoice Alpha within 20 calendar days.'
    result=analyze_bindings(source_text=source)
    assert result['pairs'][0]['status']=='MATCHED'
    assert 'conflict' not in result['pair_counts']

def test_empty_and_no_modal_text():
    for text in ['', 'Section 1. Heading\nThe term is described here.']:
        result=analyze_bindings(source_text=text)
        assert not result['pairs'] and not result['records']
        assert result['status']=='NO_SUPPORTED_OBLIGATIONS'

def test_long_input_limits_abstain():
    source='\n'.join(f'Section {i+1}. Duty\nBuyer shall pay Invoice Alpha.' for i in range(105))
    result=analyze_bindings(source_text=source)
    assert not result['complete'] and result['record_count']==100
    assert result['evaluated_pair_count']==1000
    assert result['pair_counts']=={'UNSUPPORTED':1000}

def test_assembled_coordinates_are_not_original_coordinates():
    result=analyze_bindings([dict(clause_id='c1',text='Buyer shall pay Invoice Alpha.')])
    assert result['coordinate_space']=='assembled_clause_text'

def test_unicode_and_crlf_exact_evidence():
    source='Section 7. Duty\r\nCafé: Buyer shall pay Invoice Alpha.\r\nSection 9. Duty\r\nBuyer must pay Invoice Alpha.'
    result=analyze_bindings(source_text=source)
    for r in result['records']:
        assert source[r['char_start']:r['char_end']]==r['raw_text']
        for spans in r['evidence'].values():
            for s in spans:assert source[s['char_start']:s['char_end']]==s['text']

def test_markup_abstains_without_claiming_layout_binding():
    source='<p>Buyer shall pay Invoice Alpha.</p><p>Buyer shall pay Invoice Alpha.</p>'
    result=analyze_bindings(source_text=source)
    assert not result['complete'] and result['status']=='UNSUPPORTED'
    assert all(p['status']=='UNSUPPORTED' for p in result['pairs'])
