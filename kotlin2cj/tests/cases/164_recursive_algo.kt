// Test: Recursive algorithms - Tower of Hanoi + Flood Fill
fun hanoi(n: Int, from: String, to: String, via: String, moves: ArrayList<String>) {
    if (n == 1) {
        moves.add("$from->$to")
        return
    }
    hanoi(n - 1, from, via, to, moves)
    moves.add("$from->$to")
    hanoi(n - 1, via, to, from, moves)
}

fun floodFill(grid: ArrayList<ArrayList<Int>>, r: Int, c: Int, target: Int, replacement: Int) {
    if (r < 0 || r >= grid.size || c < 0 || c >= grid[0].size) return
    if (grid[r][c] != target) return
    grid[r][c] = replacement
    floodFill(grid, r - 1, c, target, replacement)
    floodFill(grid, r + 1, c, target, replacement)
    floodFill(grid, r, c - 1, target, replacement)
    floodFill(grid, r, c + 1, target, replacement)
}

fun main() {
    // Hanoi
    val moves = ArrayList<String>()
    hanoi(3, "A", "C", "B", moves)
    println("Hanoi(3): ${moves.size} moves")
    for (m in moves) {
        println(m)
    }

    // Flood fill
    val grid = arrayListOf(
        arrayListOf(1, 1, 0, 0),
        arrayListOf(1, 1, 0, 1),
        arrayListOf(0, 0, 1, 1),
        arrayListOf(0, 0, 1, 1)
    )
    floodFill(grid, 0, 0, 1, 2)
    for (row in grid) {
        val sb = StringBuilder()
        for (i in 0..row.size - 1) {
            if (i > 0) sb.append(" ")
            sb.append(row[i])
        }
        println(sb.toString())
    }
}
