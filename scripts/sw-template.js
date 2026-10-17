/* A complete, versioned library snapshot. Installing is atomic: a failed
 * download never replaces a working offline version. */
const VERSION='__VERSION__';
const SCOPE_PATH=new URL(self.registration.scope).pathname;
const PREFIX='recall-offline-'+encodeURIComponent(SCOPE_PATH)+'-';
const CACHE=PREFIX+VERSION;
const ASSETS=__ASSET_LIST__;
const BYTES=__ASSET_BYTES__;
self.addEventListener('install',event=>event.waitUntil((async()=>{
 const cache=await caches.open(CACHE);
 try{
  // Bound concurrency to avoid overwhelming mobile networks during the initial download.
  const queue=[...ASSETS];
  await Promise.all(Array.from({length:4},async()=>{while(queue.length){const rel=queue.shift();const url=new URL(rel,self.registration.scope);const response=await fetch(new Request(url,{cache:'reload'}));if(!response.ok)throw Error('Offline download failed: '+rel);await cache.put(url,response)}}));
  await cache.put(new URL('./__offline-ready',self.registration.scope),new Response(JSON.stringify({version:VERSION,resources:ASSETS.length,bytes:BYTES})));
 }catch(error){await caches.delete(CACHE);throw error}
})()));
self.addEventListener('activate',event=>event.waitUntil((async()=>{
 // Keep old version caches while older open pages may still rely on them.
 const keys=await caches.keys();
 const old=keys.filter(k=>k.startsWith(PREFIX)&&k!==CACHE);
 if(old.length>1)await Promise.all(old.slice(0,-1).map(k=>caches.delete(k)));
 await self.clients.claim();
})()));
self.addEventListener('message',event=>{
 if(event.data?.type==='SKIP_WAITING')self.skipWaiting();
 if(event.data?.type==='STATUS')event.waitUntil((async()=>{
  const cache=await caches.open(CACHE);const ready=await cache.match(new URL('./__offline-ready',self.registration.scope));
  event.ports[0]?.postMessage({ready:!!ready,version:VERSION,resources:ASSETS.length,bytes:BYTES});
 })());
});
self.addEventListener('fetch',event=>{
 const request=event.request,url=new URL(request.url);
 if(request.method!=='GET'||url.origin!==self.location.origin||!url.pathname.startsWith(SCOPE_PATH))return;
 // Service-worker and update metadata must be fetched by the browser.
 if(url.pathname.endsWith('/sw.js')||url.pathname.endsWith('/offline-assets.json'))return;
 event.respondWith((async()=>{
  const cache=await caches.open(CACHE);
  const key=new URL(url.pathname===SCOPE_PATH?SCOPE_PATH+'index.html':url.pathname,self.location.origin);
  const cached=await cache.match(key);
  if(cached)return cached;
  return fetch(request);
 })());
});
