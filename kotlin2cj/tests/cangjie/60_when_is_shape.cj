import std.collection.*

open class Shape {}

class Circle <: Shape {
    let r: Int64
    init(r: Int64) {
        this.r = r
    }
}

class Rect <: Shape {
    let w: Int64
    let h: Int64
    init(w: Int64, h: Int64) {
        this.w = w
        this.h = h
    }
}

func area(s: Shape): Int64 {
    return match (s) {
        case s: Circle => (3 * s.r) * s.r
        case s: Rect => s.w * s.h
        case _ => 0}
}

main() {
    let shapes = ArrayList([Circle(2), Rect(3, 4), Circle(5)])
    var total = 0
    for (sh in shapes) {
        total = total + area(sh)
    }
    println(total)
}
