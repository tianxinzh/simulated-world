#!/usr/bin/env python3
"""Build the static discovery site. No network access or third-party Python packages.
Edit the content/configuration here, run this script, and deploy the generated pages.
Simulator changes are limited to metadata, language entry and local parent messages.
"""
from pathlib import Path
from urllib.parse import urlsplit
from html import escape, unescape
import hashlib, json, os, re

ROOT=Path(__file__).resolve().parents[1]
os.chdir(ROOT)
cfg=json.loads(Path('site-config.json').read_text())
for env,key in [('SW_GA4_ID','measurementId'),('SW_GSC_TOKEN','googleVerification'),('SW_BING_TOKEN','bingVerification')]:
    if os.environ.get(env): cfg[key]=os.environ[env].strip()
BASE=cfg['baseUrl'].rstrip('/')+'/'
u=urlsplit(BASE)
assert u.scheme=='https' and u.netloc and not u.query and not u.fragment, 'Use an HTTPS base URL without query or fragment'
PREFIX=u.path
assert re.fullmatch(r'/(?:[A-Za-z0-9_-]+/)*',PREFIX), 'Unsupported site base path'
assert not cfg['measurementId'] or re.fullmatch(r'G-[A-Z0-9]{6,20}',cfg['measurementId']), 'Invalid GA4 measurement ID'
for key in ['googleVerification','bingVerification']:
    assert not cfg[key] or re.fullmatch(r'[A-Za-z0-9_-]{8,200}',cfg[key]), 'Enter the verification content value, not an HTML tag'
DATE=cfg['contentDate']
REPO='https://github.com/tianxinzh/simulated-world'
index=[]
def write(path,data):
    p=Path(path);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(data,encoding='utf-8')
def j(data): return json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')
def choose(en,cn,zh): return cn if zh else en
def local(route='',zh=False): return PREFIX+('zh/' if zh else '')+route
def absolute(route='',zh=False): return BASE+('zh/' if zh else '')+route
def anchor(route,label,zh=False): return f'<a href="{local(route,zh)}">{escape(label)}</a>'
def paras(*items): return ''.join('<p>'+s+'</p>' for s in items)

def metadata(title,desc,route='',zh=False,kind='WebPage',noindex=False):
    url=absolute(route,zh);lang='zh-Hans' if zh else 'en'
    schema=[{'@context':'https://schema.org','@type':kind,'@id':url+'#page','name':title,'description':desc,'url':url,'inLanguage':lang,'dateModified':DATE,'isPartOf':{'@id':BASE+'#website'},'publisher':{'@id':BASE+'#publisher'}}]
    if route:
        schema.append({'@context':'https://schema.org','@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':1,'name':'Simulated World','item':absolute('',zh)},{'@type':'ListItem','position':2,'name':title,'item':url}]})
    else:
        schema.extend([{'@context':'https://schema.org','@type':'WebSite','@id':BASE+'#website','name':'Simulated World','url':BASE,'inLanguage':['en','zh-Hans']},{'@context':'https://schema.org','@type':'Organization','@id':BASE+'#publisher','name':'Simulated World','url':BASE,'sameAs':[REPO]}])
    if route.startswith('worlds/'):
        name='BAYPORT' if 'bayport' in route else 'BAYLINE'
        schema.append({'@context':'https://schema.org','@type':'WebApplication','name':name,'url':url,'description':desc,'applicationCategory':'EntertainmentApplication','operatingSystem':'Web browser with WebGL','isAccessibleForFree':True,'license':REPO+'/blob/main/LICENSE','creator':{'@id':BASE+'#publisher'},'screenshot':BASE+'assets/previews/'+name.lower()+'.webp'})
    result=f'<meta name="description" content="{escape(desc,quote=True)}">\n<link rel="canonical" href="{url}">\n'
    if not noindex:
        result+=f'<link rel="alternate" hreflang="en" href="{absolute(route)}">\n<link rel="alternate" hreflang="zh-Hans" href="{absolute(route,True)}">\n<link rel="alternate" hreflang="x-default" href="{absolute(route)}">\n'
    result+=f'<meta name="robots" content="{ "noindex,follow" if noindex else "index,follow,max-image-preview:large" }">\n'
    result+=f'<meta property="og:type" content="website"><meta property="og:title" content="{escape(title,quote=True)}"><meta property="og:description" content="{escape(desc,quote=True)}"><meta property="og:url" content="{url}"><meta property="og:image" content="{BASE}assets/previews/bayport.webp"><meta name="twitter:card" content="summary_large_image">\n'
    for key,name in [('googleVerification','google-site-verification'),('bingVerification','msvalidate.01')]:
        if cfg[key]: result+=f'<meta name="{name}" content="{escape(cfg[key],quote=True)}">\n'
    return result+'<script type="application/ld+json">'+j(schema)+'</script>\n'

def scripts():
    return f'<script defer src="{PREFIX}assets/site-config.js?v=growth-1"></script><script defer src="{PREFIX}assets/growth.js?v=growth-1"></script>'

def header(route,zh):
    return f'''<a class="skip" href="#content">{choose('Skip to content','跳转到正文',zh)}</a><header class="growth-header"><div class="wrap growth-nav"><a class="wordmark" href="{local('',zh)}">SIMULATED WORLD</a><nav aria-label="{choose('Main navigation','主导航',zh)}"><a href="{local('worlds/bayport/',zh)}">BAYPORT</a><a href="{local('worlds/bayline/',zh)}">BAYLINE</a><a href="{local('guides/',zh)}">{choose('Field guides','探索指南',zh)}</a><a href="{local('about/',zh)}">{choose('The workshop','关于工坊',zh)}</a><a data-language-link href="{local(route,not zh)}" lang="{'en' if zh else 'zh-CN'}">{'EN' if zh else '中文'}</a></nav></div></header>'''

def footer(zh):
    return f'''<footer class="growth-footer"><div class="wrap"><span>© 2026 Simulated World</span><a href="{local('about/',zh)}">{choose('About & source','关于与源代码',zh)}</a><a href="{local('privacy/',zh)}">{choose('Privacy','隐私',zh)}</a><button class="text-button" type="button" data-privacy>{choose('Analytics choices','统计设置',zh)}</button><a href="{PREFIX}sitemap.xml">Sitemap</a><a href="{REPO}">GitHub</a></div></footer>'''

