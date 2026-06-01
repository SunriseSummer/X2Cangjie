// ~500-line real-world style program: a small graph algorithms toolkit.
// Adjacency-list graph with BFS, DFS, connected components, cycle detection,
// degree statistics, and a tiny weighted shortest-path (Dijkstra-lite).

class Graph(val n: Int) {
    val adj = HashMap<Int, ArrayList<Int>>()

    init {
        for (i in 0 until n) {
            adj[i] = ArrayList<Int>()
        }
    }

    fun addEdge(u: Int, v: Int) {
        adj[u]?.add(v)
        adj[v]?.add(u)
    }

    fun addDirected(u: Int, v: Int) {
        adj[u]?.add(v)
    }

    fun neighbors(u: Int): List<Int> {
        return adj[u] ?: ArrayList<Int>()
    }

    fun degree(u: Int): Int {
        return neighbors(u).size
    }

    fun edgeCount(): Int {
        var total = 0
        for (i in 0 until n) {
            total = total + degree(i)
        }
        return total / 2
    }
}

fun bfs(g: Graph, start: Int): List<Int> {
    val visited = ArrayList<Boolean>()
    for (i in 0 until g.n) {
        visited.add(false)
    }
    val order = ArrayList<Int>()
    val queue = ArrayList<Int>()
    queue.add(start)
    visited[start] = true
    while (queue.isNotEmpty()) {
        val cur = queue[0]
        queue.removeAt(0)
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

fun dfsVisit(g: Graph, u: Int, visited: ArrayList<Boolean>, order: ArrayList<Int>) {
    visited[u] = true
    order.add(u)
    for (next in g.neighbors(u)) {
        if (!visited[next]) {
            dfsVisit(g, next, visited, order)
        }
    }
}

fun dfs(g: Graph, start: Int): List<Int> {
    val visited = ArrayList<Boolean>()
    for (i in 0 until g.n) {
        visited.add(false)
    }
    val order = ArrayList<Int>()
    dfsVisit(g, start, visited, order)
    return order
}

fun connectedComponents(g: Graph): Int {
    val visited = ArrayList<Boolean>()
    for (i in 0 until g.n) {
        visited.add(false)
    }
    var count = 0
    for (i in 0 until g.n) {
        if (!visited[i]) {
            count = count + 1
            val order = ArrayList<Int>()
            dfsVisit(g, i, visited, order)
        }
    }
    return count
}

fun shortestUnweighted(g: Graph, start: Int, goal: Int): Int {
    val dist = ArrayList<Int>()
    for (i in 0 until g.n) {
        dist.add(-1)
    }
    val queue = ArrayList<Int>()
    queue.add(start)
    dist[start] = 0
    while (queue.isNotEmpty()) {
        val cur = queue[0]
        queue.removeAt(0)
        for (next in g.neighbors(cur)) {
            if (dist[next] < 0) {
                dist[next] = dist[cur] + 1
                queue.add(next)
            }
        }
    }
    return dist[goal]
}

// ---- weighted graph for Dijkstra-lite ----

data class Edge(val to: Int, val weight: Int)

class WeightedGraph(val n: Int) {
    val adj = HashMap<Int, ArrayList<Edge>>()

    init {
        for (i in 0 until n) {
            adj[i] = ArrayList<Edge>()
        }
    }

    fun addEdge(u: Int, v: Int, w: Int) {
        adj[u]?.add(Edge(v, w))
        adj[v]?.add(Edge(u, w))
    }

    fun edgesFrom(u: Int): List<Edge> {
        return adj[u] ?: ArrayList<Edge>()
    }
}

fun dijkstra(g: WeightedGraph, start: Int): List<Int> {
    val dist = ArrayList<Int>()
    val done = ArrayList<Boolean>()
    for (i in 0 until g.n) {
        dist.add(1000000)
        done.add(false)
    }
    dist[start] = 0
    for (iter in 0 until g.n) {
        var best = -1
        var bestDist = 1000000
        for (i in 0 until g.n) {
            if (!done[i] && dist[i] < bestDist) {
                bestDist = dist[i]
                best = i
            }
        }
        if (best < 0) {
            break
        }
        done[best] = true
        for (e in g.edgesFrom(best)) {
            val nd = dist[best] + e.weight
            if (nd < dist[e.to]) {
                dist[e.to] = nd
            }
        }
    }
    return dist
}

// ---- union-find (disjoint set) for Kruskal MST ----

class UnionFind(val n: Int) {
    val parent = ArrayList<Int>()
    val rank = ArrayList<Int>()

    init {
        for (i in 0 until n) {
            parent.add(i)
            rank.add(0)
        }
    }

    fun find(x: Int): Int {
        var root = x
        while (parent[root] != root) {
            root = parent[root]
        }
        var cur = x
        while (parent[cur] != root) {
            val next = parent[cur]
            parent[cur] = root
            cur = next
        }
        return root
    }

    fun union(a: Int, b: Int): Boolean {
        val ra = find(a)
        val rb = find(b)
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

    fun groups(): Int {
        var count = 0
        for (i in 0 until n) {
            if (find(i) == i) {
                count = count + 1
            }
        }
        return count
    }
}

data class WEdge(val u: Int, val v: Int, val w: Int)

fun kruskal(n: Int, edges: List<WEdge>): Int {
    val sorted = edges.sortedBy { it.w }
    val uf = UnionFind(n)
    var total = 0
    var used = 0
    for (e in sorted) {
        if (uf.union(e.u, e.v)) {
            total = total + e.w
            used = used + 1
        }
    }
    if (used < n - 1) {
        return -1
    }
    return total
}

// ---- directed graph + topological sort (Kahn) ----

class DiGraph(val n: Int) {
    val adj = HashMap<Int, ArrayList<Int>>()
    val indeg = ArrayList<Int>()

    init {
        for (i in 0 until n) {
            adj[i] = ArrayList<Int>()
            indeg.add(0)
        }
    }

    fun addEdge(u: Int, v: Int) {
        adj[u]?.add(v)
        indeg[v] = indeg[v] + 1
    }

    fun successors(u: Int): List<Int> {
        return adj[u] ?: ArrayList<Int>()
    }
}

fun topoSort(g: DiGraph): List<Int> {
    val degree = ArrayList<Int>()
    for (i in 0 until g.n) {
        degree.add(g.indeg[i])
    }
    val queue = ArrayList<Int>()
    for (i in 0 until g.n) {
        if (degree[i] == 0) {
            queue.add(i)
        }
    }
    val order = ArrayList<Int>()
    var head = 0
    while (head < queue.size) {
        val u = queue[head]
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

enum class Mark { UNSEEN, ACTIVE, DONE }

fun hasCycleDirected(g: DiGraph): Boolean {
    val mark = ArrayList<Mark>()
    for (i in 0 until g.n) {
        mark.add(Mark.UNSEEN)
    }
    val stack = ArrayList<Int>()
    for (start in 0 until g.n) {
        if (mark[start] != Mark.UNSEEN) {
            continue
        }
        stack.add(start)
        while (stack.isNotEmpty()) {
            val u = stack[stack.size - 1]
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
                stack.removeAt(stack.size - 1)
            }
        }
    }
    return false
}

fun main() {
    println("=== Build Graph ===")
    val g = Graph(8)
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
    for (i in 0 until g.n) {
        println("node $i: degree ${g.degree(i)}")
    }

    println("=== BFS from 0 ===")
    val bfsOrder = bfs(g, 0)
    println(bfsOrder.joinToString(" -> "))

    println("=== DFS from 0 ===")
    val dfsOrder = dfs(g, 0)
    println(dfsOrder.joinToString(" -> "))

    println("=== Connected Components ===")
    println("Count: ${connectedComponents(g)}")

    println("=== Shortest (unweighted) ===")
    for (target in listOf(3, 4, 7)) {
        val d = shortestUnweighted(g, 0, target)
        if (d >= 0) {
            println("0 -> $target: $d hops")
        } else {
            println("0 -> $target: unreachable")
        }
    }

    println("=== Neighbor Lists ===")
    for (i in 0 until g.n) {
        val ns = g.neighbors(i)
        println("$i: ${ns.joinToString(", ")}")
    }

    println("=== Degree Histogram ===")
    val degHist = HashMap<Int, Int>()
    for (i in 0 until g.n) {
        val d = g.degree(i)
        degHist[d] = (degHist[d] ?: 0) + 1
    }
    for (deg in 0..4) {
        val c = degHist[deg] ?: 0
        if (c > 0) {
            println("degree $deg: ${"*".repeat(c)} ($c)")
        }
    }

    println("=== Weighted Graph ===")
    val wg = WeightedGraph(6)
    wg.addEdge(0, 1, 7)
    wg.addEdge(0, 2, 9)
    wg.addEdge(0, 5, 14)
    wg.addEdge(1, 2, 10)
    wg.addEdge(1, 3, 15)
    wg.addEdge(2, 3, 11)
    wg.addEdge(2, 5, 2)
    wg.addEdge(3, 4, 6)
    wg.addEdge(4, 5, 9)
    val dist = dijkstra(wg, 0)
    for (i in 0 until wg.n) {
        println("dist[0][$i] = ${dist[i]}")
    }

    println("=== Path Costs Sorted ===")
    val costs = ArrayList<Int>()
    for (i in 1 until wg.n) {
        costs.add(dist[i])
    }
    println("Sorted: ${costs.sorted().joinToString(", ")}")
    println("Max cost: ${costs.maxOrNull() ?: 0}")
    println("Total: ${costs.sum()}")

    println("=== Reachability Matrix ===")
    for (i in 0 until g.n) {
        val row = ArrayList<String>()
        for (j in 0 until g.n) {
            val d = shortestUnweighted(g, i, j)
            if (d >= 0) {
                row.add("1")
            } else {
                row.add("0")
            }
        }
        println(row.joinToString(""))
    }

    println("=== Even-degree nodes ===")
    val evenDeg = ArrayList<Int>()
    for (i in 0 until g.n) {
        if (g.degree(i) % 2 == 0) {
            evenDeg.add(i)
        }
    }
    println("Nodes: ${evenDeg.joinToString(", ")}")
    println("Count: ${evenDeg.size}")

    println("=== Triangle Count ===")
    var triangles = 0
    for (a in 0 until g.n) {
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
    println("Triangle paths (x6): $triangles")

    println("=== Minimum Spanning Tree (Kruskal) ===")
    val mstEdges = ArrayList<WEdge>()
    mstEdges.add(WEdge(0, 1, 4))
    mstEdges.add(WEdge(0, 2, 1))
    mstEdges.add(WEdge(1, 2, 2))
    mstEdges.add(WEdge(1, 3, 5))
    mstEdges.add(WEdge(2, 3, 8))
    mstEdges.add(WEdge(2, 4, 10))
    mstEdges.add(WEdge(3, 4, 3))
    val mstCost = kruskal(5, mstEdges)
    println("MST total weight: $mstCost")
    val uf = UnionFind(5)
    uf.union(0, 1)
    uf.union(2, 3)
    println("Groups after 2 unions: ${uf.groups()}")
    uf.union(1, 2)
    println("Groups after 3 unions: ${uf.groups()}")

    println("=== Topological Sort ===")
    val dag = DiGraph(6)
    dag.addEdge(5, 2)
    dag.addEdge(5, 0)
    dag.addEdge(4, 0)
    dag.addEdge(4, 1)
    dag.addEdge(2, 3)
    dag.addEdge(3, 1)
    val topo = topoSort(dag)
    println("Order: ${topo.joinToString(" -> ")}")
    println("Has cycle: ${hasCycleDirected(dag)}")

    println("=== Cyclic Directed Graph ===")
    val cyclic = DiGraph(3)
    cyclic.addEdge(0, 1)
    cyclic.addEdge(1, 2)
    cyclic.addEdge(2, 0)
    println("Has cycle: ${hasCycleDirected(cyclic)}")
    val topo2 = topoSort(cyclic)
    println("Topo size (partial if cyclic): ${topo2.size}")

    println("=== Indegree Report ===")
    for (i in 0 until dag.n) {
        println("node $i: indegree ${dag.indeg[i]}, out ${dag.successors(i).size}")
    }
}
