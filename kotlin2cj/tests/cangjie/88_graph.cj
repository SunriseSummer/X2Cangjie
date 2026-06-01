import std.collection.*
import std.deriving.*
import std.sort.*

class Graph {
    let n: Int64
    init(n: Int64) {
        this.n = n
        for (i in 0..n) {
            adj[i] = ArrayList<Int64>()
        }
    }
    let adj = HashMap<Int64, ArrayList<Int64>>()
    func addEdge(u: Int64, v: Int64) {
        adj.get(u)?.add(v)
        adj.get(v)?.add(u)
    }
    func addDirected(u: Int64, v: Int64) {
        adj.get(u)?.add(v)
    }
    func neighbors(u: Int64): ArrayList<Int64> {
        return adj.get(u) ?? ArrayList<Int64>()
    }
    func degree(u: Int64): Int64 {
        return neighbors(u).size
    }
    func edgeCount(): Int64 {
        var total = 0
        for (i in 0..n) {
            total = total + degree(i)
        }
        return total / 2
    }
}

func bfs(g: Graph, start: Int64): ArrayList<Int64> {
    let visited = ArrayList<Bool>()
    for (i in 0..g.n) {
        visited.add(false)
    }
    let order = ArrayList<Int64>()
    let queue = ArrayList<Int64>()
    queue.add(start)
    visited[start] = true
    while (!(queue.isEmpty())) {
        let cur = queue[0]
        queue.remove(at: 0)
        order.add(cur)
        for (next in g.neighbors(cur)) {
            if (!visited[next]) {
                visited[next] = true
                queue.add(next)
            }
        }
    }
    return order
}

func dfsVisit(g: Graph, u: Int64, visited: ArrayList<Bool>, order: ArrayList<Int64>): Unit {
    visited[u] = true
    order.add(u)
    for (next in g.neighbors(u)) {
        if (!visited[next]) {
            dfsVisit(g, next, visited, order)
        }
    }
}

func dfs(g: Graph, start: Int64): ArrayList<Int64> {
    let visited = ArrayList<Bool>()
    for (i in 0..g.n) {
        visited.add(false)
    }
    let order = ArrayList<Int64>()
    dfsVisit(g, start, visited, order)
    return order
}

func connectedComponents(g: Graph): Int64 {
    let visited = ArrayList<Bool>()
    for (i in 0..g.n) {
        visited.add(false)
    }
    var count = 0
    for (i in 0..g.n) {
        if (!visited[i]) {
            count = count + 1
            let order = ArrayList<Int64>()
            dfsVisit(g, i, visited, order)
        }
    }
    return count
}

func shortestUnweighted(g: Graph, start: Int64, goal: Int64): Int64 {
    let dist = ArrayList<Int64>()
    for (i in 0..g.n) {
        dist.add(-1)
    }
    let queue = ArrayList<Int64>()
    queue.add(start)
    dist[start] = 0
    while (!(queue.isEmpty())) {
        let cur = queue[0]
        queue.remove(at: 0)
        for (next in g.neighbors(cur)) {
            if (dist[next] < 0) {
                dist[next] = dist[cur] + 1
                queue.add(next)
            }
        }
    }
    return dist[goal]
}

class Edge <: ToString {
    let to: Int64
    let weight: Int64
    init(to: Int64, weight: Int64) {
        this.to = to
        this.weight = weight
    }
    public func toString(): String {
        return "Edge(to=${this.to}, weight=${this.weight})"
    }
}

class WeightedGraph {
    let n: Int64
    init(n: Int64) {
        this.n = n
        for (i in 0..n) {
            adj[i] = ArrayList<Edge>()
        }
    }
    let adj = HashMap<Int64, ArrayList<Edge>>()
    func addEdge(u: Int64, v: Int64, w: Int64) {
        adj.get(u)?.add(Edge(v, w))
        adj.get(v)?.add(Edge(u, w))
    }
    func edgesFrom(u: Int64): ArrayList<Edge> {
        return adj.get(u) ?? ArrayList<Edge>()
    }
}

