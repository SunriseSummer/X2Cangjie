package proj_dsa

import std.collection.*

class Graph <: ToString {
    let labels = ArrayList<String>()
    let adjacency = ArrayList<ArrayList<Int64>>()
    let vertexIndex = HashMap<String, Int64>()
    func addVertex(label: String): Bool {
        if (vertexIndex.contains(label)) {
            return false
        }
        vertexIndex[label] = labels.size
        labels.add(label)
        adjacency.add(ArrayList<Int64>())
        return true
    }
    func getIdx(label: String): Int64 {
        if (!vertexIndex.contains(label)) {
            return -1
        }
        return vertexIndex[label]
    }
    func addEdge(from: String, to: String): Bool {
        addVertex(from)
        addVertex(to)
        let fi = getIdx(from)
        let ti = getIdx(to)
        if ((fi < 0) || (ti < 0)) {
            return false
        }
        if (hasEdge(fi, ti)) {
            return false
        }
        adjacency[fi].add(ti)
        adjacency[ti].add(fi)
        return true
    }
    func hasEdge(a: Int64, b: Int64): Bool {
        for (v in adjacency[a]) {
            if (v == b) {
                return true
            }
        }
        return false
    }
    func neighbors(label: String): ArrayList<String> {
        let result = ArrayList<String>()
        let idx = getIdx(label)
        if (idx < 0) {
            return result
        }
        for (ni in adjacency[idx]) {
            result.add(labels[ni])
        }
        return result
    }
    func bfs(start: String): ArrayList<String> {
        let order = ArrayList<String>()
        let si = getIdx(start)
        if (si < 0) {
            return order
        }
        let visited = HashSet<Int64>()
        let queue = ArrayList<Int64>()
        var head = 0
        visited.add(si)
        queue.add(si)
        while (head < queue.size) {
            let curr = queue[head]
            head += 1
            order.add(labels[curr])
            for (ni in adjacency[curr]) {
                if (!visited.contains(ni)) {
                    visited.add(ni)
                    queue.add(ni)
                }
            }
        }
        return order
    }
    func dfs(start: String): ArrayList<String> {
        let order = ArrayList<String>()
        let si = getIdx(start)
        if (si < 0) {
            return order
        }
        let visited = HashSet<Int64>()
        dfsHelper(si, visited, order)
        return order
    }
    func dfsHelper(idx: Int64, visited: HashSet<Int64>, order: ArrayList<String>): Unit {
        visited.add(idx)
        order.add(labels[idx])
        for (ni in adjacency[idx]) {
            if (!visited.contains(ni)) {
                dfsHelper(ni, visited, order)
            }
        }
    }
    func vertexCount(): Int64 {
        return labels.size
    }
    public override func toString(): String {
        let builder = StringBuilder()
        var i = 0
        while (i < labels.size) {
            builder.append(labels[i])
            builder.append(" -> ")
            builder.append(neighbors(labels[i]).toString())
            if (i < (labels.size - 1)) {
                builder.append("\n")
            }
            i += 1
        }
        return builder.toString()
    }
}
