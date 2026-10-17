"""Build original interview exercises. Run verify-modern.py after changes."""
import html
import json
import re
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = {
    "google": ("Google recruiting: technical interview preparation", "https://www.linkedin.com/posts/google_how-to-prepare-for-technical-interviews-activity-7319057159177097217-lnuR"),
    "role": ("Google Careers: Software Engineer III, Engineering Productivity", "https://www.google.com/about/careers/applications/jobs/results/141928645512831686-software-engineer-iii/"),
    "map": ("MDN: Map insertion order and access guarantees", "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Map"),
    "heap": ("Python documentation: heapq", "https://docs.python.org/3/library/heapq.html"),
    "collections": ("Python documentation: collections", "https://docs.python.org/3/library/collections.html"),
    "asyncio": ("Python documentation: asyncio tasks and cancellation", "https://docs.python.org/3/library/asyncio-task.html"),
    "settled": ("MDN: Promise.allSettled", "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise/allSettled"),
    "integer": ("MDN: Number.MAX_SAFE_INTEGER", "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Number/MAX_SAFE_INTEGER"),
    "copy": ("Python documentation: shallow and deep copy", "https://docs.python.org/3/library/copy.html"),
    "clone": ("MDN: structuredClone", "https://developer.mozilla.org/en-US/docs/Web/API/Window/structuredClone"),
    "idb": ("MDN: IndexedDB API", "https://developer.mozilla.org/en-US/docs/Web/API/IndexedDB_API"),
    "sw": ("MDN: Service Worker API", "https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API"),
    "retry": ("AWS Builders' Library: safe retries with idempotent APIs", "https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/"),
    "pagination": ("Google AIP-158: pagination", "https://google.aip.dev/158"),
    "overload": ("Google SRE: handling overload", "https://sre.google/sre-book/handling-overload/"),
    "slo": ("Google SRE Workbook: implementing SLOs", "https://sre.google/workbook/implementing-slos/"),
    "isolation": ("PostgreSQL: transaction isolation", "https://www.postgresql.org/docs/current/transaction-iso.html"),
    "constraints": ("PostgreSQL: database constraints", "https://www.postgresql.org/docs/current/ddl-constraints.html"),
    "delivery": ("Google Cloud Pub/Sub: exactly-once delivery scope", "https://docs.cloud.google.com/pubsub/docs/exactly-once-delivery"),
}

def p(value):
    return "<p>" + html.escape(value) + "</p>"

def ul(items):
    return "<ul>" + "".join("<li>" + html.escape(x) + "</li>" for x in items) + "</ul>"

def clean(code):
    return textwrap.dedent(code).strip() + "\n"

def refs(keys):
    return [{"title": SOURCES[k][0], "url": SOURCES[k][1]} for k in keys]

CARDS = []
RUBRIC = [
    "Clarify the input, output, boundary behavior, and a small example before coding.",
    "Explain the invariant that makes the algorithm correct, then implement readable code.",
    "Trace normal and edge cases; give time and space costs using named input sizes.",
]

def coding(title, topic, prompt, constraints, examples, approach, hint, followup,
           js, py, jt, pt, complexity, notes="", source_keys=("google",),
           kind="coding", minutes=35, difficulty="Medium"):
    number = len(CARDS) + 1
    sections = [
        {"title": "Hint", "html": p(hint)},
        {"title": "Worked approach", "html": p(approach)},
        {"title": "Edge cases and tests", "html": ul(examples)},
        {"title": "Interviewer follow-up", "html": p(followup)},
        {"title": "Self-review rubric", "html": ul(RUBRIC)},
    ]
    question = p(prompt) + "<h3>Contract</h3>" + ul(constraints) + "<h3>Examples to reason through</h3>" + ul(examples[:2])
    CARDS.append({
        "id": "modern-%03d" % number, "deckId": "modern", "number": number,
        "title": title, "topic": topic, "kind": kind, "difficulty": difficulty,
        "timeMinutes": minutes, "question": question,
        "answer": p(approach) + p("Complexity: " + complexity), "sections": sections,
        "search": " ".join([title, topic, prompt, approach, hint, followup, notes]),
        "sources": refs(source_keys),
        "solutions": {
            "javascript": {"code": clean(js), "testCode": "import assert from 'node:assert/strict';\n" + clean(jt), "notes": notes or "Modern JavaScript; run the tests as an ES module in Node.js.", "complexity": complexity},
            "python": {"code": clean(py), "testCode": clean(pt), "notes": notes or "Python 3.9+; standard library only.", "complexity": complexity},
        },
    })

coding("Deduplicate a retrying event stream", "Hash maps & windows",
    "A telemetry collector receives [timestamp, eventId] pairs in timestamp order. Accept an event only if that ID has not been accepted during the preceding window seconds. Return one boolean per arrival.",
    ["Timestamps are nonnegative integers in nondecreasing order; event IDs are strings.", "window is positive. An acceptance at time a expires at a + window; a retry exactly then is accepted.", "Rejected retries do not refresh the expiry. Process a finite batch of at most 100,000 events."],
    ["[[0,'a'],[2,'a'],[5,'a']], window=5 → [true,false,true].", "[[0,'a'],[0,'b'],[0,'a']], window=1 → [true,true,false].", "Empty input returns []; test exact expiry, repeated timestamps, and unrelated IDs."],
    "Keep each ID's last accepted timestamp in a hash map. A later arrival is accepted when the ID is absent or its last acceptance is at least window seconds old. Update only on acceptance. This batch implementation keeps one entry per distinct ID; a production unbounded stream also needs expiry cleanup.",
    "Distinguish the last arrival from the last accepted arrival. Which one defines the window?",
    "Add bounded memory using an expiry queue. What changes for out-of-order events or concurrent collectors? Explain why a local map cannot enforce a global exactly-once guarantee.",
    '''
    function acceptEvents(events, window) {
      if (!(window > 0)) throw new RangeError('window must be positive');
      const acceptedAt = new Map();
      return events.map(([time, id]) => {
        if (acceptedAt.has(id) && time - acceptedAt.get(id) < window) return false;
        acceptedAt.set(id, time);
        return true;
      });
    }
    ''', '''
    def accept_events(events, window):
        if window <= 0:
            raise ValueError('window must be positive')
        accepted_at = {}
        result = []
        for time, event_id in events:
            accept = event_id not in accepted_at or time - accepted_at[event_id] >= window
            result.append(accept)
            if accept:
                accepted_at[event_id] = time
        return result
    ''', '''
    assert.deepEqual(acceptEvents([[0,'a'],[2,'a'],[5,'a']],5), [true,false,true]);
    assert.deepEqual(acceptEvents([[0,'a'],[0,'b'],[0,'a']],1), [true,true,false]);
    assert.deepEqual(acceptEvents([],1), []);
    assert.throws(() => acceptEvents([],0), RangeError);
    ''', '''
    assert accept_events([(0,'a'),(2,'a'),(5,'a')],5) == [True,False,True]
    assert accept_events([(0,'a'),(0,'b'),(0,'a')],1) == [True,True,False]
    assert accept_events([],1) == []
    try:
        accept_events([],0)
        assert False
    except ValueError:
        pass
    ''', "Expected O(n) time and O(u) auxiliary space for n arrivals and u distinct IDs, assuming expected constant-time hash operations; output uses O(n).")

coding("Smallest incident evidence window", "Sliding windows",
    "An incident timeline is an array of signal names. Find the shortest contiguous interval containing every distinct required signal at least once. Return [start, endExclusive], breaking ties by the earliest start, or null/None if impossible.",
    ["Signal names are strings; required is interpreted as a set.", "Empty required returns [0,0]. There are at most 100,000 timeline entries."],
    ["['ok','timeout','retry','ok','timeout'], required=['timeout','retry'] → [1,3].", "['ok'], required=['timeout'] → null/None; empty required → [0,0].", "Test repeated required entries, a one-element answer, and tied shortest windows."],
    "Expand the right edge, counting required signals and how many distinct requirements are present. While all are present, record the window if strictly shorter, then shrink the left edge. Each edge moves only forward, so every timeline entry enters and leaves at most once.",
    "Track the count of each required type; removing a duplicate need not invalidate a window.",
    "How would the contract and counts change if a requirement demanded three timeout events? How would you handle an infinite stream?",
    '''
    function evidenceWindow(signals, required) {
      const need = new Set(required);
      if (need.size === 0) return [0, 0];
      const counts = new Map();
      let left = 0, have = 0, best = null;
      for (let right = 0; right < signals.length; right++) {
        const item = signals[right];
        if (need.has(item)) {
          const count = (counts.get(item) ?? 0) + 1;
          counts.set(item, count);
          if (count === 1) have++;
        }
        while (have === need.size) {
          if (best === null || right + 1 - left < best[1] - best[0]) best = [left, right + 1];
          const removed = signals[left++];
          if (need.has(removed)) {
            counts.set(removed, counts.get(removed) - 1);
            if (counts.get(removed) === 0) have--;
          }
        }
      }
      return best;
    }
    ''', '''
    def evidence_window(signals, required):
        need = set(required)
        if not need:
            return [0, 0]
        counts = {}
        left = have = 0
        best = None
        for right, item in enumerate(signals):
            if item in need:
                counts[item] = counts.get(item, 0) + 1
                have += counts[item] == 1
            while have == len(need):
                if best is None or right + 1 - left < best[1] - best[0]:
                    best = [left, right + 1]
                removed = signals[left]
                left += 1
                if removed in need:
                    counts[removed] -= 1
                    have -= counts[removed] == 0
        return best
    ''', '''
    assert.deepEqual(evidenceWindow(['ok','timeout','retry','ok','timeout'],['timeout','retry']),[1,3]);
    assert.deepEqual(evidenceWindow(['a','b','a'],['a','a']),[0,1]);
    assert.equal(evidenceWindow(['ok'],['timeout']),null);
    assert.deepEqual(evidenceWindow([],[]),[0,0]);
    ''', '''
    assert evidence_window(['ok','timeout','retry','ok','timeout'],['timeout','retry']) == [1,3]
    assert evidence_window(['a','b','a'],['a','a']) == [0,1]
    assert evidence_window(['ok'],['timeout']) is None
    assert evidence_window([],[]) == [0,0]
    ''', "Expected O(n + r) time, O(r) auxiliary space, for n signals and r required entries.")

coding("Top error categories with deterministic ties", "Counting & sorting",
    "Return the k most frequent error codes in a batch. Order by descending frequency, then ascending ASCII code string so two replicas produce the same report.",
    ["Error codes are ASCII strings. k is an integer ≥ 0.", "Return all distinct codes when k exceeds their count. Input order must remain unchanged."],
    ["['503','429','503','404','429'], k=2 → ['429','503'].", "Empty input or k=0 → []; ['x','x','a'], k=9 → ['x','a'].", "Test ties, all unique codes, and codes such as '__proto__'."],
    "Count into a map, then sort distinct codes with the complete ranking rule. The straightforward solution is easy to verify and appropriate when the number of categories is small. A size-k heap is a useful optimization when the distinct count is much larger than k.",
    "A sort comparator must specify the tie-break, not rely on input order or locale-sensitive collation.",
    "Implement the size-k heap variant. How would approximate counts change the answer when a stream contains millions of distinct categories?",
    '''
    function topErrors(errors, k) {
      const counts = new Map();
      for (const e of errors) counts.set(e, (counts.get(e) ?? 0) + 1);
      return [...counts.keys()].sort((a, b) =>
        counts.get(b) - counts.get(a) || (a < b ? -1 : a > b ? 1 : 0)
      ).slice(0, k);
    }
    ''', '''
    from collections import Counter

    def top_errors(errors, k):
        counts = Counter(errors)
        return sorted(counts, key=lambda code: (-counts[code], code))[:k]
    ''', '''
    assert.deepEqual(topErrors(['503','429','503','404','429'],2),['429','503']);
    assert.deepEqual(topErrors(['x','x','a'],9),['x','a']);
    assert.deepEqual(topErrors(['__proto__','a'],1),['__proto__']);
    assert.deepEqual(topErrors(['x'],0),[]);
    assert.deepEqual(topErrors([],3),[]);
    ''', '''
    assert top_errors(['503','429','503','404','429'],2) == ['429','503']
    assert top_errors(['x','x','a'],9) == ['x','a']
    assert top_errors(['__proto__','a'],1) == ['__proto__']
    assert top_errors(['x'],0) == []
    assert top_errors([],3) == []
    ''', "Expected O(n + u log u) time and O(u) auxiliary space for n codes and u distinct values; treats code length as bounded.")

