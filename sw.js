/* A complete, versioned library snapshot. Installing is atomic: a failed
 * download never replaces a working offline version. */
const VERSION='a958dcabf8f7';
const SCOPE_PATH=new URL(self.registration.scope).pathname;
const PREFIX='recall-offline-'+encodeURIComponent(SCOPE_PATH)+'-';
const CACHE=PREFIX+VERSION;
const ASSETS=["./","./DOOCS-LICENSE.txt","./LICENSE.txt","./NEETCODE-LICENSE.txt","./PRIMER-LICENSE.txt","./app-v2.js","./credits.html","./fonts.css","./fonts/DM-Sans-LICENSE.txt","./fonts/Manrope-LICENSE.txt","./fonts/dm-sans-400.ttf","./fonts/dm-sans-600.ttf","./fonts/dm-sans-700.ttf","./fonts/manrope-400.ttf","./fonts/manrope-600.ttf","./fonts/manrope-700.ttf","./icon.svg","./icons.js","./icons/apple-touch-icon.png","./icons/icon-192.png","./icons/icon-512.png","./icons/maskable-512.png","./index.html","./library.json","./licenses/Apache-2.0.txt","./licenses/CC-BY-4.0.txt","./licenses/CC-BY-SA-4.0.txt","./licenses/DM-Sans-LICENSE.txt","./licenses/Donne-Martin-coding-NOTICE.txt","./licenses/Donne-Martin-primer-NOTICE.txt","./licenses/Manrope-LICENSE.txt","./licenses/NeetCode-MIT.txt","./licenses/Recall-MIT.txt","./manifest.json","./media-credits.json","./media-primer/4edXG0T.png","./media-primer/4j99mhe.png","./media-primer/MzExP06.png","./media-primer/V5q57vU.png","./media-primer/bWxPtQA.png","./media-primer/cdCv5g7.png","./media-primer/jj3A5N8.png","./media-primer/jrUBAF7.png","./media-primer/mint_basic.png","./media-primer/pastebin_basic.png","./media-primer/query_cache_basic.png","./media-primer/sales_rank_basic.png","./media-primer/scaling_aws_1.png","./media-primer/scaling_aws_2.png","./media-primer/scaling_aws_3.png","./media-primer/scaling_aws_4.png","./media-primer/scaling_aws_5.png","./media-primer/social_graph_basic.png","./media-primer/twitter_basic.png","./media-primer/web_crawler_basic.png","./pwa.js","./reader-model.js","./reader.css","./reader.js","./reading-order.json","./styles.css","./v2.css"];
const BYTES=8302625;
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