def page(route,title,desc,body,zh=False,noindex=False,kind='WebPage'):
    lang='zh-CN' if zh else 'en'
    html=f'''<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name="theme-color" content="#142328"><title>{escape(title)}</title>{metadata(title,desc,route,zh,kind,noindex)}<link rel="icon" href="{PREFIX}assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="{PREFIX}assets/home.css"><link rel="stylesheet" href="{PREFIX}assets/growth.css?v=growth-1">{scripts()}</head><body>{header(route,zh)}<main id="content" class="growth-main"><p class="breadcrumbs">{anchor('', 'Simulated World',zh)} / {escape(title.split(' | ')[0])}</p><div class="eyebrow">THE LITTLE WORLDS COLLECTION</div><h1>{escape(title.split(' | ')[0])}</h1><p class="lead">{escape(desc)}</p>{body}</main>{footer(zh)}</body></html>'''
    write(('zh/' if zh else '')+route+'index.html',html)
    if not noindex:index.append({'route':route,'zh':zh,'url':absolute(route,zh),'title':title})

def player(world,zh):
    raw='airport.html' if world=='bayport' else 'bayline.html'
    return f'''<section class="player-shell" data-player="{world}" aria-label="{world.upper()} player"><div class="player-screen" data-player-slot><img src="{PREFIX}assets/previews/{world}.webp" width="1440" height="900" alt="{choose('Actual '+world.upper()+' miniature world on its wooden table',world.upper()+' 木桌微缩模型实际运行画面',zh)}" fetchpriority="high"></div><div class="player-toolbar"><div class="actions"><button class="button primary" data-play type="button">{choose('Play '+world.upper(),'开始游玩 '+world.upper(),zh)} ↗</button><button class="button secondary" data-fullscreen type="button" hidden>{choose('Fullscreen','全屏',zh)}</button><button class="button secondary" data-stop type="button" hidden>{choose('Stop & unload','停止并卸载',zh)}</button><button class="button secondary" data-share type="button">{choose('Share this world','分享世界',zh)}</button></div><p data-player-status role="status">{choose('Click Play to load the interactive world. No account or install needed.','点击开始后加载互动场景，无需注册或安装。',zh)}</p><p data-share-status role="status"></p><p class="quiet-note"><a href="{PREFIX}{raw}?lang={'zh' if zh else 'en'}">{choose('Open the standalone scene','直接打开独立场景',zh)}</a> · <a download href="{PREFIX}{raw}" data-world="{world}">{choose('Download single HTML','下载单文件 HTML',zh)}</a> · {choose('WebGL and internet for Three.js required.','需要 WebGL 与加载 Three.js 的网络连接。',zh)}</p><noscript><p>{choose('JavaScript is required for the simulator, but this guide remains readable.','模拟器需要 JavaScript，但本页指南仍可阅读。',zh)}</p></noscript></div></section>'''

def table(rows,zh):
    return '<div class="table-scroll"><table><thead><tr><th>'+choose('Control','控件',zh)+'</th><th>'+choose('What it does','作用',zh)+'</th><th>'+choose('Shortcut','快捷键',zh)+'</th></tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+escape(x)+'</td>' for x in row)+'</tr>' for row in rows)+'</tbody></table></div>'

def related(zh):
    return '<h2>'+choose('Keep exploring','继续探索',zh)+'</h2><div class="actions">'+anchor('worlds/bayport/','BAYPORT',zh)+anchor('worlds/bayline/','BAYLINE',zh)+anchor('guides/',choose('All field guides','全部指南',zh),zh)+'</div>'

CONTROLS={
 'bayport':([
 ('Traffic lever','Drag up or down to change all traffic speed. Space pauses without changing the chosen setting.','↑ / ↓; Space'),('Time dial','Click through day, sunset, night and dawn, or drag to scrub. Double-click restores automatic cycling.','N; A for auto'),('Airfield switch','Enable or disable runway and taxiway lights; enabled lights brighten as the sky darkens.','L'),('City button','Toggle terminal, city, street and bridge lighting.','B'),('Departure button','Release the waiting plane, or queue its next departure. Rescue activity holds new clearances.','R or T'),('Fire rescue','Dispatch the fire truck on its assigned response route. It then returns to normal.','E')],[
 ('交通推杆','上下拖动调节交通速度。空格暂停时保留速度设置。','↑ / ↓；空格'),('日夜旋钮','点击切换白天、黄昏、夜晚和黎明；拖动自由调节；双击恢复自动循环。','N；A 恢复自动'),('跑道灯开关','开启或关闭跑道和滑行道灯；开启后随天色变暗而增强。','L'),('城市灯按钮','切换航站楼、城市、道路及桥梁灯光。','B'),('起飞按钮','放行等待中的飞机，或将下一次起飞加入队列；消防响应时暂缓新的许可。','R 或 T'),('消防救援','消防车沿预定路线出动，然后返回。','E')]),
 'bayline':([
 ('Red throttle','Drag to change the speed of both mainline trains.','↑ / ↓'),('Lighting toggle','Cycle automatic, always-on and off.','L'),('Day / night','Smoothly switch the scene toward day or night.','N'),('Turntable','Index the turntable toward the next roundhouse stall.','R'),('Port machinery','Pause or resume harbor crane and vehicle activity.','P'),('Horn','Play a synthesized three-note horn after interacting.','H'),('Emergency stop','Stop or resume trains without freezing the bay or sky.','Space')],[
 ('红色牵引杆','拖动调节两列主线列车的速度。','↑ / ↓'),('灯光开关','依次切换自动、常亮及关闭。','L'),('昼夜切换','平滑过渡至白天或夜晚。','N'),('转车台','转向下一个机库泊位。','R'),('港口机械','暂停或恢复吊机及港口车辆。','P'),('鸣笛','交互后播放程序合成的三音汽笛。','H'),('列车急停','停止或恢复列车，不冻结海湾和天空。','空格')])}

