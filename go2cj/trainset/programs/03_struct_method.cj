open class Point {
    public var X: Int64
    public var Y: Int64
    public init(X: Int64, Y: Int64) {
        this.X = X
        this.Y = Y
    }
    public func Sum(): Int64 {
        return this.X + this.Y
    }
}

main(): Unit {
    var p = Point(X: 3, Y: 4)
    println(p.Sum())
    return 0
}
