"""Build the offline catalog from the verified metadata, original guides, and credited code."""
import json,html,pathlib,re
ROOT=pathlib.Path(__file__).resolve().parents[1]
def read(name):return json.loads((ROOT/'source'/'leetcode'/name).read_text())
metadata=read('catalog.json');guides=read('guides.json');refs=read('reference-solutions.json')
escape=lambda x:html.escape(str(x))
paragraph=lambda x:'<p>'+escape(x)+'</p>'
cards=[]
for p in metadata['problems']:
 key=str(p['number']);g=guides[key]
 assert len(g['edgeCases'])>=3 and g['summary'] and g['approach'] and g['complexity'],key
 code=refs[key]
 assert all(code[x]['code'].strip() for x in ['javascript','python']),key
 sections=[{'title':'How to approach it','html':paragraph(g['approach'])},{'title':'Target complexity','html':paragraph(g['complexity'])+'<p>These bounds describe the target approach above. Compare the reference implementation’s data structures and copying costs before assigning it the same bounds.</p>'}]
 question=paragraph(g['summary'])+'<p class="code-note">Independent study brief. Open the official problem for the complete constraints and judge examples.</p>'
 answer=''.join('<h3>'+escape(s['title'])+'</h3>'+s['html'] for s in sections)
 answer+='<h3>Cases to walk through</h3><ul>'+''.join('<li>'+escape(x)+'</li>' for x in g['edgeCases'])+'</ul>'
 sources=[{'title':'LeetCode #'+key+' · '+p['title'],'url':p['url']}]+[{'title':l['title'],'url':l['source']} for l in metadata['lists'] if l['id'] in p['studyLists']]
 cards.append({'id':'leetcode-'+key,'number':p['number'],'title':p['title'],'summary':g['summary'],'topic':p['topic'],'deckId':'leetcode','kind':'coding','difficulty':p['difficulty'],'question':question,'answer':answer,'sections':sections,'edgeCases':g['edgeCases'],'studyLists':p['studyLists'],'leetcode':{'number':p['number'],'slug':p['slug'],'url':p['url'],'premium':p['premium'],'checkedAt':metadata['retrievedAt']},'solutions':code,'sources':sources,'sourceOrder':p['sourceOrder'],'search':' '.join(['leetcode',key,'#'+key,p['slug'],*p['topics'],*[l['title'] for l in metadata['lists'] if l['id'] in p['studyLists']]])})
assert len(cards)==347
for l in metadata['lists']:assert sum(l['id'] in c['studyLists'] for c in cards)==l['count'],l['id']
deck={'id':'leetcode','title':'Popular LeetCode','description':'347 distinct problems from six popular study lists. Original study briefs, credited JavaScript and Python references, and links to the official judge.','kind':'coding','icon':'code','license':'Mixed: original guides; credited reference code under CC-BY-SA-4.0 or MIT','source':'https://leetcode.com/studyplan/'}
(ROOT/'public'/'leetcode-deck.json').write_text(json.dumps({'deck':deck,'cards':cards,'studyLists':metadata['lists'],'checkedAt':metadata['retrievedAt']},ensure_ascii=False,separators=(',',':'))+'\n')
chapters=[
('arrays-hashing','Arrays & Hashing','Build lookup tables, counts, prefixes, and useful array invariants.'),
('two-pointers','Two Pointers','Move through sequences with a purpose: boundaries, ordering, and pairs.'),
('sliding-window','Sliding Window','Grow and shrink a contiguous range while preserving a useful condition.'),
('stack','Stack','Model nested structure and remember the unresolved candidates.'),
('binary-search','Binary Search','Identify the monotone decision, then shrink the answer space.'),
('linked-list','Linked List','Reason about pointer ownership, rewiring, and sentinel nodes.'),
('trees','Trees','Connect local subtree answers to a complete traversal.'),
('tries','Tries','Share prefixes to organize words and prune search.'),
('heap','Heap / Priority Queue','Keep the next best candidate without sorting every update.'),
('backtracking','Backtracking','Enumerate valid choices, restore state, and prune impossible branches.'),
('graphs','Graphs','Use reachability, traversal layers, and connectivity to model relationships.'),
('advanced-graphs','Advanced Graphs','Build on graph basics with weights, ordering, and spanning trees.'),
('one-dp','1-D Dynamic Programming','Choose a state that makes repeated subproblems explicit.'),
('two-dp','2-D Dynamic Programming','Track interacting choices across sequences, grids, and intervals.'),
('greedy','Greedy','Prove why a local choice leaves a valid optimal continuation.'),
('intervals','Intervals','Reason about overlap, boundaries, and chronological order.'),
('math','Math & Geometry','Turn numeric and geometric structure into smaller computations.'),
('bits','Bit Manipulation','Use binary representation carefully, including JavaScript integer limits.')]
order=json.loads((ROOT/'public'/'reading-order.json').read_text());order['chapters']=[x for x in order['chapters'] if not x['id'].startswith('lc-')]
for id,topic,description in chapters:
 matching=sorted((c for c in cards if c['topic']==topic),key=lambda c:({'Easy':0,'Medium':1,'Hard':2}[c['difficulty']],c['sourceOrder'],c['number']))
 assert matching,topic
 order['chapters'].append({'id':'lc-'+id,'title':topic+' practice','part':'LeetCode practice','description':description+' Progress from easy to medium to hard.','cardIds':[c['id'] for c in matching]})
(ROOT/'public'/'reading-order.json').write_text(json.dumps(order,ensure_ascii=False,indent=2)+'\n')
print('Built',len(cards),'LeetCode guides with paired code; added',len(chapters),'curated chapters.')
