// Large #1 (iter5): topological sort with cycle detection (~200 lines)
class Graph {
    var nodes: [String] = []
    var adj: [String: [String]] = [:]

    func addNode(_ n: String) {
        for x in nodes {
            if x == n {
                return
            }
        }
        nodes.append(n)
        adj[n] = []
    }

    func addEdge(_ from: String, _ to: String) {
        addNode(from)
        addNode(to)
        var cur = adj[from] ?? []
        cur.append(to)
        adj[from] = cur
    }

    func indegree(_ n: String) -> Int {
        var c = 0
        for u in nodes {
            let succ = adj[u] ?? []
            for v in succ {
                if v == n {
                    c += 1
                }
            }
        }
        return c
    }

    // Kahn's algorithm. Returns ordered list and a flag for cycle.
    func topoSort() -> ([String], Bool) {
        var inDeg: [String: Int] = [:]
        for n in nodes {
            inDeg[n] = indegree(n)
        }
        var ready: [String] = []
        for n in nodes {
            if (inDeg[n] ?? 0) == 0 {
                ready.append(n)
            }
        }
        var order: [String] = []
        while ready.count > 0 {
            let u = ready[0]
            ready.remove(at: 0)
            order.append(u)
            let succ = adj[u] ?? []
            for v in succ {
                let d = (inDeg[v] ?? 0) - 1
                inDeg[v] = d
                if d == 0 {
                    ready.append(v)
                }
            }
        }
        let hasCycle = order.count != nodes.count
        return (order, hasCycle)
    }

    func summary() -> String {
        var s = ""
        for n in nodes {
            s = s + "\(n)->\(adj[n] ?? []) "
        }
        return s
    }
}

// Acyclic example: build pipeline
let g1 = Graph()
g1.addEdge("src", "compile")
g1.addEdge("compile", "link")
g1.addEdge("link", "package")
g1.addEdge("compile", "test")
g1.addEdge("test", "package")
g1.addEdge("package", "deploy")

print("g1: " + g1.summary())
let r1 = g1.topoSort()
print("g1 order: \(r1.0)")
print("g1 cycle: \(r1.1)")

// Acyclic, multiple roots
let g2 = Graph()
g2.addEdge("a", "c")
g2.addEdge("b", "c")
g2.addEdge("c", "d")
g2.addEdge("e", "d")
print("g2: " + g2.summary())
let r2 = g2.topoSort()
print("g2 order: \(r2.0)")
print("g2 cycle: \(r2.1)")

// Cyclic
let g3 = Graph()
g3.addEdge("x", "y")
g3.addEdge("y", "z")
g3.addEdge("z", "x")   // cycle
print("g3: " + g3.summary())
let r3 = g3.topoSort()
print("g3 order: \(r3.0)")
print("g3 cycle: \(r3.1)")

// Disconnected
let g4 = Graph()
g4.addEdge("p", "q")
g4.addEdge("r", "s")
g4.addNode("lonely")
print("g4: " + g4.summary())
let r4 = g4.topoSort()
print("g4 order: \(r4.0)")
print("g4 cycle: \(r4.1)")
print("g4 node count: \(g4.nodes.count)")
