import assert from 'node:assert/strict';
import vm from 'node:vm';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const solutions=JSON.parse(fs.readFileSync(path.join(root,'public/javascript-solutions.json'),'utf8'));
const cards=JSON.parse(fs.readFileSync(path.join(root,'public/deck.json'),'utf8')).cards;
let assertions=0, passed=0;
const failures=[];
// These are authored, trusted local snippets. vm separates declarations between
// cards; it is NOT a security boundary and must not run arbitrary user input.
for (const card of cards.slice(0,100)) {
  const entry=solutions[card.id];
  try {
    assert.ok(entry, `Missing JavaScript companion for ${card.id}`);
    for (const field of ['code','testCode','notes','complexity']) assert.equal(typeof entry[field],'string');
    const trackedAssert=new Proxy(assert, {
      apply(target,receiver,args) { assertions++; return Reflect.apply(target,receiver,args); },
      get(target,key) {
        const value=Reflect.get(target,key);
        if (typeof value !== 'function') return value;
        return (...args)=>{ assertions++; return value(...args); };
      }
    });
    const context=vm.createContext({assert:trackedAssert});
    // Assertions are realm-local so arrays/objects use the same prototypes as
    // expected values. Node's strict assert sees both from this context.
    new vm.Script(`${entry.code}\n${entry.testCode}`,{filename:`card-${card.number}-${card.id}.js`}).runInContext(context,{timeout:3000});
    passed++;
  } catch (error) { failures.push({number:card.number,title:card.title,error:error.stack}); }
}
for (const failure of failures) console.error(`${failure.number}. ${failure.title}\n${failure.error}\n`);
console.log(`${passed}/${Math.min(cards.length,100)} JavaScript companion snippets passed; ${assertions} example/edge assertions executed.`);
if (failures.length) process.exitCode=1;

let propertyAssertions=0;
function propertyCheck(number, body) {
  const entry=solutions[cards.find(card=>card.number===number).id];
  const context=vm.createContext({assert:new Proxy(assert, {
    get(target,key) { const fn=Reflect.get(target,key); return typeof fn==='function' ? (...args)=>{ propertyAssertions++; return fn(...args); } : fn; }
  })});
  new vm.Script(entry.code+'\n'+body,{filename:`property-card-${number}.js`}).runInContext(context,{timeout:10000});
}

