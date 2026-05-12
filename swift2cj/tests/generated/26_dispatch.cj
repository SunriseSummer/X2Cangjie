import std.collection.*

open class Shape {
    public open func area(): Int64 {
        return 0
    }
}

open class Rect <: Shape {
    var w: Int64 = 0
    var h: Int64 = 0
    public init(w: Int64, h: Int64) {
        this.w = w
        this.h = h
    }
    public override func area(): Int64 {
        return this.w * this.h
    }
}

open class Sq <: Shape {
    var s: Int64 = 0
    public init(s: Int64) {
        this.s = s
    }
    public override func area(): Int64 {
        return this.s * this.s
    }
}

let shapes: ArrayList<Shape> = ArrayList<Shape>([Rect(3, 4), Sq(5), Rect(2, 6)])

main() {
    for (s in shapes) {
        println(s.area())
    }
    return 0
}
