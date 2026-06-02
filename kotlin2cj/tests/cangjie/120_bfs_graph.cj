import std.collection.*

func bfs(adj: ArrayList<ArrayList<Int64>>, start: Int64): ArrayList<Int64> {
    let visited = ArrayList<Bool>()
    for (i in 0..adj.size) {
        visited.add(false)
    }
    let queue = ArrayList<Int64>()
    let order = ArrayList<Int64>()
    visited[start] = true
    queue.add(start)
    while (!(queue.isEmpty())) {
        let node = queue.remove(at: 0)
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

main() {
    let adj = ArrayList<ArrayList<Int64>>()
    for (i in 0..=4) {
        adj.add(ArrayList<Int64>())
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
    let order = bfs(adj, 0)
    let parts = ArrayList<String>()
    for (v in order) {
        parts.add(v.toString())
    }
    println("BFS from 0: ${String.join(collectArray<String>(parts.iterator().map({e => e.toString()})), delimiter: " -> ")}")
}