coding("Reassemble uploaded byte ranges", "Intervals",
    "A resumable upload has received half-open byte ranges [start,end). Merge overlapping or touching ranges and return their sorted union. Also explain how the union reveals gaps in an upload of known total size.",
    ["Bounds are integers with 0 ≤ start ≤ end. Zero-length ranges add no bytes.", "Ranges may be unsorted or duplicated. Do not mutate the input."],
    ["[[4,8],[0,3],[3,5],[10,12]] → [[0,8],[10,12]].", "[[2,2],[1,4],[2,3],[1,4]] → [[1,4]].", "Empty input returns []; test nested, disjoint, and touching ranges."],
    "Sort nonempty copies by start. The union's final range is the only range that can overlap the next input range. Extend its end when the next start is at most that end; otherwise append a new range. Gaps lie before the first range, between merged ranges, and after the last range up to total size.",
    "After sorting, can a new interval overlap any output range other than the final one?",
    "Support online insertions and queries for the first missing byte. Explain when a balanced interval tree becomes useful.",
    '''
    function mergeRanges(ranges) {
      const ordered = ranges.filter(([a,b]) => a < b).map(x => [...x]).sort((a,b) => a[0]-b[0]);
      const result = [];
      for (const [start,end] of ordered) {
        const last = result[result.length-1];
        if (last && start <= last[1]) last[1] = Math.max(last[1],end);
        else result.push([start,end]);
      }
      return result;
    }
    ''', '''
    def merge_ranges(ranges):
        result = []
        for start, end in sorted((a,b) for a,b in ranges if a < b):
            if result and start <= result[-1][1]:
                result[-1][1] = max(result[-1][1], end)
            else:
                result.append([start,end])
        return result
    ''', '''
    assert.deepEqual(mergeRanges([[4,8],[0,3],[3,5],[10,12]]),[[0,8],[10,12]]);
    const input = [[2,2],[1,4],[2,3],[1,4]];
    const before = JSON.stringify(input);
    assert.deepEqual(mergeRanges(input),[[1,4]]);
    assert.equal(JSON.stringify(input),before);
    assert.deepEqual(mergeRanges([]),[]);
    ''', '''
    assert merge_ranges([[4,8],[0,3],[3,5],[10,12]]) == [[0,8],[10,12]]
    data = [[2,2],[1,4],[2,3],[1,4]]
    before = [row[:] for row in data]
    assert merge_ranges(data) == [[1,4]]
    assert data == before
    assert merge_ranges([]) == []
    ''', "O(n log n) time and O(n) auxiliary space including copied ranges and output.")

coding("Find the shortest service dependency chain", "Graphs & BFS",
    "A directed graph maps a service to the services it directly calls. Return a shortest path from source to target measured in call hops, or an empty list if unreachable.",
    ["Service names are strings. Missing adjacency entries mean no outgoing edges.", "Cycles and duplicate edges are allowed. Any shortest path is acceptable; traverse neighbors in input order for deterministic output."],
    ["a→[b,c], b→[d], c→[d], source=a,target=d → [a,b,d].", "source=target → [source], even with no adjacency entry; unreachable → [].", "Test cycles, a diamond, duplicated edges, and a path with many hops."],
    "Breadth-first search visits vertices in nondecreasing hop distance. Mark vertices when enqueued and store one parent per vertex. Once the target is dequeued, follow parents backward and reverse the path. Storing complete paths in the queue would waste space.",
    "Choose the frontier order that guarantees the first discovery has the fewest edges.",
    "What changes when call edges have different latencies? What if a dependency snapshot changes during the search?",
    '''
    function shortestChain(graph, source, target) {
      const queue = [source], parent = new Map([[source,null]]);
      for (let head=0; head<queue.length; head++) {
        const node = queue[head];
        if (node === target) {
          const path = [];
          for (let cur=target; cur!==null; cur=parent.get(cur)) path.push(cur);
          return path.reverse();
        }
        for (const next of Object.hasOwn(graph,node) ? graph[node] : []) {
          if (!parent.has(next)) { parent.set(next,node); queue.push(next); }
        }
      }
      return [];
    }
    ''', '''
    from collections import deque

    def shortest_chain(graph, source, target):
        queue = deque([source])
        parent = {source: None}
        while queue:
            node = queue.popleft()
            if node == target:
                path = []
                cur = target
                while cur is not None:
                    path.append(cur)
                    cur = parent[cur]
                return path[::-1]
            for nxt in graph.get(node, []):
                if nxt not in parent:
                    parent[nxt] = node
                    queue.append(nxt)
        return []
    ''', '''
    assert.deepEqual(shortestChain({a:['b','c'],b:['a','d'],c:['d']},'a','d'),['a','b','d']);
    assert.deepEqual(shortestChain({},'a','a'),['a']);
    assert.deepEqual(shortestChain({a:['a']},'a','z'),[]);
    assert.deepEqual(shortestChain({a:['b','b']},'a','b'),['a','b']);
    ''', '''
    assert shortest_chain({'a':['b','c'],'b':['a','d'],'c':['d']},'a','d') == ['a','b','d']
    assert shortest_chain({},'a','a') == ['a']
    assert shortest_chain({'a':['a']},'a','z') == []
    assert shortest_chain({'a':['b','b']},'a','b') == ['a','b']
    ''', "Expected O(V + E) time and O(V) auxiliary space for reachable vertices and examined edges.",
    notes="JavaScript uses a queue head index instead of repeated Array.shift and reads only own adjacency properties, so inherited names do not become graph edges.")

coding("Order a deployment dependency graph", "Graphs & topological sort",
    "Given n deployment jobs numbered 0 through n−1 and edges [prerequisite,dependent], return a valid execution order. Return null/None if there is a cycle.",
    ["All endpoints are valid job indices. Duplicate dependency edges are allowed and should be harmless.", "Any valid ordering is acceptable. Empty jobs return []."],
    ["n=4, edges=[[0,2],[1,2],[2,3]] → [0,1,2,3].", "n=2, edges=[[0,1],[1,0]] → null/None.", "Test isolated jobs, duplicate edges, an empty graph, and a self-dependency."],
    "Count incoming edges, enqueue every zero-indegree job, then remove its outgoing edges as it is processed. A newly zero-indegree job is ready. If fewer than n jobs are emitted, some jobs remain in a cycle or depend on one. Counting and later decrementing duplicate edges consistently preserves correctness.",
    "A job is ready exactly when its remaining prerequisite count reaches zero.",
    "Return parallel execution layers, identify an actual cycle, or enforce a deterministic smallest-ID-ready order. Compare FIFO and heap frontiers.",
    '''
    function deploymentOrder(n, edges) {
      const out = Array.from({length:n},()=>[]), degree = Array(n).fill(0);
      for (const [a,b] of edges) { out[a].push(b); degree[b]++; }
      const queue = [];
      for (let i=0;i<n;i++) if (degree[i]===0) queue.push(i);
      for (let head=0;head<queue.length;head++) {
        for (const next of out[queue[head]]) if (--degree[next]===0) queue.push(next);
      }
      return queue.length===n ? queue : null;
    }
    ''', '''
    from collections import deque

    def deployment_order(n, edges):
        out = [[] for _ in range(n)]
        degree = [0] * n
        for a, b in edges:
            out[a].append(b)
            degree[b] += 1
        queue = deque(i for i in range(n) if degree[i] == 0)
        result = []
        while queue:
            node = queue.popleft()
            result.append(node)
            for nxt in out[node]:
                degree[nxt] -= 1
                if degree[nxt] == 0:
                    queue.append(nxt)
        return result if len(result) == n else None
    ''', '''
    assert.deepEqual(deploymentOrder(4,[[0,2],[1,2],[2,3]]),[0,1,2,3]);
    assert.equal(deploymentOrder(2,[[0,1],[1,0]]),null);
    assert.equal(deploymentOrder(1,[[0,0]]),null);
    assert.deepEqual(deploymentOrder(2,[[0,1],[0,1]]),[0,1]);
    assert.deepEqual(deploymentOrder(0,[]),[]);
    ''', '''
    assert deployment_order(4,[[0,2],[1,2],[2,3]]) == [0,1,2,3]
    assert deployment_order(2,[[0,1],[1,0]]) is None
    assert deployment_order(1,[[0,0]]) is None
    assert deployment_order(2,[[0,1],[0,1]]) == [0,1]
    assert deployment_order(0,[]) == []
    ''', "O(V + E) time and O(V + E) space including the adjacency list.")

HEAP_JS = '''
class MinHeap {
  constructor(compare) { this.items=[]; this.compare=compare; }
  get size() { return this.items.length; }
  push(value) {
    const a=this.items; a.push(value); let i=a.length-1;
    while (i>0) {
      const p=Math.floor((i-1)/2);
      if (this.compare(a[p],a[i])<=0) break;
      [a[p],a[i]]=[a[i],a[p]]; i=p;
    }
  }
  pop() {
    const a=this.items, first=a[0], last=a.pop();
    if (a.length) {
      a[0]=last; let i=0;
      while (true) {
        let child=2*i+1;
        if (child>=a.length) break;
        if (child+1<a.length && this.compare(a[child+1],a[child])<0) child++;
        if (this.compare(a[i],a[child])<=0) break;
        [a[i],a[child]]=[a[child],a[i]]; i=child;
      }
    }
    return first;
  }
}
'''

coding("Find the least-latency service route", "Graphs & shortest paths",
    "Given a directed graph of n nodes and edges [from,to,latency], return the minimum total latency from source to target, or null/None if no route exists.",
    ["Latencies are nonnegative integers. All path sums fit in JavaScript's safe integer range.", "Nodes are 0…n−1; source and target are valid. Parallel edges and zero-cost edges are permitted."],
    ["n=3, edges=[[0,1,8],[0,2,2],[2,1,1]], source=0,target=1 → 3.", "source=target → 0; disconnected target → null/None.", "Test zero-cost cycles, parallel edges, and a node first found through a more expensive route."],
    "Use Dijkstra's algorithm with a min-heap of tentative distances. An improved distance pushes a new entry; skip stale entries when popped. The smallest non-stale distance is final because remaining edges cannot reduce it. Return only when the target is popped, not when first discovered.",
    "A FIFO queue optimizes hop count. You need a frontier ordered by total cost.",
    "Why do negative weights break this proof? Add route reconstruction. Explain why summing individual p99 latencies does not generally predict end-to-end p99.",
    HEAP_JS + '''
    function leastLatency(n, edges, source, target) {
      const out=Array.from({length:n},()=>[]), dist=Array(n).fill(Infinity);
      for (const [a,b,w] of edges) out[a].push([b,w]);
      const heap=new MinHeap((a,b)=>a[0]-b[0]);
      dist[source]=0; heap.push([0,source]);
      while (heap.size) {
        const [cost,node]=heap.pop();
        if (cost!==dist[node]) continue;
        if (node===target) return cost;
        for (const [next,weight] of out[node]) {
          const candidate=cost+weight;
          if (candidate<dist[next]) { dist[next]=candidate; heap.push([candidate,next]); }
        }
      }
      return null;
    }
    ''', '''
    import heapq

    def least_latency(n, edges, source, target):
        out = [[] for _ in range(n)]
        for a,b,w in edges:
            out[a].append((b,w))
        dist = [float('inf')] * n
        dist[source] = 0
        heap = [(0,source)]
        while heap:
            cost,node = heapq.heappop(heap)
            if cost != dist[node]:
                continue
            if node == target:
                return cost
            for nxt,weight in out[node]:
                candidate = cost + weight
                if candidate < dist[nxt]:
                    dist[nxt] = candidate
                    heapq.heappush(heap,(candidate,nxt))
        return None
    ''', '''
    assert.equal(leastLatency(3,[[0,1,8],[0,2,2],[2,1,1]],0,1),3);
    assert.equal(leastLatency(2,[],0,1),null);
    assert.equal(leastLatency(1,[],0,0),0);
    assert.equal(leastLatency(3,[[0,1,0],[1,0,0],[1,2,4],[0,2,9]],0,2),4);
    ''', '''
    assert least_latency(3,[[0,1,8],[0,2,2],[2,1,1]],0,1) == 3
    assert least_latency(2,[],0,1) is None
    assert least_latency(1,[],0,0) == 0
    assert least_latency(3,[[0,1,0],[1,0,0],[1,2,4],[0,2,9]],0,2) == 4
    ''', "O(V + E log(E+1)) time and O(V + E) space for this lazy-duplicate heap implementation.", source_keys=("heap",), minutes=40)

