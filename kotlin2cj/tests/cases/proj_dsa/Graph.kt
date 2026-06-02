class Graph {
    private val adjacency = HashMap<String, ArrayList<String>>()
    private var edgeCount: Int = 0

    fun addVertex(vertex: String): Boolean {
        if (adjacency.containsKey(vertex)) {
            return false
        }
        adjacency[vertex] = ArrayList<String>()
        return true
    }

    fun addEdge(first: String, second: String): Boolean {
        addVertex(first)
        addVertex(second)

        val firstNeighbors = adjacency[first]!!
        val secondNeighbors = adjacency[second]!!

        if (firstNeighbors.contains(second)) {
            return false
        }

        firstNeighbors.add(second)
        secondNeighbors.add(first)
        edgeCount++
        return true
    }

    fun removeEdge(first: String, second: String): Boolean {
        if (!adjacency.containsKey(first) || !adjacency.containsKey(second)) {
            return false
        }

        val firstList = adjacency[first]!!
        val secondList = adjacency[second]!!
        val idx1 = firstList.indexOf(second)
        val idx2 = secondList.indexOf(first)
        if (idx1 >= 0 && idx2 >= 0) {
            firstList.removeAt(idx1)
            secondList.removeAt(idx2)
            edgeCount--
            return true
        }
        return false
    }

    fun removeVertex(vertex: String): Boolean {
        val neighbors = adjacency[vertex] ?: return false
        val copy = ArrayList<String>()
        for (neighbor in neighbors) {
            copy.add(neighbor)
        }
        for (neighbor in copy) {
            removeEdge(vertex, neighbor)
        }
        adjacency.remove(vertex)
        return true
    }

    fun containsVertex(vertex: String): Boolean {
        return adjacency.containsKey(vertex)
    }

    fun containsEdge(first: String, second: String): Boolean {
        return adjacency[first]?.contains(second) ?: false
    }

    fun neighbors(vertex: String): ArrayList<String> {
        val result = ArrayList<String>()
        val source = adjacency[vertex] ?: return result
        for (neighbor in source) {
            result.add(neighbor)
        }
        return result
    }

    fun vertexCount(): Int {
        return adjacency.size
    }

    fun getEdgeCount(): Int {
        return edgeCount
    }

    fun degree(vertex: String): Int {
        return adjacency[vertex]?.size ?: 0
    }

    fun vertices(): ArrayList<String> {
        val result = ArrayList<String>()
        for (key in adjacency.keys) {
            result.add(key)
        }
        return result
    }

    fun bfs(start: String): ArrayList<String> {
        val order = ArrayList<String>()
        if (!adjacency.containsKey(start)) {
            return order
        }

        val visited = HashSet<String>()
        val queue = Queue<String>()
        visited.add(start)
        queue.enqueue(start)

        while (!queue.isEmpty()) {
            val vertex = queue.dequeue()!!
            order.add(vertex)
            val neighbors = adjacency[vertex]!!
            for (neighbor in neighbors) {
                if (!visited.contains(neighbor)) {
                    visited.add(neighbor)
                    queue.enqueue(neighbor)
                }
            }
        }

        return order
    }

    fun dfs(start: String): ArrayList<String> {
        val order = ArrayList<String>()
        if (!adjacency.containsKey(start)) {
            return order
        }

        val visited = HashSet<String>()
        dfsVisit(start, visited, order)
        return order
    }

    private fun dfsVisit(vertex: String, visited: HashSet<String>, order: ArrayList<String>) {
        visited.add(vertex)
        order.add(vertex)
        val neighbors = adjacency[vertex]!!
        for (neighbor in neighbors) {
            if (!visited.contains(neighbor)) {
                dfsVisit(neighbor, visited, order)
            }
        }
    }

    fun hasPath(start: String, end: String): Boolean {
        if (!adjacency.containsKey(start) || !adjacency.containsKey(end)) {
            return false
        }
        val visited = HashSet<String>()
        return hasPathVisit(start, end, visited)
    }

    private fun hasPathVisit(current: String, end: String, visited: HashSet<String>): Boolean {
        if (current == end) {
            return true
        }
        visited.add(current)
        val neighbors = adjacency[current]!!
        for (neighbor in neighbors) {
            if (!visited.contains(neighbor) && hasPathVisit(neighbor, end, visited)) {
                return true
            }
        }
        return false
    }

    fun shortestPath(start: String, end: String): ArrayList<String> {
        val path = ArrayList<String>()
        if (!adjacency.containsKey(start) || !adjacency.containsKey(end)) {
            return path
        }

        val queue = Queue<String>()
        val visited = HashSet<String>()
        val parent = HashMap<String, String>()

        queue.enqueue(start)
        visited.add(start)
        parent[start] = ""

        while (!queue.isEmpty()) {
            val current = queue.dequeue()!!
            if (current == end) {
                break
            }
            val neighbors = adjacency[current]!!
            for (neighbor in neighbors) {
                if (!visited.contains(neighbor)) {
                    visited.add(neighbor)
                    parent[neighbor] = current
                    queue.enqueue(neighbor)
                }
            }
        }

        if (!visited.contains(end)) {
            return path
        }

        val reversed = ArrayList<String>()
        var current = end
        while (current != "") {
            reversed.add(current)
            current = parent[current] ?: ""
        }

        var index = reversed.size - 1
        while (index >= 0) {
            path.add(reversed[index])
            index--
        }
        return path
    }

    override fun toString(): String {
        val builder = StringBuilder()
        val orderedVertices = vertices().sorted()
        var index = 0
        while (index < orderedVertices.size) {
            val vertex = orderedVertices[index]
            builder.append(vertex)
            builder.append(" -> ")
            builder.append(adjacency[vertex])
            if (index < orderedVertices.size - 1) {
                builder.append("\n")
            }
            index++
        }
        return builder.toString()
    }
}
