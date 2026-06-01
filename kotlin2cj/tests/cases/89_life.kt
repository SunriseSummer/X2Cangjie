// Generalization probe 3: Conway's Game of Life + grid analytics.
class Grid(val rows: Int, val cols: Int) {
    val cells = ArrayList<ArrayList<Boolean>>()

    init {
        for (r in 0 until rows) {
            val row = ArrayList<Boolean>()
            for (c in 0 until cols) {
                row.add(false)
            }
            cells.add(row)
        }
    }

    fun set(r: Int, c: Int, v: Boolean) {
        cells[r][c] = v
    }

    fun get(r: Int, c: Int): Boolean {
        if (r < 0 || r >= rows || c < 0 || c >= cols) {
            return false
        }
        return cells[r][c]
    }

    fun liveNeighbors(r: Int, c: Int): Int {
        var count = 0
        for (dr in -1..1) {
            for (dc in -1..1) {
                if (dr == 0 && dc == 0) {
                    continue
                }
                if (get(r + dr, c + dc)) {
                    count = count + 1
                }
            }
        }
        return count
    }

    fun step(): Grid {
        val next = Grid(rows, cols)
        for (r in 0 until rows) {
            for (c in 0 until cols) {
                val n = liveNeighbors(r, c)
                val alive = get(r, c)
                if (alive && (n == 2 || n == 3)) {
                    next.set(r, c, true)
                } else if (!alive && n == 3) {
                    next.set(r, c, true)
                }
            }
        }
        return next
    }

    fun population(): Int {
        var count = 0
        for (r in 0 until rows) {
            for (c in 0 until cols) {
                if (cells[r][c]) {
                    count = count + 1
                }
            }
        }
        return count
    }

    fun render(): String {
        val sb = StringBuilder()
        for (r in 0 until rows) {
            for (c in 0 until cols) {
                if (cells[r][c]) {
                    sb.append("*")
                } else {
                    sb.append(".")
                }
            }
            sb.append("\n")
        }
        return sb.toString()
    }
}

fun main() {
    val g = Grid(5, 5)
    // blinker
    g.set(2, 1, true)
    g.set(2, 2, true)
    g.set(2, 3, true)

    println("=== Generation 0 ===")
    print(g.render())
    println("Population: ${g.population()}")

    var cur = g
    val history = ArrayList<Int>()
    history.add(cur.population())
    for (gen in 1..4) {
        cur = cur.step()
        history.add(cur.population())
        println("=== Generation $gen ===")
        print(cur.render())
        println("Population: ${cur.population()}")
    }

    println("=== Population history ===")
    println(history.joinToString(" -> "))
    println("Peak: ${history.maxOrNull() ?: 0}")
    println("Total over time: ${history.sum()}")

    // glider on a bigger grid
    val big = Grid(6, 6)
    big.set(0, 1, true)
    big.set(1, 2, true)
    big.set(2, 0, true)
    big.set(2, 1, true)
    big.set(2, 2, true)
    println("=== Glider start (pop ${big.population()}) ===")
    var gg = big
    for (gen in 1..3) {
        gg = gg.step()
    }
    println("After 3 steps, population: ${gg.population()}")
    print(gg.render())
}