coding("An LRU cache for feature metadata", "Caches & data structures",
    "Implement an LRU cache supporting get(key) and put(key,value). A successful get or put makes that key most recently used. Evict the least recently used key when capacity is exceeded.",
    ["Capacity is a nonnegative integer. Keys are strings and stored values are non-null strings or numbers.", "A miss returns null/None. Updating an existing key must not evict another key. Capacity zero stores nothing."],
    ["capacity=2: put(a,1), put(b,2), get(a), put(c,3), get(b) → 1 then null/None.", "capacity=0: put(a,1), get(a) → null/None.", "Test updates, repeated gets, an empty cache, and capacity one."],
    "Maintain keys from least to most recently used. On a hit or update, move the key to the end; after insertion, remove the first key if over capacity. JavaScript Map preserves insertion order, so delete and reinsert explicitly. Python OrderedDict provides move_to_end and popitem(last=False). For a strict data-structure exercise, implement a hash table plus a doubly linked list.",
    "You need fast lookup and fast movement within an eviction order.",
    "Implement the linked-list version. Add TTL or byte-weighted capacity and discuss concurrency, stale values, and whether misses should be cached.",
    '''
    class LRUCache {
      constructor(capacity) {
        if (!Number.isInteger(capacity) || capacity<0) throw new RangeError('invalid capacity');
        this.capacity=capacity; this.data=new Map();
      }
      get(key) {
        if (!this.data.has(key)) return null;
        const value=this.data.get(key);
        this.data.delete(key); this.data.set(key,value);
        return value;
      }
      put(key,value) {
        this.data.delete(key); this.data.set(key,value);
        if (this.data.size>this.capacity) this.data.delete(this.data.keys().next().value);
      }
    }
    ''', '''
    from collections import OrderedDict

    class LRUCache:
        def __init__(self, capacity):
            if not isinstance(capacity,int) or capacity < 0:
                raise ValueError('invalid capacity')
            self.capacity = capacity
            self.data = OrderedDict()

        def get(self,key):
            if key not in self.data:
                return None
            self.data.move_to_end(key)
            return self.data[key]

        def put(self,key,value):
            self.data[key] = value
            self.data.move_to_end(key)
            if len(self.data) > self.capacity:
                self.data.popitem(last=False)
    ''', '''
    const cache=new LRUCache(2);
    cache.put('a',1); cache.put('b',2);
    assert.equal(cache.get('a'),1);
    cache.put('c',3); assert.equal(cache.get('b'),null);
    cache.put('a',9); assert.equal(cache.get('a'),9); assert.equal(cache.get('c'),3);
    const zero=new LRUCache(0); zero.put('a',1); assert.equal(zero.get('a'),null);
    ''', '''
    cache=LRUCache(2)
    cache.put('a',1); cache.put('b',2)
    assert cache.get('a') == 1
    cache.put('c',3)
    assert cache.get('b') is None
    cache.put('a',9)
    assert cache.get('a') == 9 and cache.get('c') == 3
    zero=LRUCache(0); zero.put('a',1)
    assert zero.get('a') is None
    ''', "O(capacity) space. Operations are expected O(1) on typical hash-backed implementations; ECMAScript requires average sublinear Map access, not a strict O(1) guarantee.", source_keys=("map","collections"))

coding("Rolling peak request latency", "Monotonic queues",
    "Given request latencies and a window width k, return the maximum latency in every contiguous window of k requests.",
    ["1 ≤ k ≤ len(values); empty input with k=0 returns []. Invalid widths raise an error.", "Values are finite numbers. Do not mutate the input."],
    ["[8,3,5,9,2], k=3 → [8,9,9].", "[4,4,4], k=2 → [4,4]; [1,2], k=1 → [1,2].", "Test increasing values, decreasing values, duplicates, and a full-array window."],
    "Store candidate indices in a deque with decreasing values. Expire indices outside the window; remove smaller or equal values from the back because the new value is at least as useful and expires later. The front is each window's maximum. Each index is added and removed once.",
    "An older smaller value can never win a future window that also contains a newer larger value.",
    "Support time-based windows. What changes if events arrive out of order or you need a rolling percentile instead of a maximum?",
    '''
    function rollingPeak(values,k) {
      if (values.length===0 && k===0) return [];
      if (!Number.isInteger(k) || k<1 || k>values.length) throw new RangeError('invalid width');
      const deque=[], result=[]; let head=0;
      for (let i=0;i<values.length;i++) {
        while (head<deque.length && deque[head]<=i-k) head++;
        while (head<deque.length && values[deque[deque.length-1]]<=values[i]) deque.pop();
        deque.push(i);
        if (i>=k-1) result.push(values[deque[head]]);
        // Compact consumed prefix so retained storage stays O(k).
        if (head>k) { deque.splice(0,head); head=0; }
      }
      return result;
    }
    ''', '''
    from collections import deque

    def rolling_peak(values,k):
        if not values and k == 0:
            return []
        if not isinstance(k,int) or not 1 <= k <= len(values):
            raise ValueError('invalid width')
        candidates = deque()
        result = []
        for i,value in enumerate(values):
            while candidates and candidates[0] <= i-k:
                candidates.popleft()
            while candidates and values[candidates[-1]] <= value:
                candidates.pop()
            candidates.append(i)
            if i >= k-1:
                result.append(values[candidates[0]])
        return result
    ''', '''
    assert.deepEqual(rollingPeak([8,3,5,9,2],3),[8,9,9]);
    assert.deepEqual(rollingPeak([4,4,4],2),[4,4]);
    assert.deepEqual(rollingPeak([1,2],1),[1,2]);
    assert.deepEqual(rollingPeak([],0),[]);
    assert.throws(()=>rollingPeak([1],0),RangeError);
    ''', '''
    assert rolling_peak([8,3,5,9,2],3) == [8,9,9]
    assert rolling_peak([4,4,4],2) == [4,4]
    assert rolling_peak([1,2],1) == [1,2]
    assert rolling_peak([],0) == []
    try:
        rolling_peak([1],0)
        assert False
    except ValueError:
        pass
    ''', "Amortized O(n) time, O(k) auxiliary queue space, plus O(n−k+1) output.")

coding("Fit a conversation into a token budget", "Sliding windows",
    "A conversation has per-message token costs. Find the longest contiguous block whose total cost is at most budget. Return [start,endExclusive], preferring the earliest block on ties.",
    ["Costs and budget are nonnegative integers; sums fit in JavaScript's safe integer range.", "You may return [0,0] if no nonempty block fits. This is a toy token-budget problem, not a tokenizer implementation."],
    ["[4,2,1,5,1], budget=7 → [0,3].", "[0,0,2], budget=0 → [0,2]; [8], budget=3 → [0,0].", "Test zero-cost messages, empty input, and several equal-length answers."],
    "Expand the right edge and keep the window's running sum. If over budget, advance the left edge until feasible. Nonnegative costs make this safe: removing a prefix cannot increase the sum, and an infeasible prefix cannot become feasible by extending it. Record strictly longer windows to preserve the earliest tie.",
    "The nonnegative-cost assumption gives you monotonicity; explain exactly where you use it.",
    "What if the most recent message must be included? What if messages have utility scores and can be selected noncontiguously? What breaks if costs can be negative?",
    '''
    function budgetWindow(costs,budget) {
      let left=0, sum=0, best=[0,0];
      for (let right=0;right<costs.length;right++) {
        sum+=costs[right];
        while (sum>budget) sum-=costs[left++];
        if (right+1-left>best[1]-best[0]) best=[left,right+1];
      }
      return best;
    }
    ''', '''
    def budget_window(costs,budget):
        left = total = 0
        best = [0,0]
        for right,cost in enumerate(costs):
            total += cost
            while total > budget:
                total -= costs[left]
                left += 1
            if right+1-left > best[1]-best[0]:
                best = [left,right+1]
        return best
    ''', '''
    assert.deepEqual(budgetWindow([4,2,1,5,1],7),[0,3]);
    assert.deepEqual(budgetWindow([0,0,2],0),[0,2]);
    assert.deepEqual(budgetWindow([8],3),[0,0]);
    assert.deepEqual(budgetWindow([],4),[0,0]);
    ''', '''
    assert budget_window([4,2,1,5,1],7) == [0,3]
    assert budget_window([0,0,2],0) == [0,2]
    assert budget_window([8],3) == [0,0]
    assert budget_window([],4) == [0,0]
    ''', "O(n) time and O(1) auxiliary space.")

coding("Merge regional audit streams", "Heaps & merging",
    "Each region provides an ascending array of integer event timestamps. Merge all arrays into one ascending timeline, preserving duplicates.",
    ["Each input array is already sorted. There can be empty regions or no regions.", "Return timestamps only; a production event record would also need a stable tie-break key. Do not mutate inputs."],
    ["[[1,4,9],[1,3],[],[2,8]] → [1,1,2,3,4,8,9].", "[] → []; [[5,5]] → [5,5].", "Test all-empty streams, identical timestamps, and very uneven stream lengths."],
    "Put the first item from each nonempty stream in a min-heap together with its stream and item index. Pop the smallest, append it, then push only its successor. At every step the heap contains the smallest unconsumed item from each stream, so the global minimum must be in the heap.",
    "You only need one frontier item per sorted stream.",
    "Turn the function into a lazy iterator. If network streams can pause or clocks disagree, what does a globally ordered live merge need to know before emitting?",
    HEAP_JS + '''
    function mergeStreams(streams) {
      const heap=new MinHeap((a,b)=>a[0]-b[0] || a[1]-b[1]);
      streams.forEach((stream,s)=>{ if (stream.length) heap.push([stream[0],s,0]); });
      const result=[];
      while (heap.size) {
        const [value,s,i]=heap.pop(); result.push(value);
        if (i+1<streams[s].length) heap.push([streams[s][i+1],s,i+1]);
      }
      return result;
    }
    ''', '''
    import heapq

    def merge_streams(streams):
        heap = [(stream[0],s,0) for s,stream in enumerate(streams) if stream]
        heapq.heapify(heap)
        result = []
        while heap:
            value,s,i = heapq.heappop(heap)
            result.append(value)
            if i+1 < len(streams[s]):
                heapq.heappush(heap,(streams[s][i+1],s,i+1))
        return result
    ''', '''
    const input=[[1,4,9],[1,3],[],[2,8]], before=JSON.stringify(input);
    assert.deepEqual(mergeStreams(input),[1,1,2,3,4,8,9]);
    assert.equal(JSON.stringify(input),before);
    assert.deepEqual(mergeStreams([]),[]);
    assert.deepEqual(mergeStreams([[],[]]),[]);
    assert.deepEqual(mergeStreams([[5,5]]),[5,5]);
    ''', '''
    streams=[[1,4,9],[1,3],[],[2,8]]
    before=[x[:] for x in streams]
    assert merge_streams(streams) == [1,1,2,3,4,8,9]
    assert streams == before
    assert merge_streams([]) == []
    assert merge_streams([[],[]]) == []
    assert merge_streams([[5,5]]) == [5,5]
    ''', "O(K + N log(K+1)) time, O(K) auxiliary heap space plus O(N) output, for K streams and N items.",
    source_keys=("heap",), minutes=40)

