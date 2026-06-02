class Graph {
    private val labels = ArrayList<String>()
    private val adjacency = ArrayList<ArrayList<Int>>()
    private val vertexIndex = HashMap<String, Int>()

    fun addVertex(label: String): Boolean {
        if (vertexIndex.containsKey(label)) return false
        vertexIndex[label] = labels.size
        labels.add(label)
        adjacency.add(ArrayList<Int>())
        return true
    }

    private fun getIdx(label: String): Int {
        if (!vertexIndex.containsKey(label)) return -1
        return vertexIndex[label]!!
    }

    fun addEdge(from: String, to: String): Boolean {
        addVertex(from)
        addVertex(to)
        val fi = getIdx(from)
        val ti = getIdx(to)
        if (fi < 0 || ti < 0) return false
        if (hasEdge(fi, ti)) return false
        adjacency[fi].add(ti)
        adjacency[ti].add(fi)
        return true
    }

    private fun hasEdge(a: Int, b: Int): Boolean {
        for (v in adjacency[a]) {
            if (v == b) return true
        }
        return false
    }

    fun neighbors(label: String): ArrayList<String> {
        val result = ArrayList<String>()
        val idx = getIdx(label)
        if (idx < 0) return result
        for (ni in adjacency[idx]) {
            result.add(labels[ni])
        }
        return result
    }

    fun bfs(start: String): ArrayList<String> {
        val order = ArrayList<String>()
        val si = getIdx(start)
        if (si < 0) return order
        val visited = HashSet<Int>()
        val queue = ArrayList<Int>()
        var head = 0
        visited.add(si)
        queue.add(si)
        while (head < queue.size) {
            val curr = queue[head]
            head++
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

    fun dfs(start: String): ArrayList<String> {
        val order = ArrayList<String>()
        val si = getIdx(start)
        if (si < 0) return order
        val visited = HashSet<Int>()
        dfsHelper(si, visited, order)
        return order
    }

    private fun dfsHelper(idx: Int, visited: HashSet<Int>, order: ArrayList<String>) {
        visited.add(idx)
        order.add(labels[idx])
        for (ni in adjacency[idx]) {
            if (!visited.contains(ni)) {
                dfsHelper(ni, visited, order)
            }
        }
    }

    fun vertexCount(): Int {
        return labels.size
    }

    override fun toString(): String {
        val builder = StringBuilder()
        var i = 0
        while (i < labels.size) {
            builder.append(labels[i])
            builder.append(" -> ")
            builder.append(neighbors(labels[i]).toString())
            if (i < labels.size - 1) builder.append("\n")
            i++
        }
        return builder.toString()
    }
}
