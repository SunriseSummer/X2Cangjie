import std.collection.*

func dfs(adj: ArrayList<ArrayList<Int64>>, start: Int64): ArrayList<Int64> {
    let visited = ArrayList<Bool>()
    for (i in 0..adj.size) {
        visited.add(false)
    }
    let stack = ArrayList<Int64>()
    let order = ArrayList<Int64>()
    stack.add(start)
    while (!(stack.isEmpty())) {
        let node = stack.remove(at: stack.size - 1)
        if (visited[node]) {
            continue
        }
        visited[node] = true
        order.add(node)
        let neighbors = adj[node]
        for (i in (neighbors.size - 1)..=0 : -1) {
            if (!visited[neighbors[i]]) {
                stack.add(neighbors[i])
            }
        }
    }
    return order
}

main() {
    let adj = ArrayList<ArrayList<Int64>>()
    for (i in 0..=5) {
        adj.add(ArrayList<Int64>())
    }
    adj[0].add(1)
    adj[0].add(2)
    adj[1].add(3)
    adj[1].add(4)
    adj[2].add(5)
    let order = dfs(adj, 0)
    let parts = ArrayList<String>()
    for (v in order) {
        parts.add(v.toString())
    }
    println("DFS from 0: ${String.join(collectArray<String>(parts.iterator().map({e => e.toString()})), delimiter: " -> ")}")
}
