// Graph with adjacency list: connected components, cycle detection
class Graph(val n: Int) {
    val adj = ArrayList<ArrayList<Int>>()

    init {
        for (i in 0 until n) {
            adj.add(ArrayList<Int>())
        }
    }

    fun addEdge(u: Int, v: Int) {
        adj[u].add(v)
        adj[v].add(u)
    }
}

fun connectedComponents(g: Graph): Int {
    val visited = ArrayList<Boolean>()
    for (i in 0 until g.n) visited.add(false)
    var count = 0

    for (start in 0 until g.n) {
        if (!visited[start]) {
            count++
            // BFS
            val queue = ArrayList<Int>()
            queue.add(start)
            visited[start] = true
            while (queue.isNotEmpty()) {
                val u = queue[0]
                queue.removeAt(0)
                for (v in g.adj[u]) {
                    if (!visited[v]) {
                        visited[v] = true
                        queue.add(v)
                    }
                }
            }
        }
    }
    return count
}

fun shortestPath(g: Graph, start: Int, end: Int): Int {
    if (start == end) return 0
    val dist = ArrayList<Int>()
    for (i in 0 until g.n) dist.add(-1)
    dist[start] = 0
    val queue = ArrayList<Int>()
    queue.add(start)
    while (queue.isNotEmpty()) {
        val u = queue[0]
        queue.removeAt(0)
        for (v in g.adj[u]) {
            if (dist[v] == -1) {
                dist[v] = dist[u] + 1
                if (v == end) return dist[v]
                queue.add(v)
            }
        }
    }
    return -1
}

fun main() {
    val g = Graph(7)
    g.addEdge(0, 1)
    g.addEdge(0, 2)
    g.addEdge(1, 3)
    g.addEdge(4, 5)
    // Node 6 is isolated

    println("Components: ${connectedComponents(g)}")

    // Shortest paths
    println("Path 0->3: ${shortestPath(g, 0, 3)}")
    println("Path 0->2: ${shortestPath(g, 0, 2)}")
    println("Path 0->5: ${shortestPath(g, 0, 5)}")
    println("Path 4->5: ${shortestPath(g, 4, 5)}")

    // Fully connected graph
    val g2 = Graph(4)
    g2.addEdge(0, 1)
    g2.addEdge(1, 2)
    g2.addEdge(2, 3)
    g2.addEdge(3, 0)
    println("Components2: ${connectedComponents(g2)}")
    println("Path 0->2: ${shortestPath(g2, 0, 2)}")
}
