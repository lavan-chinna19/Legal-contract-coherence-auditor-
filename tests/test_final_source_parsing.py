"""Final source-consumption regressions, not a new labelled research benchmark."""
import pytest
from src.structure import parse_contract,resolve_references
from src.obligations import analyze_bindings

def assert_exact(source,structure,result):
    assert structure.source_text==source
    assert ''.join(u['text'] for u in structure.units)==source
    for section in structure.sections:
        assert source[section['char_start']:section['char_end']]==section['text']
        assert source[section['identifier_start']:section['identifier_end']]==section['raw_identifier']
    for record in result['records']:
        assert source[record['char_start']:record['char_end']]==record['raw_text']
        for spans in record['evidence'].values():
            for span in spans:assert source[span['char_start']:span['char_end']]==span['text']

@pytest.mark.parametrize('heading',[
    'Section 1. Payment.', '1. Payment.', 'Section 1.2(a). Payment.',
    'Article IV. Payment.', '   Section 1. Payment.',
])
def test_same_line_body_is_not_discarded(heading):
    source=heading+' Buyer shall pay Invoice Alpha.'
    structure=parse_contract(source_text=source);result=analyze_bindings(source_text=source)
    assert len(result['records'])==1
    record=result['records'][0]
    assert record['actor']=='buyer' and record['action']=='PAY'
    assert record['object']=='invoice alpha'
    assert record['section_uid']==structure.sections[0]['section_uid']
    assert_exact(source,structure,result)

def test_nested_relative_heading_body_and_hierarchy():
    source=('Section 4. Services\n'
        'Section 4.2. Delivery. Provider shall deliver Report Bravo.\n'
        '(a) Customer shall pay Invoice Alpha.\n'
        'Section 4.3. Notice\nProvider shall notify Customer about Notice Cedar.')
    structure=parse_contract(source_text=source);result=analyze_bindings(source_text=source)
    assert len(result['records'])==3
    assert [r['section_identity'] for r in result['records']]==['4.2','4.2(a)','4.3']
    nodes={s['identity']:s for s in structure.sections}
    assert nodes['4.2']['parent_uid']==nodes['4']['section_uid']
    assert nodes['4.2(a)']['parent_uid']==nodes['4.2']['section_uid']
    assert_exact(source,structure,result)

def test_multiline_body_remains_available_with_inline_body():
    source=('Section 1. Payment. Buyer shall pay Invoice Alpha.\n'
        'Seller shall deliver Report Bravo.\n'
        'Section 2. Notice\nCustomer shall be notified by Provider about Notice Cedar.')
    structure=parse_contract(source_text=source);result=analyze_bindings(source_text=source)
    assert len(result['records'])==3
    assert [r['section_identity'] for r in result['records']]==['1','1','2']
    assert_exact(source,structure,result)

def test_inline_citation_is_not_a_new_heading():
    source=('Section 1. Duty. Buyer shall pay Invoice Alpha under Section 4.\n'
        'Section 4. Other\nProvider shall deliver Report Bravo.')
    structure=parse_contract(source_text=source);result=analyze_bindings(source_text=source)
    assert [s['identity'] for s in structure.sections]==['1','4']
    assert len(result['records'])==2
    assert any(r['target_id']=='4' and r['resolution_status']=='RESOLVED' for r in resolve_references(structure))
    assert_exact(source,structure,result)

@pytest.mark.parametrize('line',[
    '1 Payment Buyer shall pay Invoice Alpha.',
    '(a) Buyer shall pay Invoice Alpha.',
    'Section 4.2(b Buyer shall pay Invoice Alpha.',
])
def test_ambiguous_boundaries_retain_source_and_review(line):
    source=line+'\nSection 9. Other\nProvider shall deliver Report Bravo.'
    structure=parse_contract(source_text=source);result=analyze_bindings(source_text=source)
    assert any('pay Invoice Alpha' in r['raw_text'] for r in result['records'])
    assert structure.reviews or any(r['uncertainty'] or r['unsupported'] for r in result['records'])
    assert_exact(source,structure,result)

def test_unicode_and_crlf_inline_source():
    source='Section 1. Café. Provider shall deliver Report Bravo.\r\nSection 2. Payment. Buyer shall pay Invoice Alpha.'
    structure=parse_contract(source_text=source);result=analyze_bindings(source_text=source)
    assert len(result['records'])==2
    assert_exact(source,structure,result)

def test_large_inline_input_advertises_existing_limits():
    source='\n'.join(f'Section {i+1}. Duty. Buyer shall pay Invoice Alpha.' for i in range(105))
    result=analyze_bindings(source_text=source)
    assert not result['complete'] and 'RECORD_LIMIT' in result['issues']
    assert result['pair_counts']=={'UNSUPPORTED':1000}