for zh in [False,True]:
    for world in ['bayport','bayline']:
        airport=world=='bayport';name=world.upper()
        title=choose('Free Online Miniature Airport Simulator — BAYPORT' if airport else 'Virtual Model Railway in Your Browser — BAYLINE','免费在线微缩机场模拟器 — BAYPORT' if airport else '浏览器里的虚拟模型铁路 — BAYLINE',zh)
        desc=choose('Explore a Bay Area-inspired miniature airport on an oak table. Watch takeoffs, landings and ground traffic, and operate six physical controls. Free in your browser.' if airport else 'Follow two trains around a San Francisco-inspired tabletop railway. Work the throttle, turn the roundhouse and light the harbor. Free to explore in your browser.','在橡木桌上的湾区风格机场沙盘中观看起飞、降落和地面交通，操作六个实体控件，无需安装即可免费探索。' if airport else '跟随两列火车环游旧金山风格的桌面铁路，调节牵引速度、转动机库转车台并点亮港口，在浏览器中免费探索。',zh)
        explanation=choose('BAYPORT is an interactive airport diorama, not a cockpit flight simulator. Aircraft follow predefined routes while you control the pace, lighting and selected airport operations. There are no scores, purchases or accounts to unlock the scene.' if airport else 'BAYLINE is a virtual model railway layout, not a first-person train-driving game. Two mainline trains run through a compressed Bay Area scene with a yard, roundhouse, station, town and harbor. You control the layout rather than steer a locomotive through a realistic timetable.','BAYPORT 是互动机场沙盘，而非驾驶舱飞行模拟器。飞机沿预设路线运行，你可以调节节奏、灯光及部分机场操作。无需积分、付费或账户即可探索。' if airport else 'BAYLINE 是虚拟模型铁路布局，而非第一人称列车驾驶游戏。两列主线火车穿过经过压缩的湾区场景，沿途包括车场、机库、车站、小镇和港口。你控制的是沙盘，而不是按真实时刻表驾驶机车。',zh)
        facts=[(choose('World','世界',zh),name),(choose('Creator / source','发布者 / 源代码',zh),'Simulated World · tianxinzh / GitHub'),(choose('Price','价格',zh),choose('Free; no account','免费，无需账户',zh)),(choose('Controls','控件',zh),choose('Mouse, keyboard and touch','鼠标、键盘与触屏',zh)),(choose('Requirements','要求',zh),choose('Modern browser, WebGL, internet for Three.js','现代浏览器、WebGL、加载 Three.js 的网络',zh)),(choose('Layout','布局',zh),choose('Artistic, not a real airport or rail map','艺术化布局，并非真实机场或铁路地图',zh))]
        body=player(world,zh)+'<div class="growth-columns"><section><h2>'+choose('What can you do?','可以怎么玩？',zh)+'</h2>'+paras(explanation,choose('Begin at the front edge of the table. Drag empty space to orbit and use the scroll wheel to get closer. Try a physical control, then switch to night to see the miniature lighting. Press 0 to return to the opening view.','从桌子前沿开始，拖动空白区域环视，滚轮缩放。尝试操作实体控制台，再切换到夜晚欣赏微缩灯光。按 0 返回初始视角。',zh))+anchor('guides/'+world+'-controls/',choose('Read the complete controls and layout guide →','阅读完整操作与布局指南 →',zh))+'</section><aside class="fact-card"><h2>'+choose('At a glance','速览',zh)+'</h2><dl>'+''.join('<dt>'+escape(a)+'</dt><dd>'+escape(b)+'</dd>' for a,b in facts)+'</dl></aside></div>'
        body+='<h2>'+choose('Before you play','开始之前',zh)+'</h2>'
        for q,a in [(choose('Is this the real San Francisco airport?','这是真实的旧金山机场吗？',zh) if airport else choose('Does this reproduce an actual railway?','这是真实铁路的复刻吗？',zh),choose('No. Geography, infrastructure and distances are artistically compressed to fit the tabletop. This is not a navigation map or operational training tool.','不是。地理、基础设施和距离经过艺术化压缩以适配桌面。这不是导航地图或专业操作训练工具。',zh)),(choose('Can I run it locally?','可以在本地运行吗？',zh),choose('Yes. Download the single HTML and open it in Chrome. It still needs an internet connection to load Three.js. Models, materials and synthesized audio are generated inside that file. The download does not include an analytics tag.','可以。下载单文件 HTML 并用 Chrome 打开。仍需网络加载 Three.js，模型、材质与合成声音由文件内代码生成，下载版不包含统计标签。',zh)),(choose('What if the screen stays blank?','画面空白怎么办？',zh),choose('Allow JavaScript and WebGL, check hardware acceleration, and make sure the Three.js CDN is reachable. Stop the player before retrying. On a narrow screen, fullscreen gives the physical controls more room.','请允许 JavaScript 与 WebGL，检查硬件加速及 Three.js CDN 的网络连接。停止播放器后再重试。窄屏下可使用全屏，让实体控件有更多空间。',zh))]:
            body+='<details><summary>'+q+'</summary><p>'+a+'</p></details>'
        body+=related(zh);page('worlds/'+world+'/',title,desc,body,zh)
        gtitle=choose(name+' Controls & Tabletop Layout Guide',name+' 操作与沙盘布局指南',zh)
        gdesc=choose('A practical guide to the physical controls, keyboard shortcuts and miniature layout. Learn what changes, what keeps running, and how to reset the view.','实体控件、键盘快捷键与微缩布局实用指南：了解哪些操作会改变场景、哪些动画会继续运行，以及如何恢复视角。',zh)
        gbody=table(CONTROLS[world][int(zh)],zh)
        gbody+='<h2>'+choose('A first visit to the layout','第一次探索沙盘',zh)+'</h2>'+paras(choose('Start with the traffic moving slowly. The runway and taxiway system is separated from the terminal frontage and road traffic. Watch one aircraft approach while another completes its own circuit. At the gates, jetbridges retract for pushback rather than following aircraft across the apron. The fire response is a short demonstration along a reserved route, not an airport emergency-training scenario.' if airport else 'Start with a moderate throttle. Watch how the two trains pass the station, cross the bridge and return around their separate mainline loops. The yard and roundhouse add a workshop scene; the turntable control selects the next stall. Pause the trains and notice that the bay and port can remain active. This separates railway dispatch controls from the rest of the miniature world.','先调低交通速度。跑道、滑行道与航站楼前道路各自分区。观察一架飞机进近、另一架完成飞行环路；登机口的廊桥会为推出操作收回，而不会跟随飞机横穿停机坪。消防响应沿专用路线进行，是沙盘演示而非机场应急训练。' if airport else '先使用中等牵引速度。观察两列火车经过车站、穿过桥梁并沿各自主线返回。车场与机库营造模型工坊氛围，转车台按钮用于选择下一个泊位。暂停列车后，海湾与港口仍可保持活动，铁路调度与其他沙盘机械可以分别控制。',zh),choose('Next, compare daytime and night. Look at building windows, street lighting and the bridge, not just the moving vehicles. The physical controls are part of the model: click buttons and switches, and drag the lever instead of dragging the surrounding scenery. Hover hints explain each control.','再比较白天与夜景。不只看移动的交通工具，也留意建筑窗户、路灯及桥梁。控件本身就是模型的一部分：点击按钮与开关，拖动推杆，而非周围的场景。悬停提示会解释各个控件。',zh))
        gbody+='<h2>'+choose('Camera, sound and language','视角、声音与语言',zh)+'</h2>'+paras(choose('Drag empty space to orbit, scroll to zoom, and hold Shift while dragging to pan. Press 0 for the opening view, C for an unobstructed view, and ? for the in-scene guide. Touch supports pinch zoom. Select the sound button to enable locally synthesized audio; no recording is downloaded. Use the EN / 中文 control to change the interface.','拖动空白区域环视，滚轮缩放，按住 Shift 拖动平移。0 返回初始视角，C 隐藏界面，? 打开场景内指南。触屏支持双指缩放。点击声音按钮开启本地合成音效，无需下载音频。使用 EN / 中文 控件切换界面。',zh),choose('Controls are easiest to distinguish on a desktop or in fullscreen. If a keyboard shortcut does not act on the world, focus the canvas first; a focused website button can consume Space as a normal button activation. Reloading starts a fresh layout session.','桌面端或全屏模式更容易分辨控件。快捷键无效时，请先聚焦画布；网页按钮获得焦点后，空格可能会激活按钮而非控制场景。刷新页面会开始新的沙盘会话。',zh))
        gbody+='<div class="actions">'+anchor('worlds/'+world+'/',choose('Play '+name+' →','进入 '+name+' →',zh))+'</div>'+related(zh)
        page('guides/'+world+'-controls/',gtitle,gdesc,gbody,zh,kind='Article')

    btitle=choose('How the Three.js Miniature Worlds Are Built','Three.js 微缩世界是如何构建的',zh)
    bdesc=choose('A source-level tour of procedural geometry, instanced details, safe routes and tactile controls in BAYPORT and BAYLINE.','从源代码理解 BAYPORT 与 BAYLINE 的程序化几何体、实例化细节、预定路线和可交互实体控件。',zh)
    bbody='<h2>'+choose('One HTML per world','每个世界一个 HTML 文件',zh)+'</h2>'+paras(choose('Each simulator contains its scene logic, styles and generated assets in one HTML file. The only remote runtime library inside the standalone worlds is Three.js. The surrounding website has separate styles, guides and optional analytics; that layer is deliberately separate from the downloadable scenes.','每个模拟器在一个 HTML 文件内包含场景逻辑、样式和生成素材。独立场景唯一的远程运行库是 Three.js。外围网站的样式、指南与可选统计独立维护，不混入下载版场景。',zh))
    bbody+='<h2>'+choose('Geometry instead of downloaded models','用几何体代替下载模型',zh)+'</h2>'+paras(choose('Aircraft, trains, buildings and scenery are assembled from small geometric pieces. CanvasTexture supplies generated labels and wood grain. Repeated static pieces are batched with InstancedMesh; moving assemblies are grouped so their components follow a shared transform. That makes one airplane behave as an object rather than a collection of independently animated windows and wings.','飞机、火车、建筑及景观由基础几何体拼装。CanvasTexture 生成标签和木纹；重复静态细节使用 InstancedMesh 批处理；移动部件以组共享变换。一架飞机因此作为整体移动，而不是分别驱动每个窗口和机翼。',zh))
    bbody+='<h2>'+choose('Routes are designed before motion','先规划路线，再添加运动',zh)+'</h2>'+paras(choose('The scenes use predefined paths rather than unrestricted navigation. Separate movement corridors and reserved footprints help keep vehicles away from buildings. BAYPORT exposes a safety snapshot for regression tests. A sampled collision check is useful evidence, but it is not a mathematical guarantee that every possible frame or camera action has been covered.','场景采用预设路线，而非不受限制的自主导航。独立运动通道与预留建筑占地有助于避免车辆进入建筑。BAYPORT 提供 safety snapshot 用于回归测试。采样碰撞检查有参考价值，但并不代表对所有帧和视角操作的数学保证。',zh))
    bbody+='<h2>'+choose('The control panel is real scene geometry','控制台是真实场景几何体',zh)+'</h2>'+paras(choose('A raycaster connects a screen-space pointer to the physical lever, knobs and buttons. Drag state distinguishes a control adjustment from a camera movement. requestAnimationFrame drives motion, lighting and rendering. Resize handling updates the renderer and camera so the model remains usable on different screens.','Raycaster 将屏幕指针映射到实体推杆、旋钮与按钮；拖拽状态用于区分控件调整和视角移动。requestAnimationFrame 驱动运动、灯光和绘制。窗口大小变化时更新渲染器与相机，使不同屏幕仍可使用模型。',zh))
    bbody+='<h2>'+choose('Inspect and reuse the source','查看与复用源代码',zh)+'</h2>'+paras(f'<a href="{REPO}/blob/main/airport.html">airport.html</a> · <a href="{REPO}/blob/main/bayline.html">bayline.html</a> · <a href="{REPO}/blob/main/LICENSE">MIT license</a>',choose('Start by adjusting a color, an initial camera value or a generated sign. When changing geometry sizes, review route clearances and the control hit targets as well. Retain the MIT license notice when reusing the code.','可以先修改配色、相机初始值或程序化路牌。调整几何尺寸时，也应检查路线净空与控件点击区域。复用代码时保留 MIT 许可声明。',zh),'<a href="https://threejs.org/docs/#api/en/objects/InstancedMesh">Three.js: InstancedMesh</a> · <a href="https://threejs.org/docs/#api/en/textures/CanvasTexture">CanvasTexture</a> · <a href="https://threejs.org/docs/#api/en/core/Raycaster">Raycaster</a>')+related(zh)
    page('guides/how-built/',btitle,bdesc,bbody,zh,kind='Article')

    ttitle=choose('BAYPORT Day-to-Night Airport Tour','BAYPORT 机场昼夜漫游',zh)
    tdesc=choose('A short visual tour of the same miniature airport through daylight, sunset, night and dawn. Then try the time dial yourself.','沿白天、黄昏、夜晚和黎明探索同一座微缩机场，再亲自尝试日夜旋钮。',zh)
    tbody=''
    if Path('assets/tours/bayport-tour.webm').exists():
        tbody+=f'<video controls muted playsinline preload="none" poster="{PREFIX}assets/previews/bayport.webp" aria-label="{escape(ttitle)}"><source src="{PREFIX}assets/tours/bayport-tour.webm" type="video/webm">{choose("Your browser does not support this video.","浏览器不支持此视频。",zh)}</video><p class="quiet-note">{choose("Recorded from the running simulator. The four lighting stages are selected for demonstration; the automatic cycle is longer. No spoken audio.","录制自运行中的模拟器，四种灯光阶段为演示而切换，自动昼夜循环更长。视频无口述音轨。",zh)}</p>'
    else: tbody+=f'<img src="{PREFIX}assets/previews/bayport.webp" width="1440" height="900" style="width:100%;height:auto;border-radius:12px" alt="{escape(ttitle)}">'
    for h,p in [
      (choose('Daylight: follow the movement','白天：跟随交通',zh),choose('Start with the twin runways and apron. Watch which aircraft are taxiing, which are parked and which are airborne. Vehicles follow their own ground routes; the roads and harbor keep the wider miniature world moving.','先观察双跑道与停机坪，区分滑行、停靠和空中的飞机。车辆沿地面路线行驶，道路与港口让整个微缩世界持续运转。',zh)),
      (choose('Sunset: keep the tabletop in view','黄昏：保留桌面视角',zh),choose('Use the time dial to change the mood without changing the layout. Keep a little of the oak rim and control console in the frame: those details make the airport feel like a physical exhibit rather than an aerial map.','日夜旋钮可以在不改变布局的情况下切换氛围。画面中保留一些橡木边缘与控制台细节，更能呈现实体展览模型的感觉，而非航拍地图。',zh)),
      (choose('Night: compare two lighting systems','夜晚：比较两组灯光',zh),choose('Toggle the airfield lights separately from the city lights. Runway and taxiway lighting emphasizes the aircraft routes; building, street and bridge lights reveal the surrounding town. Look for navigation and flashing aircraft lights as the traffic passes.','分别切换机场灯和城市灯。跑道与滑行道灯突出飞机路线，建筑、路灯与桥梁灯勾勒周边小镇。交通经过时，可留意飞机导航灯与闪烁灯。',zh)),
      (choose('Dawn: reset and explore again','黎明：重新开始探索',zh),choose('Press A to restore automatic day-night cycling, or drag the dial to choose a time. Press 0 to reset the camera. The layout is designed for quiet exploration rather than winning a level, so there is no required order for the tour.','按 A 恢复自动昼夜循环，或拖动旋钮自由选择时间；按 0 恢复视角。沙盘适合自由探索，而非闯关，漫游没有固定顺序。',zh))]:tbody+='<h2>'+h+'</h2>'+paras(p)
    tbody+='<div class="actions">'+anchor('worlds/bayport/',choose('Try the time dial in BAYPORT →','进入 BAYPORT 尝试日夜旋钮 →',zh))+'</div>'+related(zh)
    page('guides/bayport-day-night/',ttitle,tdesc,tbody,zh,kind='Article')

    guidecards=[('bayport-controls',choose('BAYPORT controls & layout','BAYPORT 操作与布局',zh),choose('Traffic, time of day, departures and rescue.','交通、昼夜、起飞与消防。',zh)),('bayline-controls',choose('BAYLINE controls & layout','BAYLINE 操作与布局',zh),choose('Throttle, roundhouse, harbor and lighting.','牵引、机库、港口与灯光。',zh)),('how-built',btitle,bdesc),('bayport-day-night',ttitle,tdesc)]
    cards='<div class="growth-grid">'+''.join('<article class="growth-card"><h2>'+anchor('guides/'+r+'/',t,zh)+'</h2><p>'+d+'</p></article>' for r,t,d in guidecards)+'</div>'
    page('guides/',choose('Field Guides to the Miniature Worlds','微缩世界探索指南',zh),choose('Learn the controls, explore the layouts and look inside the code. Every guide leads back to a playable world.','学习操作、探索布局并查看代码。每篇指南都链接到可游玩的世界。',zh),cards,zh,kind='CollectionPage')

    abody='<h2>'+choose('A world on your table','把世界摆在桌上',zh)+'</h2>'+paras(choose('Simulated World is a collection of free, browser-based interactive miniature worlds. BAYPORT is a Bay Area-inspired airport diorama; BAYLINE is a San Francisco-inspired model railway. Both pair moving infrastructure with physical tabletop controls and a day-night cycle.','Simulated World 是免费浏览器互动微缩世界合集。BAYPORT 是湾区风格机场沙盘，BAYLINE 是旧金山风格模型铁路，两者均将动态基础设施、实体桌面控件与昼夜循环结合。',zh),choose('The public project is published under the GitHub account tianxinzh. The code is open source under the MIT license. The scenes have been developed through an AI-assisted workflow and iterative browser testing; they are creative software exhibits, not professionally certified aviation or railway tools.','公开项目由 GitHub 账户 tianxinzh 发布，代码采用 MIT 许可证。场景通过 AI 辅助开发与迭代浏览器测试制作，属于创意软件展品，而非经专业认证的航空或铁路工具。',zh),choose('The website and downloadable worlds have different jobs. The website explains and links the collection; the standalone HTML files contain the worlds themselves. This separation keeps the original single-file experience usable without a website account or analytics dependency.','网站与下载版分工不同：网站用于说明和发现作品，独立 HTML 文件承载世界本身。这使原有单文件体验不依赖网站账户或统计服务。',zh))
    abody+='<h2>'+choose('Limits and feedback','局限与反馈',zh)+'</h2>'+paras(choose('Landmarks, distances and routes are artistically rearranged. Performance depends on your device and browser. Open an issue for broken controls, rendering errors or ideas, and include the world name and browser version. Do not post passwords, personal data or access tokens in public issues.','地标、距离和路线经过艺术化调整，性能受设备与浏览器影响。发现控件失效、绘制错误或有新想法时，可以创建 issue，并注明世界名称与浏览器版本。不要在公开 issue 中发布密码、个人资料或访问令牌。',zh),f'<a href="{REPO}">GitHub repository</a> · <a href="{REPO}/issues">Feedback / 问题反馈</a>')+related(zh)
    page('about/',choose('About Simulated World & the Workshop','关于 Simulated World 与微缩工坊',zh),choose('Free interactive airport and model railway dioramas, published as open-source browser experiments.','免费互动机场与模型铁路沙盘，以开源浏览器实验作品的形式发布。',zh),abody,zh)

    pbody='<p class="quiet-note">'+choose('Notice updated: ','说明更新日期：',zh)+DATE+'</p>'
    pbody+='<h2>'+choose('What happens when you visit','访问时会发生什么',zh)+'</h2>'+paras(choose('Pages and images are served by GitHub Pages. Playing a world requests Three.js from a CDN; those infrastructure providers receive normal network request information such as your IP address and user agent. The standalone worlds do not load analytics or advertising scripts.','页面与图片由 GitHub Pages 提供。开始游玩时从 CDN 加载 Three.js，这些基础设施提供者会收到正常网络请求信息，例如 IP 地址与浏览器标识。独立世界不加载统计或广告脚本。',zh))
    pbody+='<h2>'+choose('Optional traffic analytics','可选流量统计',zh)+'</h2>'+paras(choose('The hosted website includes an optional Google Analytics 4 integration. It is inactive until the site operator configures a measurement ID. Even when configured, its tag is not loaded before you allow analytics. Declining does not restrict playing. This site also honors Global Privacy Control and Do Not Track by disabling optional analytics.','托管网站包含可选 Google Analytics 4 集成，只有运营者配置 measurement ID 后才可启用。即使已配置，在允许统计之前也不会加载统计标签。拒绝不影响游玩；本站也会依据 Global Privacy Control 和 Do Not Track 关闭可选统计。',zh),choose('After consent, events can include the visited page, world name, load success, first control interaction, visible play duration, sharing and source-code clicks. Campaign labels are restricted to short non-personal tags. We do not intentionally send names, email addresses, free-form input, full error messages or session recordings. Query parameters other than approved campaign tags are removed from manually reported page URLs; advertising personalization is disabled.','同意后，事件可能包含访问页面、世界名称、加载成功、首次控件操作、可见游玩时长、分享与源码点击。活动标签仅允许简短的非个人标签。我们不主动发送姓名、邮箱、自由输入文本、完整错误消息或访问过程录像。手动上报页面 URL 时会移除允许的活动标签以外的查询参数，并关闭广告个性化。',zh),choose('Analytics cookies may be set after consent. Your consent preference is stored locally as sw-consent-v1. Language preferences in the existing scenes may also be stored locally. The optional diagnostics tool stores only its on/off preference in session storage; its event log is held in memory in your own tab, not a public traffic database.','允许统计后可能设置统计 Cookie。隐私偏好以 sw-consent-v1 保存在本地；原有场景也可能本地保存语言偏好。可选诊断工具只在 session storage 保存开关状态，事件日志仅存在当前标签页内存中，不是公开流量数据库。',zh))
    pbody+='<h2>'+choose('Change your choice','修改选择',zh)+'</h2>'+paras(choose('Use Analytics choices below at any time. Declining after earlier acceptance disables future event sends, removes the relevant analytics cookies accessible to this site and reloads the page to unload the tag. It cannot erase data already received by a provider. Google and hosting providers describe their own processing and retention in their policies.','可随时使用下方统计设置。此前同意后再拒绝，会停止后续事件发送、删除本站可访问的相关统计 Cookie 并刷新页面卸载标签，但无法删除提供者已收到的数据。Google 与托管提供者的处理及保留规则请参阅其政策。',zh),f'<button class="button secondary" type="button" data-privacy>{choose("Review analytics choice","查看统计选择",zh)}</button>', '<a href="https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement">GitHub privacy</a> · <a href="https://policies.google.com/privacy">Google privacy</a>',choose('Questions about the implementation can be raised through the project repository. Do not include personal or sensitive information in a public issue.','实现方面的问题可通过项目仓库提出，请勿在公开 issue 中提交个人或敏感信息。',zh))
    page('privacy/',choose('Privacy & Analytics Choices','隐私与统计设置',zh),choose('How the hosted website, standalone scenes and optional traffic measurement handle information.','了解托管网站、独立场景与可选流量统计如何处理信息。',zh),pbody,zh)

    mbody=paras(choose('This is an integration-status and local testing page, not a live visitor dashboard. It never displays invented visitor counts. Site-wide traffic appears in your private analytics account only after the connection is configured and consenting visitors generate data.','这是集成状态与本地测试页面，不是实时访客仪表盘，不会显示虚构流量。只有配置统计服务并收到同意统计的访客数据后，才能在私有统计账户中查看全站流量。',zh))
    mbody+='<h2>'+choose('Connection status','连接状态',zh)+'</h2><pre id="integration-status" aria-live="polite"></pre><div class="actions"><a class="button secondary" href="https://analytics.google.com/">Google Analytics</a><a class="button secondary" href="https://search.google.com/search-console">Search Console</a><a class="button secondary" href="https://www.bing.com/webmasters/">Bing Webmaster Tools</a></div>'
    mbody+='<h2>'+choose('Test this tab, not everyone else','仅测试当前标签页',zh)+'</h2>'+paras(choose('Enable the local inspector, then play and use a physical control. world_open means a request, world_ready means a rendered frame, and engaged_play requires an interaction plus 60 seconds of visible play. Only named control actions count; merely moving the camera does not. Hidden or offscreen players do not accumulate play time.','开启本地检查器，再游玩并操作实体控件。world_open 表示请求加载，world_ready 表示完成绘制，engaged_play 需要一次控件交互和 60 秒可见游玩。仅控件操作计入交互，单纯移动相机不计入。隐藏或移出视口的播放器不累计时长。',zh))+'<div class="actions"><button id="debug-enable" class="button secondary">'+choose('Enable local inspector','开启本地检查器',zh)+'</button><button id="debug-disable" class="button secondary">'+choose('Clear & disable','清除并关闭',zh)+'</button></div>'+player('bayport',zh)+'<pre id="event-log" aria-live="polite">[]</pre>'
    mbody+=paras(choose('A queued-for-GA4 label is not proof that Google received an event. Check Realtime or DebugView in the configured GA4 property. Consent, browser blockers and network failures affect measured coverage. The inspector log resets when this page reloads.','queued-for-GA4 不代表 Google 已收到事件，应在对应 GA4 属性的实时报告或 DebugView 中确认。同意选择、拦截器和网络错误会影响测量覆盖范围。本页刷新后检查器日志重置。',zh))
    page('monitor/',choose('Traffic Setup & Event Inspector','流量设置与事件检查器',zh),choose('Check integration readiness and test the play funnel locally. No private analytics data is exposed here.','检查集成准备状态并本地测试游玩漏斗，不在此展示私有统计数据。',zh),mbody,zh,noindex=True)

    cbody=paras(choose('Create a tagged link for an external post. Use a different content label for each clip. Do not use these tags for ordinary links within the website, and never put personal information in campaign labels. This tool does not publish anything to social networks.','为外部帖子生成带标签的链接，每段视频使用不同 content 标签。不要给站内普通链接添加活动标签，也不要在标签中填写个人信息。本工具不会向社交平台发布任何内容。',zh))
    cbody+='''<form id="campaign-form"><div class="form-grid"><label>World<select name="world"><option value="bayport">BAYPORT</option><option value="bayline">BAYLINE</option></select></label><label>Source<input name="source" value="youtube" required maxlength="64"></label><label>Medium<input name="medium" value="social" required maxlength="64"></label><label>Campaign<input name="campaign" value="bayport_launch" required maxlength="64"></label><label>Content<input name="content" value="night_transition" maxlength="64"></label></div><div class="actions"><button class="button primary" type="submit">Build link / 生成链接</button><button class="button secondary" type="button" id="copy-campaign">Copy / 复制</button></div></form><pre id="campaign-result" role="status"></pre>'''
    cbody+='<h2>'+choose('Measure useful visits','衡量有效访问',zh)+'</h2>'+paras(choose('Compare sources by successful loads and engaged play, not clicks alone. A clip can attract interest but still fail if the world loads poorly on viewers’ phones. Use the device breakdown and world_error events before deciding the channel itself is weak.','按成功加载和有效游玩比较渠道，而不只比较点击。视频可能吸引兴趣，但手机端加载问题也会让访客流失。判断渠道效果前，先检查设备分布和 world_error 事件。',zh))+anchor('monitor/',choose('Open integration inspector →','打开集成检查器 →',zh))
    page('tools/campaign-builder/',choose('Campaign Link Builder','推广链接生成器',zh),choose('Consistent campaign tags for your BAYPORT and BAYLINE launch experiments.','为 BAYPORT 与 BAYLINE 推广实验生成一致的活动标签。',zh),cbody,zh,noindex=True)

