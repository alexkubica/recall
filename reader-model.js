// Pure ordering and URL helpers shared by the reader and its integrity checks.
export const PAGE_SIZE=10;
export function makeReadingIndex(order,cards){
 const byId=new Map(cards.map(card=>[card.id,card]));
 const seen=new Set(),chapters=order.chapters.map((chapter,index)=>({...chapter,number:index+1}));
 const entries=chapters.flatMap(chapter=>chapter.cardIds.map((id,index)=>{
  if(!byId.has(id)||seen.has(id))throw Error('Invalid reading entry: '+id);
  seen.add(id);return {card:byId.get(id),chapter,position:index+1};
 }));
 if(seen.size!==cards.length)throw Error('Reading path must include every card');
 return {chapters,entries,byId:new Map(entries.map(entry=>[entry.card.id,entry]))};
}
export function filterReading(entries,{chapter='',collection='',q='',unread=false,difficulty='',list=''},readIds=[]){
 const words=q.toLocaleLowerCase().trim().split(/\s+/).filter(Boolean),read=new Set(readIds);
 return entries.filter(({card,chapter:section})=>(!chapter||section.id===chapter)&&(!collection||card.deckId===collection)&&(!difficulty||card.difficulty?.toLowerCase()===difficulty)&&(!list||card.studyLists?.includes(list))&&(!unread||!read.has(card.id))&&words.every(word=>/^#\d+$/.test(word)?card.leetcode?.number===Number(word.slice(1)):`${card.title} ${card.topic} ${card.search} ${section.title} ${section.part}`.toLocaleLowerCase().includes(word)));
}
export function parseReadingRoute(hash,index){
 const [path,query='']=hash.replace(/^#/,'').split('?'),params=new URLSearchParams(query);
 const chapter=params.get('chapter')||'',collection=params.get('collection')||'',difficulty=params.get('difficulty')||'',list=params.get('list')||'';
 const page=Number(params.get('page'));
 return {id:path.startsWith('read/')?decodeURIComponent(path.slice(5)):null,chapter:index.chapters.some(c=>c.id===chapter)?chapter:'',collection:index.entries.some(e=>e.card.deckId===collection)?collection:'',difficulty:['easy','medium','hard'].includes(difficulty)?difficulty:'',list:index.entries.some(e=>e.card.studyLists?.includes(list))?list:'',q:(params.get('q')||'').slice(0,300),unread:params.get('unread')==='1',page:Number.isSafeInteger(page)&&page>0?page:1};
}
export function readingHash(route){
 const params=new URLSearchParams();
 for(const key of ['chapter','collection','difficulty','list','q'])if(route[key])params.set(key,route[key]);
 if(route.unread)params.set('unread','1');
 if(route.page>1)params.set('page',String(route.page));
 return '#'+(route.id?'read/'+encodeURIComponent(route.id):'library')+(params.size?'?'+params:'');
}
