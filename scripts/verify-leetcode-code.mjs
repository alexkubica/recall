import {readFile} from 'node:fs/promises';
import vm from 'node:vm';
import assert from 'node:assert/strict';
const refs=JSON.parse(await readFile(new URL('../source/leetcode/reference-solutions.json',import.meta.url)));
for(const [id,langs] of Object.entries(refs))new vm.Script(langs.javascript.code,{filename:id+'.js'});
let checks=0;
const check=(a,b)=>{assert.deepEqual(JSON.parse(JSON.stringify(a)),b);checks++};
function run(id,expression,globals={}){return new vm.Script(refs[id].javascript.code+'\n'+expression).runInNewContext(globals,{timeout:2000})}
check(run('140','wordBreak("catsanddog", ["cat","cats","and","sand","dog"]).sort()'),['cat sand dog','cats and dog']);
check(run('140','wordBreak("a", ["b"])'),[]);
check(run('221','maximalSquare([["1","0","1","0","0"],["1","0","1","1","1"],["1","1","1","1","1"],["1","0","0","1","0"]])'),4);
check(run('221','maximalSquare([["0"]])'),0);
check(run('229','majorityElement([1,2,1,2,3,2,1]).sort()'),[1,2]);
check(run('229','majorityElement([1,2,3])'),[]);
check(run('373','kSmallestPairs([1,7,11],[2,4,6],3)'),[[1,2],[1,4],[1,6]]);
check(run('373','kSmallestPairs([1],[2],10)'),[[1,2]]);
const Node=function(val,isLeaf,topLeft,topRight,bottomLeft,bottomRight){Object.assign(this,{val,isLeaf,topLeft,topRight,bottomLeft,bottomRight})};
check(run('427','construct([[1,1],[1,1]]).isLeaf',{Node}),true);
check(run('427','[construct([[1,0],[0,1]]).isLeaf, construct([[1,0],[0,1]]).topRight.val]',{Node}),[false,false]);
check(run('443','(()=>{let a=[..."aabcccccccccccc"];const n=compress(a);return [n,a.slice(0,n).join("")]})()'),[6,'a2bc12']);
check(run('443','(()=>{let a=["a"];return compress(a)})()'),1);
check(run('1372','longestZigZag({left:{right:{left:{}}}})'),3);
check(run('1372','longestZigZag({left:{left:{left:{}}}})'),1);
check(run('1489','findCriticalAndPseudoCriticalEdges(5, [[0,1,1],[1,2,1],[2,3,2],[0,3,2],[0,4,3],[3,4,3],[1,4,6]]).map(a=>a.sort((a,b)=>a-b))'),[[0,1],[2,3,4,5]]);
check(run('1489','findCriticalAndPseudoCriticalEdges(3, [[0,1,1],[1,2,1],[0,2,1]]).map(a=>a.sort())'),[[],[0,1,2]]);
check(run('2709','[canTraverseAllPairs([2,3,6]),canTraverseAllPairs([3,9,5]),canTraverseAllPairs([1]),canTraverseAllPairs([1,2])]'),[true,false,true,false]);
check(run('860','lemonadeChange([5,5,5,10,20])'),true);
check(run('860','lemonadeChange([5,5,10,10,20])'),false);
// Independent exhaustive oracles for voting, heap enumeration, and factor connectivity.
let seed=32;const rnd=n=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed%n};
for(let t=0;t<100;t++){
 const a=Array.from({length:1+rnd(12)},()=>rnd(7));
 const counts=new Map();for(const x of a)counts.set(x,(counts.get(x)||0)+1);
 check(run('229',`majorityElement(${JSON.stringify(a)}).sort((a,b)=>a-b)`),[...counts].filter(([,n])=>n>a.length/3).map(([x])=>x).sort((a,b)=>a-b));
 const left=Array.from({length:1+rnd(5)},()=>rnd(15)-7).sort((a,b)=>a-b),right=Array.from({length:1+rnd(5)},()=>rnd(15)-7).sort((a,b)=>a-b),k=1+rnd(20);
 const expected=left.flatMap(x=>right.map(y=>x+y)).sort((a,b)=>a-b).slice(0,k);
 check(run('373',`kSmallestPairs(${JSON.stringify(left)},${JSON.stringify(right)},${k}).map(([a,b])=>a+b).sort((a,b)=>a-b)`),expected);
 const nums=Array.from({length:1+rnd(8)},()=>1+rnd(35));
 const gcd=(a,b)=>b?gcd(b,a%b):a,seen=new Set([0]),queue=[0];
 for(let at=0;at<queue.length;at++)for(let j=0;j<nums.length;j++)if(!seen.has(j)&&gcd(nums[queue[at]],nums[j])>1){seen.add(j);queue.push(j)}
 check(run('2709',`canTraverseAllPairs(${JSON.stringify(nums)})`),seen.size===nums.length);
}
console.log(`PASS: ${Object.keys(refs).length} JavaScript references parse; ${checks} example and independent oracle checks cover all nine new implementations and the converted module.`);