# Runtime configuration includes public measurement and verification IDs only, never API secrets.
write('assets/site-config.js','window.SW_CONFIG=Object.freeze('+j({**cfg,'basePath':PREFIX})+');\n')

# Keep the existing gallery design. Add discovery links and a server-readable Chinese copy.
if not Path('tools/templates/home.html').exists():
    write('tools/templates/home.html',Path('index.html').read_text())
home=Path('tools/templates/home.html').read_text()
home=re.sub(r'<title>.*?</title>','<title>Free Browser Simulators: Airports &amp; Model Railways | Simulated World</title>',home,flags=re.S)
home=re.sub(r'<meta (?:name="(?:description|twitter:card|robots)"|property="og:[^"]+")[^>]*>','',home)
home=re.sub(r'<link rel="canonical"[^>]*>','',home)
home=home.replace('href="airport.html?v=2.1"',f'href="{local("worlds/bayport/")}"').replace('href="airport.html"',f'href="{local("worlds/bayport/")}"').replace('href="bayline.html"',f'href="{local("worlds/bayline/")}"')
home=home.replace('href="./"',f'href="{PREFIX}"').replace('src="assets/',f'src="{PREFIX}assets/').replace('href="assets/',f'href="{PREFIX}assets/').replace('srcset="assets/',f'srcset="{PREFIX}assets/').replace(', assets/',f', {PREFIX}assets/')
home=home.replace('assets/home.js?v=bayport-2-1','assets/home.js?v=growth-1')
home=home.replace('<script src="'+PREFIX+'assets/home.js?v=growth-1" defer></script>',scripts()+'<script src="'+PREFIX+'assets/home.js?v=growth-1" defer></script>')
home=home.replace('</head>',f'<link rel="stylesheet" href="{PREFIX}assets/growth.css?v=growth-1"></head>')
extra=f'''<section class="section wrap"><div class="eyebrow" data-en="EXPLORE AT YOUR OWN PACE" data-zh="按自己的节奏探索">EXPLORE AT YOUR OWN PACE</div><h2 class="section-title" data-en="Free browser simulators. Real little details." data-zh="免费浏览器模拟器，鲜活的微小细节。">Free browser simulators. Real little details.</h2><p class="seo-intro" data-en="Simulated World brings a miniature airport and a virtual model railway to your browser. No cockpit training, no competitive score: just interactive tabletop worlds to explore, with moving traffic, day-night lighting and physical controls." data-zh="Simulated World 把微缩机场和虚拟模型铁路带入浏览器。没有驾驶舱训练或竞技积分，只有可自由探索的互动沙盘、动态交通、昼夜灯光和实体控制台。">Simulated World brings a miniature airport and a virtual model railway to your browser. No cockpit training, no competitive score: just interactive tabletop worlds to explore, with moving traffic, day-night lighting and physical controls.</p><div class="actions"><a class="button secondary" href="{local('guides/')}" data-en="Read the field guides" data-zh="阅读探索指南">Read the field guides</a><a class="button secondary" href="{local('about/')}" data-en="About the project" data-zh="关于项目">About the project</a><a class="button secondary" href="{local('privacy/')}" data-en="Privacy" data-zh="隐私说明">Privacy</a><button class="button secondary" data-privacy type="button" data-en="Analytics choices" data-zh="统计设置">Analytics choices</button></div></section>'''
home=home.replace('</main>',extra+'</main>')
for zh in [False,True]:
    h=home
    title=choose('Free Browser Simulators: Airports & Model Railways | Simulated World','免费浏览器模拟器：微缩机场与模型铁路 | Simulated World',zh)
    desc=choose('Play BAYPORT, a free miniature airport simulator, and BAYLINE, a virtual model railway. Explore Bay Area-inspired tabletop worlds with interactive controls.','免费游玩 BAYPORT 微缩机场与 BAYLINE 虚拟模型铁路，探索湾区风格桌面世界，操作实体控制台并欣赏昼夜变化。',zh)
    h=h.replace('<html lang="en">','<html lang="zh-CN">' if zh else '<html lang="en">')
    h=re.sub(r'<title>.*?</title>','<title>'+escape(title)+'</title>',h)
    if zh:
        def translate(m):
            tag,attrs,old=m.groups(); found=re.search(r'data-zh="([^"]*)"',attrs)
            return '<'+tag+attrs+'>'+escape(unescape(found.group(1)))+'</'+tag+'>' if found else m.group(0)
        h=re.sub(r'<([a-zA-Z][\w-]*)([^<>]*\bdata-en="[^<>]*?)>([^<>]*)</\1>',translate,h)
        # Localized text for images and accessible labels.
        def attrs_zh(m):
            tag=m.group(0)
            for data,attr in [('data-alt-zh','alt'),('data-label-zh','aria-label')]:
                val=re.search(r'\b'+data+r'="([^"]*)"',tag)
                if val:tag=re.sub(r'(?<![\w-])'+attr+r'="[^"]*"',attr+'="'+val.group(1)+'"',tag)
            return tag
        h=re.sub(r'<[^<>]+>',attrs_zh,h)
        for route in ['worlds/bayport/','worlds/bayline/','guides/','about/','privacy/']:h=h.replace('href="'+local(route)+'"','href="'+local(route,True)+'"')
        h=h.replace('href="'+PREFIX+'"','href="'+local('',True)+'"')
    h=h.replace('</head>',metadata(title,desc,'',zh)+'</head>')
    # A real anchor works for language navigation even before JavaScript loads.
    h=re.sub(r'<button class="language js-only" id="lang".*?</button>',f'<a class="language" id="lang" data-language-link href="{local("",not zh)}" lang="{"en" if zh else "zh-CN"}">{"EN" if zh else "中文"}</a>',h)
    write(('zh/' if zh else '')+'index.html',h);index.append({'route':'','zh':zh,'url':absolute('',zh),'title':title})

