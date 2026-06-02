import std.collection.*

class Edge {
    let to: Int64
    let weight: Int64
    init(to: Int64, weight: Int64) {
        this.to = to
        this.weight = weight
    }
}

func dijkstra(adj: ArrayList<ArrayList<Edge>>, source: Int64): ArrayList<Int64> {
    let n = adj.size
    let dist = ArrayList<Int64>()
    let visited = ArrayList<Bool>()
    for (i in 0..n) {
        dist.add(999999)
        visited.add(false)
    }
    dist[source] = 0
    for (iter in 0..n) {
        var u = -1
        var minDist = 999999
        for (i in 0..n) {
            if (!visited[i] && (dist[i] < minDist)) {
                minDist = dist[i]
                u = i
            }
        }
        if (u == -1) {
            break
        }
        visited[u] = true
        for (edge in adj[u]) {
            let newDist = dist[u] + edge.weight
            if (newDist < dist[edge.to]) {
                dist[edge.to] = newDist
            }
        }
    }
    return dist
}

main() {
    let adj = ArrayList<ArrayList<Edge>>()
    for (i in 0..=4) {
        adj.add(ArrayList<Edge>())
    }
    adj[0].add(Edge(1, 4))
    adj[0].add(Edge(2, 1))
    adj[1].add(Edge(3, 1))
    adj[2].add(Edge(1, 2))
    adj[2].add(Edge(3, 5))
    adj[3].add(Edge(4, 3))
    let dist = dijkstra(adj, 0)
    for (i in 0..dist.size) {
        println("Dist 0->${i} = ${dist[i]}")
    }
}