coding("Longest matching configuration prefix", "Tries & strings",
    "A configuration registry assigns a value to each string prefix. Build a trie and return the value for the longest stored prefix of a query, or null/None when no prefix matches.",
    ["Prefixes and queries are ASCII strings; values are non-null strings. This is raw string-prefix matching, not URL routing or path normalization.", "An empty prefix is a default. Later inserts replace values at the exact same prefix."],
    ["Prefixes [('', 'default'), ('api/', 'shared'), ('api/pay/', 'payments')], query='api/pay/create' → 'payments'.", "query='api/payment' → 'shared'; without a default, an unmatched query → null/None.", "Test an exact match, empty query, a replacement, and a prefix that is only an intermediate trie node."],
    "Each trie edge consumes one character. Store values only at completed prefixes. Traverse the query while remembering the last value encountered; stopping at a missing edge preserves the deepest matching prefix. Separate the missing-value sentinel from legitimate values.",
    "A query can pass through nodes that are prefixes structurally but were never inserted as complete keys.",
    "Add deletion without losing longer prefixes. What changes for Unicode normalization or segment-boundary routing? Compare a compressed radix tree.",
    '''
    class PrefixRegistry {
      constructor(entries=[]) {
        this.root={children:new Map(),value:null};
        for (const [prefix,value] of entries) this.put(prefix,value);
      }
      put(prefix,value) {
        let node=this.root;
        for (const ch of prefix) {
          if (!node.children.has(ch)) node.children.set(ch,{children:new Map(),value:null});
          node=node.children.get(ch);
        }
        node.value=value;
      }
      match(query) {
        let node=this.root, best=node.value;
        for (const ch of query) {
          if (!node.children.has(ch)) break;
          node=node.children.get(ch);
          if (node.value!==null) best=node.value;
        }
        return best;
      }
    }
    ''', '''
    class PrefixRegistry:
        def __init__(self, entries=()):
            self.root = {'children': {}, 'value': None}
            for prefix,value in entries:
                self.put(prefix,value)

        def put(self,prefix,value):
            node = self.root
            for ch in prefix:
                if ch not in node['children']:
                    node['children'][ch] = {'children': {}, 'value': None}
                node = node['children'][ch]
            node['value'] = value

        def match(self,query):
            node = self.root
            best = node['value']
            for ch in query:
                if ch not in node['children']:
                    break
                node = node['children'][ch]
                if node['value'] is not None:
                    best = node['value']
            return best
    ''', '''
    const r=new PrefixRegistry([['','default'],['api/','shared'],['api/pay/','payments']]);
    assert.equal(r.match('api/pay/create'),'payments');
    assert.equal(r.match('api/payment'),'shared');
    assert.equal(r.match(''),'default');
    r.put('api/','updated'); assert.equal(r.match('api/x'),'updated');
    assert.equal(new PrefixRegistry([['abc','v']]).match('ab'),null);
    ''', '''
    r=PrefixRegistry([('','default'),('api/','shared'),('api/pay/','payments')])
    assert r.match('api/pay/create') == 'payments'
    assert r.match('api/payment') == 'shared'
    assert r.match('') == 'default'
    r.put('api/','updated')
    assert r.match('api/x') == 'updated'
    assert PrefixRegistry([('abc','v')]).match('ab') is None
    ''', "Expected O(P) build time/space for P total inserted characters; O(L) query time and O(1) query auxiliary space for query length L.")

coding("Group connected devices", "Union-find",
    "An internal inventory lists n device indices and trusted pairwise links that indicate devices belong to the same diagnostic group. Return every connected component, with members and components in ascending index order.",
    ["Devices are 0…n−1, and links are undirected. Isolated devices form one-member groups.", "Links are already authorized inventory data; this task does not infer personal identity. Duplicate links and self-links are allowed."],
    ["n=6, links=[[0,2],[2,4],[1,3]] → [[0,2,4],[1,3],[5]].", "n=0 → []; n=2, links=[[0,0],[0,1],[0,1]] → [[0,1]].", "Test a chain, disconnected groups, a cycle, and no links."],
    "Use disjoint-set union with path compression and union by size. Union each pair, then visit device indices in increasing order and append each device to its root's group. The first encounter with a component is its smallest index, so insertion-ordered group maps already provide the required component order.",
    "Connectivity merges sets; you do not need to keep every path after processing each edge.",
    "Why is deleting a link harder? Compare recomputing connected components with offline dynamic connectivity or a rollback union-find.",
    '''
    function deviceGroups(n,links) {
      const parent=Array.from({length:n},(_,i)=>i), size=Array(n).fill(1);
      function find(x) {
        while (x!==parent[x]) { parent[x]=parent[parent[x]]; x=parent[x]; }
        return x;
      }
      for (const [a,b] of links) {
        let x=find(a), y=find(b);
        if (x===y) continue;
        if (size[x]<size[y]) [x,y]=[y,x];
        parent[y]=x; size[x]+=size[y];
      }
      const groups=new Map();
      for (let i=0;i<n;i++) {
        const root=find(i);
        if (!groups.has(root)) groups.set(root,[]);
        groups.get(root).push(i);
      }
      return [...groups.values()];
    }
    ''', '''
    def device_groups(n,links):
        parent = list(range(n))
        size = [1] * n
        def find(x):
            while x != parent[x]:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x
        for a,b in links:
            x,y = find(a),find(b)
            if x == y:
                continue
            if size[x] < size[y]:
                x,y = y,x
            parent[y] = x
            size[x] += size[y]
        groups = {}
        for i in range(n):
            groups.setdefault(find(i),[]).append(i)
        return list(groups.values())
    ''', '''
    assert.deepEqual(deviceGroups(6,[[0,2],[2,4],[1,3]]),[[0,2,4],[1,3],[5]]);
    assert.deepEqual(deviceGroups(2,[[0,0],[0,1],[0,1]]),[[0,1]]);
    assert.deepEqual(deviceGroups(3,[]),[[0],[1],[2]]);
    assert.deepEqual(deviceGroups(0,[]),[]);
    ''', '''
    assert device_groups(6,[[0,2],[2,4],[1,3]]) == [[0,2,4],[1,3],[5]]
    assert device_groups(2,[[0,0],[0,1],[0,1]]) == [[0,1]]
    assert device_groups(3,[]) == [[0],[1],[2]]
    assert device_groups(0,[]) == []
    ''', "O((n+m) α(n)) amortized time and O(n) space for m links, where α is the inverse Ackermann function.")

coding("Choose a worker's minimum batch capacity", "Binary search",
    "Jobs arrive in a fixed order with positive integer costs. A worker processes a contiguous prefix of remaining jobs per batch, with total cost at most capacity. Find the minimum integer capacity that completes all jobs in at most batches batches.",
    ["batches is a positive integer. A job cannot be split or reordered.", "All sums fit in JavaScript's safe integer range. Empty jobs return zero."],
    ["costs=[7,2,5,10,8], batches=2 → 18, using [7,2,5] and [10,8].", "costs=[3,4], batches=9 → 4; batches=1 → 7.", "Test empty jobs, one huge job, and a minimum capacity exactly equal to a job cost."],
    "For a proposed capacity, greedily fill each batch before starting another. This uses the fewest possible batches for that capacity. Feasibility is monotone: more capacity never requires more batches. Binary-search between the largest job and the total cost using the predicate neededBatches ≤ batches.",
    "Instead of choosing the partition directly, ask whether a proposed capacity is sufficient.",
    "Return the partition too. What changes if jobs can be reordered or workers have unequal capacities? Explain why arbitrary partitioning is a different problem.",
    '''
    function minCapacity(costs,batches) {
      if (!Number.isInteger(batches) || batches<1) throw new RangeError('invalid batch count');
      if (!costs.length) return 0;
      let low=0, high=0;
      for (const cost of costs) { low=Math.max(low,cost); high+=cost; }
      function needed(cap) {
        let count=1, used=0;
        for (const cost of costs) {
          if (used+cost>cap) { count++; used=0; }
          used+=cost;
        }
        return count;
      }
      while (low<high) {
        const mid=low+Math.floor((high-low)/2);
        if (needed(mid)<=batches) high=mid;
        else low=mid+1;
      }
      return low;
    }
    ''', '''
    def min_capacity(costs,batches):
        if not isinstance(batches,int) or batches < 1:
            raise ValueError('invalid batch count')
        if not costs:
            return 0
        low,high = max(costs),sum(costs)
        def needed(cap):
            count,used = 1,0
            for cost in costs:
                if used+cost > cap:
                    count += 1
                    used = 0
                used += cost
            return count
        while low < high:
            mid = low+(high-low)//2
            if needed(mid) <= batches:
                high = mid
            else:
                low = mid+1
        return low
    ''', '''
    assert.equal(minCapacity([7,2,5,10,8],2),18);
    assert.equal(minCapacity([3,4],9),4);
    assert.equal(minCapacity([3,4],1),7);
    assert.equal(minCapacity([],2),0);
    assert.throws(()=>minCapacity([1],0),RangeError);
    ''', '''
    assert min_capacity([7,2,5,10,8],2) == 18
    assert min_capacity([3,4],9) == 4
    assert min_capacity([3,4],1) == 7
    assert min_capacity([],2) == 0
    try:
        min_capacity([1],0)
        assert False
    except ValueError:
        pass
    ''', "O(n log(S+1)) time and O(1) auxiliary space, where S is total cost.")

coding("Count target-sized usage bursts", "Prefix sums",
    "A usage ledger contains signed deltas: consumption is positive and refunds are negative. Count contiguous nonempty intervals whose net usage equals target.",
    ["Deltas and target are integers with absolute value ≤ 1,000,000. Input length ≤ 100,000, so sums, differences, and counts fit in JavaScript's safe integer range.", "Intervals are distinguished by index, even if their values match."],
    ["[2,-1,2,1], target=3 → 2: [2,-1,2] and [2,1].", "[0,0,0], target=0 → 6; [] → 0.", "Test negative targets, repeated prefix sums, and an interval that starts at index zero."],
    "If a prefix sum at position j is s, an earlier prefix with sum s−target defines one valid interval ending at j. Count earlier prefix sums in a map, starting with sum zero appearing once. Query before inserting the current sum so empty intervals are excluded. A sliding window fails with negative deltas.",
    "Subtract two prefix sums to express an interval sum. You need counts of earlier sums, not just their presence.",
    "Return one matching interval or all intervals. Explain why listing all answers can require quadratic output even when counting is linear.",
    '''
    function usageBursts(deltas,target) {
      const counts=new Map([[0,1]]); let sum=0, result=0;
      for (const delta of deltas) {
        sum+=delta; result+=counts.get(sum-target) ?? 0;
        counts.set(sum,(counts.get(sum) ?? 0)+1);
      }
      return result;
    }
    ''', '''
    def usage_bursts(deltas,target):
        counts = {0:1}
        total = result = 0
        for delta in deltas:
            total += delta
            result += counts.get(total-target,0)
            counts[total] = counts.get(total,0)+1
        return result
    ''', '''
    assert.equal(usageBursts([2,-1,2,1],3),2);
    assert.equal(usageBursts([0,0,0],0),6);
    assert.equal(usageBursts([-2,-1,1],-3),1);
    assert.equal(usageBursts([],0),0);
    ''', '''
    assert usage_bursts([2,-1,2,1],3) == 2
    assert usage_bursts([0,0,0],0) == 6
    assert usage_bursts([-2,-1,1],-3) == 1
    assert usage_bursts([],0) == 0
    ''', "Expected O(n) time and O(n) auxiliary space.")

