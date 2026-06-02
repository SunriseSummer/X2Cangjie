import std.collection.*

class UnionFind {
    let n: Int64
    init(n: Int64) {
        this.n = n
        components = n
        for (i in 0..n) {
            parent.add(i)
            rank.add(0)
        }
    }
    let parent = ArrayList<Int64>()
    let rank = ArrayList<Int64>()
    var components: Int64
    func find(x: Int64): Int64 {
        var root = x
        while (parent[root] != root) {
            root = parent[root]
        }
        var curr = x
        while (curr != root) {
            let next = parent[curr]
            parent[curr] = root
            curr = next
        }
        return root
    }
    func union(x: Int64, y: Int64): Bool {
        let rootX = find(x)
        let rootY = find(y)
        if (rootX == rootY) {
            return false
        }
        if (rank[rootX] < rank[rootY]) {
            parent[rootX] = rootY
        } else if (rank[rootX] > rank[rootY]) {
            parent[rootY] = rootX
        } else {
            parent[rootY] = rootX
            rank[rootX] = rank[rootX] + 1
        }
        components -= 1
        return true
    }
    func connected(x: Int64, y: Int64): Bool {
        return find(x) == find(y)
    }
}

main() {
    let uf = UnionFind(6)
    println("Components: ${uf.components}")
    uf.union(0, 1)
    uf.union(2, 3)
    uf.union(4, 5)
    println("Components: ${uf.components}")
    println("0-1 connected: ${uf.connected(0, 1)}")
    println("0-2 connected: ${uf.connected(0, 2)}")
    uf.union(1, 3)
    println("Components: ${uf.components}")
    println("0-2 connected: ${uf.connected(0, 2)}")
    println("0-3 connected: ${uf.connected(0, 3)}")
    uf.union(3, 5)
    println("Components: ${uf.components}")
    println("0-5 connected: ${uf.connected(0, 5)}")
    println("4-1 connected: ${uf.connected(4, 1)}")
}
