from pathlib import Path
import hashlib, sys
path=Path(sys.argv[1]) if len(sys.argv)>1 else Path('airport.html')
s=path.read_text()
assert hashlib.sha256(s.encode()).hexdigest()=='fdea390911b48d98a014d7c8b3db9c3dcc0c8746545d6407a31bed80c4613d9e', 'Airport source changed: inspect before applying.'
def edit(old,new):
 global s
 assert s.count(old)==1, (s.count(old),old[:100])
 s=s.replace(old,new,1)
edit("const T=THREE, PI=Math.PI, TAU=2*PI, G=11.5;","const T=THREE, PI=Math.PI, TAU=2*PI, G=23; // BAYLINE-style standing-height workbench")
edit("const camera=new T.PerspectiveCamera(52,innerWidth/innerHeight,.2,330);","const camera=new T.PerspectiveCamera(42,innerWidth/innerHeight,.2,360);")
edit("exhibition.position.set(0,28,29)","exhibition.position.set(0,G+17,29)")
edit("sun.position.set(-30,68,20)","sun.position.set(-30,G+56,20)")
edit("fill.position.set(24,35,-27)","fill.position.set(24,G+26,-27)")
anchor="function building(x,z,w,d,h,color,name,opt={}){"
edit(anchor,"""function sceneryMark(){return {counts:new Map([...B.data].map(([k,v])=>[k,v.length])),children:model.children.length,blockers:blockers.length};}
function lowerScenery(mark,factor){
 const stretch=new T.Matrix4().makeScale(1,factor,1);
 for(const [kind,items] of B.data)for(let i=mark.counts.get(kind)||0;i<items.length;i++)items[i][0].premultiply(stretch);
 for(let i=mark.children;i<model.children.length;i++){const o=model.children[i];o.position.y*=factor;o.scale.y*=factor;}
 for(let i=mark.blockers;i<blockers.length;i++){blockers[i].minY*=factor;blockers[i].maxY*=factor;}
}
"""+anchor)
start=s.index('const wood=new T.MeshStandardMaterial(')
end=s.index('// 房间的三扇大窗',start)
s=s[:start]+"""const wood=new T.MeshStandardMaterial({map:woodTexture(),color:'#e2bc8a',roughness:.54,metalness:.02});
// One continuous oak worktop, with the controls recessed into its front apron.
const worktop=meshBox(scene,70.4,1.15,54.5,0,0,G-1.125,1.0,wood);worktop.name='BAYLINE oak worktop';
const roomB=new Batch(scene);
for(const z of[-23.15,25.7])meshBox(scene,67,1.6,.65,0,0,G-2.3,z,wood);
for(const x of[-32.2,32.2])meshBox(scene,.65,1.6,48.85,0,x,G-2.3,1.275,wood);
for(const x of[-31.4,31.4])for(const z of[-20.7,23.4]){
 meshBox(scene,2.1,G-1.8,2.1,0,x,(G-1.8)/2,z,wood);
 roomB.box(x,.2,z,2.22,.4,2.22,'#29393a','metal');
}
for(const x of[-31.4,31.4])meshBox(scene,.8,.85,44.1,0,x,G*.36,1.35,wood);
for(const z of[-20.7,23.4])meshBox(scene,62.8,.85,.8,0,0,G*.36,z,wood);
roomB.box(0,-.28,0,210,.5,175,'#48514e');
for(let x=-90;x<100;x+=5){roomB.box(x,-.013,9,.026,.012,155,'#344946');for(let z=-65;z<85;z+=14)roomB.box(x+2.5,-.007,z+(Math.floor(x/5)%2)*7,4.97,.01,.024,'#354c48');}
roomB.box(0,42,-43,210,84,.7,'#284047');roomB.box(-85,42,0,.7,84,86,'#263b43');
roomB.box(0,1.0,-42.5,210,2,.28,'#526660');roomB.box(0,2.2,-42.35,210,.12,.34,'#899889');
for(let x=-78;x<100;x+=5)roomB.box(x,G*.47,-42.56,.065,G*.74,.05,'#3b5555');
"""+s[end:]
start=s.index('for(let x of [-48,0,48])')
end=s.index('roomB.flush();',start)
s=s[:start]+"""// Smaller sky windows keep the airport, rather than the room, in the foreground.
for(const x of[-48,48]){
 const panel=new T.Mesh(new T.PlaneGeometry(26,13),skyMat);panel.position.set(x,G+13,-42.58);scene.add(panel);
 for(const xx of[x-13.5,x+13.5])roomB.box(xx,G+13,-42,.8,14.5,.8,'#536b67');
 for(const yy of[G+6,G+20])roomB.box(x,yy,-42,27.8,.8,.8,'#536b67');
 roomB.box(x,G+13,-41.8,.45,13.5,.9,'#81918a');roomB.box(x,G+6,-41.2,28,.4,1.6,'#baae8a');
}
label('SAN FRANCISCO',9,G+19,-42.3,22,3.4,{bg:'#253f46',fg:'#dbc397',size:72,border:true},scene);
label('BAYPORT  /  AVIATION WORKSHOP',-21,G+13,-42.3,22,2.0,{bg:'#233c42',fg:'#b5c6b6',size:52,border:true},scene);
for(const [x,y,w] of[[-23,G+7,24],[22,G+11,18]])meshBox(scene,w,.45,2.1,0,x,y,-40.9,wood);
for(let i=0;i<9;i++)roomB.box(-32+i*1.55,G+8.4,-41.05,.82,2.4+(i%3)*.16,.95,['#ab8960','#688a81','#bc8d69','#59727b'][i%4]);
"""+s[end:]
edit("V(0,-.34,23.03,68,.28,.16,'#355e5e');","""V(0,-.34,23.03,68,.28,.16,'#355e5e');
for(const z of[-23.35,23.25])meshBox(model,68.6,.27,.20,0,0,-.21,z,wood);
for(const x of[-34.2,34.2])meshBox(model,.20,.27,46.8,0,x,-.21,-.05,wood);""")
edit("water:new T.MeshStandardMaterial({color:'#227f91',roughness:.32,metalness:.36})","water:new T.MeshStandardMaterial({color:'#3b989b',roughness:.32,metalness:.24})")
edit("57.2,.21,46,'#a8b193'","57.2,.21,46,'#a3b58c'")
edit("const cityColors=", "const skylineMark=sceneryMark();\nconst cityColors=")
edit("for(let x=-15;x<21;x+=3.7)","lowerScenery(skylineMark,.76);\nfor(let x=-15;x<21;x+=3.7)")
edit("building(.5,13.3,25,3.4,2.05", "const terminalMark=sceneryMark();\nbuilding(.5,13.3,25,3.4,2.05")
edit("for(let x of[-11.5,12.5])", "lowerScenery(terminalMark,.80);\nfor(let x of[-11.5,12.5])")
edit("V(-18,3.05,7.3", "const towerMark=sceneryMark();\nV(-18,3.05,7.3")
edit("rb.flush();", "rb.flush();lowerScenery(towerMark,.72);")
edit("V(-26,.045,9", "const hangarMark=sceneryMark();\nV(-26,.045,9")
edit("building(-26,14.0", "lowerScenery(hangarMark,.84);\nbuilding(-26,14.0")
edit("building(6.0,19.05", "const hotelMark=sceneryMark();\nbuilding(6.0,19.05")
edit("planter(9.0,19.2", "lowerScenery(hotelMark,.66);\nplanter(9.0,19.2")
edit("const departures=plane('narrow','#bd7651',.96);", "const departures=plane('narrow','#bd7651',1.10);")
edit("const arrivals=plane('wide','#487e8b',.94);", "const arrivals=plane('wide','#487e8b',1.08);")
edit("arrProgress:.867", "arrProgress:.969")
edit("depWait:8", "depWait:4")
edit("consoleGroup.position.set(0,G-.33,26.25);consoleGroup.rotation.x=.17", "consoleGroup.position.set(0,G-.33,25.3);consoleGroup.rotation.x=.10")
edit("meshBox(scene,54.1,1.9,.24,0,0,G-1.55,28.64,wood);", "meshBox(scene,54.1,1.65,.24,0,0,G-1.40,28.38,wood);")
s=s.replace('28.78','28.52').replace('28.79','28.53').replace('28.8,32.2','28.54,32.2')
start=s.index('const view={theta:.38')
end=s.index('const raycaster=',start)
s=s[:start]+"""// 42-degree lens and a 30-degree three-quarter view, shared with BAYLINE.
// A continuous aspect-aware fit prevents the table from shrinking abruptly on phones.
const HOME={theta:.46,elevation:.53,target:new T.Vector3(-1.4,G+.5,1.0)};
function homeRadius(){
 const aspect=innerWidth/innerHeight,tanY=Math.tan(camera.fov*PI/360),tanX=tanY*aspect;
 const st=Math.sin(HOME.theta),ct=Math.cos(HOME.theta),se=Math.sin(HOME.elevation),ce=Math.cos(HOME.elevation);
 const eye=new T.Vector3(st*ce,se,ct*ce),right=new T.Vector3(ct,0,-st),up=new T.Vector3(-st*se,ce,-ct*se);
 let radius=76;
 for(const x of[-35.2,35.2])for(const z of[-26.25,28.8])for(const y of[G-2.5,G+1]){
  const p=new T.Vector3(x,y,z).sub(HOME.target),depth=p.dot(eye);
  radius=Math.max(radius,depth+Math.abs(p.dot(right))/(tanX*.92),depth+Math.abs(p.dot(up))/(tanY*.80));
 }
 return radius;
}
const view={theta:HOME.theta,elevation:HOME.elevation,radius:homeRadius(),target:HOME.target.clone(),desiredTheta:HOME.theta,desiredElevation:HOME.elevation,desiredRadius:homeRadius(),pan:HOME.target.clone()};
function updateCamera(dt,immediate=false){
 const k=immediate?1:1-Math.exp(-dt*12);view.theta=lerp(view.theta,view.desiredTheta,k);view.elevation=lerp(view.elevation,view.desiredElevation,k);view.radius=lerp(view.radius,view.desiredRadius,k);view.target.lerp(view.pan,k);
 const r=view.radius,c=Math.cos(view.elevation);camera.position.set(view.target.x+Math.sin(view.theta)*r*c,view.target.y+Math.sin(view.elevation)*r,view.target.z+Math.cos(view.theta)*r*c);
 // Preserve the protected observation shell, above both aircraft flight circuits.
 if(Math.abs(camera.position.x)<39&&camera.position.z<30&&camera.position.y<G+18)camera.position.y=G+18;
 camera.position.x=Math.max(camera.position.x,-79);camera.position.y=Math.max(camera.position.y,G+6);camera.lookAt(view.target);camera.updateMatrixWorld();
}
function resetView(){view.desiredTheta=HOME.theta;view.desiredElevation=HOME.elevation;view.desiredRadius=homeRadius();view.pan.copy(HOME.target);}
updateCamera(1,true);scene.updateMatrixWorld(true);

"""+s[end:]
s=s.replace('dist,34,150','dist,34,Math.max(150,homeRadius()*1.25)').replace('*.00075),34,150','*.00075),34,Math.max(150,homeRadius()*1.25)')
edit("window.addEventListener('resize',()=>{camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();renderer.setSize(innerWidth,innerHeight);renderer.setPixelRatio(Math.min(devicePixelRatio,1.6));});","""let fittedRadius=homeRadius();
window.addEventListener('resize',()=>{const zoom=view.desiredRadius/fittedRadius;camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();fittedRadius=homeRadius();view.desiredRadius=clamp(fittedRadius*zoom,34,Math.max(150,fittedRadius*1.25));renderer.setSize(innerWidth,innerHeight);renderer.setPixelRatio(Math.min(devicePixelRatio,1.6));});""")
edit("version:'2.0-bayline-aligned'", "version:'2.1-aircraft-framing'")
path.write_text(s)
print(path,len(s.encode()),hashlib.sha256(s.encode()).hexdigest())
