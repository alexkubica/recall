import {readFile,writeFile,readdir,stat} from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {makeReadingIndex} from '../public/reader-model.js';
const root=fileURLToPath(new URL('../public/',import.meta.url));
const strict=process.argv.includes('--strict');
async function json(name,optional=false){try{return JSON.parse(await readFile(path.join(root,name),'utf8'))}catch(e){if(optional&&!strict)return null;throw e}}
const original=await json('deck.json');
const js=await json('javascript-solutions.json',true)||{};
const primer=await json('primer-decks.json',true)||{decks:[],cards:[]};
const leetcode=await json('leetcode-deck.json');
const modern=await json('modern-deck.json',true)||{cards:[]};
let oo={};try{oo=JSON.parse(await readFile(path.join(root,'oo-javascript-solutions.json'),'utf8'))}catch{}
const coding={id:'coding',title:'Coding foundations',description:'100 classic challenges. Build a solid foundation in algorithms and data structures.',source:original.source,license:'Apache-2.0',kind:'coding',icon:'code'};
const decks=[coding,...primer.decks,...(modern.deck?[modern.deck]:[]),leetcode.deck];
const cards=[...original.cards.map(c=>({...c,deckId:'coding',kind:'coding',source:original.source,solutions:{javascript:js[c.id]}})),...primer.cards,...modern.cards,...leetcode.cards].map(c=>({...c,solutions:{...(c.solutions||{}),...(oo[c.id]?{javascript:oo[c.id]}:{})}}));
const licenseFiles={'MIT':'licenses/Recall-MIT.txt','Apache-2.0':'licenses/Apache-2.0.txt','CC-BY-4.0':'licenses/CC-BY-4.0.txt','CC-BY-SA-4.0':'licenses/CC-BY-SA-4.0.txt'};
for(const c of cards){
 const coding=c.deckId==='coding',primerCard=['system-design','system-exercises','oo-design'].includes(c.deckId);
 const license=coding?'Apache-2.0':primerCard?'CC-BY-4.0':'CC-BY-SA-4.0';
 c.attribution={author:coding||primerCard?'Donne Martin and contributors; adaptations by Recall contributors':'Recall contributors',copyright:coding?'Copyright 2015 Donne Martin; changes 2026 Recall contributors':primerCard?'Copyright 2017 Donne Martin; changes 2026 Recall contributors':'Copyright 2026 Recall contributors',license,licenseUrl:licenseFiles[license],sourceUrl:coding?'https://github.com/donnemartin/interactive-coding-challenges':primerCard?'https://github.com/donnemartin/system-design-primer':'https://github.com/alexkubica/recall',changes:c.publicationChanges||(c.deckId==='leetcode'?'Independent brief and study guide. Reference code has separate author/license credits below.':'Original exercise; external documentation linked for further reading.')};
 if(c.deckId==='system-exercises')c.attribution.mediaCredits='media-credits.json';
}
const ids=new Set();
for(const c of cards){if(ids.has(c.id))throw Error('Duplicate card '+c.id);ids.add(c.id);if(!c.question||!c.answer)throw Error('Missing content '+c.id);c.search=[c.title,c.topic,c.summary||'',c.question,c.answer].join(' ').replace(/<[^>]*>/g,' ');c.sections||=[{title:'Answer',html:c.answer}];}
for(const d of decks){d.count=cards.filter(c=>c.deckId===d.id).length;if(!d.count)throw Error('Empty deck '+d.id);}
if(strict){if(Object.keys(oo).length!==6)throw Error('Expected all 6 OO JavaScript companions');if(original.cards.some(c=>!js[c.id]?.code))throw Error('JavaScript companion missing');if(primer.cards.length!==56)throw Error('Expected all 56 primer cards');if(modern.cards.length<30)throw Error('Expected at least 30 modern exercises');}
makeReadingIndex(await json('reading-order.json'),cards);
const library={version:5,name:'Recall interview collection',decks,cards,studyLists:leetcode.studyLists,updated:'2026-10-17'};
await writeFile(path.join(root,'library.json'),JSON.stringify(library));
async function files(dir=''){const out=[];for(const e of await readdir(path.join(root,dir),{withFileTypes:true})){const rel=path.posix.join(dir,e.name);if(e.isDirectory())out.push(...await files(rel));else out.push(rel)}return out}
const excluded=new Set(['.nojekyll','sw.js','offline-assets.json','deck.json','javascript-solutions.json','primer-decks.json','modern-deck.json','leetcode-deck.json','oo-javascript-solutions.json','app.js','primer-import-report.json']);
const assets=(await files()).filter(f=>!excluded.has(f)&&!f.endsWith('.map')&&!f.endsWith('.DS_Store')&&!f.includes('manifest-import')&&!f.includes('import-manifest')).sort();
const template=await readFile(new URL('./sw-template.js',import.meta.url),'utf8');
const hash=createHash('sha256').update(template);let bytes=0;
for(const asset of assets){const data=await readFile(path.join(root,asset));hash.update(asset).update(data);bytes+=data.length;}
const version=hash.digest('hex').slice(0,12);
const manifest={version,assets:['./',...assets.map(x=>'./'+x)],bytes,cards:cards.length,decks:decks.length};
await writeFile(path.join(root,'offline-assets.json'),JSON.stringify(manifest));
await writeFile(path.join(root,'sw.js'),template.replaceAll('__VERSION__',version).replace('__ASSET_LIST__',JSON.stringify(manifest.assets)).replace('__ASSET_BYTES__',String(bytes)));
console.log(JSON.stringify({version,decks:decks.map(d=>[d.title,d.count]),cards:cards.length,offlineAssets:manifest.assets.length,offlineMB:(bytes/1048576).toFixed(2)},null,2));