coding("Split a compact identifier into known tokens", "Dynamic programming",
    "A compact identifier is formed by concatenating dictionary tokens. Return any segmentation into the fewest tokens, or null/None if no segmentation exists.",
    ["Identifier and tokens use ASCII; dictionary tokens are nonempty and may be reused.", "Empty identifier returns []. On ties, choose the earliest last-split index at each DP state. Intended identifier length ≤ 500."],
    ["text='cloudapilog', tokens=['cloud','api','log','cloudapi'] → ['cloudapi','log'].", "text='cache', tokens=['cat'] → null/None; empty text → [].", "Test repeated tokens, duplicates in the dictionary, and multiple equally short segmentations."],
    "Let dp[end] be the fewest tokens needed for text[:end]. For each earlier start, if the prefix to start is reachable and text[start:end] is a token, relax dp[end] with dp[start]+1. Save the chosen predecessor and reconstruct backward. Iterate starts ascending and update only on strict improvement to define ties.",
    "A greedy longest-token choice may block the remaining suffix. What state summarizes a solved prefix?",
    "Use a trie to avoid creating and hashing every substring. How would costs per token or a huge dictionary change the state and data structure?",
    '''
    function splitIdentifier(text,tokens) {
      const dictionary=new Set(tokens), n=text.length;
      const dp=Array(n+1).fill(Infinity), prev=Array(n+1).fill(-1); dp[0]=0;
      for (let end=1;end<=n;end++) {
        for (let start=0;start<end;start++) {
          if (dp[start]+1<dp[end] && dictionary.has(text.slice(start,end))) {
            dp[end]=dp[start]+1; prev[end]=start;
          }
        }
      }
      if (!Number.isFinite(dp[n])) return null;
      const result=[];
      for (let end=n;end>0;end=prev[end]) result.push(text.slice(prev[end],end));
      return result.reverse();
    }
    ''', '''
    def split_identifier(text,tokens):
        dictionary = set(tokens)
        n = len(text)
        dp = [float('inf')] * (n+1)
        prev = [-1] * (n+1)
        dp[0] = 0
        for end in range(1,n+1):
            for start in range(end):
                if dp[start]+1 < dp[end] and text[start:end] in dictionary:
                    dp[end] = dp[start]+1
                    prev[end] = start
        if dp[n] == float('inf'):
            return None
        result = []
        end = n
        while end > 0:
            result.append(text[prev[end]:end])
            end = prev[end]
        return result[::-1]
    ''', '''
    assert.deepEqual(splitIdentifier('cloudapilog',['cloud','api','log','cloudapi']),['cloudapi','log']);
    assert.equal(splitIdentifier('cache',['cat']),null);
    assert.deepEqual(splitIdentifier('',[]),[]);
    assert.deepEqual(splitIdentifier('aaaa',['a','aa','aaa']),['a','aaa']);
    assert.deepEqual(splitIdentifier('abcdef',['abcd','abc','def']),['abc','def']);
    ''', '''
    assert split_identifier('cloudapilog',['cloud','api','log','cloudapi']) == ['cloudapi','log']
    assert split_identifier('cache',['cat']) is None
    assert split_identifier('',[]) == []
    assert split_identifier('aaaa',['a','aa','aaa']) == ['a','aaa']
    assert split_identifier('abcdef',['abcd','abc','def']) == ['abc','def']
    ''', "O(n²) candidate splits; O(n³ + D) worst-case time when substring creation/hashing costs O(n). O(n + D) auxiliary space for DP and dictionary of total size D.", minutes=40)

coding("Schedule nonoverlapping maintenance jobs", "Greedy algorithms",
    "Each maintenance job has a half-open interval [start,end). Choose the maximum number of jobs that can run on one exclusive maintenance lane, and return their original indices in scheduled order.",
    ["Each start is strictly less than its end. Touching jobs are compatible.", "Sort ties by earlier start then original index. The input is unchanged; any maximum-cardinality schedule is valid."],
    ["[[0,4],[1,2],[2,3],[3,5]] → [1,2,3].", "[[1,3],[3,4]] → [0,1]; [] → [].", "Test equal end times, nested intervals, and an earliest-start job that blocks many shorter jobs."],
    "Sort by finishing time and repeatedly accept a job whose start is at least the last accepted end. The earliest-finishing compatible job leaves at least as much room as any alternative first job. An exchange argument then applies the same reasoning to the remaining jobs.",
    "Choosing the earliest start or shortest duration can fail. Which choice leaves the most future scheduling room?",
    "What changes if jobs have different values, or if there are two maintenance lanes? Explain why the weighted version needs more than this greedy rule.",
    '''
    function maintenanceSchedule(intervals) {
      const jobs=intervals.map(([start,end],index)=>({start,end,index}));
      jobs.sort((a,b)=>a.end-b.end || a.start-b.start || a.index-b.index);
      const chosen=[]; let end=-Infinity;
      for (const job of jobs) {
        if (job.start>=end) { chosen.push(job.index); end=job.end; }
      }
      return chosen;
    }
    ''', '''
    def maintenance_schedule(intervals):
        jobs = sorted((end,start,index) for index,(start,end) in enumerate(intervals))
        chosen = []
        last_end = float('-inf')
        for end,start,index in jobs:
            if start >= last_end:
                chosen.append(index)
                last_end = end
        return chosen
    ''', '''
    assert.deepEqual(maintenanceSchedule([[0,4],[1,2],[2,3],[3,5]]),[1,2,3]);
    assert.deepEqual(maintenanceSchedule([[1,3],[3,4]]),[0,1]);
    assert.deepEqual(maintenanceSchedule([[0,3],[1,3],[3,5]]),[0,2]);
    assert.deepEqual(maintenanceSchedule([]),[]);
    ''', '''
    assert maintenance_schedule([[0,4],[1,2],[2,3],[3,5]]) == [1,2,3]
    assert maintenance_schedule([[1,3],[3,4]]) == [0,1]
    assert maintenance_schedule([[0,3],[1,3],[3,5]]) == [0,2]
    assert maintenance_schedule([]) == []
    ''', "O(n log n) time and O(n) auxiliary space including copied jobs and output.")

coding("Find the largest connected outage region", "Graphs & iterative DFS",
    "A rectangular monitoring grid uses 1 for an affected cell and 0 for a healthy cell. Return the size of the largest region of affected cells connected horizontally or vertically.",
    ["The grid is rectangular and binary. Diagonal contact does not connect regions.", "Do not mutate the grid. Avoid recursion because a long thin region can exceed a language's call-stack limit."],
    ["[[1,1,0],[0,1,0],[1,0,1]] → 3.", "[[1,0],[0,1]] → 1; [] or [[]] → 0.", "Test all healthy cells, all affected cells, and a one-row region."],
    "Scan all cells. For each unvisited affected cell, run iterative depth-first search, marking neighbors when pushed to avoid duplicate work. Count that component and update the maximum. The outer scan and all traversals together visit each cell at most once.",
    "A separate visited structure preserves the caller's data. Mark when discovering, not after popping.",
    "Return the component's boundary, update the answer as cells fail over time, or process a grid too large for memory. Which changes require a different representation?",
    '''
    function largestOutage(grid) {
      const rows=grid.length, cols=rows ? grid[0].length : 0;
      const seen=new Set(); let best=0;
      for (let r=0;r<rows;r++) for (let c=0;c<cols;c++) {
        const key=r*cols+c;
        if (!grid[r][c] || seen.has(key)) continue;
        const stack=[[r,c]]; seen.add(key); let count=0;
        while (stack.length) {
          const [x,y]=stack.pop(); count++;
          for (const [dx,dy] of [[1,0],[-1,0],[0,1],[0,-1]]) {
            const a=x+dx, b=y+dy, next=a*cols+b;
            if (a>=0 && a<rows && b>=0 && b<cols && grid[a][b] && !seen.has(next)) {
              seen.add(next); stack.push([a,b]);
            }
          }
        }
        best=Math.max(best,count);
      }
      return best;
    }
    ''', '''
    def largest_outage(grid):
        rows = len(grid)
        cols = len(grid[0]) if rows else 0
        seen = set()
        best = 0
        for r in range(rows):
            for c in range(cols):
                if not grid[r][c] or (r,c) in seen:
                    continue
                stack = [(r,c)]
                seen.add((r,c))
                count = 0
                while stack:
                    x,y = stack.pop()
                    count += 1
                    for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
                        a,b = x+dx,y+dy
                        if 0 <= a < rows and 0 <= b < cols and grid[a][b] and (a,b) not in seen:
                            seen.add((a,b))
                            stack.append((a,b))
                best = max(best,count)
        return best
    ''', '''
    const grid=[[1,1,0],[0,1,0],[1,0,1]], before=JSON.stringify(grid);
    assert.equal(largestOutage(grid),3); assert.equal(JSON.stringify(grid),before);
    assert.equal(largestOutage([[1,0],[0,1]]),1);
    assert.equal(largestOutage([[1,1,1,1]]),4);
    assert.equal(largestOutage([]),0); assert.equal(largestOutage([[]]),0);
    ''', '''
    grid=[[1,1,0],[0,1,0],[1,0,1]]
    before=[row[:] for row in grid]
    assert largest_outage(grid) == 3 and grid == before
    assert largest_outage([[1,0],[0,1]]) == 1
    assert largest_outage([[1,1,1,1]]) == 4
    assert largest_outage([]) == 0 and largest_outage([[]]) == 0
    ''', "Expected O(rows × columns) time and O(rows × columns) auxiliary space.")

coding("Keep 64-bit event IDs lossless", "JavaScript & Python semantics",
    "An API serializes nonnegative 64-bit IDs as canonical decimal strings. Return unique IDs sorted by numeric value, still as strings. Explain why parsing through a JavaScript Number can corrupt identity.",
    ["Each ID matches 0 or a nonzero digit followed by digits, with value ≤ 2^64−1. Input is already validated.", "Never convert the IDs through a floating-point representation. Do not mutate the input."],
    ["['9007199254740993','2','9007199254740992','2'] → ['2','9007199254740992','9007199254740993'].", "['0','18446744073709551615','0'] → ['0','18446744073709551615'].", "Test the 2^53 boundary, duplicates, empty input, and 10 versus 2."],
    "Deduplicate the canonical strings, then compare exact integers. JavaScript BigInt represents these IDs exactly; return −1, 0, or 1 from the comparator rather than subtracting BigInts as a sort result. Python int already supports arbitrary precision. Keep the strings at JSON boundaries. JavaScript Number cannot distinguish every integer beyond its safe-integer bound of 2^53−1.",
    "Sorting strings lexicographically gives the wrong result for '10' and '2'; Number arithmetic loses precision near 2^53.",
    "Support arbitrarily long decimal IDs using length then lexicographic order. How should an API schema prevent a client from accidentally decoding IDs as numbers?",
    '''
    function sortIds(ids) {
      return [...new Set(ids)].sort((a,b)=>{
        const x=BigInt(a), y=BigInt(b);
        return x<y ? -1 : x>y ? 1 : 0;
      });
    }
    ''', '''
    def sort_ids(ids):
        return sorted(set(ids), key=int)
    ''', '''
    assert.deepEqual(sortIds(['9007199254740993','2','9007199254740992','2']),['2','9007199254740992','9007199254740993']);
    assert.deepEqual(sortIds(['0','18446744073709551615','0']),['0','18446744073709551615']);
    assert.deepEqual(sortIds(['10','2']),['2','10']);
    assert.deepEqual(sortIds([]),[]);
    assert.equal(Number('9007199254740992'),Number('9007199254740993'));
    ''', '''
    assert sort_ids(['9007199254740993','2','9007199254740992','2']) == ['2','9007199254740992','9007199254740993']
    assert sort_ids(['0','18446744073709551615','0']) == ['0','18446744073709551615']
    assert sort_ids(['10','2']) == ['2','10']
    assert sort_ids([]) == []
    assert int('9007199254740992') != int('9007199254740993')
    ''', "O(n + u log u) time and O(u) auxiliary space for bounded-width 64-bit IDs; u is the distinct count.",
    source_keys=("integer",), kind="concept", minutes=20)

