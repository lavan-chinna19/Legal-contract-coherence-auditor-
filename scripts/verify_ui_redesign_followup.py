import asyncio,json,time,urllib.request
from pathlib import Path
from verify_ui_redesign import Browser,OUT,API,KEY

async def main():
 checks=[];result={'status':'RUNNING','checks':checks}
 def check(name,condition,detail=None):
  assert condition,(name,detail)
  checks.append({'name':name,'status':'PASS','detail':detail});print('PASS:',name,flush=True)
 async def wait(b,expr,timeout=30):
  end=time.monotonic()+timeout
  while time.monotonic()<end:
   if await b.js(f"Boolean({expr})"):return
   await asyncio.sleep(.2)
  raise AssertionError('Timeout: '+expr)
 pages=json.load(urllib.request.urlopen('http://127.0.0.1:9333/json'));page=next(p for p in pages if p['type']=='page')
 import websockets
 async with websockets.connect(page['webSocketDebuggerUrl'],max_size=16*1024*1024) as ws:
  b=Browser(ws)
  try:
   await b.call('Runtime.enable');await b.call('Page.enable');await b.call('Network.enable')
   await b.call('Emulation.setDeviceMetricsOverride',{'width':1440,'height':1000,'deviceScaleFactor':1,'mobile':False})
   await b.call('Page.reload');await wait(b,"document.querySelector('#nav-settings')")
   await wait(b,"document.querySelector('#backend-status-pill')?.textContent==='Engine available'")
   await b.click('#nav-settings');await b.fill('#api-key-input',KEY);await b.click('#connect-engine-btn');await wait(b,"document.querySelector('h1')?.textContent==='New Audit'")
   await b.click('#nav-reports-history');await wait(b,"document.querySelector('.saved-audits li button')");await b.click('.saved-audits li button');await wait(b,"document.querySelector('#view-findings')")
   for width,label in [(1440,'desktop'),(834,'tablet'),(390,'mobile')]:
    await b.call('Emulation.setDeviceMetricsOverride',{'width':width,'height':1000 if width>400 else 844,'deviceScaleFactor':1,'mobile':False})
    async def nav(id):
     await b.js(f"document.getElementById({json.dumps('nav-'+id)}).click()")
     await asyncio.sleep(.2)
    for view in ['findings','review','analytics','explanations','references']:
     await nav('audit-results');await b.click('#view-'+view);await asyncio.sleep(.3)
     check(f'Final {label} {view} fits viewport',await b.js('document.documentElement.scrollWidth<=innerWidth'))
     check(f'{label} active result tab remains visible',await b.js("(() => {const e=document.querySelector('.workspace-tabs [aria-selected=true]').getBoundingClientRect(),g=document.querySelector('.workspace-tabs').getBoundingClientRect();return e.left>=g.left-1&&e.right<=g.right+1;})()"))
     await b.screenshot(f'final-{label}-{view}.png')
    for section in ['new-audit','reports-history','settings','research-tools']:
     await nav(section)
     check(f'{label} {section} fits viewport',await b.js('document.documentElement.scrollWidth<=innerWidth'))
     if section=='research-tools':
      for view in ['evaluation','compatibility','robustness']:
       await b.click('#view-'+view);await asyncio.sleep(.3)
       check(f'{label} research {view} fits viewport',await b.js('document.documentElement.scrollWidth<=innerWidth'))
    if width>768:
     gap=await b.js("document.querySelector('.main-wrapper').getBoundingClientRect().left-document.querySelector('.sidebar').getBoundingClientRect().right")
     check(f'{label} sidebar has no duplicate column offset',abs(gap)<2,gap)
    await nav('audit-results');await b.click('#view-findings')
    await b.js("document.getElementById('view-findings').focus()")
    await b.call('Input.dispatchKeyEvent',{'type':'keyDown','key':'ArrowRight','code':'ArrowRight'});await b.call('Input.dispatchKeyEvent',{'type':'keyUp','key':'ArrowRight','code':'ArrowRight'})
    check(f'{label} result tabs support arrow-key focus and selection',await b.js("document.activeElement.id==='view-review'&&document.getElementById('view-review').getAttribute('aria-selected')==='true'"))
    await nav('settings')
    for theme in ['light','dark']:
     await b.click('#theme-btn-'+theme);await wait(b,f"document.documentElement.dataset.theme==='{theme}'")
     contrast=await b.js("""(() => {function rgb(s){return(s.match(/[\\d.]+/g)||[]).slice(0,3).map(Number)}function lum(v){return v.map(n=>n/255).map(n=>n<=.04045?n/12.92:((n+.055)/1.055)**2.4).reduce((a,n,i)=>a+n*[.2126,.7152,.0722][i],0)}const h=document.querySelector('h1'),s=getComputedStyle(h),bg=getComputedStyle(document.querySelector('header'));let a=lum(rgb(s.color)),c=lum(rgb(bg.backgroundColor));return (Math.max(a,c)+.05)/(Math.min(a,c)+.05);})()""")
     check(f'{label} {theme} heading contrast meets 4.5:1',contrast>=4.5,contrast)
     await b.screenshot(f'final-{label}-settings-{theme}.png')
    if width<=768:
     await b.click('button[aria-label="Open navigation"]');await wait(b,"document.querySelector('.sidebar.mobile-open')")
     check('Mobile navigation drawer is visibly inside viewport',await b.js("document.querySelector('.sidebar.mobile-open').getBoundingClientRect().left>=0 && document.querySelector('.sidebar.mobile-open').getBoundingClientRect().right<=innerWidth"))
     await b.call('Input.dispatchKeyEvent',{'type':'keyDown','key':'Tab','code':'Tab','modifiers':8});await b.call('Input.dispatchKeyEvent',{'type':'keyUp','key':'Tab','code':'Tab','modifiers':8})
     check('Mobile Shift+Tab stays inside navigation',await b.js("document.querySelector('.sidebar').contains(document.activeElement)"))
     await b.call('Input.dispatchKeyEvent',{'type':'keyDown','key':'Escape','code':'Escape'});await b.call('Input.dispatchKeyEvent',{'type':'keyUp','key':'Escape','code':'Escape'})
     await wait(b,"document.activeElement?.getAttribute('aria-label')==='Open navigation'")
     check('Final mobile Escape restores trigger focus',await b.js("document.activeElement.getAttribute('aria-label')==='Open navigation'"))
     await b.click('button[aria-label="Open navigation"]');await wait(b,"document.querySelector('.sidebar.mobile-open')")
     await b.click('#nav-settings');await wait(b,"document.activeElement?.id==='page-title'")
     check('Selecting the current mobile section closes navigation and focuses its heading',await b.js("!document.querySelector('.sidebar.mobile-open') && document.activeElement.id==='page-title'"))
     check('Primary navigation opens content at the top',await b.js('scrollY===0'))
   await b.js("document.getElementById('nav-new-audit').click()")
   root=(await b.call('DOM.getDocument'))['root']['nodeId'];node=(await b.call('DOM.querySelector',{'nodeId':root,'selector':'#file-input'}))['nodeId']
   await b.call('DOM.setFileInputFiles',{'nodeId':node,'files':[str(OUT/'fixtures/workflow-contract.txt')]})
   if await b.js("document.querySelector('#privacy-consent').checked"):await b.click('#privacy-consent')
   check('Consented upload required even with a valid identity and selected file',await b.js("document.querySelector('#preview-btn').disabled"))
   await b.click('#privacy-consent');bad=OUT/'fixtures/unsupported.csv';bad.write_text('synthetic unsupported input')
   await b.call('DOM.setFileInputFiles',{'nodeId':node,'files':[str(bad)]});await b.click('#preview-btn');await wait(b,"document.querySelector('[role=alert]')")
   check('Unsupported input shows a real validation error',await b.js("document.querySelector('[role=alert]').textContent.includes('Choose a PDF, DOCX or UTF-8 TXT file')"))
   check('No uncaught exceptions in final follow-up',not b.exceptions,b.exceptions)
   result.update(status='PASS',passed=len(checks),failed=0)
  except Exception as e:
   result.update(status='FAIL',passed=len(checks),failed=1,error=str(e));await b.screenshot('followup-failure.png');raise
  finally:(OUT/'browser-followup.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
 print(json.dumps({'status':result['status'],'passed':len(checks)}))
if __name__=='__main__':asyncio.run(main())
