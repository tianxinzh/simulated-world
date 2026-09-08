/* Simulated World: hosted-page features only. Standalone worlds never load this file. */
(() => {
  'use strict';
  const cfg=window.SW_CONFIG||{}, zh=document.documentElement.lang.startsWith('zh');
  const text=(en,cn)=>zh?cn:en;
  const root=cfg.basePath||'/simulated-world/';
  const store={get(k){try{return localStorage.getItem(k)}catch{return null}},set(k,v){try{localStorage.setItem(k,v)}catch{}},remove(k){try{localStorage.removeItem(k)}catch{}}};
  const tab={get(k){try{return sessionStorage.getItem(k)}catch{return null}},set(k,v){try{sessionStorage.setItem(k,v)}catch{}}};
  const id=/^G-[A-Z0-9]{6,20}$/.test(cfg.measurementId||'')?cfg.measurementId:'';
  const privacySignal=navigator.globalPrivacyControl===true||navigator.doNotTrack==='1';
  let choice=store.get('sw-consent-v1')||'unset', loaded=false, diagnostic=new URLSearchParams(location.search).get('debug')==='1'||tab.get('sw-debug')==='1';
  let buffer=[];
  const allowed=new Set(['page_view','world_open','world_ready','world_interaction','engaged_play','watched_play','world_error','world_end','share','github_click','download','language_change']);
  const keys=new Set(['world','release','language','entry_point','control','error_code','visible_seconds','load_ms','method','acq_source','acq_medium','acq_campaign','acq_content']);
  const campaign={};
  for(const k of ['source','medium','campaign','content']){const v=new URLSearchParams(location.search).get('utm_'+k);if(v&&/^[a-z0-9_.-]{1,64}$/i.test(v))campaign['acq_'+k]=v.toLowerCase();}
  function cleanURL(raw){try{const u=new URL(raw,location.href);const q=new URLSearchParams();for(const k of ['source','medium','campaign','content']){const v=u.searchParams.get('utm_'+k);if(v&&/^[a-z0-9_.-]{1,64}$/i.test(v))q.set('utm_'+k,v);}return u.origin+u.pathname+(q.size?'?'+q:'')}catch{return ''}}
  function permitted(){return Boolean(id)&&choice==='accepted'&&!privacySignal;}
  function record(name,data,status){if(!diagnostic)return;buffer.push({time:new Date().toISOString(),name,data,status});if(buffer.length>160)buffer.shift();window.dispatchEvent(new CustomEvent('sw:diagnostic'));}
  function event(name,data={}){
    if(!allowed.has(name))return;
    const safe={language:zh?'zh':'en',...campaign};
    for(const [k,v]of Object.entries(data)){if(!keys.has(k))continue;if(typeof v==='number'&&Number.isFinite(v))safe[k]=Math.round(v);else if(typeof v==='string'&&/^[a-zA-Z0-9_. -]{1,80}$/.test(v))safe[k]=v;}
    const status=permitted()&&loaded?'queued-for-GA4':!id?'local-only: no measurement ID':'local-only: no analytics consent';
    if(permitted()&&loaded)window.gtag('event',name,{...safe,page_location:cleanURL(location.href),page_referrer:document.referrer?new URL(document.referrer).origin:'',...(diagnostic?{debug_mode:true}:{})});
    record(name,safe,status);
  }
  function activate(){
    if(!permitted()||loaded)return;
    loaded=true;window['ga-disable-'+id]=false;window.dataLayer=window.dataLayer||[];
    window.gtag=function(){window.dataLayer.push(arguments)};
    window.gtag('consent','default',{analytics_storage:'denied',ad_storage:'denied',ad_user_data:'denied',ad_personalization:'denied'});
    window.gtag('consent','update',{analytics_storage:'granted',ad_storage:'denied',ad_user_data:'denied',ad_personalization:'denied'});
    window.gtag('js',new Date());
    window.gtag('config',id,{send_page_view:false,allow_google_signals:false,allow_ad_personalization_signals:false,cookie_path:root,cookie_flags:'SameSite=Lax;Secure',page_location:cleanURL(location.href),page_referrer:document.referrer?new URL(document.referrer).origin:''});
    const script=document.createElement('script');script.async=true;script.src='https://www.googletagmanager.com/gtag/js?id='+id;
    script.onerror=()=>record('tag_load_error',{},'GA4 blocked or unavailable; delivery not confirmed');document.head.appendChild(script);
    event('page_view');
  }
  function deleteCookies(){
    // Delete only the GA cookies for this installation, across common path scopes.
    const names=document.cookie.split(';').map(x=>x.trim().split('=')[0]).filter(x=>x==='_ga'||x==='_ga_'+id.slice(2));
    for(const name of names)for(const path of new Set(['/',root]))for(const domain of ['',location.hostname,'.'+location.hostname])document.cookie=name+'=;Max-Age=0;path='+path+(domain?';domain='+domain:'')+';SameSite=Lax';
  }
  function saveChoice(value){
    choice=value;store.set('sw-consent-v1',value);
    if(value==='accepted')activate();else{if(id)window['ga-disable-'+id]=true;deleteCookies();}
    document.getElementById('sw-consent')?.remove();
    window.dispatchEvent(new CustomEvent('sw:diagnostic'));
    // Unload an already active Google tag completely after revocation.
    if(value!=='accepted'&&loaded)location.reload();
  }
  function privacyPanel(){
    if(document.getElementById('sw-consent'))return;
    const panel=document.createElement('section');panel.id='sw-consent';panel.className='consent-panel';panel.setAttribute('role','region');panel.setAttribute('aria-label',text('Analytics choices','流量统计设置'));
    const p=document.createElement('p');
    p.textContent=privacySignal?text('Your browser privacy preference is respected. Optional analytics is disabled.','已遵循浏览器隐私偏好，可选统计已关闭。'):!id?text('Optional analytics is not connected. No visitor data is being sent to an analytics service. You can still save your preference.','尚未连接可选统计服务，不会向统计平台发送访客数据。你仍可保存隐私偏好。'):text('Allow optional analytics? We measure visits and play events to improve the worlds. No advertising or session recordings. The simulators work either way.','允许可选流量统计吗？我们统计访问与游玩事件以改进体验，不投放广告，也不录制访问过程。不允许也能正常游玩。');
    panel.append(p);const controls=document.createElement('div');controls.className='actions';
    for(const [value,en,cn]of [['rejected','Decline','不允许'],['accepted','Allow analytics','允许统计']]){const b=document.createElement('button');b.type='button';b.className='button secondary';b.textContent=text(en,cn);b.disabled=value==='accepted'&&privacySignal;b.onclick=()=>saveChoice(value);controls.append(b);}
    const a=document.createElement('a');a.href=root+(zh?'zh/':'')+'privacy/';a.textContent=text('Privacy notice','隐私说明');controls.append(a);panel.append(controls);document.body.append(panel);
  }
  const analytics={event,status:()=>({configured:Boolean(id),measurementId:id||null,consent:choice,browserPrivacySignal:privacySignal,tagRequested:loaded,delivery:'Not confirmed here; use GA4 Realtime or DebugView'}),privacy:privacyPanel,debug(on=true){diagnostic=on;tab.set('sw-debug',on?'1':'0');if(!on)buffer=[];window.dispatchEvent(new CustomEvent('sw:diagnostic'));},events:()=>buffer.slice()};
  window.SW=analytics;activate();if(!loaded)event('page_view');
  if(id&&choice==='unset'&&!privacySignal)privacyPanel();
  document.addEventListener('click',e=>{
    const el=e.target.closest('a,button');if(!el)return;
    if(el.matches('[data-privacy]')){e.preventDefault();privacyPanel();}
    if(el.matches('a[href*="github.com/tianxinzh/simulated-world"]'))event('github_click');
    if(el.matches('a[download]'))event('download',{world:el.dataset.world||'unknown'});
    if(el.matches('[data-language-link]'))event('language_change');
  });

  const sessions=new Map();
  function attach(frame,world,entry='world_page'){
    if(sessions.has(frame)||!['bayport','bayline'].includes(world))return;
    const state={frame,world,release:world==='bayport'?'2.1':'1.0',entry_point:entry,started:performance.now(),ready:false,interaction:false,seconds:0,viewed:false,engaged:false,onScreen:false,last:performance.now()};
    const params=()=>({world,release:state.release,entry_point:entry});
    sessions.set(frame,state);event('world_open',params());
    const observer=new IntersectionObserver(entries=>{state.onScreen=entries[0].isIntersecting&&entries[0].intersectionRatio>=.25;},{threshold:[0,.25]});observer.observe(frame);state.observer=observer;
    state.timer=setInterval(()=>{
      if(!frame.isConnected){detach(frame);return;}
      const now=performance.now(),delta=Math.min(2,(now-state.last)/1000);state.last=now;
      if(state.ready&&state.onScreen&&!document.hidden)state.seconds+=delta;
      if(!state.ready&&!state.timedOut&&now-state.started>45000){state.timedOut=true;event('world_error',{...params(),error_code:'load_timeout'});}
      if(state.seconds>=60&&!state.viewed){state.viewed=true;event('watched_play',{...params(),visible_seconds:state.seconds});}
      if(state.seconds>=60&&state.interaction&&!state.engaged){state.engaged=true;event('engaged_play',{...params(),visible_seconds:state.seconds});}
    },500);
    frame.addEventListener('load',()=>{try{frame.contentWindow.postMessage({type:'sw:hello'},location.origin);}catch{}});
    return state;
  }
  function detach(frame){const s=sessions.get(frame);if(!s)return;clearInterval(s.timer);s.observer.disconnect();if(s.ready)event('world_end',{world:s.world,entry_point:s.entry_point,visible_seconds:s.seconds});sessions.delete(frame);}
  window.SWPlayer={attach,detach};
  window.addEventListener('message',e=>{
    if(e.origin!==location.origin||!e.data||e.data.type!=='sw:world')return;
    const s=[...sessions.values()].find(x=>x.frame.contentWindow===e.source&&x.world===e.data.world);if(!s)return;
    const base={world:s.world,release:s.release,entry_point:s.entry_point};
    if(e.data.event==='ready'&&!s.ready){s.ready=true;event('world_ready',{...base,load_ms:performance.now()-s.started});s.frame.parentElement?.querySelector('[data-player-status]')?.replaceChildren(document.createTextNode(text('Ready. The physical tabletop controls are interactive.','加载完成，可操作桌前实体控制台。')));}
    else if(e.data.event==='interaction'&&s.ready&&!s.interaction){s.interaction=true;event('world_interaction',{...base,control:e.data.control||'control'});}
    else if(e.data.event==='error'&&!s.failed){s.failed=true;event('world_error',{...base,error_code:'scene_error'});}
  });
  document.querySelectorAll('[data-player]').forEach(shell=>{
    const world=shell.dataset.player,btn=shell.querySelector('[data-play]'),slot=shell.querySelector('[data-player-slot]');let frame=null;
    const stop=shell.querySelector('[data-stop]'),full=shell.querySelector('[data-fullscreen]');
    btn?.addEventListener('click',()=>{
      if(frame)return;frame=document.createElement('iframe');frame.title=(world==='bayport'?'BAYPORT':'BAYLINE')+text(' interactive miniature','互动沙盘');frame.allow='fullscreen';frame.setAttribute('allowfullscreen','');frame.referrerPolicy='same-origin';
      frame.src=root+(world==='bayport'?'airport.html':'bayline.html')+'?embed=1&lang='+(zh?'zh':'en');
      slot.replaceChildren(frame);attach(frame,world);btn.hidden=true;stop.hidden=false;full.hidden=false;
      shell.querySelector('[data-player-status]').textContent=text('Loading Three.js and building the world…','正在加载 Three.js 并构建沙盘……');
    });
    stop?.addEventListener('click',()=>{if(!frame)return;detach(frame);frame.remove();frame=null;const img=document.createElement('img');img.src=root+'assets/previews/'+world+'.webp';img.alt=text('Simulator preview','模拟器预览');img.width=1440;img.height=900;slot.replaceChildren(img);btn.hidden=false;stop.hidden=true;full.hidden=true;shell.querySelector('[data-player-status]').textContent=text('Stopped. Press Play to start again.','已停止，点击开始可重新游玩。');});
    full?.addEventListener('click',async()=>{try{await slot.requestFullscreen();}catch{shell.querySelector('[data-player-status]').textContent=text('Use the direct-open link below for a larger view.','请使用下方直接打开链接进入大画面。');}});
  });
  const mutation=new MutationObserver(()=>{for(const [frame]of sessions)if(!frame.isConnected)detach(frame);});mutation.observe(document.body,{childList:true,subtree:true});
  document.querySelectorAll('[data-share]').forEach(b=>b.addEventListener('click',async()=>{
    const url=document.querySelector('link[rel="canonical"]')?.href||cleanURL(location.href);const out=document.querySelector('[data-share-status]');
    try{if(navigator.share){await navigator.share({title:document.title,url});event('share',{method:'native'});}else{await navigator.clipboard.writeText(url);event('share',{method:'clipboard'});}if(out)out.textContent=text('Link shared or copied.','链接已分享或复制。');}catch(e){if(e.name!=='AbortError'&&out)out.textContent=url;}
  }));
  const tool=document.getElementById('campaign-form');
  if(tool){tool.addEventListener('submit',e=>{e.preventDefault();const fd=new FormData(tool);const url=new URL(root+'worlds/'+fd.get('world')+'/',location.origin);for(const name of ['source','medium','campaign','content']){const value=String(fd.get(name)||'').trim().toLowerCase();if(value&&!/^[a-z0-9_.-]{1,64}$/.test(value)){document.getElementById('campaign-result').textContent='Use letters, digits, dots, hyphens or underscores; never personal information.';return;}if(value)url.searchParams.set('utm_'+name,value);}document.getElementById('campaign-result').textContent=url.href;});document.getElementById('copy-campaign')?.addEventListener('click',async()=>{try{await navigator.clipboard.writeText(document.getElementById('campaign-result').textContent);}catch{}});}
  if(document.getElementById('integration-status')){
    const render=()=>{document.getElementById('integration-status').textContent=JSON.stringify({...analytics.status(),searchConsoleTagPresent:!!cfg.googleVerification,bingTagPresent:!!cfg.bingVerification,ownershipVerification:'Must be completed in each provider account; a tag is not proof of verification.'},null,2);document.getElementById('event-log').textContent=JSON.stringify(buffer,null,2);};
    window.addEventListener('sw:diagnostic',render);document.getElementById('debug-enable').onclick=()=>analytics.debug(true);document.getElementById('debug-disable').onclick=()=>analytics.debug(false);render();
  }
})();
