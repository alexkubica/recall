import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {makeReadingIndex,filterReading,readingHash,parseReadingRoute} from '../public/reader-model.js';
const read=async p=>JSON.parse(await readFile(new URL('../'+p,import.meta.url)));
const [library,catalog,guides,order,offline]=await Promise.all(['public/library.json','source/leetcode/catalog.json','source/leetcode/guides.json','public/reading-order.json','public/offline-assets.json'].map(read));
const cards=library.cards.filter(c=>c.deckId==='leetcode'),index=makeReadingIndex(order,library.cards);
assert.equal(cards.length,347);assert.equal(library.cards.length,533);
assert.equal(new Set(cards.map(c=>c.leetcode.number)).size,347);assert.equal(new Set(cards.map(c=>c.leetcode.slug)).size,347);
assert.equal(cards.filter(c=>c.leetcode.premium).length,7);
for(const c of cards){
 const p=catalog.problems.find(p=>p.number===c.number);
 assert.ok(p);assert.equal(c.id,`leetcode-${p.number}`);assert.equal(c.title,p.title);assert.equal(c.leetcode.url,`https://leetcode.com/problems/${p.slug}/`);
 assert.deepEqual(c.studyLists,p.studyLists);assert.ok(guides[String(p.number)]);
 for(const lang of ['javascript','python']){
  const s=c.solutions[lang];assert.ok(s.code.length>50&&s.sourceUrl.startsWith('https://github.com/'));
  assert.ok(['MIT','CC-BY-SA-4.0'].includes(s.license));assert.ok(s.code.includes(s.sourceUrl));
 }
 assert.ok(c.edgeCases.length>=3);
 assert.ok(index.byId.get(c.id).chapter.id.startsWith('lc-'));
}
for(const l of catalog.lists){
 const found=filterReading(index.entries,{list:l.id});assert.equal(found.length,l.count,l.title);
 assert.deepEqual(new Set(found.map(e=>e.card.id)),new Set(cards.filter(c=>c.studyLists.includes(l.id)).map(c=>c.id)));
 for(const difficulty of ['easy','medium','hard']){
  const match=filterReading(index.entries,{list:l.id,difficulty,collection:'leetcode'});
  assert.ok(match.every(e=>e.card.difficulty.toLowerCase()===difficulty&&e.card.studyLists.includes(l.id)));
  const route={id:match[0]?.card.id||null,chapter:'',collection:'leetcode',difficulty,list:l.id,q:'',unread:false,page:1};
  assert.deepEqual(parseReadingRoute(readingHash(route),index),route);
 }
}
for(const chapter of index.chapters.filter(c=>c.id.startsWith('lc-'))){
 const ranks=chapter.cardIds.map(id=>({Easy:0,Medium:1,Hard:2})[index.byId.get(id).card.difficulty]);
 assert.deepEqual(ranks,[...ranks].sort());
}
assert.equal(filterReading(index.entries,{collection:'leetcode',q:'#1'}).some(e=>e.card.id==='leetcode-1'),true);
assert.equal(filterReading(index.entries,{collection:'leetcode',q:'two sum'}).some(e=>e.card.id==='leetcode-1'),true);
assert.equal(filterReading(index.entries,{collection:'coding',list:'leetcode-75'}).length,0);
assert.equal(parseReadingRoute('#library?difficulty=garbage&list=unknown',index).difficulty,'');
assert.equal(parseReadingRoute('#library?difficulty=garbage&list=unknown',index).list,'');
for(const file of ['DOOCS-LICENSE.txt','NEETCODE-LICENSE.txt','library.json'])assert.ok(offline.assets.includes('./'+file));
console.log('PASS: 347 unique official IDs/slugs, all six exact list memberships, 694 credited references, difficulty/list intersections, curated order, URL round trips, Premium labels, and offline credits.');
