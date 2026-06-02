import std.collection.*

func topologicalSort(numNodes: Int64, edges: ArrayList<ArrayList<Int64>>): ArrayList<Int64> {
    let inDegree = ArrayList<Int64>()
    let adj = ArrayList<ArrayList<Int64>>()
    for (i in 0..numNodes) {
        inDegree.add(0)
        adj.add(ArrayList<Int64>())
    }
    for (edge in edges) {
        adj[edge[0]].add(edge[1])
        inDegree[edge[1]] = inDegree[edge[1]] + 1
    }
    let queue = ArrayList<Int64>()
    for (i in 0..numNodes) {
        if (inDegree[i] == 0) {
            queue.add(i)
        }
    }
    let result = ArrayList<Int64>()
    while (!(queue.isEmpty())) {
        let node = queue.remove(at: 0)
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

main() {
    let edges = ArrayList<ArrayList<Int64>>()
    edges.add(ArrayList([5, 2]))
    edges.add(ArrayList([5, 0]))
    edges.add(ArrayList([4, 0]))
    edges.add(ArrayList([4, 1]))
    edges.add(ArrayList([2, 3]))
    edges.add(ArrayList([3, 1]))
    let order = topologicalSort(6, edges)
    let parts = ArrayList<String>()
    for (v in order) {
        parts.add(v.toString())
    }
    println("Topological order: ${String.join(collectArray<String>(parts.iterator().map({e => e.toString()})), delimiter: " ")}")
}
