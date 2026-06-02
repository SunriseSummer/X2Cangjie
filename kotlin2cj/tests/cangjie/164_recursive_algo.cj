import std.collection.*

func hanoi(n: Int64, from: String, to: String, via: String, moves: ArrayList<String>): Unit {
    if (n == 1) {
        moves.add("${from}->${to}")
        return
    }
    hanoi(n - 1, from, via, to, moves)
    moves.add("${from}->${to}")
    hanoi(n - 1, via, to, from, moves)
}

func floodFill(grid: ArrayList<ArrayList<Int64>>, r: Int64, c: Int64, target: Int64, replacement: Int64): Unit {
    if ((((r < 0) || (r >= grid.size)) || (c < 0)) || (c >= grid[0].size)) {
        return
    }
    if (grid[r][c] != target) {
        return
    }
    grid[r][c] = replacement
    floodFill(grid, r - 1, c, target, replacement)
    floodFill(grid, r + 1, c, target, replacement)
    floodFill(grid, r, c - 1, target, replacement)
    floodFill(grid, r, c + 1, target, replacement)
}

main() {
    let moves = ArrayList<String>()
    hanoi(3, "A", "C", "B", moves)
    println("Hanoi(3): ${moves.size} moves")
    for (m in moves) {
        println(m)
    }
    let grid = ArrayList([ArrayList([1, 1, 0, 0]), ArrayList([1, 1, 0, 1]), ArrayList([0, 0, 1, 1]), ArrayList([0, 0, 1, 1])])
    floodFill(grid, 0, 0, 1, 2)
    for (row in grid) {
        let sb = StringBuilder()
        for (i in 0..=(row.size - 1)) {
            if (i > 0) {
                sb.append(" ")
            }
            sb.append(row[i])
        }
        println(sb.toString())
    }
}