const seeded=`
let seed=3421;
function random(limit) { seed=(Math.imul(seed,1664525)+1013904223)>>>0; return seed%limit; }
`;
for (const [number,fn] of [[66,'insertionSort'],[68,'mergeSort'],[70,'quickSort'],[71,'radixSort'],[74,'selectionSort']]) {
  propertyCheck(number,seeded+`
    for(let trial=0;trial<100;trial++) {
      const values=Array.from({length:random(30)},()=>random(101)-50);
      assert.deepEqual(${fn}(values.slice()),values.slice().sort((a,b)=>a-b));
    }
  `);
}
propertyCheck(100,seeded+`
  const heap=new MinHeap(), oracle=[];
  for(let trial=0;trial<500;trial++) {
    if(random(3)>0) { const value=random(101)-50; heap.insert(value); oracle.push(value); }
    else { oracle.sort((a,b)=>a-b); assert.equal(heap.extractMin(),oracle.length?oracle.shift():null); }
  }
  oracle.sort((a,b)=>a-b);
  for(const value of oracle) assert.equal(heap.extractMin(),value);
  assert.equal(heap.extractMin(),null);
`);
propertyCheck(81,`
  const count=n=>n.toString(2).replaceAll('0','').length;
  for(let value=1n;value<=1024n;value++) {
    const actual=nextSamePopcount(value), bits=count(value);
    let smaller=value-1n,larger=value+1n;
    while(smaller>0n && count(smaller)!==bits) smaller--;
    while(count(larger)!==bits) larger++;
    assert.equal(actual.smaller,smaller>0n?smaller:null); assert.equal(actual.larger,larger);
  }
`);
propertyCheck(85,`
  for(let a=-50n;a<=50n;a++) for(let b=-50n;b<=50n;b++) assert.equal(subtractWithoutArithmetic(a,b),a-b);
`);
propertyCheck(45,seeded+`
  for(let trial=0;trial<200;trial++) {
    const number=(random(65536)*65536+random(65536))>>>0; let best=0;
    for(let bit=0;bit<32;bit++) {
      const changed=(number|(1<<bit))>>>0; let run=0;
      for(let j=0;j<32;j++) { run=((changed>>>j)&1)?run+1:0; best=Math.max(best,run); }
    }
    assert.equal(longestOnesAfterFlip(number),best);
  }
`);
propertyCheck(56,seeded+`
  for(let trial=0;trial<150;trial++) {
    const values=Array.from({length:random(9)},()=>random(11)-5);
    let best=0;
    for(let mask=0;mask<2**values.length;mask++) {
      const sequence=values.filter((_,i)=>mask&(1<<i));
      if(sequence.every((x,i)=>i===0||sequence[i-1]<x)) best=Math.max(best,sequence.length);
    }
    const result=longestIncreasingSubsequence(values); assert.equal(result.length,best);
    let next=0; for(const value of values) if(result[next]===value) next++;
    assert.equal(next,result.length); assert.ok(result.every((x,i)=>i===0||result[i-1]<x));
  }
`);
propertyCheck(60,seeded+`
  function brute(prices,k,start=0) {
    let best=0;
    if(k===0) return 0;
    for(let buy=start;buy<prices.length;buy++) for(let sell=buy+1;sell<prices.length;sell++) {
      best=Math.max(best,prices[sell]-prices[buy]+brute(prices,k-1,sell+1));
    }
    return best;
  }
  for(let trial=0;trial<250;trial++) {
    const prices=Array.from({length:random(9)},()=>random(11)-3),k=random(4), result=maxProfitWithTrades(prices,k);
    assert.equal(result.profit,brute(prices,k)); assert.ok(result.transactions.length<=k);
    let previous=-1,profit=0;
    for(const {buy,sell} of result.transactions) { assert.ok(buy>previous&&sell>buy&&sell<prices.length); previous=sell; profit+=prices[sell]-prices[buy]; }
    assert.equal(profit,result.profit);
  }
`);
propertyCheck(72,seeded+`
  for(let trial=0;trial<200;trial++) {
    const values=Array.from({length:random(20)},()=>random(8)).sort((a,b)=>a-b),rotate=random(values.length+1);
    const rotated=values.slice(rotate).concat(values.slice(0,rotate));
    for(let target=0;target<9;target++) {
      const index=searchRotated(rotated,target);
      if(rotated.includes(target)) assert.equal(rotated[index],target); else assert.equal(index,null);
    }
  }
`);
propertyCheck(34,seeded+`
  for(let trial=0;trial<60;trial++) {
    const n=5,g=new Graph(),dist=Array.from({length:n},(_,i)=>Array.from({length:n},(_,j)=>i===j?0:Infinity));
    for(let i=0;i<n;i++) g.addNode(i);
    for(let i=0;i<n;i++) for(let j=0;j<n;j++) if(i!==j&&random(3)===0) { const w=random(8); g.addEdge(i,j,w); dist[i][j]=w; }
    for(let k=0;k<n;k++) for(let i=0;i<n;i++) for(let j=0;j<n;j++) dist[i][j]=Math.min(dist[i][j],dist[i][k]+dist[k][j]);
    for(let i=0;i<n;i++) for(let j=0;j<n;j++) {
      const result=shortestWeightedPath(g,i,j);
      if(dist[i][j]===Infinity) assert.equal(result,null);
      else { assert.equal(result.distance,dist[i][j]); assert.equal(result.path[0],i); assert.equal(result.path.at(-1),j); let cost=0; for(let p=1;p<result.path.length;p++) cost+=g.edges.get(result.path[p-1]).get(result.path[p]); assert.equal(cost,dist[i][j]); }
    }
  }
`);
console.log(`${propertyAssertions} deterministic property assertions passed across 13 algorithm variants.`);
