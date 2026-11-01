"""Actual local HTTP/model workflow; existing date/neural analysis must remain identical."""
from copy import deepcopy
from io import BytesIO
import pytest
from tests.test_temporal_integration import client,analyze,OWNER,OTHER
from src.api import jobs

SOURCE=('Section 1. Duty\nBuyer shall pay Invoice Alpha within 10 calendar days after receipt of Invoice Alpha.\n'
        'Section 2. Duty\nBuyer must remit Invoice Alpha within 20 calendar days after receipt of Invoice Alpha.')
ROUTE='/v1/experimental/obligation-bindings'

@pytest.mark.parametrize('fmt',['txt','pdf','docx'])
def test_binding_opt_in_history_and_report_workflow(client,fmt):
    _,job_id,source,before=analyze(client,SOURCE,fmt)
    payload=dict(job_id=job_id,experimental=True)
    assert 'obligation_binding' not in before['metadata']
    assert client.post(ROUTE,json=payload).status_code==401
    assert client.post(ROUTE,headers=OTHER,json=payload).status_code==404
    assert client.post(ROUTE,headers=OWNER,json=dict(payload,experimental=False)).status_code==400
    assert client.post(ROUTE,headers=OWNER,json=dict(payload,experimental='true')).status_code==422
    response=client.post(ROUTE,headers=OWNER,json=payload)
    assert response.status_code==200,response.text
    binding=response.json()
    assert binding['pair_counts']=={'MATCHED':1}
    assert binding['experimental'] is True and binding['coordinate_space']=='original_extracted_text'
    for record in binding['records']:
        assert source[record['char_start']:record['char_end']]==record['raw_text']
    after=client.get(f'/v1/jobs/{job_id}/results',headers=OWNER).json()
    stripped=deepcopy(after);assert stripped['metadata'].pop('obligation_binding')==binding
    assert stripped==before  # All neural, reference, graph, date and state fields, not just scores.
    jobs.JOB_STORE.pop(job_id)
    reopened=client.get(f'/v1/jobs/{job_id}/results',headers=OWNER).json()
    assert reopened==after
    for fmt_out in ['pdf','docx']:
        url=f'/v1/jobs/{job_id}/report/{fmt_out}'
        assert client.get(url,headers=OTHER).status_code==404
        response=client.get(url,headers=OWNER)
        assert response.status_code==200 and len(response.content)>1000
        if fmt_out=='pdf':
            import pdfplumber
            with pdfplumber.open(BytesIO(response.content)) as pdf:text='\n'.join(p.extract_text() or '' for p in pdf.pages)
        else:
            from docx import Document
            text='\n'.join(p.text for p in Document(BytesIO(response.content)).paragraphs)
        for required in ['Experimental obligation binding','MATCHED','potentially comparable','invoice alpha',binding['source_sha256']]:assert required in text

def test_ambiguous_binding_and_legacy_analysis(client):
    _,job_id,_,before=analyze(client,'Section 1. Duty\nIt shall pay Invoice Alpha.\nSection 2. Duty\nBuyer shall pay Invoice Alpha.','txt')
    response=client.post(ROUTE,headers=OWNER,json=dict(job_id=job_id,experimental=True))
    assert response.status_code==200 and response.json()['pair_counts']=={'UNCERTAIN':1}
    meta=jobs.JOB_STORE[job_id].result['metadata']
    original=meta.pop('original_source_text')
    try:assert client.post(ROUTE,headers=OWNER,json=dict(job_id=job_id,experimental=True)).status_code==409
    finally:meta['original_source_text']=original

def test_oversize_stored_source_rejected_without_partial_binding(client):
    _,job_id,_,_=analyze(client,SOURCE,'txt')
    meta=jobs.JOB_STORE[job_id].result['metadata'];original=meta['original_source_text']
    meta['original_source_text']='x'*250001
    try:
        assert client.post(ROUTE,headers=OWNER,json=dict(job_id=job_id,experimental=True)).status_code==413
        assert 'obligation_binding' not in meta
    finally:meta['original_source_text']=original
