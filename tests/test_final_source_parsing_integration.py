"""Real same-line source-body ingestion, local models, saved evidence and renderers."""
from copy import deepcopy
from io import BytesIO
import pytest
from tests.test_temporal_integration import client,analyze,OWNER,OTHER
from src.api import jobs

SOURCE=('Section 1. Services\n'
        'Section 1.1. Payment. Provider shall pay Invoice Alpha.\n'
        '(a) Provider shall deliver Report Bravo.\n'
        'Section 2. Duty. Invoice Alpha must be paid by Provider. See Section 1.1.')

@pytest.mark.parametrize('fmt',['txt','pdf','docx'])
def test_inline_body_real_application_workflow(client,fmt):
    _,job_id,source,before=analyze(client,SOURCE,fmt)
    structure=before['metadata']['structural_document']
    assert ''.join(u['text'] for u in structure['units'])==source
    nodes={n['identity']:n for n in structure['sections']}
    assert set(nodes)=={'1','1.1','1.1(a)','2'}
    assert nodes['1.1']['parent_uid']==nodes['1']['section_uid']
    assert nodes['1.1(a)']['parent_uid']==nodes['1.1']['section_uid']
    route='/v1/experimental/obligation-bindings';payload=dict(job_id=job_id,experimental=True)
    assert client.post(route,json=payload).status_code==401
    assert client.post(route,headers=OTHER,json=payload).status_code==404
    response=client.post(route,headers=OWNER,json=payload)
    assert response.status_code==200,response.text
    binding=response.json()
    assert binding['record_count']==3
    assert [r['section_identity'] for r in binding['records']]==['1.1','1.1(a)','2']
    assert any(p['status']=='MATCHED' for p in binding['pairs'])
    for record in binding['records']:
        assert source[record['char_start']:record['char_end']]==record['raw_text']
        for spans in record['evidence'].values():
            for span in spans:assert source[span['char_start']:span['char_end']]==span['text']
    after=client.get(f'/v1/jobs/{job_id}/results',headers=OWNER).json()
    core=deepcopy(after);assert core['metadata'].pop('obligation_binding')==binding
    assert core==before
    jobs.JOB_STORE.pop(job_id)
    assert client.get(f'/v1/jobs/{job_id}/results',headers=OWNER).json()==after
    for fmt_out in ['pdf','docx']:
        url=f'/v1/jobs/{job_id}/report/{fmt_out}'
        assert client.get(url).status_code==401
        assert client.get(url,headers=OTHER).status_code==404
        response=client.get(url,headers=OWNER)
        assert response.status_code==200 and len(response.content)>1000
        if fmt_out=='pdf':
            import pdfplumber
            with pdfplumber.open(BytesIO(response.content)) as pdf:text='\n'.join(p.extract_text() or '' for p in pdf.pages)
        else:
            from docx import Document
            text='\n'.join(p.text for p in Document(BytesIO(response.content)).paragraphs)
        for expected in ['Experimental obligation binding','invoice alpha','report bravo','MATCHED',binding['source_sha256']]:assert expected in text