# Adapt gallery JavaScript to stable language URLs and keep live previews measurable.
js=Path('assets/home.js').read_text()
if 'SW_GROWTH_GALLERY' not in js:
    js='// SW_GROWTH_GALLERY\n'+js
    js=js.replace("let language = storage.get('sw-language') === 'zh' ? 'zh' : 'en';","let language = document.documentElement.lang.startsWith('zh') ? 'zh' : 'en';\n  const root = window.SW_CONFIG.basePath;")
    js=js.replace("button.addEventListener('click', () => { language = language === 'en' ? 'zh' : 'en'; storage.set('sw-language', language); applyLanguage(); });","button.addEventListener('click', () => { storage.set('sw-language', language === 'en' ? 'zh' : 'en'); });")
    js=js.replace("'Simulated World — 湾区微缩世界' : 'Simulated World — Small worlds, brought to life'","'免费浏览器模拟器：微缩机场与模型铁路 | Simulated World' : 'Free Browser Simulators: Airports & Model Railways | Simulated World'")
    js=js.replace("$('#preview-launch').href = scene.path;","$('#preview-launch').href = root + (language === 'zh' ? 'zh/' : '') + 'worlds/' + key + '/';")
    js=js.replace("$('#preview-fallback').href = scene.path;","$('#preview-fallback').href = $('#preview-launch').href;")
    js=js.replace('frame.src = scene.path;',"frame.src = root + (key === 'bayport' ? 'airport.html' : 'bayline.html') + '?embed=1&lang=' + language;")
    js=js.replace('mount.replaceChildren(frame);',"mount.replaceChildren(frame);\n        window.SWPlayer?.attach(frame, key, 'homepage_preview');")
    write('assets/home.js',js)

