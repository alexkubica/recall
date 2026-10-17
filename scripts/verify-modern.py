"""Execute every published reference solution, plus seeded independent oracle cases.

Usage: python3 scripts/verify-modern.py
Requires Python 3.9+ and Node 20+; uses only standard libraries. The generated
programs use the exact code and tests shipped in public/modern-deck.json.
"""
import html.parser
import itertools
import json
import random
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RNG = random.Random(20261016)
DATA = json.loads((ROOT / 'public' / 'modern-deck.json').read_text())
CARDS = DATA['cards']
EXTRA = {card['id']: {'javascript': [], 'python': []} for card in CARDS}
ORACLE_COUNTS = {}

def case(number, js_function, py_function, args, expected):
    card_id = 'modern-%03d' % number
    # Parse JSON rather than embed object literals: a literal __proto__ key has
    # special prototype semantics, while an API JSON payload has an own key.
    EXTRA[card_id]['javascript'].append('assert.deepEqual(%s(...JSON.parse(%s)), %s);' % (js_function,json.dumps(json.dumps(args)),json.dumps(expected)))
    EXTRA[card_id]['python'].append('assert %s(*%r) == %r' % (py_function,args,expected))
    ORACLE_COUNTS[card_id] = ORACLE_COUNTS.get(card_id,0)+1

class SafeHTML(html.parser.HTMLParser):
    ALLOWED = {'p','h3','ul','li','strong','em','code','pre','br'}
    def handle_starttag(self, tag, attrs):
        assert tag in self.ALLOWED, 'Unexpected HTML tag: '+tag
        assert not attrs, 'Unexpected HTML attributes'

def validate_schema():
    assert DATA['deck']['id'] == 'modern'
    assert len(CARDS) == 30
    assert len({c['id'] for c in CARDS}) == len(CARDS)
    assert [c['number'] for c in CARDS] == list(range(1,31))
    assert sum(c['kind']=='coding' for c in CARDS) == 18
    assert sum(c['kind']=='concept' for c in CARDS) == 4
    assert sum(c['kind']=='design' for c in CARDS) == 8
    for card in CARDS:
        assert card['deckId'] == 'modern'
        assert card['title'] and card['search'] and card['sources']
        assert 15 <= card['timeMinutes'] <= 60
        assert all(s['url'].startswith('https://') for s in card['sources'])
        for value in [card['question'],card['answer'],*(s['html'] for s in card['sections'])]:
            SafeHTML().feed(value)
        titles = {s['title'] for s in card['sections']}
        assert 'Hint' in titles and 'Interviewer follow-up' in titles and 'Self-review rubric' in titles
        if card['kind'] != 'design':
            assert set(card['solutions']) == {'javascript','python'}
            for solution in card['solutions'].values():
                assert all(solution[k] for k in ('code','testCode','notes','complexity'))

# Small exhaustive/reference models favor clarity over implementation similarity.
for _ in range(90):
    time = 0
    events = []
    for _ in range(RNG.randrange(14)):
        time += RNG.randrange(4)
        events.append([time,RNG.choice(['a','b','c','__proto__'])])
    window = RNG.randrange(1,8)
    accepted = []
    expected = []
    for t,key in events:
        ok = not any(k==key and t-window < when <= t for when,k in accepted)
        expected.append(ok)
        if ok:
            accepted.append((t,key))
    case(1,'acceptEvents','accept_events',[events,window],expected)

for _ in range(100):
    signals = [RNG.choice('abcd') for _ in range(RNG.randrange(10))]
    required = [RNG.choice('abcx') for _ in range(RNG.randrange(4))]
    windows = [(j-i,i,j) for i in range(len(signals)+1) for j in range(i,len(signals)+1) if set(required) <= set(signals[i:j])]
    best = min(windows) if windows else None
    expected = [best[1],best[2]] if best is not None else None
    case(2,'evidenceWindow','evidence_window',[signals,required],expected)

for _ in range(70):
    errors = [RNG.choice(['503','400','429','__proto__','a']) for _ in range(RNG.randrange(15))]
    k = RNG.randrange(8)
    expected = sorted(set(errors),key=lambda e:(-errors.count(e),e))[:k]
    case(3,'topErrors','top_errors',[errors,k],expected)

