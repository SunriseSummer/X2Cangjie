enum class Direction {
    NORTH, EAST, SOUTH, WEST
}
fun turnRight(d: Direction): Direction {
    return when (d) {
        Direction.NORTH -> Direction.EAST
        Direction.EAST -> Direction.SOUTH
        Direction.SOUTH -> Direction.WEST
        else -> Direction.NORTH
    }
}
fun name(d: Direction): String {
    return when (d) {
        Direction.NORTH -> "N"
        Direction.EAST -> "E"
        Direction.SOUTH -> "S"
        else -> "W"
    }
}
fun main() {
    var d = Direction.NORTH
    for (i in 0..3) {
        print(name(d))
        d = turnRight(d)
    }
    println("")
    println(d == Direction.NORTH)
}
