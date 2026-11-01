"""Real Chrome acceptance of the local UI refactor; synthetic fixtures only.

Start the documented isolated demo API/frontend and a separate Chrome profile
with remote debugging on loopback 9333. Outputs stay under ignored tmp/.
"""
import asyncio, base64, json, time, urllib.request, zipfile
from pathlib import Path
import websockets

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'tmp/ui-redesign'
URL = 'http://127.0.0.1:3002/'
API = 'http://127.0.0.1:8012'
KEY = 'dev_auditor_key_12345'  # Explicit public synthetic-demo credential.

class Browser:
    def __init__(self, ws):
        self.ws, self.counter, self.responses, self.exceptions = ws, 0, [], []
    async def call(self, method, params=None):
        self.counter += 1; ident = self.counter
        await self.ws.send(json.dumps({'id': ident, 'method': method, 'params': params or {}}))
        while True:
            data = json.loads(await asyncio.wait_for(self.ws.recv(), 40))
            if data.get('method') == 'Runtime.exceptionThrown': self.exceptions.append(data['params']['exceptionDetails'].get('text', 'JavaScript exception'))
            if data.get('method') == 'Network.responseReceived':
                r = data['params']['response']
                if r['url'].startswith(API): self.responses.append({'url': r['url'], 'status': r['status']})
            if data.get('id') == ident:
                if 'error' in data: raise RuntimeError(data['error']['message'])
                return data.get('result', {})
    async def js(self, expression):
        r = await self.call('Runtime.evaluate', {'expression': expression, 'awaitPromise': True, 'returnByValue': True})
        if 'exceptionDetails' in r: raise RuntimeError(str(r['exceptionDetails']))
        return r.get('result', {}).get('value')
    async def ready(self, selector, enabled=False):
        end=time.monotonic()+15
        while time.monotonic()<end:
            condition=f"(() => {{ const e=document.querySelector({json.dumps(selector)}); return !!e && (!{str(enabled).lower()} || !e.disabled); }})()"
            if await self.js(condition):return
            await asyncio.sleep(.05)
        raise AssertionError('Control did not become ready: '+selector)
    async def click(self, selector):
        await self.ready(selector, enabled=True)
        await self.js(f"(() => {{const e=document.querySelector({json.dumps(selector)}); if(!e||e.disabled) throw new Error('Unavailable control: '+{json.dumps(selector)}); e.click();}})()")
    async def fill(self, selector, value):
        await self.ready(selector, enabled=True)
        await self.js(f"(() => {{const e=document.querySelector({json.dumps(selector)}); const type=e.tagName==='SELECT'?HTMLSelectElement:HTMLInputElement; Object.getOwnPropertyDescriptor(type.prototype,'value').set.call(e,{json.dumps(value)}); e.dispatchEvent(new Event('input',{{bubbles:true}})); e.dispatchEvent(new Event('change',{{bubbles:true}}));}})()")
    async def screenshot(self, name):
        r = await self.call('Page.captureScreenshot', {'format':'png','captureBeyondViewport':False})
        (OUT / name).write_bytes(base64.b64decode(r['data']))

