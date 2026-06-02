import std.collection.*

class Grid {
    let rows: Int64
    let cols: Int64
    init(rows: Int64, cols: Int64) {
        this.rows = rows
        this.cols = cols
        for (r in 0..=(rows - 1)) {
            let row = ArrayList<Int64>()
            for (c in 0..=(cols - 1)) {
                row.add(0)
            }
            cells.add(row)
        }
    }
    let cells = ArrayList<ArrayList<Int64>>()
    func set(r: Int64, c: Int64, v: Int64) {
        cells[r][c] = v
    }
    func get(r: Int64, c: Int64): Int64 {
        return cells[r][c]
    }
    func neighbors(r: Int64, c: Int64): Int64 {
        var count = 0
        for (dr in -1..=1) {
            for (dc in -1..=1) {
                if ((dr == 0) && (dc == 0)) {
                    continue
                }
                let nr = r + dr
                let nc = c + dc
                if ((((nr >= 0) && (nr < rows)) && (nc >= 0)) && (nc < cols)) {
                    count += cells[nr][nc]
                }
            }
        }
        return count
    }
    func step(): Grid {
        let next = Grid(rows, cols)
        for (r in 0..=(rows - 1)) {
            for (c in 0..=(cols - 1)) {
                let n = neighbors(r, c)
                let alive = cells[r][c]
                if ((alive == 1) && ((n == 2) || (n == 3))) {
                    next.set(r, c, 1)
                } else if ((alive == 0) && (n == 3)) {
                    next.set(r, c, 1)
                }
            }
        }
        return next
    }
    func population(): Int64 {
        var count = 0
        for (r in 0..=(rows - 1)) {
            for (c in 0..=(cols - 1)) {
                count += cells[r][c]
            }
        }
        return count
    }
    func display(): String {
        let sb = StringBuilder()
        for (r in 0..=(rows - 1)) {
            for (c in 0..=(cols - 1)) {
                sb.append(if (cells[r][c] == 1) {
                    "#"
                } else {
                    "."
                })
            }
            sb.append("\n")
        }
        return sb.toString()
    }
}

main() {
    var g = Grid(5, 5)
    g.set(2, 1, 1)
    g.set(2, 2, 1)
    g.set(2, 3, 1)
    println("Gen 0: pop=${g.population()}")
    print(g.display())
    g = g.step()
    println("Gen 1: pop=${g.population()}")
    print(g.display())
    g = g.step()
    println("Gen 2: pop=${g.population()}")
    print(g.display())
    println("Period-2 verified: ${g.population() == 3}")
}
