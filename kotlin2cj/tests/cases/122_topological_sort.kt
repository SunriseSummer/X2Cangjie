// Topological Sort (Kahn's algorithm)
fun topologicalSort(numNodes: Int, edges: ArrayList<ArrayList<Int>>): ArrayList<Int> {
    val inDegree = ArrayList<Int>()
    val adj = ArrayList<ArrayList<Int>>()
    for (i in 0 until numNodes) {
        inDegree.add(0)
        adj.add(ArrayList<Int>())
    }
    for (edge in edges) {
        adj[edge[0]].add(edge[1])
        inDegree[edge[1]] = inDegree[edge[1]] + 1
    }
    val queue = ArrayList<Int>()
    for (i in 0 until numNodes) {
        if (inDegree[i] == 0) queue.add(i)
    }
    val result = ArrayList<Int>()
    while (queue.isNotEmpty()) {
        val node = queue.removeAt(0)
        result.add(node)
        for (neighbor in adj[node]) {
            inDegree[neighbor] = inDegree[neighbor] - 1
            if (inDegree[neighbor] == 0) {
                queue.add(neighbor)
            }
        }
    }
    return result
}

fun main() {
    val edges = ArrayList<ArrayList<Int>>()
    edges.add(arrayListOf(5, 2))
    edges.add(arrayListOf(5, 0))
    edges.add(arrayListOf(4, 0))
    edges.add(arrayListOf(4, 1))
    edges.add(arrayListOf(2, 3))
    edges.add(arrayListOf(3, 1))

    val order = topologicalSort(6, edges)
    val parts = ArrayList<String>()
    for (v in order) {
        parts.add(v.toString())
    }
    println("Topological order: ${parts.joinToString(" ")}")
}