for _ in range(90):
    intervals = []
    occupied = set()
    for _ in range(RNG.randrange(10)):
        a,b = sorted([RNG.randrange(15),RNG.randrange(15)])
        intervals.append([a,b])
        occupied.update(range(a,b))
    expected = []
    for byte in sorted(occupied):
        if expected and expected[-1][1] == byte:
            expected[-1][1] += 1
        else:
            expected.append([byte,byte+1])
    case(4,'mergeRanges','merge_ranges',[intervals],expected)

EXTRA['modern-005']['javascript'].append('''
function checkedChain(graph,source,target) {
  const path=shortestChain(graph,source,target);
  if (!path.length) return null;
  assert.equal(path[0],source); assert.equal(path[path.length-1],target);
  for (let i=1;i<path.length;i++) assert.ok((Object.hasOwn(graph,path[i-1]) ? graph[path[i-1]] : []).includes(path[i]));
  return path.length-1;
}
''')
EXTRA['modern-005']['python'].append('''
def checked_chain(graph,source,target):
    path=shortest_chain(graph,source,target)
    if not path:
        return None
    assert path[0]==source and path[-1]==target
    assert all(b in graph.get(a,[]) for a,b in zip(path,path[1:]))
    return len(path)-1
''')
for _ in range(70):
    names = ['a','b','c','d','__proto__','constructor']
    n = RNG.randrange(1,7)
    names = names[:n]
    graph = {name:[other for other in names if RNG.random()<0.25] for name in names}
    source,target = RNG.choice(names),RNG.choice(names)
    dist = [[0 if i==j else 100 for j in range(n)] for i in range(n)]
    for i,name in enumerate(names):
        for other in graph[name]:
            dist[i][names.index(other)] = min(dist[i][names.index(other)],1)
    for k in range(n):
        for i in range(n):
            for j in range(n):
                dist[i][j] = min(dist[i][j],dist[i][k]+dist[k][j])
    expected = dist[names.index(source)][names.index(target)]
    case(5,'checkedChain','checked_chain',[graph,source,target],None if expected==100 else expected)

EXTRA['modern-006']['javascript'].append('''
function checkedOrder(n,edges) {
  const order=deploymentOrder(n,edges);
  if (order===null) return false;
  assert.deepEqual([...order].sort((a,b)=>a-b),Array.from({length:n},(_,i)=>i));
  for (const [a,b] of edges) assert.ok(order.indexOf(a)<order.indexOf(b));
  return true;
}
''')
EXTRA['modern-006']['python'].append('''
def checked_order(n,edges):
    order=deployment_order(n,edges)
    if order is None:
        return False
    assert sorted(order)==list(range(n))
    assert all(order.index(a)<order.index(b) for a,b in edges)
    return True
''')
for _ in range(70):
    n = RNG.randrange(7)
    edges = [[a,b] for a in range(n) for b in range(n) if RNG.random()<0.2]
    if edges and RNG.random()<0.5:
        edges.append(RNG.choice(edges))
    expected = any(all(order.index(a)<order.index(b) for a,b in edges) for order in itertools.permutations(range(n)))
    case(6,'checkedOrder','checked_order',[n,edges],expected)

for _ in range(100):
    n = RNG.randrange(1,7)
    edges = [[a,b,RNG.randrange(10)] for a in range(n) for b in range(n) if RNG.random()<0.25]
    source,target = RNG.randrange(n),RNG.randrange(n)
    dist = [float('inf')]*n
    dist[source] = 0
    for _ in range(n-1):
        previous = dist[:]
        for a,b,w in edges:
            dist[b] = min(dist[b],previous[a]+w)
    expected = None if dist[target]==float('inf') else dist[target]
    case(7,'leastLatency','least_latency',[n,edges,source,target],expected)

EXTRA['modern-008']['javascript'].append('''
function exerciseCache(capacity,operations) {
  const cache=new LRUCache(capacity), result=[];
  for (const [op,key,value] of operations) {
    if (op==='put') cache.put(key,value);
    else result.push(cache.get(key));
  }
  return result;
}
''')
EXTRA['modern-008']['python'].append('''
def exercise_cache(capacity,operations):
    cache=LRUCache(capacity)
    result=[]
    for op,key,value in operations:
        if op=='put':
            cache.put(key,value)
        else:
            result.append(cache.get(key))
    return result
''')
for _ in range(80):
    capacity = RNG.randrange(5)
    operations = []
    order = []
    expected = []
    for _ in range(30):
        key = RNG.choice('abcde')
        op = RNG.choice(['get','put'])
        value = RNG.randrange(10)
        operations.append([op,key,value])
        entry = next((item for item in order if item[0]==key),None)
        if entry:
            order.remove(entry)
        if op=='get':
            expected.append(entry[1] if entry else None)
            if entry:
                order.append(entry)
        else:
            order.append((key,value))
            order = order[-capacity:] if capacity else []
    case(8,'exerciseCache','exercise_cache',[capacity,operations],expected)

