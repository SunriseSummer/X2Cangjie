import std.collection.*
import std.deriving.*

class Season <: ToString & Equatable<Season> {
    let _ordinal: Int64
    public let months: Int64
    init(_ordinal: Int64, months: Int64) {
        this._ordinal = _ordinal
        this.months = months
    }
    public static let SPRING = Season(0, 3)
    public static let SUMMER = Season(1, 3)
    public static let AUTUMN = Season(2, 3)
    public static let WINTER = Season(3, 3)
    public func toString(): String {
            if (this == Season.SPRING) { return "SPRING" }
            if (this == Season.SUMMER) { return "SUMMER" }
            if (this == Season.AUTUMN) { return "AUTUMN" }
            if (this == Season.WINTER) { return "WINTER" }
return "Season(?)"
    }
    public operator func ==(rhs: Season): Bool {
        return this._ordinal == rhs._ordinal
    }
    public operator func !=(rhs: Season): Bool {
        return !(this == rhs)
    }
}

main() {
    let seasons = ArrayList([Season.SPRING, Season.SUMMER, Season.AUTUMN, Season.WINTER])
    for (s in seasons) {
        println("${s}: ${s.months} months")
    }
    let current = Season.SUMMER
    println("Is summer? ${current == Season.SUMMER}")
    println("Is winter? ${current == Season.WINTER}")
}
