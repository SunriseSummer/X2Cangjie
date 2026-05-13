interface Shape {
    func Area(): Float64
}

open class Square <: Shape {
    public var Side: Float64
    public init(Side: Float64) {
        this.Side = Side
    }
    public override func Area(): Float64 {
        return this.Side * this.Side
    }
}

main(): Unit {
    var sh: Shape = Square(Side: 3.0)
    println(sh.Area())
    return 0
}
