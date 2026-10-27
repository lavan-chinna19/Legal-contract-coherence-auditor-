"""Phase 2 grammar, source preservation and conservative resolution contracts."""
import json
from pathlib import Path
from io import BytesIO
import pytest
from src.structure import parse_contract, resolve_references
from src.rules.dependency_graph import detect_dependencies
from src.rules.reference_checker import CrossReferenceChecker
from src.config import ClauseRecord

def parse(text):
    return parse_contract(doc_id='structure_test',source_text=text)

def assert_source(doc):
    source=doc.source_text
    assert ''.join(u['text'] for u in doc.units)==source
    for s in doc.sections:
        assert source[s['heading_start']:s['heading_end']]==s['heading_text']
        assert source[s['identifier_start']:s['identifier_end']]==s['raw_identifier']
        assert source[s['title_start']:s['title_end']]==s['title']
        assert source[s['char_start']:s['char_end']]==s['text']
    for r in doc.references:assert source[r['char_start']:r['char_end']]==r['text']

@pytest.mark.parametrize('citation',['Section 4 above applies here.','Section 4 shall apply.','Section 4 is binding.',
    'Section 4 provides the definition.','Exhibit Q supplies the specifications.'])
def test_sentence_start_is_not_a_heading(citation):
    doc=parse('Section 7. Payment\n'+citation)
    assert [s['identity'] for s in doc.sections]==['7']
    assert len(doc.references)==1
    assert resolve_references(doc)[0]['resolution_status']=='MISSING'
    assert_source(doc)

@pytest.mark.parametrize('citation',['Section 4','pursuant to Section 4','See Section 4, above',
    'the above Section 4','Section 4 above','Section 4 (above)'])
def test_supported_singular_and_punctuation(citation):
    doc=parse('Section 4. Meaning\nA definition.\nSection 8. Payment\nThe terms refer to '+citation+'.')
    resolutions=resolve_references(doc)
    assert len(resolutions)==1 and resolutions[0]['resolution_status']=='RESOLVED'
    assert not detect_dependencies([],structure=doc)['findings']
    assert_source(doc)

@pytest.mark.parametrize('citation',['Section 4 above','the above Section 4','Section 4, above'])
def test_wrong_above(citation):
    doc=parse('Section 8. Payment\nSee '+citation+'.\nSection 4. Meaning\nA definition.')
    graph=detect_dependencies([],structure=doc)
    assert len(graph['findings'])==1
    f=graph['findings'][0]
    assert doc.source_text[f['source_char_start']:f['source_char_end']]==f['reference']
    assert doc.source_text[f['target']['source_char_start']:f['target']['source_char_end']]==f['target']['excerpt']

@pytest.mark.parametrize('citation',['Section 4 below','the below Section 4','Section 4, below'])
def test_correct_below_and_nondirectional(citation):
    doc=parse('Section 8. Payment\nSee '+citation+'.\nSection 4. Meaning\nA definition.')
    assert detect_dependencies([],structure=doc)['status']=='NO_FINDINGS'
    assert detect_dependencies([],structure=parse(doc.source_text.replace(citation,'Section 4')))['status']=='NO_FINDINGS'

def test_hierarchy_and_relative_child():
    doc=parse('4. Services\n4.2 Delivery\n4.2.1 Timetable\n4.3 Payment\n(a) Fees\nSection 9. Reference\nSee Section 4.3(a).')
    nodes={s['identity']:s for s in doc.sections}
    assert set(nodes)=={'4','4.2','4.2.1','4.3','4.3(a)','9'}
    assert nodes['4.2']['parent_uid']==nodes['4']['section_uid']
    assert nodes['4.2.1']['parent_uid']==nodes['4.2']['section_uid']
    assert nodes['4.3(a)']['parent_uid']==nodes['4.3']['section_uid']
    assert resolve_references(doc)[0]['resolution_status']=='RESOLVED'
    assert_source(doc)

