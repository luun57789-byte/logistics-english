# Builds dist/ : a standalone PWA version of app.html that runs in any browser without Claude.
import os,shutil,re
from PIL import Image,ImageDraw
os.makedirs('dist',exist_ok=True)
s=open('app.html').read()
cap_start=s.index("(async()=>{try{if(window.claude&&claude.use)")
cap_end=s.index("\n",s.index('if(location.hash==="#phat-am")route()}}catch(e){}})();'))
adapter=r'''DICT=browserDict();
DL={save({filename}){const a=document.createElement("a");a.href="tu-vung-logistics.pdf";a.download=filename;document.body.appendChild(a);a.click();a.remove();return Promise.resolve()}};
if("serviceWorker" in navigator&&location.protocol.startsWith("http")){navigator.serviceWorker.register("sw.js").then(r=>r.update()).catch(()=>{});let rl=false;navigator.serviceWorker.addEventListener("controllerchange",()=>{if(!rl){rl=true;location.reload()}})}'''
s=s[:cap_start]+adapter+s[cap_end:]
# savePdf: no fetch needed
s=s.replace('const r=await fetch("tu-vung-logistics.pdf");if(!r.ok)throw new Error("fetch");const b=new Uint8Array(await r.arrayBuffer());\n    await DL.save({filename:"Tu-vung-logistics-"+VOCAB.length+"-tu.pdf",data:b});m.textContent="Đã gửi file PDF. Mở file và in như bình thường."}',
            'await DL.save({filename:"Tu-vung-logistics-"+VOCAB.length+"-tu.pdf"});m.textContent="Đã tải file PDF. Mở file và in như bình thường."}')
assert 'DL.save({filename:"Tu' in s
s=s.replace("Âm thanh dùng giọng đọc của Claude khi có; nếu không, dùng giọng tiếng Anh có sẵn trên máy bạn.","Âm thanh dùng giọng tiếng Anh có sẵn trên máy bạn; nếu không nghe thấy, hãy kiểm tra âm lượng và chế độ im lặng.")
s=s.replace("Đang mở micro…","Đang mở micro… (trình duyệt có thể hỏi quyền dùng micro)")
head='''<!doctype html>
<html lang="vi"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#173a5e">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" href="icon-192.png">
<link rel="apple-touch-icon" href="icon-192.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0;font:14px system-ui,sans-serif}img{max-width:100%}[hidden]{display:none!important}</style>
</head><body>
'''
open('dist/index.html','w').write(head+s+"\n</body></html>\n")
shutil.copy('tu-vung-logistics.pdf','dist/tu-vung-logistics.pdf')
open('dist/manifest.webmanifest','w').write('''{"name":"Logistics English Dock","short_name":"Logistics EN","start_url":"./","display":"standalone","background_color":"#eef1f4","theme_color":"#173a5e","lang":"vi",
"icons":[{"src":"icon-192.png","sizes":"192x192","type":"image/png"},{"src":"icon-512.png","sizes":"512x512","type":"image/png","purpose":"any maskable"}]}''')
import hashlib
ver=hashlib.md5(open('dist/index.html','rb').read()).hexdigest()[:8]
open('dist/sw.js','w').write('''const C="led-%s";const F=["./","index.html","manifest.webmanifest","icon-192.png","icon-512.png","tu-vung-logistics.pdf"];
self.addEventListener("install",e=>{e.waitUntil(caches.open(C).then(c=>c.addAll(F)));self.skipWaiting()});
self.addEventListener("activate",e=>{e.waitUntil(caches.keys().then(k=>Promise.all(k.filter(x=>x!==C).map(x=>caches.delete(x)))));self.clients.claim()});
self.addEventListener("fetch",e=>{if(e.request.method!=="GET"||new URL(e.request.url).origin!==location.origin)return;const nav=e.request.mode==="navigate"||/\.(html|webmanifest|js)$|\/$/.test(new URL(e.request.url).pathname);e.respondWith(fetch(nav?e.request.url:e.request,nav?{cache:"no-store",credentials:"same-origin"}:undefined).then(r=>{const cp=r.clone();if(r.ok&&new URL(e.request.url).origin===location.origin)caches.open(C).then(c=>c.put(e.request,cp));return r}).catch(()=>caches.match(e.request).then(r=>r||caches.match("index.html"))))});
''' % ver)
for n in (192,512):
  im=Image.new('RGB',(n,n),'#173a5e');d=ImageDraw.Draw(im);u=n/16
  d.rounded_rectangle([3*u,5*u,13*u,11*u],radius=u*0.4,fill='#e8a317')
  for i in range(9): x=3.6*u+i*1.1*u; d.rectangle([x,5.6*u,x+0.35*u,10.4*u],fill='#c98a0c')
  im.save(f'dist/icon-{n}.png')
open('dist/.nojekyll','w').write('')
print('dist ok',ver)
