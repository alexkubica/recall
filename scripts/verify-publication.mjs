import assert from 'node:assert/strict';
import {readFile,readdir} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
const root=fileURLToPath(new URL('../',import.meta.url)),pub=path.join(root,'public');
const json=async name=>JSON.parse(await readFile(path.join(pub,name),'utf8'));
const library=await json('library.json'),manifest=await json('offline-assets.json'),media=await json('media-credits.json');
const cached=new Set(manifest.assets.map(x=>x.replace(/^\.\//,'')));
assert.equal(library.cards.length,533);assert.equal(media.assets.length,20);
for(const c of library.cards){
 assert(c.attribution?.author&&c.attribution?.copyright&&c.attribution?.changes,'Missing credit: '+c.id);
 assert(cached.has(c.attribution.licenseUrl),'License not offline: '+c.id);
 for(const m of JSON.stringify(c).matchAll(/src=\\?"([^"\\]+)\\?"/g)){
  assert(!/^https?:/.test(m[1]),'Remote image: '+c.id);
  assert(cached.has(m[1]),'Uncached image: '+m[1]);
 }
}
for(const a of media.assets){
 assert.equal(a.license,'CC-BY-4.0');assert(a.sourceUrl&&a.author&&a.changes);
 const bytes=await readFile(path.join(pub,a.path));assert.equal(createHash('sha256').update(bytes).digest('hex'),a.sha256);
 assert(cached.has(a.path));
}
assert(cached.has('credits.html'));assert(cached.has('media-credits.json'));
for(const file of ['Apache-2.0.txt','CC-BY-4.0.txt','CC-BY-SA-4.0.txt','NeetCode-MIT.txt','Recall-MIT.txt','DM-Sans-LICENSE.txt','Manrope-LICENSE.txt'])assert(cached.has('licenses/'+file));
const forbidden=['Assume you are an awesome parent','What is HATEOAS and why','The optimized solutions is discussed in more depth','Typically, quicksort is significantly faster in practice','When the number of vertices in the graph is known ahead of time','media/quicksort_wikipedia.gif','trycloudflare.com','/Users/'];
async function walk(dir){for(const e of await readdir(dir,{withFileTypes:true})){
 if(['.git','dist','node_modules','__pycache__'].includes(e.name))continue;
 const file=path.join(dir,e.name),rel=path.relative(root,file);
 assert(!/\.(apkg|anki2|anki21|anki21b|sqlite|pem|key|log)$/.test(e.name),'Private/raw file: '+rel);
 assert(!/^\.env(?:\.|$)/.test(e.name),'Environment file: '+rel);
 if(e.isDirectory()){assert(!['work','runtime'].includes(e.name),'Work directory: '+rel);await walk(file);continue}
 if(/\.(js|mjs|py|json|html|md|txt|css)$/.test(e.name)&&!rel.endsWith('verify-publication.mjs')){
  const text=await readFile(file,'utf8');for(const marker of forbidden)assert(!text.includes(marker),'Excluded content marker in '+rel);
  assert(!/-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----|gh[pousr]_[A-Za-z0-9]{30,}/.test(text),'Potential credential in '+rel);
 }
}}
await walk(root);
const files=await readdir(path.join(pub,'media-primer'));assert.deepEqual(files.sort(),media.assets.map(a=>path.basename(a.path)).sort());
console.log('Publication checks passed: 533 credited cards, 20 attributed image hashes, offline notices, no excluded archives/content/runtime or credential markers.');
