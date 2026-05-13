open class Point {
    public var X: Int64
    public var Y: Int64
    public init(X: Int64, Y: Int64) {
        this.X = X
        this.Y = Y
    }
}

main() {
    var p = Point(3, 4)
    println(p.X)
    println(p.Y)
    return 0
}
