import std.collection.*

class Cell <: ToString {
    let row: Int64
    let col: Int64
    init(row: Int64, col: Int64) {
        this.row = row
        this.col = col
    }
    public func toString(): String {
        return "Cell(row=${this.row}, col=${this.col})"
    }
}

func heuristic(a: Cell, b: Cell): Int64 {
    let dr = a.row - b.row
    let dc = a.col - b.col
    return if (dr < 0) {
        -dr
    } else {
        dr
    } + if (dc < 0) {
        -dc
    } else {
        dc
    }
}

func aStarSearch(grid: ArrayList<ArrayList<Int64>>, start: Cell, goal: Cell): Int64 {
    let rows = grid.size
    let cols = grid[0].size
    let openSet = ArrayList<Cell>()
    let gScore = HashMap<String, Int64>()
    let fScore = HashMap<String, Int64>()
    let closed = HashSet<String>()
    func key(c: Cell): String {
        return "${c.row},${c.col}"
    }
    gScore[key(start)] = 0
    fScore[key(start)] = heuristic(start, goal)
    openSet.add(start)
    let dr = ArrayList([-1, 1, 0, 0])
    let dc = ArrayList([0, 0, -1, 1])
    while (!(openSet.isEmpty())) {
        var bestIdx = 0
        for (i in 1..openSet.size) {
            let fi = (fScore.get(key(openSet[i])) ?? 999999)
            let fb = (fScore.get(key(openSet[bestIdx])) ?? 999999)
            if (fi < fb) {
                bestIdx = i
            }
        }
        let current = openSet[bestIdx]
        openSet.remove(at: bestIdx)
        if ((current.row == goal.row) && (current.col == goal.col)) {
            return (gScore.get(key(current)) ?? -1)
        }
        closed.add(key(current))
        let currentG = (gScore.get(key(current)) ?? 999999)
        for (d in 0..4) {
            let nr = current.row + dr[d]
            let nc = current.col + dc[d]
            if ((((nr < 0) || (nr >= rows)) || (nc < 0)) || (nc >= cols)) {
                continue
            }
            if (grid[nr][nc] == 1) {
                continue
            }
            let neighbor = Cell(nr, nc)
            let nk = key(neighbor)
            if (closed.contains(nk)) {
                continue
            }
            let tentativeG = currentG + 1
            let prevG = (gScore.get(nk) ?? 999999)
            if (tentativeG < prevG) {
                gScore[nk] = tentativeG
                fScore[nk] = tentativeG + heuristic(neighbor, goal)
                var found = false
                for (o in openSet) {
                    if ((o.row == nr) && (o.col == nc)) {
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

main() {
    let grid = ArrayList([ArrayList([0, 0, 0, 0, 0]), ArrayList([0, 1, 1, 0, 0]), ArrayList([0, 0, 0, 0, 0]), ArrayList([0, 0, 1, 1, 0]), ArrayList([0, 0, 0, 0, 0])])
    let dist = aStarSearch(grid, Cell(0, 0), Cell(4, 4))
    println("Distance: ${dist}")
    let dist2 = aStarSearch(grid, Cell(0, 0), Cell(0, 4))
    println("Distance: ${dist2}")
    let blocked = ArrayList([ArrayList([0, 1]), ArrayList([1, 0])])
    let dist3 = aStarSearch(blocked, Cell(0, 0), Cell(1, 1))
    println("Distance: ${dist3}")
}