for _ in range(100):
    values = [RNG.randrange(-10,15) for _ in range(RNG.randrange(1,35))]
    k = RNG.randrange(1,len(values)+1)
    expected = [max(values[i:i+k]) for i in range(len(values)-k+1)]
    case(9,'rollingPeak','rolling_peak',[values,k],expected)

for _ in range(100):
    costs = [RNG.randrange(8) for _ in range(RNG.randrange(10))]
    budget = RNG.randrange(15)
    length,start,end = min((-(j-i),i,j) for i in range(len(costs)+1) for j in range(i,len(costs)+1) if sum(costs[i:j])<=budget)
    case(10,'budgetWindow','budget_window',[costs,budget],[start,end])

for _ in range(80):
    streams = [sorted(RNG.randrange(-10,20) for _ in range(RNG.randrange(10))) for _ in range(RNG.randrange(8))]
    expected = sorted(x for stream in streams for x in stream)
    case(11,'mergeStreams','merge_streams',[streams],expected)

EXTRA['modern-012']['javascript'].append('function queryPrefixes(entries,queries) { const r=new PrefixRegistry(entries); return queries.map(q=>r.match(q)); }')
EXTRA['modern-012']['python'].append('def query_prefixes(entries,queries):\n    r=PrefixRegistry(entries)\n    return [r.match(q) for q in queries]')
for _ in range(70):
    entries = [(''.join(RNG.choice('abc/') for _ in range(RNG.randrange(6))),str(i)) for i in range(RNG.randrange(12))]
    queries = [''.join(RNG.choice('abc/') for _ in range(RNG.randrange(9))) for _ in range(12)]
    latest = dict(entries)
    expected = []
    for query in queries:
        matching = [p for p in latest if query.startswith(p)]
        expected.append(latest[max(matching,key=len)] if matching else None)
    case(12,'queryPrefixes','query_prefixes',[entries,queries],expected)

for _ in range(80):
    n = RNG.randrange(10)
    links = [[a,b] for a in range(n) for b in range(a,n) if RNG.random()<0.2]
    unvisited = set(range(n))
    expected = []
    while unvisited:
        component = {min(unvisited)}
        changed = True
        while changed:
            changed = False
            for a,b in links:
                if (a in component) != (b in component):
                    component.update([a,b]); changed=True
        expected.append(sorted(component))
        unvisited -= component
    case(13,'deviceGroups','device_groups',[n,links],expected)

for _ in range(80):
    costs = [RNG.randrange(1,8) for _ in range(RNG.randrange(1,8))]
    batches = RNG.randrange(1,len(costs)+3)
    expected = sum(costs)
    # Enumerate every cut pattern, independent of binary-search feasibility.
    for cuts in itertools.product([False,True],repeat=len(costs)-1):
        if sum(cuts)+1 > batches:
            continue
        groups = [costs[0]]
        for cut,cost in zip(cuts,costs[1:]):
            if cut: groups.append(cost)
            else: groups[-1] += cost
        expected = min(expected,max(groups))
    case(14,'minCapacity','min_capacity',[costs,batches],expected)

for _ in range(100):
    values = [RNG.randrange(-4,5) for _ in range(RNG.randrange(12))]
    target = RNG.randrange(-6,7)
    expected = sum(sum(values[i:j])==target for i in range(len(values)) for j in range(i+1,len(values)+1))
    case(15,'usageBursts','usage_bursts',[values,target],expected)

