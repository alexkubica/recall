export const offline={state:'preparing',detail:'Preparing offline library…',update:false,version:null};
let registration,installPrompt,listener=()=>{};
export function onOfflineChange(fn){listener=fn;fn(offline)}
const notify=()=>listener(offline);
function fail(message){offline.state='error';offline.detail=message;notify()}
async function status(){
 const worker=navigator.serviceWorker?.controller||registration?.active;if(!worker)return;
 const channel=new MessageChannel();
 const timeout=setTimeout(()=>{if(offline.state!=='ready')fail('Offline download not confirmed. Tap to retry.')},10000);
 channel.port1.onmessage=e=>{clearTimeout(timeout);if(e.data.ready){offline.state='ready';offline.version=e.data.version;offline.detail=`${e.data.resources} files saved · ${(e.data.bytes/1048576).toFixed(1)} MB`;notify()}};
 worker.postMessage({type:'STATUS'},[channel.port2]);
}
export async function prepareOffline(){
 if(!('serviceWorker' in navigator)){fail('Offline saving is unavailable in this browser. Open in Safari or Chrome.');return}
 offline.state='preparing';offline.detail='Saving the complete library for offline use…';notify();
 try{
  registration=await navigator.serviceWorker.register('./sw.js',{scope:'./',updateViaCache:'none'});
  if(registration.waiting){offline.update=true;notify()}
  registration.addEventListener('updatefound',()=>{
   const installing=registration.installing;installing?.addEventListener('statechange',()=>{
    if(installing.state==='installed'&&navigator.serviceWorker.controller){offline.update=true;notify()}
    if(installing.state==='redundant'&&offline.state!=='ready')fail('Offline download interrupted. Tap to retry.');
   });
  });
  await navigator.serviceWorker.ready;await status();
 }catch{fail('Could not save offline yet. Check your connection and tap to retry.')}
}
let requestedUpdate=false;
navigator.serviceWorker?.addEventListener('controllerchange',()=>{if(requestedUpdate)location.reload();else status()});
window.addEventListener('online',notify);window.addEventListener('offline',notify);
window.addEventListener('beforeinstallprompt',e=>{e.preventDefault();installPrompt=e;notify()});
window.addEventListener('appinstalled',()=>{installPrompt=null;notify()});
export async function installApp(){if(!installPrompt)return false;await installPrompt.prompt();await installPrompt.userChoice;installPrompt=null;return true}
export function applyUpdate(){if(registration?.waiting){requestedUpdate=true;registration.waiting.postMessage({type:'SKIP_WAITING'})}}
export function isInstalled(){return matchMedia('(display-mode: standalone)').matches||navigator.standalone===true}
