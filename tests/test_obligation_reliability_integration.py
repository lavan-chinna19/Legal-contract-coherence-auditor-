"""Source-backed repaired grammar through actual authenticated local application workflows."""
from copy import deepcopy
from io import BytesIO
import pytest
from tests.test_temporal_integration import client,analyze,OWNER,OTHER
from src.api import jobs

SOURCE=('Section 1. Duty\nThe provider and subcontractor shall notify the customer about Notice Alpha.\n'
        'Section 2. Duty\nThe customer shall be notified by the provider and subcontractor about Notice Alpha.')

@pytest.mark.parametrize('fmt',['txt','pdf','docx'])
def test_repaired_binding_auth_persistence_exports(client,fmt):
    _,job_id,source,before=analyze(client,SOURCE,fmt)
    url='/v1/experimental/obligation-bindings';payload=dict(job_id=job_id,experimental=True)
    assert client.post(url,json=payload).status_code==401
    assert client.post(url,headers=OTHER,json=payload).status_code==404
    response=client.post(url,headers=OWNER,json=payload)
    assert response.status_code==200,response.text
    binding=response.json()
    assert binding['version']=='experimental-obligation-binding-v1.1'
    assert binding['pairs'][0]['status']=='MATCHED'
    assert binding['pairs'][0]['actor_action_relationship']=='MATCHED'
    for rec in binding['records']:
        assert rec['actors']==['provider','subcontractor'] and rec['actor_mode']=='JOINT'
        assert rec['event_type']=='NOTIFY:notice' and rec['event_instance']=='notice alpha'
        assert source[rec['char_start']:rec['char_end']]==rec['raw_text']
        for spans in rec['evidence'].values():
            for span in spans:assert source[span['char_start']:span['char_end']]==span['text']
    after=client.get(f'/v1/jobs/{job_id}/results',headers=OWNER).json()
    core=deepcopy(after);assert core['metadata'].pop('obligation_binding')==binding
    assert core==before
    jobs.JOB_STORE.pop(job_id)
    assert client.get(f'/v1/jobs/{job_id}/results',headers=OWNER).json()==after
    for export in ['pdf','docx']:
        response=client.get(f'/v1/jobs/{job_id}/report/{export}',headers=OWNER)
        assert response.status_code==200
        if export=='pdf':
            import pdfplumber
            with pdfplumber.open(BytesIO(response.content)) as pdf:text='\n'.join(p.extract_text() or '' for p in pdf.pages)
        else:
            from docx import Document
            text='\n'.join(p.text for p in Document(BytesIO(response.content)).paragraphs)
        for required in ['JOINT','PASSIVE','NOTIFY:notice','notice alpha','provider','subcontractor','MATCHED']:
            assert required in text