# Install a small inline, network-free bridge. It never posts to a foreign parent.
bridge="""<!-- SW BRIDGE -->
<script>
(()=>{let ready=false,lastInput=0;const sent=new Map();const world='WORLD';
for(const type of ['pointerdown','pointerup','keydown','input'])window.addEventListener(type,e=>{if(e.isTrusted)lastInput=Date.now();},{capture:true,passive:true});
function send(event,control=''){if(window.parent===window||location.protocol==='file:')return;try{if(window.parent.location.origin!==location.origin)return;window.parent.postMessage({type:'sw:world',world,event,control},location.origin);}catch{}}
window.__swEmit=(event,control='')=>{if(event==='ready'){ready=true;send('ready');return;}if(event==='interaction'){if(!ready||Date.now()-lastInput>2000)return;const now=Date.now();if(now-(sent.get(control)||0)<1500)return;sent.set(control,now);}send(event,String(control).slice(0,40));};
window.addEventListener('message',e=>{if(e.source===parent&&e.origin===location.origin&&e.data?.type==='sw:hello'&&ready)send('ready');});
window.addEventListener('error',()=>send('error'));window.addEventListener('unhandledrejection',()=>send('error'));
})();
</script>
<!-- /SW BRIDGE -->
"""
for file,world in [('airport.html','bayport'),('bayline.html','bayline')]:
    s=Path(file).read_text()
    if '<!-- SW BRIDGE -->' not in s:
        assert s.count('if(!ready){ready=true;')==1, 'Ready hook changed'
        s=s.replace('</head>',bridge.replace('WORLD',world)+'</head>',1)
        s=s.replace('if(!ready){ready=true;','if(!ready){ready=true;window.__swEmit?.("ready");',1)
        sig='function trigger(key){' if world=='bayport' else 'function action(id){'
        assert s.count(sig)==1
        s=s.replace(sig,sig+'window.__swEmit?.("interaction",'+('key' if world=='bayport' else 'id')+');',1)
        sig='function setSpeed(value,notify=false){';assert s.count(sig)==1
        s=s.replace(sig,sig+'window.__swEmit?.("interaction","speed");',1)
        if world=='bayport':
            old="let language='en';try{language=localStorage.getItem('bayport-language')==='zh'?'zh':'en';}catch(_){}"
            assert old in s;s=s.replace(old,old+"const requestedLanguage=new URLSearchParams(location.search).get('lang');if(requestedLanguage==='en'||requestedLanguage==='zh')language=requestedLanguage;",1)
        else:
            s=s.replace("let currentLang='en';","let currentLang=new URLSearchParams(location.search).get('lang')==='zh'?'zh':'en';",1)
    # Player URLs stay usable; descriptive pages are the indexed discovery entry points.
    s=re.sub(r'<!-- SW PLAYER META -->.*?<!-- /SW PLAYER META -->','',s,flags=re.S)
    meta=f'<!-- SW PLAYER META --><meta name="description" content="Interactive {world.upper()} standalone miniature. Visit the world guide for controls and requirements."><link rel="canonical" href="{BASE}{file}"><meta name="robots" content="noindex,follow"><!-- /SW PLAYER META -->'
    s=s.replace('</head>',meta+'</head>',1);write(file,s)