EXTRA['modern-016']['javascript'].append('''
function checkedSplit(text,tokens) {
  const parts=splitIdentifier(text,tokens);
  if (parts===null) return null;
  assert.equal(parts.join(''),text); assert.ok(parts.every(x=>tokens.includes(x)));
  return parts.length;
}
''')
EXTRA['modern-016']['python'].append('''
def checked_split(text,tokens):
    parts=split_identifier(text,tokens)
    if parts is None:
        return None
    assert ''.join(parts)==text and all(p in tokens for p in parts)
    return len(parts)
''')
for _ in range(80):
    value = ''.join(RNG.choice('ab') for _ in range(RNG.randrange(9)))
    tokens = [x for x in ['a','b','aa','ab','ba','bb','aaa','bbb'] if RNG.random()<0.5]
    def enumerate_splits(s):
        if not s: return [0]
        return [1+count for token in tokens if s.startswith(token) for count in enumerate_splits(s[len(token):])]
    options = enumerate_splits(value)
    expected = min(options) if options else None
    case(16,'checkedSplit','checked_split',[value,tokens],expected)

EXTRA['modern-017']['javascript'].append('''
function checkedSchedule(intervals) {
  const chosen=maintenanceSchedule(intervals);
  assert.equal(new Set(chosen).size,chosen.length);
  for (let i=1;i<chosen.length;i++) assert.ok(intervals[chosen[i-1]][1]<=intervals[chosen[i]][0]);
  return chosen.length;
}
''')
EXTRA['modern-017']['python'].append('''
def checked_schedule(intervals):
    chosen=maintenance_schedule(intervals)
    assert len(set(chosen))==len(chosen)
    assert all(intervals[a][1]<=intervals[b][0] for a,b in zip(chosen,chosen[1:]))
    return len(chosen)
''')
for _ in range(80):
    intervals = []
    for _ in range(RNG.randrange(9)):
        start = RNG.randrange(10)
        intervals.append([start,start+RNG.randrange(1,6)])
    expected = 0
    for mask in range(1<<len(intervals)):
        selected = sorted(intervals[i] for i in range(len(intervals)) if mask>>i&1)
        if all(a[1]<=b[0] for a,b in zip(selected,selected[1:])):
            expected=max(expected,len(selected))
    case(17,'checkedSchedule','checked_schedule',[intervals],expected)

for _ in range(80):
    rows,cols = RNG.randrange(6),RNG.randrange(6)
    grid = [[RNG.randrange(2) for _ in range(cols)] for _ in range(rows)]
    affected = {(r,c) for r in range(rows) for c in range(cols) if grid[r][c]}
    expected = 0
    while affected:
        component = {min(affected)}
        while True:
            grown = component | {p for p in affected if any(abs(p[0]-q[0])+abs(p[1]-q[1])==1 for q in component)}
            if grown==component: break
            component=grown
        expected=max(expected,len(component))
        affected -= component
    case(18,'largestOutage','largest_outage',[grid],expected)

for _ in range(70):
    ids = [str(RNG.randrange(2**64)) for _ in range(RNG.randrange(12))]
    ids += ids[:3]
    # Canonical positive decimal strings also compare by length then lexically.
    expected = sorted(set(ids),key=lambda x:(len(x),x))
    case(19,'sortIds','sort_ids',[ids],expected)

def main():
    validate_schema()
    node = shutil.which('node')
    assert node, 'Node.js is required'
    scratch = ROOT / 'work'
    scratch.mkdir(exist_ok=True)
    failures = []
    programs = 0
    with tempfile.TemporaryDirectory(prefix='modern-check-',dir=scratch) as tmp:
        for card in CARDS:
            for language,solution in card.get('solutions',{}).items():
                extension = '.mjs' if language=='javascript' else '.py'
                program = Path(tmp)/(card['id']+extension)
                program.write_text(solution['code']+'\n'+solution['testCode']+'\n'+'\n'.join(EXTRA[card['id']][language])+'\n')
                command = [node,str(program)] if language=='javascript' else [sys.executable,str(program)]
                result = subprocess.run(command,capture_output=True,text=True,timeout=20)
                programs += 1
                if result.returncode:
                    failures.append((card['id'],language,result.stderr or result.stdout))
                    print('FAIL',card['id'],language)
                else:
                    print('PASS',card['id'],language,'(%d oracle cases)' % ORACLE_COUNTS.get(card['id'],0))
    for card_id,language,error in failures:
        print('\n%s %s\n%s' % (card_id,language,error),file=sys.stderr)
    if failures:
        raise SystemExit(1)
    print('\nValidated 30 cards; %d standalone solution/test programs passed; %d seeded oracle cases per language (%d executions total), plus embedded deterministic/async tests.' % (programs,sum(ORACLE_COUNTS.values()),2*sum(ORACLE_COUNTS.values())))

if __name__=='__main__':
    main()
