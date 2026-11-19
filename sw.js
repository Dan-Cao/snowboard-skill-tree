// Bump VERSION on every content change so phones pick up the update.
const VERSION="v1";
const FILES=["./","./index.html","./manifest.webmanifest","./icon-192.png","./icon-512.png"];
self.addEventListener("install",e=>{e.waitUntil(caches.open(VERSION).then(c=>c.addAll(FILES)));self.skipWaiting()});
self.addEventListener("activate",e=>{e.waitUntil(caches.keys().then(k=>Promise.all(k.filter(x=>x!==VERSION).map(x=>caches.delete(x)))));self.clients.claim()});
// Cache-first so it opens with no signal; refresh cache in background when online.
self.addEventListener("fetch",e=>{
  if(e.request.method!=="GET")return;
  e.respondWith(caches.match(e.request,{ignoreSearch:true}).then(r=>{
    const net=fetch(e.request).then(res=>{if(res.ok){const cp=res.clone();caches.open(VERSION).then(c=>c.put(e.request,cp))}return res}).catch(()=>r);
    return r||net;
  }));
});
