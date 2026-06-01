import std.deriving.*

@Derive[Equatable]
enum Direction <: ToString {
    | NORTH | EAST | SOUTH | WEST
    public func toString(): String {
    return match (this) {
                case NORTH => "NORTH"
            case EAST => "EAST"
            case SOUTH => "SOUTH"
            case WEST => "WEST"
}
    }
}

func turnRight(d: Direction): Direction {
    return match (d) {
        case Direction.NORTH => Direction.EAST
        case Direction.EAST => Direction.SOUTH
        case Direction.SOUTH => Direction.WEST
        case _ => Direction.NORTH}
}

func name(d: Direction): String {
    return match (d) {
        case Direction.NORTH => "N"
        case Direction.EAST => "E"
        case Direction.SOUTH => "S"
        case _ => "W"}
}

main() {
    var d = Direction.NORTH
    for (i in 0..=3) {
        print(name(d))
        d = turnRight(d)
    }
    println("")
    println(d == Direction.NORTH)
}
