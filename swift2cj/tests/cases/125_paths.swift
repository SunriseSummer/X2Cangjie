// Large #1 (iter8): count paths in a DAG using memoization
class Dag {
    var adj: [String: [String]] = [:]
    func addEdge(_ a: String, _ b: String) {
        var xs = adj[a] ?? []
        xs.append(b)
        adj[a] = xs
        if adj[b] == nil {
            adj[b] = []
        }
    }
    func countPaths(_ start: String, _ end: String) -> Int {
        var memo: [String: Int] = [:]
        return dfs(start, end, &memo)
    }
    func dfs(_ node: String, _ end: String, _ memo: inout [String: Int]) -> Int {
        if node == end {
            return 1
        }
        let cached = memo[node]
        if let v = cached {
            return v
        }
        var total = 0
        let xs = adj[node] ?? []
        for n in xs {
            total += dfs(n, end, &memo)
        }
        memo[node] = total
        return total
    }
    func describe() -> String {
        var s = ""
        for (k, v) in adj {
            s = s + k + "->\(v) "
        }
        return s
    }
}

let g = Dag()
g.addEdge("A", "B")
g.addEdge("A", "C")
g.addEdge("B", "D")
g.addEdge("C", "D")
g.addEdge("B", "E")
g.addEdge("D", "F")
g.addEdge("E", "F")
print("paths A->F = \(g.countPaths("A", "F"))")
print("paths B->F = \(g.countPaths("B", "F"))")
print("paths C->F = \(g.countPaths("C", "F"))")
