// Dijkstra's shortest path (simple version with adjacency list)
class Edge(val to: Int, val weight: Int)

fun dijkstra(adj: ArrayList<ArrayList<Edge>>, source: Int): ArrayList<Int> {
    val n = adj.size
    val dist = ArrayList<Int>()
    val visited = ArrayList<Boolean>()
    for (i in 0 until n) {
        dist.add(999999)
        visited.add(false)
    }
    dist[source] = 0

    for (iter in 0 until n) {
        // Find unvisited node with minimum distance
        var u = -1
        var minDist = 999999
        for (i in 0 until n) {
            if (!visited[i] && dist[i] < minDist) {
                minDist = dist[i]
                u = i
            }
        }
        if (u == -1) break
        visited[u] = true
        for (edge in adj[u]) {
            val newDist = dist[u] + edge.weight
            if (newDist < dist[edge.to]) {
                dist[edge.to] = newDist
            }
        }
    }
    return dist
}

fun main() {
    val adj = ArrayList<ArrayList<Edge>>()
    for (i in 0..4) {
        adj.add(ArrayList<Edge>())
    }
    adj[0].add(Edge(1, 4))
    adj[0].add(Edge(2, 1))
    adj[1].add(Edge(3, 1))
    adj[2].add(Edge(1, 2))
    adj[2].add(Edge(3, 5))
    adj[3].add(Edge(4, 3))

    val dist = dijkstra(adj, 0)
    for (i in 0 until dist.size) {
        println("Dist 0->$i = ${dist[i]}")
    }
}
