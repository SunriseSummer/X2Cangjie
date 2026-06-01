// A* pathfinding on a grid
data class Cell(val row: Int, val col: Int)

fun heuristic(a: Cell, b: Cell): Int {
    val dr = a.row - b.row
    val dc = a.col - b.col
    return (if (dr < 0) -dr else dr) + (if (dc < 0) -dc else dc)
}

fun aStarSearch(grid: ArrayList<ArrayList<Int>>, start: Cell, goal: Cell): Int {
    val rows = grid.size
    val cols = grid[0].size

    val openSet = ArrayList<Cell>()
    val gScore = HashMap<String, Int>()
    val fScore = HashMap<String, Int>()
    val closed = HashSet<String>()

    fun key(c: Cell): String = "${c.row},${c.col}"

    gScore[key(start)] = 0
    fScore[key(start)] = heuristic(start, goal)
    openSet.add(start)

    val dr = arrayListOf(-1, 1, 0, 0)
    val dc = arrayListOf(0, 0, -1, 1)

    while (openSet.isNotEmpty()) {
        var bestIdx = 0
        for (i in 1 until openSet.size) {
            val fi = fScore.getOrDefault(key(openSet[i]), 999999)
            val fb = fScore.getOrDefault(key(openSet[bestIdx]), 999999)
            if (fi < fb) bestIdx = i
        }
        val current = openSet[bestIdx]
        openSet.removeAt(bestIdx)

        if (current.row == goal.row && current.col == goal.col) {
            return gScore.getOrDefault(key(current), -1)
        }

        closed.add(key(current))
        val currentG = gScore.getOrDefault(key(current), 999999)

        for (d in 0 until 4) {
            val nr = current.row + dr[d]
            val nc = current.col + dc[d]
            if (nr < 0 || nr >= rows || nc < 0 || nc >= cols) continue
            if (grid[nr][nc] == 1) continue
            val neighbor = Cell(nr, nc)
            val nk = key(neighbor)
            if (closed.contains(nk)) continue

            val tentativeG = currentG + 1
            val prevG = gScore.getOrDefault(nk, 999999)
            if (tentativeG < prevG) {
                gScore[nk] = tentativeG
                fScore[nk] = tentativeG + heuristic(neighbor, goal)
                var found = false
                for (o in openSet) {
                    if (o.row == nr && o.col == nc) {
                        found = true
                        break
                    }
                }
                if (!found) {
                    openSet.add(neighbor)
                }
            }
        }
    }
    return -1
}

fun main() {
    val grid = arrayListOf(
        arrayListOf(0, 0, 0, 0, 0),
        arrayListOf(0, 1, 1, 0, 0),
        arrayListOf(0, 0, 0, 0, 0),
        arrayListOf(0, 0, 1, 1, 0),
        arrayListOf(0, 0, 0, 0, 0)
    )

    val dist = aStarSearch(grid, Cell(0, 0), Cell(4, 4))
    println("Distance: $dist")

    val dist2 = aStarSearch(grid, Cell(0, 0), Cell(0, 4))
    println("Distance: $dist2")

    val blocked = arrayListOf(
        arrayListOf(0, 1),
        arrayListOf(1, 0)
    )
    val dist3 = aStarSearch(blocked, Cell(0, 0), Cell(1, 1))
    println("Distance: $dist3")
}
