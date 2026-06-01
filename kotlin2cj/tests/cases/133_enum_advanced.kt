// Advanced enum usage with when matching and ordinal-based logic
enum class Direction {
    NORTH, SOUTH, EAST, WEST
}

enum class Priority {
    LOW, MEDIUM, HIGH, CRITICAL
}

fun opposite(d: Direction): Direction {
    return when (d) {
        Direction.NORTH -> Direction.SOUTH
        Direction.SOUTH -> Direction.NORTH
        Direction.EAST -> Direction.WEST
        Direction.WEST -> Direction.EAST
    }
}

fun priorityLabel(p: Priority): String {
    return when (p) {
        Priority.LOW -> "[low]"
        Priority.MEDIUM -> "[med]"
        Priority.HIGH -> "[HIGH]"
        Priority.CRITICAL -> "[!!!]"
    }
}

fun main() {
    // Direction opposites
    val dirs = arrayListOf(Direction.NORTH, Direction.EAST, Direction.SOUTH, Direction.WEST)
    for (d in dirs) {
        println("$d -> ${opposite(d)}")
    }

    // Priority labels
    val priorities = arrayListOf(Priority.LOW, Priority.MEDIUM, Priority.HIGH, Priority.CRITICAL)
    for (p in priorities) {
        println("${priorityLabel(p)} $p")
    }

    // Enum comparison
    println(Direction.NORTH == Direction.NORTH)
    println(Direction.NORTH == Direction.SOUTH)
}
