open class Point {
    var x: Int64 = 0
    var y: Int64 = 0
    public init(x: Int64, y: Int64) {
        this.x = x
        this.y = y
    }
    public open func sumSquares(): Int64 {
        return this.x * this.x + this.y * this.y
    }
}

let p = Point(3, 4)

main() {
    println("r2=${p.sumSquares()}")
    return 0
}
