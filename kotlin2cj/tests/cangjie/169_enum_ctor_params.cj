import std.collection.*
import std.deriving.*

class Direction <: ToString & Equatable<Direction> {
    let _ordinal: Int64
    public let dx: Int64
    public let dy: Int64
    init(_ordinal: Int64, dx: Int64, dy: Int64) {
        this._ordinal = _ordinal
        this.dx = dx
        this.dy = dy
    }
    public static let UP = Direction(0, 0, -1)
    public static let DOWN = Direction(1, 0, 1)
    public static let LEFT = Direction(2, -1, 0)
    public static let RIGHT = Direction(3, 1, 0)
    public func toString(): String {
            if (this == Direction.UP) { return "UP" }
            if (this == Direction.DOWN) { return "DOWN" }
            if (this == Direction.LEFT) { return "LEFT" }
            if (this == Direction.RIGHT) { return "RIGHT" }
return "Direction(?)"
    }
    public operator func ==(rhs: Direction): Bool {
        return this._ordinal == rhs._ordinal
    }
    public operator func !=(rhs: Direction): Bool {
        return !(this == rhs)
    }
}

class Color <: ToString & Equatable<Color> {
    let _ordinal: Int64
    public let r: Int64
    public let g: Int64
    public let b: Int64
    init(_ordinal: Int64, r: Int64, g: Int64, b: Int64) {
        this._ordinal = _ordinal
        this.r = r
        this.g = g
        this.b = b
    }
    public static let RED = Color(0, 255, 0, 0)
    public static let GREEN = Color(1, 0, 255, 0)
    public static let BLUE = Color(2, 0, 0, 255)
    public static let WHITE = Color(3, 255, 255, 255)
    public func toString(): String {
            if (this == Color.RED) { return "RED" }
            if (this == Color.GREEN) { return "GREEN" }
            if (this == Color.BLUE) { return "BLUE" }
            if (this == Color.WHITE) { return "WHITE" }
return "Color(?)"
    }
    public operator func ==(rhs: Color): Bool {
        return this._ordinal == rhs._ordinal
    }
    public operator func !=(rhs: Color): Bool {
        return !(this == rhs)
    }
}

func move(x: Int64, y: Int64, dir: Direction): String {
    return "(${x + dir.dx}, ${y + dir.dy})"
}

main() {
    let dirs = ArrayList([Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT])
    for (d in dirs) {
        println("${d}: dx=${d.dx}, dy=${d.dy}")
    }
    println(move(5, 5, Direction.UP))
    println(move(5, 5, Direction.RIGHT))
    let colors = ArrayList([Color.RED, Color.GREEN, Color.BLUE, Color.WHITE])
    for (c in colors) {
        println("${c}: rgb=(${c.r},${c.g},${c.b})")
    }
    println(Direction.UP == Direction.UP)
    println(Direction.UP == Direction.DOWN)
}