coding("Bound concurrency without losing result order", "Async & concurrency",
    "Implement mapSettledLimit(items, limit, asyncFn). Run at most limit calls at once, continue after failures, and return outcomes in input order as {status:'fulfilled',value} or {status:'rejected',reason:string}.",
    ["limit is a positive integer; reject invalid limits even for empty input. asyncFn may fail synchronously or asynchronously.", "Assume a finite input array and each operation eventually settles. This limits concurrency, not requests per second.", "Cancellation of the whole operation is outside this basic contract; discuss it as a follow-up."],
    ["[1,2,3] with doubling and limit=2 → fulfilled values [2,4,6] in input order regardless of completion order.", "An operation that fails for 2 produces a rejected middle slot; items 1 and 3 still complete.", "Test empty input, invalid limits, peak in-flight calls, and one worker."],
    "Launch at most limit workers. Each claims the next index before awaiting, runs one operation, stores its settled outcome into that index, and repeats. Claiming is synchronous in the single-event-loop model. Catch failures inside each worker so one rejected operation does not stop the batch. Creating one task per item behind a semaphore would still allocate O(n) tasks.",
    "Use a small worker pool and a shared next-index counter. Output order does not need to equal completion order.",
    "Add an abort signal, deadlines, or a producer that applies backpressure. Explain how rate limiting differs and how you would prevent a never-settling operation from hanging the batch.",
    '''
    async function mapSettledLimit(items,limit,asyncFn) {
      if (!Number.isInteger(limit) || limit<1) throw new RangeError('invalid limit');
      const results=Array(items.length); let next=0;
      async function worker() {
        while (next<items.length) {
          const index=next++;
          try { results[index]={status:'fulfilled',value:await asyncFn(items[index],index)}; }
          catch (error) { results[index]={status:'rejected',reason:error instanceof Error ? error.message : String(error)}; }
        }
      }
      await Promise.all(Array.from({length:Math.min(limit,items.length)},()=>worker()));
      return results;
    }
    ''', '''
    import asyncio

    async def map_settled_limit(items,limit,async_fn):
        if not isinstance(limit,int) or isinstance(limit,bool) or limit < 1:
            raise ValueError('invalid limit')
        results = [None] * len(items)
        next_index = 0
        async def worker():
            nonlocal next_index
            while next_index < len(items):
                index = next_index
                next_index += 1
                try:
                    value = await async_fn(items[index],index)
                    results[index] = {'status':'fulfilled','value':value}
                except Exception as error:
                    results[index] = {'status':'rejected','reason':str(error)}
        await asyncio.gather(*(worker() for _ in range(min(limit,len(items)))))
        return results
    ''', '''
    let active=0,peak=0;
    const outcomes=await mapSettledLimit([1,2,3,4],2,async value=>{
      active++; peak=Math.max(peak,active);
      try { await new Promise(resolve=>setTimeout(resolve,0)); if(value===2) throw new Error('bad'); return value*2; }
      finally { active--; }
    });
    assert.equal(peak,2); assert.equal(active,0);
    assert.deepEqual(outcomes,[{status:'fulfilled',value:2},{status:'rejected',reason:'bad'},{status:'fulfilled',value:6},{status:'fulfilled',value:8}]);
    assert.deepEqual(await mapSettledLimit([],3,async x=>x),[]);
    await assert.rejects(()=>mapSettledLimit([],0,async x=>x),RangeError);
    assert.deepEqual(await mapSettledLimit([1],1,()=>{throw 'oops';}),[{status:'rejected',reason:'oops'}]);
    const finish=[];
    const reversed=mapSettledLimit([10,20],2,(_,index)=>new Promise(resolve=>{finish[index]=resolve;}));
    finish[1](40); await Promise.resolve(); finish[0](20);
    assert.deepEqual(await reversed,[{status:'fulfilled',value:20},{status:'fulfilled',value:40}]);
    ''', '''
    async def test():
        active = peak = 0
        async def operation(value,index):
            nonlocal active,peak
            active += 1
            peak = max(peak,active)
            try:
                await asyncio.sleep(0)
                if value == 2:
                    raise ValueError('bad')
                return value*2
            finally:
                active -= 1
        outcomes = await map_settled_limit([1,2,3,4],2,operation)
        assert peak == 2 and active == 0
        assert outcomes == [{'status':'fulfilled','value':2},{'status':'rejected','reason':'bad'},{'status':'fulfilled','value':6},{'status':'fulfilled','value':8}]
        assert await map_settled_limit([],3,operation) == []
        try:
            await map_settled_limit([],0,operation)
            assert False
        except ValueError:
            pass
        finished = []
        gates = [asyncio.Event(),asyncio.Event()]
        started = asyncio.Event()
        started_count = 0
        async def reversed_operation(value,index):
            nonlocal started_count
            started_count += 1
            if started_count == 2:
                started.set()
            await gates[index].wait()
            finished.append(index)
            return value*2
        task = asyncio.create_task(map_settled_limit([10,20],2,reversed_operation))
        await started.wait()
        gates[1].set()
        await asyncio.sleep(0)
        gates[0].set()
        assert await task == [{'status':'fulfilled','value':20},{'status':'fulfilled','value':40}]
        assert finished == [1,0]
    asyncio.run(test())
    ''', "O(n) scheduling work, O(min(n,limit)) active workers, and O(n) result storage; wall time depends on task durations.",
    source_keys=("settled","asyncio"), kind="concept", minutes=40)

coding("Coalesce concurrent cache misses", "Async & concurrency",
    "Implement an in-process single-flight loader: overlapping requests for the same key share one pending load. Remove the entry after either success or failure so a later request can retry. Requests for different keys remain independent.",
    ["Keys are strings. Callers for a given key agree on the loader; only the first overlapping loader runs.", "This is deduplication of pending work, not a permanent value cache or a distributed lock.", "One Python caller being cancelled must not cancel the shared load for other callers. JavaScript cancellation is not exposed by this API."],
    ["Two overlapping get('a', loader) calls run loader once and both receive its result.", "A failed load is removed; the next get('a', successfulLoader) can succeed.", "Test synchronous throw in JavaScript, simultaneous different keys, and a cancelled Python waiter."],
    "Store the promise/task before executing or awaiting the load. Reuse it while pending and remove it on either outcome. Cleanup checks identity so an older completion cannot remove a newer entry. In Python, shield the shared task from a waiter's cancellation. Cleanup retrieves unobserved exceptions if every waiter has gone away; callers still receive the original task's error.",
    "Cache the pending operation itself. A cache that is populated only after await cannot prevent duplicate work.",
    "Add per-caller deadlines without aborting other waiters. When should the underlying operation be cancelled? How would cross-process coalescing differ?",
    '''
    class SingleFlight {
      constructor() { this.pending=new Map(); }
      get(key,loader) {
        if (this.pending.has(key)) return this.pending.get(key);
        const promise=Promise.resolve().then(loader);
        this.pending.set(key,promise);
        const cleanup=()=>{ if (this.pending.get(key)===promise) this.pending.delete(key); };
        promise.then(cleanup,cleanup);
        return promise;
      }
    }
    ''', '''
    import asyncio

    class SingleFlight:
        def __init__(self):
            self.pending = {}

        async def get(self,key,loader):
            if key not in self.pending:
                async def run():
                    return await loader()
                task = asyncio.create_task(run())
                self.pending[key] = task
                def cleanup(done):
                    if self.pending.get(key) is done:
                        del self.pending[key]
                    if not done.cancelled():
                        done.exception()
                task.add_done_callback(cleanup)
            return await asyncio.shield(self.pending[key])
    ''', '''
    const flight=new SingleFlight(); let calls=0, release;
    const gate=new Promise(resolve=>{release=resolve;});
    const loader=async()=>{calls++; await gate; return 7;};
    const a=flight.get('a',loader), b=flight.get('a',loader);
    assert.equal(a,b);
    await Promise.resolve(); assert.equal(calls,1); release();
    assert.deepEqual(await Promise.all([a,b]),[7,7]);
    await assert.rejects(flight.get('fail',()=>{throw new Error('failed');}),/failed/);
    assert.equal(await flight.get('fail',async()=>9),9);
    assert.deepEqual(await Promise.all([flight.get('x',async()=>1),flight.get('y',async()=>2)]),[1,2]);
    assert.equal(flight.pending.size,0);
    ''', '''
    async def test():
        flight=SingleFlight()
        gate=asyncio.Event()
        started=asyncio.Event()
        calls=0
        async def loader():
            nonlocal calls
            calls += 1
            started.set()
            await gate.wait()
            return 7
        first=asyncio.create_task(flight.get('a',loader))
        second=asyncio.create_task(flight.get('a',loader))
        await started.wait()
        assert calls == 1
        first.cancel()
        try:
            await first
            assert False
        except asyncio.CancelledError:
            pass
        gate.set()
        assert await second == 7
        async def failed():
            raise ValueError('failed')
        try:
            await flight.get('fail',failed)
            assert False
        except ValueError:
            pass
        async def good():
            return 9
        assert await flight.get('fail',good) == 9
        assert not flight.pending
    asyncio.run(test())
    ''', "Expected O(1) map work per call and O(k) shared state for k distinct pending keys, excluding the loaders and waiter objects.",
    source_keys=("asyncio",), kind="concept", minutes=40)

coding("Isolate mutable retry request snapshots", "JavaScript & Python semantics",
    "A retry test builds attempts with Array(count).fill(request) in JavaScript or [request] * count in Python. Mutating attempt 0's nested headers unexpectedly changes other attempts. Implement buildAttempts(request,count) so the original and every attempt have independent nested data.",
    ["The request is a finite JSON-like tree of objects/dictionaries, arrays/lists, strings, booleans, null/None, and numbers. It contains no functions, custom classes, cycles, or shared-reference identity requirements.", "count is a nonnegative integer. Each attempt must be a full deep snapshot taken before the function returns."],
    ["After creating two attempts, change attempts[0].headers.tags[0]; attempts[1] and the original must keep their prior tag.", "count=0 → []; empty request still yields independent objects.", "Test modifying an inner list, adding a key, and changing the original after snapshotting."],
    "Both array fill and list multiplication duplicate references, not nested objects. A shallow spread/dict copy only separates the outer container. Deep-copy separately for each attempt: structuredClone in JavaScript and copy.deepcopy in Python support this contract. A deep copy is independent but remains mutable; immutability is a separate policy.",
    "Draw the object graph. Which nodes are shared after copying only the outer object?",
    "When is schema-based copying better than a generic deep clone? Discuss unsupported values, large binary payloads, transfer semantics, and immutable persistent structures.",
    '''
    function buildAttempts(request,count) {
      if (!Number.isInteger(count) || count<0) throw new RangeError('invalid count');
      return Array.from({length:count},()=>structuredClone(request));
    }
    ''', '''
    from copy import deepcopy

    def build_attempts(request,count):
        if not isinstance(count,int) or isinstance(count,bool) or count < 0:
            raise ValueError('invalid count')
        return [deepcopy(request) for _ in range(count)]
    ''', '''
    const request={headers:{tags:['safe']},body:{id:1}};
    const attempts=buildAttempts(request,2);
    attempts[0].headers.tags[0]='changed'; attempts[0].extra=true;
    request.body.id=99;
    assert.deepEqual(attempts[1],{headers:{tags:['safe']},body:{id:1}});
    assert.equal(request.headers.tags[0],'safe');
    assert.deepEqual(buildAttempts({},0),[]);
    const empty=buildAttempts({},2); assert.notEqual(empty[0],empty[1]);
    assert.throws(()=>buildAttempts({},-1),RangeError);
    ''', '''
    request={'headers':{'tags':['safe']},'body':{'id':1}}
    attempts=build_attempts(request,2)
    attempts[0]['headers']['tags'][0]='changed'
    attempts[0]['extra']=True
    request['body']['id']=99
    assert attempts[1] == {'headers':{'tags':['safe']},'body':{'id':1}}
    assert request['headers']['tags'][0] == 'safe'
    assert build_attempts({},0) == []
    empty=build_attempts({},2)
    assert empty[0] is not empty[1]
    try:
        build_attempts({},-1)
        assert False
    except ValueError:
        pass
    ''', "O(count × size(request)) time and output space, plus traversal memory for cloning one request.",
    source_keys=("clone","copy"), kind="concept", minutes=20)

def design(title,topic,prompt,requirements,scale,walkthrough,tradeoffs,tests,hint,followup,rubric,source_keys,minutes=40):
    number = len(CARDS)+1
    sections = [
        {"title":"Hint","html":p(hint)},
        {"title":"Worked walkthrough","html":ul(walkthrough)},
        {"title":"Trade-offs","html":ul(tradeoffs)},
        {"title":"Failure cases and tests","html":ul(tests)},
        {"title":"Interviewer follow-up","html":p(followup)},
        {"title":"Self-review rubric","html":ul(rubric)},
    ]
    CARDS.append({
        "id":"modern-%03d" % number,"deckId":"modern","number":number,
        "title":title,"topic":topic,"kind":"design","difficulty":"Medium","timeMinutes":minutes,
        "question":p(prompt)+"<h3>Requirements</h3>"+ul(requirements)+"<h3>Assumed scale</h3>"+p(scale),
        "answer":p(walkthrough[0])+p("Treat these numbers and choices as exercise assumptions. A strong answer states the consistency guarantee, walks through one request and one failure, and explains a simpler alternative."),
        "sections":sections,"search":" ".join([title,topic,prompt,scale,*walkthrough,*tradeoffs,*tests,followup]),
        "sources":refs(source_keys),
    })

