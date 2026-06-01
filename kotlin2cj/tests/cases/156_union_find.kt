// Union-Find (Disjoint Set Union) data structure
class UnionFind(val n: Int) {
    val parent = ArrayList<Int>()
    val rank = ArrayList<Int>()
    var components: Int

    init {
        components = n
        for (i in 0 until n) {
            parent.add(i)
            rank.add(0)
        }
    }

    fun find(x: Int): Int {
        var root = x
        while (parent[root] != root) {
            root = parent[root]
        }
        // Path compression
        var curr = x
        while (curr != root) {
            val next = parent[curr]
            parent[curr] = root
            curr = next
        }
        return root
    }

    fun union(x: Int, y: Int): Boolean {
        val rootX = find(x)
        val rootY = find(y)
        if (rootX == rootY) return false

        if (rank[rootX] < rank[rootY]) {
            parent[rootX] = rootY
        } else if (rank[rootX] > rank[rootY]) {
            parent[rootY] = rootX
        } else {
            parent[rootY] = rootX
            rank[rootX] = rank[rootX] + 1
        }
        components--
        return true
    }

    fun connected(x: Int, y: Int): Boolean = find(x) == find(y)
}

fun main() {
    val uf = UnionFind(6)
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

    // All in one component
    println("4-1 connected: ${uf.connected(4, 1)}")
}
