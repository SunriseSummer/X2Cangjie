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

main() {
    var sh: Shape = Square(3.0)
    println(Int64(sh.Area()))
    return 0
}