func dijkstra(g: WeightedGraph, start: Int64): ArrayList<Int64> {
    let dist = ArrayList<Int64>()
    let done = ArrayList<Bool>()
    for (i in 0..g.n) {
        dist.add(1000000)
        done.add(false)
    }
    dist[start] = 0
    for (iter in 0..g.n) {
        var best = -1
        var bestDist = 1000000
        for (i in 0..g.n) {
            if (!done[i] && (dist[i] < bestDist)) {
                bestDist = dist[i]
                best = i
            }
        }
        if (best < 0) {
            break
        }
        done[best] = true
        for (e in g.edgesFrom(best)) {
            let nd = dist[best] + e.weight
            if (nd < dist[e.to]) {
                dist[e.to] = nd
            }
        }
    }
    return dist
}

class UnionFind {
    let n: Int64
    init(n: Int64) {
        this.n = n
        for (i in 0..n) {
            parent.add(i)
            rank.add(0)
        }
    }
    let parent = ArrayList<Int64>()
    let rank = ArrayList<Int64>()
    func find(x: Int64): Int64 {
        var root = x
        while (parent[root] != root) {
            root = parent[root]
        }
        var cur = x
        while (parent[cur] != root) {
            let next = parent[cur]
            parent[cur] = root
            cur = next
        }
        return root
    }
    func union(a: Int64, b: Int64): Bool {
        let ra = find(a)
        let rb = find(b)
        if (ra == rb) {
            return false
        }
        if (rank[ra] < rank[rb]) {
            parent[ra] = rb
        } else if (rank[ra] > rank[rb]) {
            parent[rb] = ra
        } else {
            parent[rb] = ra
            rank[ra] = rank[ra] + 1
        }
        return true
    }
    func groups(): Int64 {
        var count = 0
        for (i in 0..n) {
            if (find(i) == i) {
                count = count + 1
            }
        }
        return count
    }
}

class WEdge <: ToString {
    let u: Int64
    let v: Int64
    let w: Int64
    init(u: Int64, v: Int64, w: Int64) {
        this.u = u
        this.v = v
        this.w = w
    }
    public func toString(): String {
        return "WEdge(u=${this.u}, v=${this.v}, w=${this.w})"
    }
}

func kruskal(n: Int64, edges: ArrayList<WEdge>): Int64 {
    let sorted = ({ => let _s = collectArrayList(edges.iterator()); sort(_s, key: { it => it.w }, stable: true); _s })()
    let uf = UnionFind(n)
    var total = 0
    var used = 0
    for (e in sorted) {
        if (uf.union(e.u, e.v)) {
            total = total + e.w
            used = used + 1
        }
    }
    if (used < (n - 1)) {
        return -1
    }
    return total
}

class DiGraph {
    let n: Int64
    init(n: Int64) {
        this.n = n
        for (i in 0..n) {
            adj[i] = ArrayList<Int64>()
            indeg.add(0)
        }
    }
    let adj = HashMap<Int64, ArrayList<Int64>>()
    let indeg = ArrayList<Int64>()
    func addEdge(u: Int64, v: Int64) {
        adj.get(u)?.add(v)
        indeg[v] = indeg[v] + 1
    }
    func successors(u: Int64): ArrayList<Int64> {
        return adj.get(u) ?? ArrayList<Int64>()
    }
}

func topoSort(g: DiGraph): ArrayList<Int64> {
    let degree = ArrayList<Int64>()
    for (i in 0..g.n) {
        degree.add(g.indeg[i])
    }
    let queue = ArrayList<Int64>()
    for (i in 0..g.n) {
        if (degree[i] == 0) {
            queue.add(i)
        }
    }
    let order = ArrayList<Int64>()
    var head = 0
    while (head < queue.size) {
        let u = queue[head]
        head = head + 1
        order.add(u)
        for (v in g.successors(u)) {
            degree[v] = degree[v] - 1
            if (degree[v] == 0) {
                queue.add(v)
            }
        }
    }
    return order
}