def test_exact_nested_identity_and_decimal_policy():
    doc=parse('Section 4.2(a). Fees\nSection 9. References\nSee Sections 4.2(a) and 4.2(b). See Section 4.02(a).')
    rs=resolve_references(doc)
    assert [(r['target_id'],r['resolution_status']) for r in rs]==[
        ('4.2(a)','RESOLVED'),('4.2(b)','MISSING'),('4.02(a)','MISSING')]
    assert_source(doc)

def test_relative_child_sentence_and_unsupported_word_identity():
    doc=parse('Section 4.2. Duties\n(a) The supplier must deliver.\nSection 9. Reference\nSee Section 4.2(a). See Section four.')
    assert any(s['identity']=='4.2(a)' for s in doc.sections)
    rs=resolve_references(doc)
    assert rs[0]['resolution_status']=='RESOLVED' and rs[1]['resolution_status']=='UNSUPPORTED'
    assert_source(doc)

def test_external_agreement_is_review_not_local_missing():
    doc=parse('Section 7. Payment\nSee Section 4 of the Master Agreement.')
    assert resolve_references(doc)[0]['resolution_status']=='UNSUPPORTED'

def test_heading_title_noun_is_not_a_reference():
    doc=parse('Section 7. Schedule of Fees\nThe fee is agreed.\nSection 9. Reference\nSee Section 7.')
    assert len(doc.references)==1
    assert resolve_references(doc)[0]['resolution_status']=='RESOLVED'

@pytest.mark.parametrize('citation',['Sections 4 and 5','Sections 4, 5 and 6','Sections 4, 5, and 6'])
def test_plural(citation):
    doc=parse('Section 4. First\nSection 5. Second\nSection 6. Third\nSection 8. References\nSee '+citation+'.')
    rs=resolve_references(doc)
    assert len(rs)==(2 if citation=='Sections 4 and 5' else 3)
    assert all(r['resolution_status']=='RESOLVED' for r in rs)

def test_inclusive_range_missing_middle():
    doc=parse('Section 4.1. First\nSection 4.3. Third\nSection 8. References\nSee Sections 4.1 through 4.3.')
    rs=resolve_references(doc)
    assert [(r['target_id'],r['resolution_status']) for r in rs]==[('4.1','RESOLVED'),('4.2','MISSING'),('4.3','RESOLVED')]
    assert_source(doc)

@pytest.mark.parametrize('reference',['Sections 4.3 through 4.1','Sections 4 through 9999999999',
    'Sections 4.1 through 5.3','Section 4..2','Section 4.2(b','Sections 4-5','Sections 4 or 5'])
def test_unsupported_syntax_abstains(reference):
    doc=parse('Section 4. Meaning\nSection 9. References\nSee '+reference+'.')
    rs=resolve_references(doc)
    assert rs and all(r['status']=='REVIEW_REQUIRED' for r in rs)
    assert not detect_dependencies([],structure=doc)['findings']

def test_duplicates_and_ambiguous_headings_abstain():
    doc=parse('Section 4. First\nSection 4. Second\nSection 9. References\nSee Section 4 above.')
    assert len([s for s in doc.sections if s['identity']=='4'])==2
    assert resolve_references(doc)[0]['resolution_status']=='AMBIGUOUS_TARGET'
    assert detect_dependencies([],structure=doc)['status']=='REVIEW_REQUIRED'
    uncertain=parse('Section 4 payment terms\nSection 9. Reference\nSee Section 4.')
    assert resolve_references(uncertain)[-1]['resolution_status']=='AMBIGUOUS_STRUCTURE'
    assert not CrossReferenceChecker().analyze_document([],structure=uncertain)['flags']

def test_bare_marker_cannot_establish_a_heading_or_absence():
    doc=parse('Section 4.\nSection 9. Reference\nSee Section 4.')
    assert [s['identity'] for s in doc.sections]==['9']
    assert doc.reviews and all(r['status']=='REVIEW_REQUIRED' for r in resolve_references(doc))

