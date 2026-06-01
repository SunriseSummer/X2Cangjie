// BFS on adjacency list graph
fun bfs(adj: ArrayList<ArrayList<Int>>, start: Int): ArrayList<Int> {
    val visited = ArrayList<Boolean>()
    for (i in 0 until adj.size) {
        visited.add(false)
    }
    val queue = ArrayList<Int>()
    val order = ArrayList<Int>()
    visited[start] = true
    queue.add(start)
    while (queue.isNotEmpty()) {
        val node = queue.removeAt(0)
        order.add(node)
        for (neighbor in adj[node]) {
            if (!visited[neighbor]) {
                visited[neighbor] = true
                queue.add(neighbor)
            }
        }
    }
    return order
}

fun main() {
    // Graph: 0-1, 0-2, 1-3, 2-3, 3-4
    val adj = ArrayList<ArrayList<Int>>()
    for (i in 0..4) {
        adj.add(ArrayList<Int>())
    }
    adj[0].add(1)
    adj[0].add(2)
    adj[1].add(0)
    adj[1].add(3)
    adj[2].add(0)
    adj[2].add(3)
    adj[3].add(1)
    adj[3].add(2)
    adj[3].add(4)
    adj[4].add(3)

    val order = bfs(adj, 0)
    val parts = ArrayList<String>()
    for (v in order) {
        parts.add(v.toString())
    }
    println("BFS from 0: ${parts.joinToString(" -> ")}")
}