@Derive[Equatable]
enum Mark <: ToString {
    | UNSEEN | ACTIVE | DONE
    public func toString(): String {
    return match (this) {
                case UNSEEN => "UNSEEN"
            case ACTIVE => "ACTIVE"
            case DONE => "DONE"
}
    }
}

func hasCycleDirected(g: DiGraph): Bool {
    let mark = ArrayList<Mark>()
    for (i in 0..g.n) {
        mark.add(Mark.UNSEEN)
    }
    let stack = ArrayList<Int64>()
    for (start in 0..g.n) {
        if (mark[start] != Mark.UNSEEN) {
            continue
        }
        stack.add(start)
        while (!(stack.isEmpty())) {
            let u = stack[stack.size - 1]
            if (mark[u] == Mark.UNSEEN) {
                mark[u] = Mark.ACTIVE
            }
            var pushed = false
            for (v in g.successors(u)) {
                if (mark[v] == Mark.ACTIVE) {
                    return true
                }
                if (mark[v] == Mark.UNSEEN) {
                    stack.add(v)
                    pushed = true
                }
            }
            if (!pushed) {
                mark[u] = Mark.DONE
                stack.remove(at: stack.size - 1)
            }
        }
    }
    return false
}

main() {
    println("=== Build Graph ===")
    let g = Graph(8)
    g.addEdge(0, 1)
    g.addEdge(0, 2)
    g.addEdge(1, 3)
    g.addEdge(2, 3)
    g.addEdge(3, 4)
    g.addEdge(5, 6)
    g.addEdge(6, 7)
    println("Nodes: ${g.n}")
    println("Edges: ${g.edgeCount()}")
    println("=== Degrees ===")
    for (i in 0..g.n) {
        println("node ${i}: degree ${g.degree(i)}")
    }
    println("=== BFS from 0 ===")
    let bfsOrder = bfs(g, 0)
    println(String.join(collectArray<String>(bfsOrder.iterator().map({e => e.toString()})), delimiter: " -> "))
    println("=== DFS from 0 ===")
    let dfsOrder = dfs(g, 0)
    println(String.join(collectArray<String>(dfsOrder.iterator().map({e => e.toString()})), delimiter: " -> "))
    println("=== Connected Components ===")
    println("Count: ${connectedComponents(g)}")
    println("=== Shortest (unweighted) ===")
    for (target in ArrayList([3, 4, 7])) {
        let d = shortestUnweighted(g, 0, target)
        if (d >= 0) {
            println("0 -> ${target}: ${d} hops")
        } else {
            println("0 -> ${target}: unreachable")
        }
    }
    println("=== Neighbor Lists ===")
    for (i in 0..g.n) {
        let ns = g.neighbors(i)
        println("${i}: ${String.join(collectArray<String>(ns.iterator().map({e => e.toString()})), delimiter: ", ")}")
    }
    println("=== Degree Histogram ===")
    let degHist = HashMap<Int64, Int64>()
    for (i in 0..g.n) {
        let d = g.degree(i)
        degHist[d] = (degHist.get(d) ?? 0) + 1
    }
    for (deg in 0..=4) {
        let c = degHist.get(deg) ?? 0
        if (c > 0) {
            println("degree ${deg}: ${("*" * c)} (${c})")
        }
    }
    println("=== Weighted Graph ===")
    let wg = WeightedGraph(6)
    wg.addEdge(0, 1, 7)
    wg.addEdge(0, 2, 9)
    wg.addEdge(0, 5, 14)
    wg.addEdge(1, 2, 10)
    wg.addEdge(1, 3, 15)
    wg.addEdge(2, 3, 11)
    wg.addEdge(2, 5, 2)
    wg.addEdge(3, 4, 6)
    wg.addEdge(4, 5, 9)
    let dist = dijkstra(wg, 0)
    for (i in 0..wg.n) {
        println("dist[0][${i}] = ${dist[i]}")
    }
    println("=== Path Costs Sorted ===")
    let costs = ArrayList<Int64>()
    for (i in 1..wg.n) {
        costs.add(dist[i])
    }
    println("Sorted: ${String.join(collectArray<String>(({ => let _s = collectArrayList(costs.iterator()); sort(_s, stable: true); _s })().iterator().map({e => e.toString()})), delimiter: ", ")}")
    println("Max cost: ${costs.iterator().reduce({a, b => if (a > b) { a } else { b }}) ?? 0}")
    println("Total: ${costs.iterator().fold<Int64>(0, {acc, x => acc + x})}")
    println("=== Reachability Matrix ===")
    for (i in 0..g.n) {
        let row = ArrayList<String>()
        for (j in 0..g.n) {
            let d = shortestUnweighted(g, i, j)
            if (d >= 0) {
                row.add("1")
            } else {
                row.add("0")
            }
        }
        println(String.join(collectArray<String>(row.iterator().map({e => e.toString()})), delimiter: ""))
    }
    println("=== Even-degree nodes ===")
    let evenDeg = ArrayList<Int64>()
    for (i in 0..g.n) {
        if ((g.degree(i) % 2) == 0) {
            evenDeg.add(i)
        }
    }
    println("Nodes: ${String.join(collectArray<String>(evenDeg.iterator().map({e => e.toString()})), delimiter: ", ")}")
    println("Count: ${evenDeg.size}")
    println("=== Triangle Count ===")
    var triangles = 0
    for (a in 0..g.n) {
        for (b in g.neighbors(a)) {
            for (c in g.neighbors(b)) {
                if (c != a) {
                    for (d in g.neighbors(c)) {
                        if (d == a) {
                            triangles = triangles + 1
                        }
                    }
                }
            }
        }
    }
    println("Triangle paths (x6): ${triangles}")
    println("=== Minimum Spanning Tree (Kruskal) ===")
    let mstEdges = ArrayList<WEdge>()
    mstEdges.add(WEdge(0, 1, 4))
    mstEdges.add(WEdge(0, 2, 1))
    mstEdges.add(WEdge(1, 2, 2))
    mstEdges.add(WEdge(1, 3, 5))
    mstEdges.add(WEdge(2, 3, 8))
    mstEdges.add(WEdge(2, 4, 10))
    mstEdges.add(WEdge(3, 4, 3))
    let mstCost = kruskal(5, mstEdges)
    println("MST total weight: ${mstCost}")
    let uf = UnionFind(5)
    uf.union(0, 1)
    uf.union(2, 3)
    println("Groups after 2 unions: ${uf.groups()}")
    uf.union(1, 2)
    println("Groups after 3 unions: ${uf.groups()}")
    println("=== Topological Sort ===")
    let dag = DiGraph(6)
    dag.addEdge(5, 2)
    dag.addEdge(5, 0)
    dag.addEdge(4, 0)
    dag.addEdge(4, 1)
    dag.addEdge(2, 3)
    dag.addEdge(3, 1)
    let topo = topoSort(dag)
    println("Order: ${String.join(collectArray<String>(topo.iterator().map({e => e.toString()})), delimiter: " -> ")}")
    println("Has cycle: ${hasCycleDirected(dag)}")
    println("=== Cyclic Directed Graph ===")
    let cyclic = DiGraph(3)
    cyclic.addEdge(0, 1)
    cyclic.addEdge(1, 2)
    cyclic.addEdge(2, 0)
    println("Has cycle: ${hasCycleDirected(cyclic)}")
    let topo2 = topoSort(cyclic)
    println("Topo size (partial if cyclic): ${topo2.size}")
    println("=== Indegree Report ===")
    for (i in 0..dag.n) {
        println("node ${i}: indegree ${dag.indeg[i]}, out ${dag.successors(i).size}")
    }
}