@pytest.mark.parametrize('line',['100 units','2026-06-01','4 dollars per month','2026. Inventory count','3.14 percent'])
def test_numbers_are_not_invented_headings(line):
    doc=parse('Section 9. Payment\n'+line+'\nThe parties agree.')
    assert [s['identity'] for s in doc.sections]==['9']
    assert_source(doc)

def test_comparisons_crlf_and_unicode_preserved():
    source='Preamble — €20\r\nSection 4. Payment\r\nIf cost < 100, see Section 99; if units > 20, deliver.\r\n'
    doc=parse(source)
    assert doc.source_text==source and resolve_references(doc)[0]['resolution_status']=='MISSING'
    assert_source(doc)

def test_clause_ids_and_coordinate_spaces():
    text='Section 4. Payment\nSee Section 99.'
    clause=ClauseRecord('original_id','source_doc',text,'test',0,200,200+len(text),'test')
    doc=parse_contract([clause])
    assert doc.coordinate_space=='assembled_clause_text'
    assert doc.references[0]['source_clause_id']=='original_id'
    assert_source(doc)

def test_empty_malformed_and_markup():
    assert parse('').sections==[] and resolve_references(parse(''))==[]
    with pytest.raises(ValueError):parse_contract(source_text=123)
    with pytest.raises(ValueError):parse_contract([{'text':None}])
    doc=parse('<p>Section 4. Heading</p><p>See Section 9.</p>')
    assert all(r['status']=='REVIEW_REQUIRED' for r in resolve_references(doc))
    assert_source(doc)

def test_bounded_parse_abstains_on_truncated_structure():
    from src.structure.parser import MAX_SECTIONS,MAX_SOURCE_CHARS
    source='\n'.join(f'Section {i}. Duties' for i in range(MAX_SECTIONS+1))+'\nSee Section 999999.'
    doc=parse(source)
    assert len(doc.sections)==MAX_SECTIONS
    assert all(r['resolution_status']=='UNSUPPORTED' for r in resolve_references(doc))
    assert_source(doc)
    with pytest.raises(ValueError):parse('x'*(MAX_SOURCE_CHARS+1))

def test_bounded_reference_count_retains_source():
    from src.structure.parser import MAX_REFERENCES
    doc=parse('Section 4. Duties\n'+'See Section 4. '*(MAX_REFERENCES+1))
    assert len(doc.references)==MAX_REFERENCES
    assert all(r['resolution_status']=='UNSUPPORTED' for r in resolve_references(doc))
    assert_source(doc)

@pytest.mark.parametrize('format',['txt','pdf','docx'])
def test_real_ingestion_preserves_structural_evidence(format):
    from src.api.ingestion import parse_document
    text='Section 8. Payment\nSee Section 4, above.\nSection 4. Terms\nIf price < 100, see Section 99; if volume > 20, deliver.'
    if format=='txt':data=text.encode('utf8')
    elif format=='docx':
        from docx import Document
        document=Document()
        for line in text.splitlines():document.add_paragraph(line)
        out=BytesIO();document.save(out);data=out.getvalue()
    else:
        from reportlab.pdfgen.canvas import Canvas
        out=BytesIO();canvas=Canvas(out)
        for i,line in enumerate(text.splitlines()):canvas.drawString(30,790-i*20,line)
        canvas.save();data=out.getvalue()
    extracted=parse_document(data,'test.'+format);doc=parse(extracted)
    assert_source(doc)
    assert any(r['target_id']=='99' and r['resolution_status']=='MISSING' for r in resolve_references(doc))
    assert len(detect_dependencies([],structure=doc)['findings'])==1

def test_existing_canonical_directional_cases():
    path=Path(__file__).parents[1]/'evaluations/phase1_detection_baseline_2026_10_26/corpus.json'
    cases=json.loads(path.read_text(encoding='utf8'))['cases'];checked=0
    for case in cases:
        if case['stratum']=='canonical' and 'directional_position' in case['task_labels']:
            doc=parse('\n\n'.join(case['clauses']))
            assert bool(detect_dependencies([],structure=doc)['findings'])==case['task_labels']['directional_position']
            checked+=1
    assert checked==13
