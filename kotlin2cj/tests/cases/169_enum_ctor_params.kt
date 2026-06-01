// Test: Enum with constructor parameters
enum class Direction(val dx: Int, val dy: Int) {
    UP(0, -1),
    DOWN(0, 1),
    LEFT(-1, 0),
    RIGHT(1, 0)
}

enum class Color(val r: Int, val g: Int, val b: Int) {
    RED(255, 0, 0),
    GREEN(0, 255, 0),
    BLUE(0, 0, 255),
    WHITE(255, 255, 255)
}

fun move(x: Int, y: Int, dir: Direction): String {
    return "(${x + dir.dx}, ${y + dir.dy})"
}

fun main() {
    val dirs = listOf(Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT)
    for (d in dirs) {
        println("${d}: dx=${d.dx}, dy=${d.dy}")
    }

    println(move(5, 5, Direction.UP))
    println(move(5, 5, Direction.RIGHT))

    // Color enum with properties
    val colors = listOf(Color.RED, Color.GREEN, Color.BLUE, Color.WHITE)
    for (c in colors) {
        println("${c}: rgb=(${c.r},${c.g},${c.b})")
    }

    // Equality
    println(Direction.UP == Direction.UP)
    println(Direction.UP == Direction.DOWN)
}
