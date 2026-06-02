import std.collection.*
import std.deriving.*

@Derive[Equatable]
enum Direction <: ToString {
    | NORTH | SOUTH | EAST | WEST
    public func toString(): String {
    return match (this) {
                case NORTH => "NORTH"
            case SOUTH => "SOUTH"
            case EAST => "EAST"
            case WEST => "WEST"
}
    }
}

@Derive[Equatable]
enum Priority <: ToString {
    | LOW | MEDIUM | HIGH | CRITICAL
    public func toString(): String {
    return match (this) {
                case LOW => "LOW"
            case MEDIUM => "MEDIUM"
            case HIGH => "HIGH"
            case CRITICAL => "CRITICAL"
}
    }
}

func opposite(d: Direction): Direction {
    return match (d) {
        case Direction.NORTH => Direction.SOUTH
        case Direction.SOUTH => Direction.NORTH
        case Direction.EAST => Direction.WEST
        case Direction.WEST => Direction.EAST}
}

func priorityLabel(p: Priority): String {
    return match (p) {
        case Priority.LOW => "[low]"
        case Priority.MEDIUM => "[med]"
        case Priority.HIGH => "[HIGH]"
        case Priority.CRITICAL => "[!!!]"}
}

main() {
    let dirs = ArrayList([Direction.NORTH, Direction.EAST, Direction.SOUTH, Direction.WEST])
    for (d in dirs) {
        println("${d} -> ${opposite(d)}")
    }
    let priorities = ArrayList([Priority.LOW, Priority.MEDIUM, Priority.HIGH, Priority.CRITICAL])
    for (p in priorities) {
        println("${priorityLabel(p)} ${p}")
    }
    println(Direction.NORTH == Direction.NORTH)
    println(Direction.NORTH == Direction.SOUTH)
}
