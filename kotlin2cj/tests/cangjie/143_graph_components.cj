import std.collection.*

class Graph {
    let n: Int64
    init(n: Int64) {
        this.n = n
        for (i in 0..n) {
            adj.add(ArrayList<Int64>())
        }
    }
    let adj = ArrayList<ArrayList<Int64>>()
    func addEdge(u: Int64, v: Int64) {
        adj[u].add(v)
        adj[v].add(u)
    }
}

func connectedComponents(g: Graph): Int64 {
    let visited = ArrayList<Bool>()
    for (i in 0..g.n) {
        visited.add(false)
    }
    var count = 0
    for (start in 0..g.n) {
        if (!visited[start]) {
            count += 1
            let queue = ArrayList<Int64>()
            queue.add(start)
            visited[start] = true
            while (!(queue.isEmpty())) {
                let u = queue[0]
                queue.remove(at: 0)
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

func shortestPath(g: Graph, start: Int64, end: Int64): Int64 {
    if (start == end) {
        return 0
    }
    let dist = ArrayList<Int64>()
    for (i in 0..g.n) {
        dist.add(-1)
    }
    dist[start] = 0
    let queue = ArrayList<Int64>()
    queue.add(start)
    while (!(queue.isEmpty())) {
        let u = queue[0]
        queue.remove(at: 0)
        for (v in g.adj[u]) {
            if (dist[v] == -1) {
                dist[v] = dist[u] + 1
                if (v == end) {
                    return dist[v]
                }
                queue.add(v)
            }
        }
    }
    return -1
}

main() {
    let g = Graph(7)
    g.addEdge(0, 1)
    g.addEdge(0, 2)
    g.addEdge(1, 3)
    g.addEdge(4, 5)
    println("Components: ${connectedComponents(g)}")
    println("Path 0->3: ${shortestPath(g, 0, 3)}")
    println("Path 0->2: ${shortestPath(g, 0, 2)}")
    println("Path 0->5: ${shortestPath(g, 0, 5)}")
    println("Path 4->5: ${shortestPath(g, 4, 5)}")
    let g2 = Graph(4)
    g2.addEdge(0, 1)
    g2.addEdge(1, 2)
    g2.addEdge(2, 3)
    g2.addEdge(3, 0)
    println("Components2: ${connectedComponents(g2)}")
    println("Path 0->2: ${shortestPath(g2, 0, 2)}")
}
