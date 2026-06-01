// DFS on adjacency list graph (iterative)
fun dfs(adj: ArrayList<ArrayList<Int>>, start: Int): ArrayList<Int> {
    val visited = ArrayList<Boolean>()
    for (i in 0 until adj.size) {
        visited.add(false)
    }
    val stack = ArrayList<Int>()
    val order = ArrayList<Int>()
    stack.add(start)
    while (stack.isNotEmpty()) {
        val node = stack.removeAt(stack.size - 1)
        if (visited[node]) continue
        visited[node] = true
        order.add(node)
        // Push neighbors in reverse for consistent order
        val neighbors = adj[node]
        for (i in neighbors.size - 1 downTo 0) {
            if (!visited[neighbors[i]]) {
                stack.add(neighbors[i])
            }
        }
    }
    return order
}

fun main() {
    val adj = ArrayList<ArrayList<Int>>()
    for (i in 0..5) {
        adj.add(ArrayList<Int>())
    }
    adj[0].add(1)
    adj[0].add(2)
    adj[1].add(3)
    adj[1].add(4)
    adj[2].add(5)

    val order = dfs(adj, 0)
    val parts = ArrayList<String>()
    for (v in order) {
        parts.add(v.toString())
    }
    println("DFS from 0: ${parts.joinToString(" -> ")}")
}
