import assert from 'node:assert/strict';
import {readFile,access} from 'node:fs/promises';
import vm from 'node:vm';
const root=new URL('../public/',import.meta.url);
const json=async f=>JSON.parse(await readFile(new URL(f,root),'utf8'));
const [library,original,manifest,offline,oo]=await Promise.all(['library.json','deck.json','manifest.json','offline-assets.json','oo-javascript-solutions.json'].map(json));
assert.equal(library.cards.length,533);
assert.deepEqual(library.decks.map(d=>d.count),[100,42,8,6,30,347]);
assert.equal(new Set(library.cards.map(c=>c.id)).size,533);
for(const c of original.cards){const migrated=library.cards.find(x=>x.id===c.id);assert.equal(migrated.question,c.question);assert.equal(migrated.answer,c.answer);assert.ok(migrated.solutions.javascript.code);}
const assets=new Set(offline.assets);
let imageReferences=0;
for(const c of library.cards){
 assert.ok(library.decks.some(d=>d.id===c.deckId));
 for(const html of [c.question,c.answer,...c.sections.map(s=>s.html)]){
  assert.ok(!/<(?:script|iframe|object|embed)\b|\son[a-z]+\s*=/i.test(html),c.id+' active HTML');
  for(const m of html.matchAll(/<img[^>]+src=["']([^"']+)["']/g)){const src=m[1];assert.ok(!/^(https?:|\/\/)/.test(src),c.id+' external image');assert.ok(assets.has('./'+src.replace(/^\.\//,'')),c.id+' uncached image '+src);imageReferences++;}
 }
}
assert.equal(library.cards.filter(c=>c.solutions?.javascript?.code).length,475);
assert.equal(library.cards.filter(c=>c.deckId==='modern'&&c.solutions?.python?.code).length,22);
for(const item of manifest.icons){await access(new URL(item.src,root));assert.ok(assets.has('./'+item.src.replace(/^\.\//,'')));}
for(const asset of assets)if(asset!=='./')await access(new URL(asset,root));
for(const [id,s] of Object.entries(oo))new vm.Script(s.code+'\n'+s.testCode,{filename:id}).runInNewContext({assert},{timeout:3000});
const source=await readFile(new URL('app-v2.js',root),'utf8');
assert.ok(source.includes("KEY='recall-coding-v1'"),'Existing browser progress key must remain unchanged');
// Run the actual backup validator with old-version progress and hostile IDs.
const validId=(id)=>typeof id==='string'&&/^[a-z0-9][a-z0-9-]{0,99}$/i.test(id)&&!['constructor','prototype','__proto__'].includes(id);
const validate=vm.runInNewContext('('+source.slice(source.indexOf('function validate('),source.indexOf('\ntry{const old='))+')',{validId});
const id=original.cards[0].id;
const old={reviews:{[id]:{due:123456,interval:7,count:3,rating:'easy'}},saved:[id],notes:{[id]:'Keep this note'},history:[{id,at:1234,rating:'good'}]};
const migrated=validate(old);assert.equal(migrated.notes[id],old.notes[id]);assert.equal(migrated.saved[0],id);assert.equal(migrated.reviews[id].count,3);assert.equal(migrated.history.length,1);
const bad=validate(JSON.parse('{"reviews":{"__proto__":{"due":1,"interval":2,"count":3,"rating":"easy"}},"saved":["constructor"],"notes":{"__proto__":"bad"},"history":[]}'));
assert.equal(Object.keys(bad.reviews).length,0);assert.equal(bad.saved.length,0);assert.equal(Object.keys(bad.notes).length,0);
console.log(`PASS: 533 cards / 6 decks; 475 JS companions; 22 modern Python solutions; ${imageReferences} cached image references; 6 OO executable tests; v1 progress migration; install/offline asset integrity.`);
