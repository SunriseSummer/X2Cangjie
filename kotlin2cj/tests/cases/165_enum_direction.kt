// Test: Enum with when-expression + direction simulation
enum class Direction {
    UP, DOWN, LEFT, RIGHT;
}

fun opposite(d: Direction): Direction = when (d) {
    Direction.UP -> Direction.DOWN
    Direction.DOWN -> Direction.UP
    Direction.LEFT -> Direction.RIGHT
    Direction.RIGHT -> Direction.LEFT
}

fun dx(d: Direction): Int = when (d) {
    Direction.RIGHT -> 1
    Direction.LEFT -> -1
    else -> 0
}

fun dy(d: Direction): Int = when (d) {
    Direction.DOWN -> 1
    Direction.UP -> -1
    else -> 0
}

fun main() {
    val dirs = arrayListOf(Direction.UP, Direction.RIGHT, Direction.RIGHT, Direction.DOWN, Direction.DOWN, Direction.LEFT)
    var x = 0
    var y = 0
    for (d in dirs) {
        x += dx(d)
        y += dy(d)
    }
    println("Position: ($x, $y)")

    for (d in arrayListOf(Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT)) {
        println("$d -> ${opposite(d)}")
    }

    // Path tracing
    val path = arrayListOf(Direction.RIGHT, Direction.RIGHT, Direction.UP, Direction.LEFT)
    val visited = ArrayList<String>()
    var cx = 0
    var cy = 0
    visited.add("($cx,$cy)")
    for (d in path) {
        cx += dx(d)
        cy += dy(d)
        visited.add("($cx,$cy)")
    }
    val sb = StringBuilder()
    for (i in 0..visited.size - 1) {
        if (i > 0) sb.append("->")
        sb.append(visited[i])
    }
    println(sb.toString())
}
