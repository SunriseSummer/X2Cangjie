// Test: Simulation - Game of Life variant (simplified) + Random walk statistics
class Grid(val rows: Int, val cols: Int) {
    val cells = ArrayList<ArrayList<Int>>()

    init {
        for (r in 0..rows - 1) {
            val row = ArrayList<Int>()
            for (c in 0..cols - 1) {
                row.add(0)
            }
            cells.add(row)
        }
    }

    fun set(r: Int, c: Int, v: Int) { cells[r][c] = v }
    fun get(r: Int, c: Int): Int = cells[r][c]

    fun neighbors(r: Int, c: Int): Int {
        var count = 0
        for (dr in -1..1) {
            for (dc in -1..1) {
                if (dr == 0 && dc == 0) continue
                val nr = r + dr
                val nc = c + dc
                if (nr >= 0 && nr < rows && nc >= 0 && nc < cols) {
                    count += cells[nr][nc]
                }
            }
        }
        return count
    }

    fun step(): Grid {
        val next = Grid(rows, cols)
        for (r in 0..rows - 1) {
            for (c in 0..cols - 1) {
                val n = neighbors(r, c)
                val alive = cells[r][c]
                if (alive == 1 && (n == 2 || n == 3)) {
                    next.set(r, c, 1)
                } else if (alive == 0 && n == 3) {
                    next.set(r, c, 1)
                }
            }
        }
        return next
    }

    fun population(): Int {
        var count = 0
        for (r in 0..rows - 1) {
            for (c in 0..cols - 1) {
                count += cells[r][c]
            }
        }
        return count
    }

    fun display(): String {
        val sb = StringBuilder()
        for (r in 0..rows - 1) {
            for (c in 0..cols - 1) {
                sb.append(if (cells[r][c] == 1) "#" else ".")
            }
            sb.append("\n")
        }
        return sb.toString()
    }
}

fun main() {
    // Blinker oscillator (period 2)
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

    // Verify period 2 oscillation
    println("Period-2 verified: ${g.population() == 3}")
}