design("Design an offline-first review app", "Offline & synchronization",
    "Design a study app that remains useful on a phone during a week without connectivity, then reconciles progress across two devices. Explain storage, synchronization, conflict behavior, and updates.",
    ["Reading downloaded decks and recording reviews must work offline after initial installation/download.","A review must not disappear or be counted twice after reconnecting. Note edits from two devices must not silently overwrite each other.","Users need a visible download state, pending-sync count, and portable export."],
    "Assume 50,000 daily active users × 200 reviews/day = 10 million review events/day, about 116/s average and 1,200/s at a 10× peak. At 256 bytes/event, raw events are about 2.56 GB/day before indexes and replication. A typical device caches 20 MB of deck data.",
    ["Separate immutable deck assets, local user state, and a durable outbox of pending operations. The app renders from local state immediately and synchronizes in the background when it can.",
     "Use a service worker to cache a versioned application shell/deck assets and IndexedDB for structured progress plus the outbox. Commit the local review and its outbox event in one transaction. Display a ready-for-offline status only after required assets are cached.",
     "Give each operation a device-generated unique ID and tenant/user scope. POST batches with these IDs; the server deduplicates transactionally, assigns a monotone server sequence, and returns acknowledgements plus a pull cursor. Delete acknowledged outbox entries only after their acknowledgements are durable locally.",
     "Model reviews as append-only events so concurrent devices can both contribute. State a deterministic scheduling policy: for example, process accepted review events in server sequence order and recompute the card schedule. Device timestamps remain display metadata because clocks can disagree. Deduplication removes retries, not genuinely separate reviews.",
     "For notes, send the base revision. If it is stale, retain both versions and offer a merge instead of last-write-wins data loss. Keep deck content version separate from progress IDs so a content update does not reset learning history.",
     "Coordinate shell/deck/schema upgrades, provide a recoverable export, and test storage eviction. A browser can remove local data; offline storage alone is not a backup. Reauthenticate on reconnect, scope caches by account, and clear private local data on an explicit sign-out policy."],
    ["An append-only review log simplifies retry handling and auditability but needs compaction/checkpoints for long histories.","Automatic conflict resolution feels smooth but needs a product rule; preserving both note edits is safer when intent cannot be inferred.","Download-on-demand reduces storage; downloading all chosen decks gives a stronger offline promise. Background execution differs by mobile platform, so sync-on-open must work."],
    ["Kill the app between local write and upload, and between server commit and response; repeated uploads must converge without missing reviews.","Edit the same note on two offline devices, skew a device clock, update the deck while offline, and exhaust storage.","Install online, confirm caching, disable all network, reopen from the home screen, review cards, then reconnect and verify counts."],
    "Draw two separate flows: the local transaction and the later server acknowledgement. Identify which side owns each identifier and cursor.",
    "How would you support encrypted private notes, account switching, tombstones for deletions, or a device returning after a year?",
    ["Defines offline readiness and transaction boundaries.","Shows duplicate suppression and a concrete conflict policy.","Distinguishes cache availability from durable backup and explains update recovery."],
    ("idb","sw"),minutes=45)

design("Make a job-creation API safe to retry", "API correctness",
    "Design POST /render-jobs so a client can safely retry after a timeout without creating a second rendering job. Cover two identical requests arriving concurrently and the server crashing after commit but before replying.",
    ["Clients supply a stable idempotency key for one intended creation.","The same key and same request return the original job; reusing a key for a different request is rejected.","The guarantee lasts 24 hours and is scoped to the authenticated tenant. Job execution is asynchronous."],
    "Assume 100 new jobs/s and a 24-hour deduplication window: 8.64 million active idempotency records. At an illustrative 200 bytes/record, raw records alone use about 1.73 GB; account separately for indexes, request hashes, and response data.",
    ["Make (tenant_id, idempotency_key) a unique database key. Store a canonical request digest, job ID, creation status, and expiry. Authenticate and authorize before lookup; the key is not an authorization token.",
     "In one database transaction, reserve the idempotency key, create the job row, and write an outbox row for execution. A concurrent duplicate is serialized by the uniqueness constraint; after the winning transaction completes, compare its request digest and return its job ID or a mismatch error.",
     "If the transaction aborts, none of those rows should remain committed. If commit succeeds but the response is lost, a retry reads the committed record and returns the same outcome. Do not claim that a pre-check followed by a separate insert is race-free.",
     "An outbox relay publishes pending jobs and records its progress. Publishing may happen twice if it crashes between publish and marking sent, so workers use the job ID to make state transitions idempotent. External side effects require their own deduplication protocol.",
     "Document key retention and expiry precisely. A request replayed after the window may create a new job; clients needing longer protection must retain a business operation ID or use a longer policy. Bound key length and per-tenant storage abuse."],
    ["Persisting the original response provides exact replay but uses more storage than retaining a canonical resource ID.","Hashing the request alone is not an intent identifier: two identical jobs may be intentionally separate. A caller-chosen key represents intent.","A distributed cache can speed lookup, but correctness should live in an atomic durable boundary, with careful expiry semantics."],
    ["Fire 100 simultaneous same-key requests; assert one job row and one logical execution.","Drop the response after commit, fail the outbox relay after publication, and replay a request after expiry.","Reuse a key with a changed payload and from a different tenant; verify mismatch handling and tenant isolation."],
    "Choose a single transaction that joins the intent record, resource creation, and reliable enqueueing.",
    "How would you support operations that take minutes, retryable versus terminal failures, and a non-idempotent external rendering provider?",
    ["Specifies the key's scope, retention, and payload-mismatch behavior.","Handles concurrent duplicates and the commit/response failure window.","Separates request deduplication from end-to-end execution guarantees."],
    ("retry","constraints"))

design("Protect a multi-tenant API from bursts", "Reliability & rate limiting",
    "Design per-tenant admission control for a shared API. A tenant should sustain 100 requests/s and briefly burst to 200 requests without overwhelming shared backends.",
    ["Return a clear rejection response and useful retry guidance when the tenant budget is exhausted.","Protect the backend with a global concurrency/load limit as well as per-tenant fairness.","Explain behavior during limiter failure and across two regions."],
    "Assume 1,000 active tenants and 20,000 incoming requests/s total, with heavily skewed traffic. A typical admitted request holds backend resources for 100 ms; 20,000 requests/s at that mean duration implies roughly 2,000 concurrent requests before queues and overhead.",
    ["Use one token bucket per tenant: capacity 200, refill 100 tokens/s. On arrival, refill by elapsed time up to capacity, then atomically consume one token if available. Store balance and last-refill time together at the limiter's authoritative shard.",
     "Use a single atomic operation or server-side script for read/refill/decrement; separate reads and writes overspend under concurrency. Base elapsed time on a consistent server clock and clamp negative elapsed time. Expire inactive buckets only after enough time to refill fully.",
     "A depleted bucket returns HTTP 429 with a retry delay derived from the deficit. Clients apply bounded backoff with jitter. Rate limiting does not replace a concurrency cap, bounded queue, deadlines, or shedding low-priority work under backend overload.",
     "Choose failure behavior by endpoint: strict fail-closed for costly scarce operations; a small local emergency allowance for a read endpoint that can tolerate bounded overshoot. Record fallback activations and make the overshoot bound explicit.",
     "For two regions, either route a tenant to one authoritative bucket, coordinate globally at added latency, or allocate regional quotas whose sum stays within the global budget. Independently issuing the full quota in both regions doubles the allowed rate. Rebalancing quota requires careful ownership and failure handling."],
    ["Central coordination strengthens the global limit but adds latency and a dependency; local buckets are faster but can overshoot.","Token buckets permit controlled bursts; sliding logs track exact recent arrivals but cost more memory and work.","A tenant's rate is only one dimension: request cost, active streams, or tokens may be more meaningful than raw request count."],
    ["Send simultaneous requests at refill boundaries, idle then burst, skew clocks, and fail the authoritative shard.","Create one hot tenant, rebalance regions, and prove the maximum overshoot under fallback.","Measure admitted/rejected requests by bounded labels, limiter latency, backend saturation, and queue age."],
    "Write the bucket state and atomic update first. Then identify the guarantee lost when you add replicas or fallbacks.",
    "Support weighted requests, tenant priorities, long-lived streaming calls, or a limit that must never be exceeded globally.",
    ["Derives refill and burst behavior and includes atomicity.","Distinguishes rate, concurrency, queue length, and overload.","Quantifies the consistency/failure trade-off instead of assuming global correctness from local counters."],
    ("overload",))

design("Deliver webhooks despite retries and outages", "Queues & delivery",
    "Design a webhook delivery service that accepts tenant events, reliably attempts delivery to registered destinations, and tolerates duplicates, slow receivers, and multi-hour outages.",
    ["Persist events before acknowledging acceptance. Retry transient failures with bounded backoff; preserve terminal failures for inspection/replay.","Give each event a stable delivery identity and authenticate payloads.","Do not claim exactly-once business side effects at an arbitrary receiver."],
    "Assume 500 events/s × 1 KB/event = about 43.2 GB/day of raw payloads. A six-hour destination outage can accumulate 10.8 million events if all traffic targets it; isolate that backlog so healthy tenants continue.",
    ["Accept the event into durable storage and enqueue an event reference through a transaction/outbox boundary. Partition work by tenant or destination and enforce per-destination concurrency so one slow endpoint cannot occupy the entire worker fleet.",
     "A worker acquires a bounded lease, signs the payload with a rotating destination secret, and sends a stable event ID plus a timestamp. Apply connection and total deadlines, response-size limits, and a configured egress policy for registered URLs.",
     "Mark success on the agreed successful response range. Retry network errors, timeouts, and selected retryable statuses with exponential backoff and jitter; honor bounded retry guidance. Cap attempts or event age, then move the record to an inspectable failed state. Do not retry every permanent 4xx indefinitely.",
     "If a receiver commits and its acknowledgement is lost, the sender cannot know whether processing happened. It must retry and the receiver should deduplicate the stable event ID in the same transaction as its business update. A queue's exactly-once feature has a specific scope and does not make arbitrary HTTP effects exactly once.",
     "Expose delivery attempts, next retry, and a controlled replay API. Monitor oldest backlog age, success rate, attempt amplification, per-destination latency, and failed-event count. Preserve ordering only where required; strict ordering can let one poison event block later ones."],
    ["At-least-once delivery is recoverable but requires duplicate-tolerant consumers. At-most-once avoids retries but can lose events.","Per-destination ordering simplifies some consumers and reduces throughput/availability when a message fails.","Long retention helps recovery but consumes storage and may retain sensitive payloads; store only what the product needs."],
    ["Kill a worker after the receiver accepts but before local acknowledgement; expect a duplicate with the same ID.","Simulate 429, 500, a permanent 400, a hanging response, secret rotation, and an invalid registered destination.","Drain a large backlog without starving new traffic or unrelated tenants; replay must retain a deliberate deduplication policy."],
    "Walk through the ambiguous outcome after a receiver commits but the sender times out. No broker setting can remove that ambiguity by itself.",
    "How would you handle per-user ordering, schema evolution, destination deletion, and receiver-managed replay cursors?",
    ["Identifies the durable acknowledgement boundary and lease/retry policy.","Explains duplicate handling end to end, with correct scope for guarantees.","Prevents one tenant or poison event from exhausting shared resources."],
    ("delivery","retry"),minutes=45)

