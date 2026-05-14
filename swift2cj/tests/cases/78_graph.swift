// Large #2: graph algorithms — BFS/DFS/shortest-path (~250 lines)
class Graph {
    let n: Int
    var adj: [[Int]] = []

    init(n: Int) {
        self.n = n
        for _ in 0 ..< n {
            let empty: [Int] = []
            adj.append(empty)
        }
    }

    func addEdge(_ u: Int, _ v: Int) {
        adj[u].append(v)
        adj[v].append(u)
    }

    func degree(_ u: Int) -> Int {
        return adj[u].count
    }

    func neighbors(_ u: Int) -> [Int] {
        return adj[u]
    }
}

// A simple integer queue (FIFO) backed by ArrayList
class IntQueue {
    var buf: [Int] = []

    func push(_ x: Int) {
        buf.append(x)
    }

    func pop() -> Int {
        let x = buf[0]
        buf.remove(at: 0)
        return x
    }

    func size() -> Int {
        return buf.count
    }

    func isEmpty() -> Bool {
        return buf.count == 0
    }
}

func bfs(_ g: Graph, _ start: Int) -> [Int] {
    var dist: [Int] = []
    for _ in 0 ..< g.n {
        dist.append(-1)
    }
    dist[start] = 0
    let q = IntQueue()
    q.push(start)
    while !q.isEmpty() {
        let u = q.pop()
        for v in g.neighbors(u) {
            if dist[v] < 0 {
                dist[v] = dist[u] + 1
                q.push(v)
            }
        }
    }
    return dist
}

// recursive DFS that records the visit order
func dfsHelper(_ g: Graph, _ u: Int, _ visited: inout [Bool], _ order: inout [Int]) -> Void {
    visited[u] = true
    order.append(u)
    for v in g.neighbors(u) {
        if !visited[v] {
            dfsHelper(g, v, &visited, &order)
        }
    }
}

func dfs(_ g: Graph, _ start: Int) -> [Int] {
    var visited: [Bool] = []
    for _ in 0 ..< g.n {
        visited.append(false)
    }
    var order: [Int] = []
    dfsHelper(g, start, &visited, &order)
    return order
}

// count connected components
func components(_ g: Graph) -> Int {
    var visited: [Bool] = []
    for _ in 0 ..< g.n {
        visited.append(false)
    }
    var count = 0
    for s in 0 ..< g.n {
        if !visited[s] {
            count += 1
            var order: [Int] = []
            dfsHelper(g, s, &visited, &order)
        }
    }
    return count
}

func sumList(_ xs: [Int]) -> Int {
    var s = 0
    for x in xs {
        s += x
    }
    return s
}

func formatList(_ xs: [Int]) -> String {
    var out = "["
    var first = true
    for x in xs {
        if !first {
            out = out + ", "
        }
        out = out + "\(x)"
        first = false
    }
    out = out + "]"
    return out
}

// Build a graph:
//   0 - 1 - 2
//   |       |
//   3 ----- 4 - 5
//   6 - 7  (separate component)
//   8       (lone)
let g = Graph(n: 9)
g.addEdge(0, 1)
g.addEdge(1, 2)
g.addEdge(0, 3)
g.addEdge(2, 4)
g.addEdge(3, 4)
g.addEdge(4, 5)
g.addEdge(6, 7)

print("n = \(g.n)")
print("degree(0) = \(g.degree(0))")
print("degree(4) = \(g.degree(4))")
print("degree(8) = \(g.degree(8))")

let d = bfs(g, 0)
print("bfs dist = " + formatList(d))
print("bfs sum = \(sumList(d))")

let order = dfs(g, 0)
print("dfs order = " + formatList(order))

let cc = components(g)
print("components = \(cc)")

// More queries
let d4 = bfs(g, 4)
print("bfs from 4 = " + formatList(d4))
let d6 = bfs(g, 6)
print("bfs from 6 = " + formatList(d6))
let d8 = bfs(g, 8)
print("bfs from 8 = " + formatList(d8))
