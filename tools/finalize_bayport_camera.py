from pathlib import Path
import hashlib
p=Path('airport.html')
s=p.read_text()
assert hashlib.sha256(s.encode()).hexdigest()=='90d160f13ded2880d56f9cfe73fe44cf1c6fbe69d5c206d8ef64e962f83cb4b3', 'Unexpected source; review before patching'
def edit(a,b):
 global s
 assert s.count(a)==1, (s.count(a),a)
 s=s.replace(a,b,1)
edit('let radius=76;', 'let radius=84;')
edit('radius=Math.max(radius,depth+Math.abs(p.dot(right))/(tanX*.92),depth+Math.abs(p.dot(up))/(tanY*.80));', 'radius=Math.max(radius,depth+Math.abs(p.dot(right))/(tanX*.94));')
edit('const eye=new T.Vector3(st*ce,se,ct*ce),right=new T.Vector3(ct,0,-st),up=new T.Vector3(-st*se,ce,-ct*se);', 'const eye=new T.Vector3(st*ce,se,ct*ce),right=new T.Vector3(ct,0,-st);')
edit('// A continuous aspect-aware fit prevents the table from shrinking abruptly on phones.', '// Fit the board laterally on narrow screens; retain the close BAYLINE tabletop crop on desktop.')
edit('camera.lookAt(view.target);camera.updateMatrixWorld();', '''camera.lookAt(view.target);
 // A portrait fit moves the eye back, not the miniature into a fixed fog bank.
 scene.fog.near=Math.max(125,view.radius*1.45);scene.fog.far=Math.max(240,view.radius*2.8);
 const far=Math.max(360,view.radius+180);if(Math.abs(camera.far-far)>1){camera.far=far;camera.updateProjectionMatrix();}
 camera.updateMatrixWorld();''')
edit("label('INTERNATIONAL',-22.2,G-2.08,28.53", "label('INTERNATIONAL',-22.2,G-1.99,28.53")
edit('0,G-2.19,28.54,32.2,.34,apronHintOptions', '0,G-2.02,28.54,32.2,.34,apronHintOptions')
p.write_text(s)
assert hashlib.sha256(p.read_bytes()).hexdigest()=='fac07aef5ac0026c0a389c3e1a15c0b927e1b37a5172e7185e6c2fe9a52c4167'
print(len(s.encode()),hashlib.sha256(s.encode()).hexdigest())