async def main():
    checks=[]; result={'status':'RUNNING','checks':checks}
    def record(name, detail=None):
        checks.append({'name':name,'status':'PASS','detail':detail}); print('PASS:',name,flush=True)
        (OUT/'browser-acceptance.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    pages=json.load(urllib.request.urlopen('http://127.0.0.1:9333/json'))
    page=next(p for p in pages if p['type']=='page')
    async with websockets.connect(page['webSocketDebuggerUrl'], max_size=16*1024*1024) as ws:
        b=Browser(ws)
        async def expect(name, expression, timeout=30):
            end=time.monotonic()+timeout; last=None
            while time.monotonic()<end:
                last=await b.js(expression)
                if last: record(name); return last
                await asyncio.sleep(.25)
            await b.screenshot('failed-browser-state.png')
            raise AssertionError(f'{name}: condition not reached ({last!r})')
        try:
            await b.call('Page.enable'); await b.call('Runtime.enable'); await b.call('Network.enable')
            downloads=OUT/'downloads';downloads.mkdir(exist_ok=True)
            await b.call('Browser.setDownloadBehavior',{'behavior':'allow','downloadPath':str(downloads),'eventsEnabled':True})
            await b.call('Emulation.setDeviceMetricsOverride',{'width':1440,'height':1000,'deviceScaleFactor':1,'mobile':False})
            await b.call('Page.navigate',{'url':URL})
            await expect('New Audit initial screen',"document.querySelector('h1')?.textContent==='New Audit'",60)
            await expect('Four primary destinations without duplicate global tabs',"document.querySelectorAll('nav[aria-label=\"Primary navigation\"] button').length===4 && !document.querySelector('.tab-nav')")
            await expect('Connection credentials absent from main workflow',"!document.querySelector('#api-key-input') && !document.querySelector('#backend-url-input')")
            await expect('Upload requires authentication and privacy consent',"document.querySelector('#preview-btn').disabled===true")
            await expect('Engine probe confirms hydrated interactive page',"document.querySelector('#backend-status-pill')?.textContent==='Engine available'",30)
            await b.screenshot('desktop-new-audit.png')
            await b.click('#nav-settings'); await b.fill('#api-key-input','invalid_demo_identity'); await b.click('#connect-engine-btn')
            await expect('Invalid key produces actionable authentication error',"document.querySelector('[role=alert]')?.textContent.includes('Authentication failed')")
            await b.fill('#api-key-input',KEY); await b.click('#connect-engine-btn')
            await expect('Settings connection returns to New Audit',"document.querySelector('h1')?.textContent==='New Audit'")
            await expect('Engine status reflects authenticated local connection',"document.querySelector('#backend-status-pill')?.textContent==='Local engine connected'")
            for suffix in ['txt','pdf','docx']:
                await b.click('#nav-new-audit')
                root=(await b.call('DOM.getDocument'))['root']['nodeId']
                node=(await b.call('DOM.querySelector',{'nodeId':root,'selector':'#file-input'}))['nodeId']
                await b.call('DOM.setFileInputFiles',{'nodeId':node,'files':[str(OUT/'fixtures'/f'workflow-contract.{suffix}')]})
                if not await b.js('document.querySelector("#privacy-consent").checked'): await b.click('#privacy-consent')
                await b.click('#preview-btn')
                await expect(f'{suffix.upper()} extracts a real clause preview',"document.querySelector('[aria-label=\"Clause preview\"]')?.textContent.includes('extracted clauses')",60)
                await expect(f'{suffix.upper()} preview does not run inference automatically',"document.querySelector('h1').textContent==='New Audit' && !document.querySelector('#view-findings')")
                await b.click('#analyze-preview-btn')
                await expect(f'{suffix.upper()} local inference reaches Audit Results',"document.querySelector('h1')?.textContent==='Audit Results'",180)
                await expect(f'{suffix.upper()} findings separated by evidence type',"document.querySelectorAll('.finding-groups>details').length===4")
                await expect(f'{suffix.upper()} document name retained',f"document.querySelector('.document-bar')?.textContent.includes('workflow-contract.{suffix}')")
                if suffix=='txt':
                    await b.click('#view-references')
                    await expect('Reference check requires explicit opt-in',"document.querySelector('#run-reference-check').disabled")
                    await b.click('#reference-opt-in'); await b.click('#run-reference-check')
                    await expect('Reference evidence saved with supported textual conflict',"document.querySelector('.reference-evidence')?.textContent.includes('Evidence is saved') && document.querySelector('.reference-evidence').textContent.includes('1 supported textual conflicts')")
                    await b.click('#view-findings')
                    await expect('Textual conflicts stay separate from model anomalies',"document.querySelector('.finding-groups').textContent.includes('Supported textual conflicts') && document.querySelector('.finding-groups').textContent.includes('Statistical NLP anomalies')")
                    await b.click('#view-review')
                    await expect('Authoritative clause review available',"document.querySelector('.review-split-grid')!==null")
                    await b.click('#inspector-open-xai-btn')
                    await expect('Clause selection navigates to explanations',"document.querySelector('#xai-workspace-container')!==null")
                    await expect('Attribution endpoint actually responds',f"performance.getEntriesByType('resource').some(e=>e.name.includes('/v1/xai/attribution') && e.responseEnd>0)",120)
                    await b.click('#xai-tab-sensitivity')
                    await expect('Sensitivity endpoint actually responds',"performance.getEntriesByType('resource').some(e=>e.name.includes('/v1/xai/sensitivity') && e.responseEnd>0)",120)
                    await b.click('#view-review'); await b.click('#inspector-explore-reposition-btn')
                    await expect('Suggested positions remain accessible as experimental',"document.querySelector('[aria-label=\"Suggested Clause Positions (Experimental)\"]')!==null")
                    await expect('Counterfactual endpoint actually responds',"performance.getEntriesByType('resource').some(e=>e.name.includes('/v1/experimental/reposition') && e.responseEnd>0)",120)
                    await b.click('#nav-research-tools'); await b.click('#view-compatibility')
                    await expect('Pretrained compatibility map moved into Research Tools',"performance.getEntriesByType('resource').some(e=>e.name.includes('learned_clause_pair_compatibility.json') && e.responseEnd>0)")
                    await b.click('#view-robustness'); await b.click('#redteam-opt-in-checkbox'); await b.click('#btn-run-redteam-experiment')
                    await expect('Robustness experiment actually responds',"performance.getEntriesByType('resource').some(e=>e.name.includes('/v1/experimental/redteam') && e.responseEnd>0)",120)
                    await b.click('#view-evaluation'); await expect('Historical evaluation separated from current results',"document.querySelector('.research-evaluation')?.textContent.includes('50.0%')")
                await b.click('#nav-reports-history')
                await expect(f'{suffix.upper()} saved history lists this audit',f"document.querySelector('.saved-audits')?.textContent.includes('workflow-contract.{suffix}')")
                if suffix=='txt':
                    await b.fill('#reviewer-id-input','ui_synthetic_reviewer'); await b.fill('#feedback-provenance-select','SYNTHETIC_TEST'); await b.click('#submit-feedback-btn')
                    await expect('Reviewer feedback saved through actual API',"document.querySelector('main')?.textContent.includes('Reviewer feedback saved.')")
                for fmt in ['pdf','docx']:
                    before=set(downloads.glob(f'*.{fmt}'))
                    await b.js(f"[...document.querySelectorAll('button')].find(e=>e.textContent==='Download {fmt.upper()}').click()")
                    end=time.monotonic()+25;new=set()
                    while time.monotonic()<end:
                        new=set(downloads.glob(f'*.{fmt}'))-before
                        if new and all(p.stat().st_size>1000 for p in new):break
                        await asyncio.sleep(.3)
                    assert new,f'Browser {fmt} download missing'
                    path=next(iter(new))
                    if fmt=='pdf':assert path.read_bytes().startswith(b'%PDF-')
                    else:
                        with zipfile.ZipFile(path) as archive: assert b'LexAudit' in archive.read('word/document.xml')
                    record(f'{suffix.upper()} actual {fmt.upper()} download is valid',{'bytes':path.stat().st_size})
                await b.click('.saved-audits li button')
                await expect(f'{suffix.upper()} saved audit reopens',"document.querySelector('h1')?.textContent==='Audit Results'")
                if suffix=='txt':
                    await expect('Saved audit retains explicit reference findings',"[...document.querySelectorAll('.finding-groups summary')].find(e=>e.textContent.includes('Supported textual conflicts'))?.querySelector('span')?.textContent==='1'")
            owned=await b.js(f"fetch('{API}/v1/documents',{{headers:{{'X-API-Key':{json.dumps(KEY)}}}}}).then(r=>r.json())")
            doc=next(d for d in owned['documents'] if d.get('job_id'))
            for name,path in [('results',f"/v1/jobs/{doc['job_id']}/results"),('preview',f"/v1/documents/{doc['doc_id']}/clauses"),('PDF export',f"/v1/jobs/{doc['job_id']}/report/pdf"),('DOCX export',f"/v1/jobs/{doc['job_id']}/report/docx")]:
                status=await b.js(f"fetch({json.dumps(API+path)},{{headers:{{'X-API-Key':'client_b_key_67890'}}}}).then(r=>r.status)")
                assert status in (403,404),(name,status);record(f'Other-owner {name} denied',{'status':status})
            for width,label in [(1440,'desktop'),(834,'tablet'),(390,'mobile')]:
                await b.call('Emulation.setDeviceMetricsOverride',{'width':width,'height':1000 if width>400 else 844,'deviceScaleFactor':1,'mobile':False})
                await b.click('#nav-audit-results') if width>768 else None
                if width<=768:
                    await b.click('button[aria-label="Open navigation"]')
                    await expect('Mobile menu moves focus inside dialog',"document.activeElement?.getAttribute('aria-label')==='Close navigation'")
                    await b.call('Input.dispatchKeyEvent',{'type':'keyDown','key':'Escape','code':'Escape'}); await b.call('Input.dispatchKeyEvent',{'type':'keyUp','key':'Escape','code':'Escape'})
                    await expect('Mobile Escape closes menu and restores focus',"!document.querySelector('.sidebar.mobile-open') && document.activeElement?.getAttribute('aria-label')==='Open navigation'")
                for view in ['findings','review','analytics','explanations','references']:
                    await b.click(f'#view-{view}')
                    await expect(f'{label} {view} has no page overflow',"document.documentElement.scrollWidth<=innerWidth",30)
                await b.screenshot(f'{label}-results.png')
            await b.js("document.getElementById('nav-settings').click()")
            await b.click('#theme-btn-dark'); await expect('Dark theme applies',"document.documentElement.dataset.theme==='dark'")
            await b.screenshot('mobile-settings-dark.png'); await b.click('#theme-btn-light')
            await expect('Browser storage contains no credentials or document excerpts',f"![...Object.values(localStorage),...Object.values(sessionStorage)].some(v=>v.includes({json.dumps(KEY)})||v.includes('SYNTHETIC WORKFLOW FIXTURE'))")
            await b.js("[...document.querySelectorAll('button')].find(e=>e.textContent==='Sign out and clear session').click()")
            await expect('Sign out clears authenticated identity',"document.querySelector('#connect-engine-btn')?.textContent==='Connect engine'")
            await b.js("document.getElementById('nav-audit-results').click()")
            await expect('Sign out clears document content and results',"document.querySelector('main').textContent.includes('No audit selected') && !document.querySelector('.document-bar')")
            await b.call('Page.reload')
            await expect('Reload requires fresh Settings authentication',"document.querySelector('#preview-btn')?.disabled===true",60)
            await expect('No decorative emojis or internal phase codes in normal workflow',"!/[\\u{1F300}-\\u{1FAFF}]/u.test(document.querySelector('main').textContent) && !/P4D|PHASE 4|Prompt [0-9]/i.test(document.querySelector('main').textContent)")
            for endpoint in ['/v1/xai/attribution','/v1/xai/sensitivity','/v1/experimental/reposition','/v1/experimental/redteam']:
                assert any(endpoint in r['url'] and r['status']==200 for r in b.responses),endpoint
                record('Actual successful response: '+endpoint)
            assert not b.exceptions,b.exceptions
            record('No uncaught application JavaScript exceptions')
            result.update(status='PASS',passed=len(checks),failed=0,api_responses=b.responses,exceptions=b.exceptions)
        except Exception as e:
            result.update(status='FAIL',passed=len(checks),failed=1,error=str(e),api_responses=b.responses,exceptions=b.exceptions)
            await b.screenshot('failed-browser-state.png')
            raise
        finally:(OUT/'browser-acceptance.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps({'status':result['status'],'passed':len(checks)},indent=2))

if __name__=='__main__':asyncio.run(main())
