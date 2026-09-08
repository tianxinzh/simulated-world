const {chromium}=require('playwright');
const fs=require('node:fs');
const assert=require('node:assert/strict');
const cfg=JSON.parse(fs.readFileSync('site-config.json','utf8'));
const prefix=new URL(cfg.baseUrl).pathname;
const host='http://127.0.0.1:8765';
const base=host+prefix;
const inventory=JSON.parse(fs.readFileSync('site-inventory.json','utf8'));
const report={seo:[],layouts:[],players:[],privacy:{},campaign:{},limitations:['GA4 network delivery and provider-account ownership are not tested: no real measurement or verification credentials were supplied.','Visible-play thresholds use real elapsed time after real rendering and trusted input; test rendering is stopped during the timer-only segment.']};
fs.mkdirSync('test-results',{recursive:true});
(async()=>{
 const browser=await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--no-sandbox']});
 try{
  const api=await browser.newContext();const links=new Set();
  for(const p of inventory.pages){
   const path=(p.zh?'zh/':'')+p.route;
   const response=await api.request.get(base+path);assert.equal(response.status(),200,path);
   const html=await response.text();
   const canonical=[...html.matchAll(/<link rel="canonical" href="([^"]+)"/g)].map(x=>x[1]);assert.deepEqual(canonical,[p.url]);
   assert.equal((html.match(/<h1[ >]/g)||[]).length,1,path+' h1');
   assert(/<meta name="description" content="[^"]{15,}"/.test(html),path+' description');
   assert(!html.includes('content="noindex'),path+' unexpectedly noindex');
   for(const lang of ['en','zh-Hans','x-default'])assert(html.includes('hreflang="'+lang+'"'),path+' language '+lang);
   const alt=[...html.matchAll(/<link rel="alternate" hreflang="([^"]+)" href="([^"]+)"/g)];
   assert(alt.some(x=>x[1]==='en'&&x[2]===cfg.baseUrl+p.route));assert(alt.some(x=>x[1]==='zh-Hans'&&x[2]===cfg.baseUrl+'zh/'+p.route));
   for(const match of html.matchAll(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/g)){const data=JSON.parse(match[1]);assert(Array.isArray(data)&&data.length);assert(!JSON.stringify(data).includes('aggregateRating'));}
   for(const m of html.matchAll(/(?:href|src)="([^"]+)"/g)){const value=m[1].replaceAll('&amp;','&');if(value.startsWith(prefix))links.add(value.split('#')[0]);}
   report.seo.push({path,canonical:canonical[0],status:200,hreflang:'pass',structuredData:'valid JSON'});
  }
  assert.equal(inventory.pages.length,20);
  for(const path of links){const r=await api.request.get(host+path);assert.equal(r.status(),200,'broken internal resource '+path);}
  for(const path of ['airport.html','bayline.html','monitor/','tools/campaign-builder/']){
   const r=await api.request.get(base+path);const html=await r.text();assert(html.includes('content="noindex,follow"'),path);
  }
  for(const world of ['airport','bayline']){const source=fs.readFileSync(world+'.html','utf8');assert(!source.includes('googletagmanager'));assert(!source.includes('assets/growth.js'));assert(source.includes('SW BRIDGE'));}
  const sitemap=fs.readFileSync('sitemap.xml','utf8');assert.equal((sitemap.match(/<loc>/g)||[]).length,20);assert(!/monitor\/|campaign-builder|airport\.html|\?v=/.test(sitemap));
  await api.close();
  for(const width of [1440,1024,768,390,320]){
   for(const path of ['', 'zh/', 'worlds/bayport/','zh/worlds/bayport/']){
    const page=await browser.newPage({viewport:{width,height:1000},reducedMotion:'reduce'});const errors=[],requests=[];
    page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>requests.push(r.url()));
    await page.goto(base+path,{waitUntil:'networkidle'});
    assert.equal(await page.locator('iframe').count(),0,'No eager WebGL');assert(!requests.some(u=>/three.*\.js/.test(u)),'Eager dependency');
    assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'overflow '+width+' '+path);
    if(path===''||path==='zh/'){
     await page.locator('[data-filter="air"]').click();assert.equal(await page.locator('.world-card:visible h3').innerText(),'BAYPORT');
     await page.locator('[data-filter="all"]').click();
     const lang=await page.locator('#lang').getAttribute('href');assert.equal(lang,prefix+(path===''?'zh/':''));
    }
    if([1440,390].includes(width))await page.screenshot({path:'test-results/'+(path.replaceAll('/','-')||'home')+width+'.png',fullPage:true});
    assert.deepEqual(errors,[]);report.layouts.push({width,path,overflow:false,eagerWebGL:false,errors});await page.close();
   }
  }
  const plainContext=await browser.newContext({javaScriptEnabled:false});const plain=await plainContext.newPage();await plain.goto(base+'zh/worlds/bayline/');assert((await plain.locator('h1').innerText()).includes('虚拟模型铁路'));assert.equal(await plain.locator('iframe').count(),0);await plainContext.close();
  for(const world of ['bayport','bayline']){
   const page=await browser.newPage({viewport:{width:1440,height:1000}});const errors=[];page.on('pageerror',e=>errors.push(e.message));
   await page.goto(base+'worlds/'+world+'/?debug=1',{waitUntil:'networkidle'});
   await page.locator('[data-play]').click();
   await page.waitForFunction(()=>window.SW.events().some(x=>x.name==='world_ready'),null,{timeout:90000});
   const frame=await(await page.locator('iframe').elementHandle()).contentFrame();
   await page.locator('iframe').evaluate(el=>el.scrollIntoView({block:'center',behavior:'instant'}));await frame.locator('#stage').press('l');await frame.locator('#stage').press('ArrowUp');
   await page.waitForFunction(()=>window.SW.events().some(x=>x.name==='world_interaction'));
   const counts=await page.evaluate(()=>Object.fromEntries(['world_open','world_ready','world_interaction'].map(k=>[k,SW.events().filter(x=>x.name===k).length])));assert.deepEqual(counts,{world_open:1,world_ready:1,world_interaction:1});
   assert((await page.locator('[data-player-status]').innerText()).includes('Ready.'));
   if(world==='bayport'){
    await page.screenshot({path:'test-results/world-live.png'});
    // First prove the real renderer and trusted keyboard controls above; freeze only test rendering before advancing timers.
    await frame.evaluate(()=>{window.requestAnimationFrame=()=>0});
    await page.locator('[data-player]').evaluate(el=>el.style.display='none');await page.waitForTimeout(500);await page.waitForTimeout(65000);
    assert.equal(await page.evaluate(()=>SW.events().filter(x=>x.name==='engaged_play').length),0,'hidden player counted');
    await page.locator('[data-player]').evaluate(el=>el.style.display='');await page.locator('iframe').evaluate(el=>el.scrollIntoView({block:'center',behavior:'instant'}));await page.waitForTimeout(500);await page.waitForTimeout(62000);
    assert.equal(await page.evaluate(()=>SW.events().filter(x=>x.name==='engaged_play').length),1,'engaged threshold');assert.equal(await page.evaluate(()=>SW.events().filter(x=>x.name==='watched_play').length),1);
    await page.waitForTimeout(2000);assert.equal(await page.evaluate(()=>SW.events().filter(x=>x.name==='engaged_play').length),1,'duplicate engagement');
    const prior=await page.evaluate(()=>SW.events().length);await page.evaluate(()=>window.dispatchEvent(new MessageEvent('message',{origin:'https://evil.example',source:frames[0],data:{type:'sw:world',world:'bayport',event:'error'}})));assert.equal(await page.evaluate(()=>SW.events().length),prior,'untrusted origin accepted');
   }
   await page.locator('[data-stop]').click();assert.equal(await page.locator('iframe').count(),0);assert.equal(await page.evaluate(()=>SW.events().filter(x=>x.name==='world_end').length),1);
   assert.deepEqual(errors,[]);report.players.push({world,realWebGL:'rendered',trustedControlInput:'pass',deduplication:'pass',visiblePlayElapsedTimeTest:world==='bayport'?'pass':'not repeated',unloaded:true,errors});await page.close();
  }
  const homepage=await browser.newPage({viewport:{width:1440,height:1000}});await homepage.goto(base+'?debug=1');await homepage.locator('.world-card [data-preview="bayport"]').click();await homepage.waitForFunction(()=>SW.events().some(x=>x.name==='world_ready'),null,{timeout:90000});assert((await homepage.locator('#preview-launch').getAttribute('href')).endsWith('worlds/bayport/'));await homepage.locator('#preview-close').click();await homepage.waitForFunction(()=>document.querySelectorAll('iframe').length===0);await homepage.close();
  const testCfg={...cfg,basePath:prefix,measurementId:'G-TEST123456'};
  const privacy=await browser.newPage();const requests=[];
  await privacy.route('**/assets/site-config.js*',r=>r.fulfill({contentType:'application/javascript',body:'window.SW_CONFIG='+JSON.stringify(testCfg)}));
  await privacy.route('https://www.googletagmanager.com/**',r=>{requests.push(r.request().url());return r.fulfill({contentType:'application/javascript',body:'/* Isolated GA stub: no production data transmitted. */'})});
  await privacy.goto(base+'worlds/bayport/?utm_source=youtube&utm_campaign=test&secret=do-not-send',{waitUntil:'networkidle'});assert.equal(requests.length,0);
  await privacy.evaluate(()=>SW.event('world_open',{world:'preconsent'}));
  await privacy.getByRole('button',{name:'Allow analytics',exact:true}).click();await privacy.waitForFunction(()=>window.dataLayer?.length>4);await privacy.waitForTimeout(500);assert.equal(requests.length,1);
  const queue=await privacy.evaluate(()=>window.dataLayer.map(x=>Array.from(x)));
  assert(queue.some(x=>x[0]==='consent'&&x[1]==='default'&&x[2].analytics_storage==='denied'));
  assert(queue.some(x=>x[0]==='consent'&&x[1]==='update'&&x[2].analytics_storage==='granted'));
  assert(!JSON.stringify(queue).includes('do-not-send'));assert(!JSON.stringify(queue).includes('preconsent'));
  await privacy.evaluate(()=>SW.privacy());await privacy.getByRole('button',{name:'Decline',exact:true}).click();await privacy.waitForFunction(()=>window.SW?.status().consent==='rejected'&&!window.SW.status().tagRequested);await privacy.waitForLoadState('networkidle');assert.equal(requests.length,1);
  report.privacy={beforeConsentRequests:0,afterConsentTagRequests:1,revocation:'tag not reloaded',querySanitization:'pass',preConsentReplay:false,GA4:'test stub only; no real property configured'};await privacy.close();
  const gpc=await browser.newPage();await gpc.addInitScript(()=>Object.defineProperty(navigator,'globalPrivacyControl',{get:()=>true}));await gpc.route('**/assets/site-config.js*',r=>r.fulfill({contentType:'application/javascript',body:'window.SW_CONFIG='+JSON.stringify(testCfg)}));let gpcCalls=0;await gpc.route('https://www.googletagmanager.com/**',r=>{gpcCalls++;return r.abort()});await gpc.goto(base);await gpc.evaluate(()=>SW.privacy());assert(await gpc.getByRole('button',{name:'Allow analytics',exact:true}).isDisabled());assert.equal(gpcCalls,0);report.privacy.globalPrivacyControl='pass';await gpc.close();
  const campaign=await browser.newPage();await campaign.goto(base+'tools/campaign-builder/');await campaign.locator('#campaign-form button[type="submit"]').click();const result=await campaign.locator('#campaign-result').innerText();assert(result.includes('/worlds/bayport/?utm_source=youtube'));await campaign.locator('[name=source]').fill('person@example.com');await campaign.locator('#campaign-form button[type="submit"]').click();assert((await campaign.locator('#campaign-result').innerText()).includes('never personal'));report.campaign={validLink:result,rejectsEmail:'pass'};await campaign.close();
 }finally{await browser.close();fs.writeFileSync('test-results/growth-report.json',JSON.stringify(report,null,2));}
 console.log(JSON.stringify({pages:report.seo.length,layouts:report.layouts.length,players:report.players,privacy:report.privacy,campaign:report.campaign},null,2));
})().catch(e=>{console.error(e);process.exitCode=1});
