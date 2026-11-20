import base64, json, time
from playwright.sync_api import sync_playwright

URL='http://127.0.0.1:3000'
PROJECT_ID='war97-isolated-multibatch-20261120'
NODE_ID='war97-batch-node'

def image_data(color):
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="320" height="220"><rect width="320" height="220" fill="{color}"/></svg>'
    return 'data:image/svg+xml;base64,'+base64.b64encode(svg.encode()).decode()

colors={'img-red':'#dc2626','img-green':'#16a34a','img-blue':'#2563eb'}
images=[dict(id=k,status='success',content=image_data(c),naturalWidth=320,naturalHeight=220,bytes=110,mimeType='image/svg+xml') for k,c in colors.items()]
node={'id':NODE_ID,'type':'image','title':'WAR97 multi-image isolated','position':{'x':200,'y':260},'width':280,'height':193,
      'metadata':{'content':images[0]['content'],'status':'success','generationType':'generation','count':3,'images':images,'primaryImageId':'img-red','naturalWidth':320,'naturalHeight':220}}
project={'id':PROJECT_ID,'title':'WAR97 isolated interaction test','createdAt':'2026-11-20T00:00:00.000Z','updatedAt':'2026-11-20T00:00:00.000Z',
         'nodes':[node],'connections':[],'chatSessions':[],'activeChatId':None,'backgroundMode':'lines','showImageInfo':False,
         'viewport':{'x':0,'y':0,'k':1}}

with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/home/sean/.cache/ms-playwright/chromium-1234/chrome-linux64/chrome',headless=True,args=['--no-sandbox'])
    context=browser.new_context(viewport={'width':1500,'height':1000},device_scale_factor=1)
    page=context.new_page()
    errs=[]
    page.on('pageerror',lambda e: errs.append(str(e)))
    page.goto(URL+'/canvas',wait_until='domcontentloaded',timeout=30000)
    result=page.evaluate("""async ({project}) => {
      const db=await new Promise((ok,fail)=>{
        const q=indexedDB.open('infinite-canvas');
        q.onupgradeneeded=()=>{if(!q.result.objectStoreNames.contains('app_state'))q.result.createObjectStore('app_state');};
        q.onsuccess=()=>ok(q.result);q.onerror=()=>fail(q.error);
      });
      await new Promise((ok,fail)=>{
        const tx=db.transaction('app_state','readwrite');
        tx.objectStore('app_state').put(JSON.stringify({storageRevision:1,state:{projects:[project],deletedProjects:[]},version:0}),'infinite-canvas:canvas_store_v2');
        tx.oncomplete=ok;tx.onerror=()=>fail(tx.error);
      });
      db.close(); return 'seeded';
    }""", {'project':project})
    print('seed',result,flush=True)
    page.goto(URL+'/canvas/'+PROJECT_ID,wait_until='domcontentloaded',timeout=30000)
    page.wait_for_timeout(1200)
    print('url',page.url,flush=True)
    root=page.locator('[data-node-id="'+NODE_ID+'"]')
    print('root',root.count(), 'buttons',root.locator('button').evaluate_all("(arr)=>arr.map(b=>({text:b.textContent,aria:b.getAttribute('aria-label'),title:b.getAttribute('title')}))") if root.count() else [],flush=True)
    if not root.count():
        print('body',page.locator('body').inner_text()[:2000],flush=True)
        raise SystemExit(11)
    batch=root.locator('button[aria-label]').filter(has_text='3')
    print('batch matched',batch.count(),flush=True)
    if not batch.count():
        batch=root.locator('button[aria-label]').filter(has_text='3')
    batch.first.click()
    page.wait_for_timeout(800)
    print('children',page.locator('[data-batch-image-id]').evaluate_all("(arr)=>arr.map(a=>({id:a.dataset.batchImageId,rect:a.getBoundingClientRect().toJSON()}))"),flush=True)
    results=[]
    for key in ['img-green','img-blue']:
        child=page.locator('[data-batch-image-id="'+key+'"]')
        if child.count()!=1: raise RuntimeError('Missing child '+key)
        child.hover(position={'x':100,'y':100},force=True)
        page.wait_for_timeout(150)
        page.keyboard.press('v')
        page.wait_for_timeout(220)
        modal_img=page.locator('.ant-modal img')
        src=modal_img.first.get_attribute('src') if modal_img.count() else None
        correct=(src==next(x['content'] for x in images if x['id']==key))
        print('V preview',key,'modal',modal_img.count(),'correct',correct,flush=True)
        page.screenshot(path='/home/sean/projects/canvas-lab/docs/validation/WAR-97/20261120-'+key+'-preview.png',full_page=True)
        results.append({'image':key,'previewCorrect':correct,'modalCount':modal_img.count()})
        page.keyboard.press('v')
        page.wait_for_timeout(650)
        closed=(not modal_img.is_visible()) if modal_img.count() else True
        print('V close',key,'closed',closed,flush=True)
        if not closed: raise RuntimeError('V did not close modal for '+key)
    print('JS_ERRORS',errs,flush=True)
    print('RESULT',json.dumps(results),flush=True)
    page.screenshot(path='/home/sean/projects/canvas-lab/docs/validation/WAR-97/20261120-expanded-batch.png',full_page=True)
    context.close();browser.close()
    if not all(r['previewCorrect'] for r in results) or errs: raise SystemExit(12)