# Visuals are unchanged by metadata and message hooks; preserve image provenance, update source digests.
manifest_path=Path('assets/previews/manifest.json')
if manifest_path.exists():
    manifest=json.loads(manifest_path.read_text())
    for scene in manifest['scenes']:
        digest=hashlib.sha256(Path(scene['file']).read_bytes()).hexdigest()
        if scene['sha256']!=digest:
            scene.setdefault('capturedSourceSha256',scene['sha256']);scene['sha256']=digest
            scene['metadataNote']='Same scene visuals; added metadata, language entry and local parent event hooks after capture.'
    write(str(manifest_path),json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')

# A sitemap contains only canonical indexable content URLs, never debug/campaign/player variants.
urls=''.join(f'<url><loc>{escape(x["url"])}</loc><lastmod>{DATE}</lastmod></url>\n' for x in sorted(index,key=lambda x:x['url']))
write('sitemap.xml','<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+urls+'</urlset>\n')
robots=f'''# Effective only when served at the HOST ROOT /robots.txt.
# At github.io/simulated-world/robots.txt this does not control crawling.
# On GitHub Pages submit the sitemap directly; do not claim this config applies to the host.
User-agent: *
Allow: /

User-agent: OAI-SearchBot
Allow: /

Sitemap: {BASE}sitemap.xml
'''
write('robots.txt',robots)
write('docs/robots-host-root.txt',robots)
write('site-inventory.json',json.dumps({'baseUrl':BASE,'pages':index,'analyticsConfigured':bool(cfg['measurementId']),'verificationTagsConfigured':{'google':bool(cfg['googleVerification']),'bing':bool(cfg['bingVerification'])}},ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'indexablePages':len(index),'analyticsConfigured':bool(cfg['measurementId']),'baseUrl':BASE},indent=2))
