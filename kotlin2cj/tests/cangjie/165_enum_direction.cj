import std.collection.*
import std.deriving.*

@Derive[Equatable]
enum Direction <: ToString {
    | UP | DOWN | LEFT | RIGHT
    public func toString(): String {
    return match (this) {
                case UP => "UP"
            case DOWN => "DOWN"
            case LEFT => "LEFT"
            case RIGHT => "RIGHT"
}
    }
}

func opposite(d: Direction): Direction {
    return match (d) {
        case Direction.UP => Direction.DOWN
        case Direction.DOWN => Direction.UP
        case Direction.LEFT => Direction.RIGHT
        case Direction.RIGHT => Direction.LEFT}
}

func dx(d: Direction): Int64 {
    return match (d) {
        case Direction.RIGHT => 1
        case Direction.LEFT => -1
        case _ => 0}
}

func dy(d: Direction): Int64 {
    return match (d) {
        case Direction.DOWN => 1
        case Direction.UP => -1
        case _ => 0}
}

main() {
    let dirs = ArrayList([Direction.UP, Direction.RIGHT, Direction.RIGHT, Direction.DOWN, Direction.DOWN, Direction.LEFT])
    var x = 0
    var y = 0
    for (d in dirs) {
        x += dx(d)
        y += dy(d)
    }
    println("Position: (${x}, ${y})")
    for (d in ArrayList([Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT])) {
        println("${d} -> ${opposite(d)}")
    }
    let path = ArrayList([Direction.RIGHT, Direction.RIGHT, Direction.UP, Direction.LEFT])
    let visited = ArrayList<String>()
    var cx = 0
    var cy = 0
    visited.add("(${cx},${cy})")
    for (d in path) {
        cx += dx(d)
        cy += dy(d)
        visited.add("(${cx},${cy})")
    }
    let sb = StringBuilder()
    for (i in 0..=(visited.size - 1)) {
        if (i > 0) {
            sb.append("->")
        }
        sb.append(visited[i])
    }
    println(sb.toString())
}