design("Paginate a changing activity feed", "APIs & data access",
    "Design a paginated tenant activity feed that remains efficient deep into a large history while new events arrive. Explain cursor contents, ordering, permissions, and what consistency the client gets.",
    ["Return up to 50 rows per page, newest first, with an opaque next-page token.","Support a fixed tenant and event-type filter across a traversal.","Define behavior for inserts and deletions during pagination; do not promise a snapshot accidentally."],
    "Assume 50 million retained rows, 2,000 list requests/s, and a target p95 under 150 ms. Rows have immutable created_at and a unique ID; many rows share the same timestamp.",
    ["Define a total order (created_at DESC, id DESC). For a page after cursor (t,id), query rows whose tuple is smaller, with the same tenant/filter, ordered by the same keys, LIMIT pageSize+1. The extra row determines whether another page exists.",
     "Use an index beginning with the equality predicates such as (tenant_id,event_type,created_at DESC,id DESC), adjusting to actual query patterns. Large OFFSET values require the database to find and skip earlier rows; keyset pagination seeks near the cursor instead.",
     "Encode the last returned tuple, normalized filter/version, tenant scope, expiry, and optionally a traversal high-water mark in a signed opaque token. Validate size and version; reject changed filters. The token is a continuation mechanism, not authorization: check access on every request.",
     "Choose a moving-view guarantee: new higher-ranked rows appear on refresh, not in later pages. Deletions may shorten pages. Immutable order keys avoid moving existing rows across the boundary. A first-page high-water mark can exclude later high-ranked inserts but does not provide a full snapshot when rows can be deleted or backfilled.",
     "If a stable export is required, create a snapshot/materialized export job with its own lifecycle instead of holding a database transaction open across a user's long browsing session. Bound page size, token lifetime, query timeout, and allowed filters."],
    ["Keyset pagination supports efficient sequential traversal but cannot cheaply jump to arbitrary page 1,000.","Opaque tokens let the backend evolve; exposing raw offsets or database keys as a public contract makes migrations harder.","A moving feed prioritizes fresh data and low cost. Stable historical exports need stronger snapshot semantics and storage."],
    ["Use many equal timestamps, insert new rows between pages, delete the last row from a prior page, and change permissions mid-traversal.","Tamper with the token, change filters, use an expired token, and try a token from another tenant.","Measure deep-page plans and latency with realistic skew; verify no duplicate rows when immutable keys and a fixed query are used."],
    "Choose a unique stable ordering before designing the token. A timestamp alone is not enough.",
    "Add reverse pagination, full-text ranking, multi-region writes, or a legally auditable point-in-time export.",
    ["Uses a unique order and matching seek predicate/index.","Binds tokens to query context while rechecking permissions.","States the actual consistency contract for concurrent changes."],
    ("pagination","isolation"))

design("Prevent a hot-key cache stampede", "Caching & reliability",
    "A read API uses cache-aside metadata caching. When a popular key expires, thousands of requests hit the origin simultaneously. Design a recovery path that protects the origin and returns appropriately fresh data.",
    ["For this exercise, metadata may be stale for at most 60 seconds after its freshness TTL; authorization decisions may not use this stale policy.","A failed refresh must not create an unbounded request pile-up.","Explain local versus fleet-wide request coalescing and data updates racing with refreshes."],
    "Assume 15,000 reads/s, an origin sustainable capacity of 2,000 reads/s, and one hot key receiving 1,000 reads/s. An origin refresh takes 200 ms, so an uncoalesced miss burst can create roughly 200 simultaneous refreshes for that one key.",
    ["Store value, source version, fresh-until, and stale-until. Fresh entries return immediately. A stale-but-allowed entry returns its value while triggering a refresh. After stale-until, either wait within a short bound for a refresh or fail according to the endpoint's contract.",
     "Coalesce same-key refreshes within each process using a pending promise/task. For fleet-wide protection, use a bounded distributed lease or a dedicated refresh worker so many processes do not each call the origin. A lease is an optimization: its expiry may allow overlapping refreshes.",
     "Write refreshed values only if their source version is at least the stored version, or use a compare-and-set rule. Otherwise a slow old refresh can overwrite a newer value. A lock alone does not solve the stale-writer problem after lease expiry.",
     "Add TTL jitter to spread synchronized expirations, a global refresh concurrency cap, deadlines, and backoff after repeated failures. Jitter spreads many keys; it does not prevent one extremely hot key from stamping. Use negative caching only for explicitly safe, short-lived not-found outcomes.",
     "Monitor origin QPS, refresh concurrency, hit/fresh/stale/miss rates, age served, lease contention, and refresh failures. Include tenant/permission/version context in cache keys where values differ; a fast cache must not leak another tenant's data."],
    ["Stale-while-revalidate improves availability but requires a real product freshness allowance.","Distributed leases reduce duplicate work but add a dependency; local coalescing is simpler and may suffice at small scale.","Longer TTL improves hit rate but delays visibility; invalidation/versioning adds coordination and failure cases."],
    ["Expire the hottest key under load; confirm refresh work is bounded rather than proportional to request count.","Crash the lease holder, delay an old refresh beyond lease expiry, and publish a newer source version during that delay.","Simulate origin failure until stale-until passes; verify the app stops serving data beyond its stated freshness limit."],
    "Separate fresh, stale-but-allowed, and unusable states. Then decide who may refresh each state and for how long.",
    "What changes for rapidly changing permissions, large values, a multilevel CDN/application cache, or a backend that cannot return versions?",
    ["Bounds duplicate refreshes and waiting clients.","States freshness limits and handles stale writers.","Tests overload and failures rather than assuming a good cache hit rate is sufficient."],
    ("overload",))

design("Ship a change with measurable reliability", "SLOs & rollout",
    "Design a rollout and monitoring plan for a new API implementation. The dashboard shows a stable average latency, but a small group of users experiences failures and long waits. Decide what to measure and when to stop the rollout.",
    ["Define a user-centered success SLI and a latency SLI with explicit denominators.","Roll out gradually with a fast rollback or disable path.","Avoid high-cardinality telemetry labels containing arbitrary user IDs, URLs, or request bodies."],
    "Assume 10 million eligible requests/day and a 99.9% successful-request SLO over 28 days. At a steady volume, 280 million requests allow about 280,000 unsuccessful requests. A 5% failure rate burns budget 50× faster than the allowed 0.1% error rate.",
    ["Define eligible requests and success precisely: for example, valid authorized requests that return a correct response before the product deadline. Separate expected client errors from service failures deliberately, rather than silently removing all 4xx or timeouts from the denominator.",
     "Measure latency as a distribution or as the fraction below a user-relevant threshold. A mean hides tails, and averaging per-instance p99 values does not produce a global p99. Aggregate compatible histogram buckets/counts or an appropriate distribution representation.",
     "Canary the change on a small, representative traffic slice; compare success, latency, resource use, and business correctness with a control. Segment using bounded dimensions such as region, client version, and endpoint class to uncover concentrated failures.",
     "Set rollback triggers before release: sustained excess errors, deadline misses, saturation, or a correctness invariant violation. Use both short and longer observation windows to distinguish a short spike from persistent budget consumption. Keep a manual stop and test the rollback path.",
     "Propagate request deadlines and trace context. Use metrics for fleet-wide detection, sampled traces for causality, and structured logs for specific events. Redact sensitive data and keep a release/version marker so an incident can be correlated to the change.",
     "After a rollback, preserve evidence, reduce impact, and write down the failed assumption and a prevention test. A green dashboard is insufficient if the SLI excludes the affected users or the sample is too small."],
    ["A small canary reduces blast radius but needs enough traffic and representative cohorts to reveal failures.","Aggressive rollback thresholds reduce damage but can react to noise; thresholds should reflect volume and business cost.","More tracing helps diagnosis but adds storage/overhead and privacy exposure; sampling needs a deliberate policy."],
    ["Inject a failure limited to one region or client version; ensure segmentation catches it.","Cause a long-tail latency regression while holding the mean steady, and simulate missing telemetry.","Exercise rollback with a backward-compatible data/schema migration; verify older code can still serve safely."],
    "Start from a user's successful interaction, not CPU utilization. Identify the population your denominator excludes.",
    "How would you handle low-traffic services, asynchronous workflows, schema changes that cannot be rolled back, or an SLO that conflicts with cost?",
    ["Defines measurable SLIs and calculates budget consumption correctly.","Distinguishes detection, diagnosis, and mitigation.","Connects rollout decisions to user impact and validates rollback compatibility."],
    ("slo",),minutes=35)

design("Reserve scarce inventory without overselling", "Transactions & consistency",
    "Design a reservation API for a limited-capacity workshop. Multiple clients may reserve the last seat at the same time; clients retry and abandoned reservations expire.",
    ["Never confirm more seats than capacity. A user cannot hold duplicate active reservations for the same workshop.","Reservation creation is retry-safe and holds expire after 10 minutes unless confirmed.","Explain which state changes must be atomic and how confirmation races with expiry."],
    "Assume 2 million workshops, usually under 100 seats each. Normal traffic is 300 reservation requests/s, but a popular workshop can receive 5,000 requests/s for its last few seats. Most contention is concentrated on one row/key.",
    ["Choose one authoritative database transaction for the capacity invariant. A simple model locks the workshop row, checks remaining capacity, inserts a reservation with a unique business/idempotency key, and decrements remaining seats atomically. An atomic conditional UPDATE ... WHERE remaining > 0 is another valid foundation.",
     "Store reservations with an explicit state such as HELD, CONFIRMED, EXPIRED, or CANCELLED, plus expires_at and an idempotency key. Enforce duplicate-active-reservation policy with an appropriate database constraint or a separate unique active-ownership row; application pre-checks alone race.",
     "Confirm using a conditional state transition that verifies HELD and an unexpired deadline under the same lock/transaction policy. The expiry worker similarly changes HELD to EXPIRED and releases capacity exactly once. Whichever valid transition wins prevents the other from also releasing or confirming the seat.",
     "A periodic expiry worker is not a precise timer. The confirmation path must check expiry itself, and reservation creation may reclaim expired holds transactionally if the product needs immediate reuse. Use the authoritative database time for these decisions.",
     "Handle transaction serialization/deadlock failures with bounded retries and the same operation identity. Do not perform slow external calls while holding the hot row lock. Emit confirmation notifications through an outbox so notification failure does not roll back an already committed reservation.",
     "Scale hot workshops by limiting admission/queueing contention before the database and making rejection fast. Sharding helps independent workshops; splitting one capacity invariant across shards requires quota allocation or stronger coordination, not just adding replicas."],
    ["Pessimistic locking gives a clear invariant but serializes a hot workshop. Optimistic compare-and-swap may retry heavily under contention.","Long holds are user-friendly but reduce availability of scarce seats; short holds need clear expiry UX.","Read replicas can serve browsing availability approximately, but final reservation decisions must use the authoritative transaction."],
    ["Race 100 clients for one seat; exactly one hold succeeds and capacity never becomes negative.","Race confirmation with expiry, retry a committed reservation after a lost response, and replay the expiry job.","Kill workers after committing a state change, inject transaction conflicts, and verify the capacity plus held/confirmed-count invariant."],
    "Write the invariant and the legal state transitions before selecting databases. Find the smallest atomic boundary that preserves them.",
    "Add multi-seat reservations, cancellation, waitlists, or reservations spanning two workshops. Which operations introduce multi-resource transactions?",
    ["Protects capacity and uniqueness with database-enforced atomicity.","Handles expiry/confirmation and retry races without double release.","Explains hot-key contention and the actual consistency requirements."],
    ("isolation","constraints"),minutes=45)

DECK = {
    "id":"modern",
    "title":"Modern interview practice",
    "description":"30 original exercises for mid-level SWE preparation: 18 core algorithms in current engineering contexts, 4 JavaScript/Python semantics and concurrency problems, and 8 practical design discussions. Practice clarifying, reasoning, coding, testing, and explaining trade-offs. Designed to complement preparation for roles such as Google L4; not official Google material, actual interview questions, or a guarantee of any interview format. Confirm role-specific expectations with your recruiter.",
    "source":"Original exercises; primary references verified 2026-10-16.",
    "license":"Original practice content",
    "updatedAt":"2026-10-16",
    "languages":["javascript","python"],
    "sources":refs(("google","role")),
    "practiceGuide":[
        "Spend a few minutes clarifying requirements and walking through an example before coding.",
        "State your invariant, compare a simple baseline to an improved approach, and name the input sizes in complexity analysis.",
        "Use the language selector to study both implementations, but choose one language for a timed attempt.",
        "Run or trace the edge cases before reading the reference tests. Treat follow-ups as separate extensions.",
        "Design cards are supplemental engineering practice. System design expectations vary by role and level; framework trivia is not the focus.",
    ],
}

if __name__ == '__main__':
    assert len(CARDS) == 30
    output = ROOT / 'public' / 'modern-deck.json'
    output.write_text(json.dumps({'deck':DECK,'cards':CARDS},ensure_ascii=False,indent=2)+'\n')
    print('Wrote %s with %d original exercises' % (output,len(CARDS)))
