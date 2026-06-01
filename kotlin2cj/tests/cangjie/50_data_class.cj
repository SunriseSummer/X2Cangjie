class Point <: ToString {
    let x: Int64
    let y: Int64
    init(x: Int64, y: Int64) {
        this.x = x
        this.y = y
    }
    public func toString(): String {
        return "Point(x=${this.x}, y=${this.y})"
    }
}

func dist2(a: Point, b: Point): Int64 {
    let dx = a.x - b.x
    let dy = a.y - b.y
    return (dx * dx) + (dy * dy)
}

main() {
    let p = Point(0, 0)
    let q = Point(3, 4)
    println("p=(${p.x}, ${p.y})")
    println(dist2(p, q))
}
