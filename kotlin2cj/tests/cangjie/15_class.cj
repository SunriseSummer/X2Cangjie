class Point {
    let x: Int64
    let y: Int64
    init(x: Int64, y: Int64) {
        this.x = x
        this.y = y
    }
    func sumSquares(): Int64 {
        return (x * x) + (y * y)
    }
}

main() {
    let p = Point(3, 4)
    println("x=${p.x} y=${p.y} r2=${p.sumSquares()}")
}
